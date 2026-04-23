"""Feed/backup routes: /feed/generate, /feed/status, /feed/files, /feed/select, /feed/labels, /feed/posts, /feed/post/<idx>"""
import os
from flask import Blueprint, request, jsonify
from config import BASE, login_required
from blogger_client import _get_service

feed_bp = Blueprint('feed', __name__)

FEED_DIR = os.path.join(BASE, 'blog_backup')
_feed_cache = None
_active_feed = None


def _list_feed_files():
    if not os.path.isdir(FEED_DIR):
        return []
    return sorted(
        [fn for fn in os.listdir(FEED_DIR)
         if fn.endswith('.atom') and os.path.isfile(os.path.join(FEED_DIR, fn))],
        reverse=True,
    )


def _resolve_active_feed():
    global _active_feed
    if _active_feed and os.path.exists(os.path.join(FEED_DIR, _active_feed)):
        return _active_feed
    files = _list_feed_files()
    _active_feed = files[0] if files else None
    return _active_feed


def _parse_feed():
    global _feed_cache
    if _feed_cache is not None:
        return _feed_cache
    filename = _resolve_active_feed()
    if not filename:
        _feed_cache = []
        return _feed_cache
    feed_path = os.path.join(FEED_DIR, filename)
    if not os.path.exists(feed_path):
        _feed_cache = []
        return _feed_cache
    import xml.etree.ElementTree as ET
    import html as _html_lib
    tree = ET.parse(feed_path)
    root = tree.getroot()
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'blogger': 'http://schemas.google.com/blogger/2018',
    }
    posts = []
    for entry in root.findall('atom:entry', ns):
        btype = entry.find('blogger:type', ns)
        if btype is None or btype.text != 'POST':
            continue
        title_el = entry.find('atom:title', ns)
        title = title_el.text if title_el is not None else '(no title)'
        content_el = entry.find('atom:content', ns)
        content_raw = content_el.text if content_el is not None else ''
        content_html = _html_lib.unescape(content_raw) if content_raw else ''
        published_el = entry.find('atom:published', ns)
        published = published_el.text if published_el is not None else ''
        updated_el = entry.find('atom:updated', ns)
        updated = updated_el.text if updated_el is not None else ''
        status_el = entry.find('blogger:status', ns)
        status = status_el.text if status_el is not None else ''
        filename_el = entry.find('blogger:filename', ns)
        fn = filename_el.text if filename_el is not None else ''
        labels = [cat.get('term', '') for cat in entry.findall('atom:category', ns)
                  if cat.get('term', '')]
        posts.append({
            'title': title, 'content': content_html,
            'published': published, 'updated': updated,
            'status': status, 'filename': fn, 'labels': labels,
        })
    posts.sort(key=lambda p: p['published'], reverse=True)
    for i, p in enumerate(posts):
        p['idx'] = i
    _feed_cache = posts
    return _feed_cache


@feed_bp.route('/feed/generate', methods=['POST'])
@login_required
def feed_generate():
    global _feed_cache, _active_feed
    svc = _get_service()
    if not svc:
        return jsonify({'error': 'Not authenticated with Blogger — connect in Blog Editor first'}), 401
    data = request.get_json() or {}
    blog_id = data.get('blog_id', '').strip()
    if not blog_id:
        return jsonify({'error': 'blog_id required'}), 400

    import html as _html_lib
    import re
    from urllib.parse import urlparse
    from datetime import datetime

    try:
        blog_info = svc.blogs().get(blogId=blog_id).execute()
        blog_name = blog_info.get('name', '')
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    slug = re.sub(r'[^a-z0-9]', '', blog_name.lower())
    date_str = datetime.now().strftime('%Y%m%d')
    save_filename = f'{slug}_{date_str}.atom'

    all_posts = []
    page_token = None
    while True:
        params = dict(blogId=blog_id, maxResults=50, orderBy='PUBLISHED',
                      status=['LIVE', 'DRAFT'], fetchImages=False)
        if page_token:
            params['pageToken'] = page_token
        try:
            r = svc.posts().list(**params).execute()
        except Exception as e:
            return jsonify({'error': str(e), 'fetched': len(all_posts)}), 400
        all_posts.extend(r.get('items', []))
        page_token = r.get('nextPageToken')
        if not page_token:
            break

    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<feed xmlns='http://www.w3.org/2005/Atom' xmlns:blogger='http://schemas.google.com/blogger/2018'>",
        f"  <id>tag:blogger.com,1999:blog-{blog_id}</id>",
        f"  <title>{_html_lib.escape(blog_name)}</title>",
    ]
    for p in all_posts:
        title     = _html_lib.escape(p.get('title', ''))
        content   = _html_lib.escape(p.get('content', ''))
        published = p.get('published', '')
        updated   = p.get('updated', '')
        status    = p.get('status', 'LIVE')
        labels    = p.get('labels', [])
        fn        = urlparse(p.get('url', '')).path or ''
        lines += [
            "  <entry>",
            "    <blogger:type>POST</blogger:type>",
            f"    <blogger:status>{status}</blogger:status>",
            f"    <title>{title}</title>",
            f"    <published>{published}</published>",
            f"    <updated>{updated}</updated>",
            f"    <content type='html'>{content}</content>",
        ]
        for lbl in labels:
            lines.append(f"    <category scheme='tag:blogger.com,1999:blog-{blog_id}' term='{_html_lib.escape(lbl)}'/>")
        if fn:
            lines.append(f"    <blogger:filename>{fn}</blogger:filename>")
        lines.append("  </entry>")
    lines.append("</feed>")

    os.makedirs(FEED_DIR, exist_ok=True)
    save_path = os.path.join(FEED_DIR, save_filename)
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    _active_feed = save_filename
    _feed_cache = None
    posts = _parse_feed()
    return jsonify({'success': True, 'count': len(posts), 'blog_name': blog_name,
                    'filename': save_filename, 'files': _list_feed_files()})


@feed_bp.route('/feed/status')
@login_required
def feed_status():
    files = _list_feed_files()
    active = _resolve_active_feed()
    exists = active is not None
    count, years = 0, []
    if exists:
        posts = _parse_feed()
        count = len(posts)
        years = sorted({p['published'][:4] for p in posts if p['published']}, reverse=True)
    return jsonify({'exists': exists, 'count': count, 'years': years,
                    'file': active, 'files': files})


@feed_bp.route('/feed/files')
@login_required
def feed_files():
    files = _list_feed_files()
    active = _resolve_active_feed()
    return jsonify({'files': files, 'active': active})


@feed_bp.route('/feed/select', methods=['POST'])
@login_required
def feed_select():
    global _feed_cache, _active_feed
    data = request.get_json() or {}
    filename = data.get('filename', '').strip()
    if not filename:
        return jsonify({'error': 'filename required'}), 400
    if '/' in filename or '\\' in filename or '..' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    path = os.path.join(FEED_DIR, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    _active_feed = filename
    _feed_cache = None
    posts = _parse_feed()
    years = sorted({p['published'][:4] for p in posts if p['published']}, reverse=True)
    return jsonify({'success': True, 'count': len(posts), 'years': years, 'file': filename})


@feed_bp.route('/feed/labels')
@login_required
def feed_labels():
    posts = _parse_feed()
    counts = {}
    for p in posts:
        for lbl in p['labels']:
            counts[lbl] = counts.get(lbl, 0) + 1
    labels = sorted(counts.items(), key=lambda x: -x[1])
    return jsonify({'labels': [{'name': n, 'count': c} for n, c in labels]})


@feed_bp.route('/feed/posts')
@login_required
def feed_posts():
    posts = _parse_feed()
    search = request.args.get('search', '').strip().lower()
    year   = request.args.get('year', '').strip()
    label  = request.args.get('label', '').strip()
    page   = max(1, int(request.args.get('page', 1)))
    per_page = 40

    filtered = posts
    if search:
        filtered = [p for p in filtered if search in p['title'].lower()]
    if year:
        filtered = [p for p in filtered if p['published'].startswith(year)]
    if label:
        filtered = [p for p in filtered if label in p['labels']]

    total = len(filtered)
    start = (page - 1) * per_page
    items = filtered[start:start + per_page]
    result = [{'idx': p['idx'], 'title': p['title'], 'published': p['published'],
               'labels': p['labels'], 'status': p['status']} for p in items]
    return jsonify({'posts': result, 'total': total, 'page': page, 'per_page': per_page,
                    'has_more': start + per_page < total})


@feed_bp.route('/feed/post/<int:idx>')
@login_required
def feed_get_post(idx):
    posts = _parse_feed()
    if idx < 0 or idx >= len(posts):
        return jsonify({'error': 'Not found'}), 404
    p = posts[idx]
    return jsonify({'idx': idx, 'title': p['title'], 'published': p['published'],
                    'updated': p['updated'], 'labels': p['labels'],
                    'status': p['status'], 'filename': p['filename'],
                    'content': p['content']})
