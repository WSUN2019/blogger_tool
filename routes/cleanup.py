"""Cleanup routes: /blogger/cleanup/scan, /blogger/cleanup/fix-one"""
import re
from flask import Blueprint, request, jsonify
from config import login_required
from blogger_client import _get_service

cleanup_bp = Blueprint('cleanup', __name__)

_DEFAULT_FONTS_TAG = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Playfair+Display:ital,wght@0,400;0,700;1,400&amp;'
    'family=Lato:wght@300;400;700&amp;display=swap" rel="stylesheet"></link>'
)


def _build_tag_re(tag: str):
    base = re.sub(r'\s*</link>\s*$', '', tag.strip(), flags=re.IGNORECASE)
    return re.compile(re.escape(base) + r'\s*(?:</link>)?', re.IGNORECASE)


def _strip_custom_tag(html: str, tag: str) -> str:
    return _build_tag_re(tag).sub('', html).strip()


@cleanup_bp.route('/blogger/cleanup/scan', methods=['POST'])
@login_required
def blogger_cleanup_scan():
    svc = _get_service()
    if not svc:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json() or {}
    blog_id = data.get('blog_id', '')
    tag = data.get('tag', _DEFAULT_FONTS_TAG).strip()
    if not blog_id:
        return jsonify({'error': 'blog_id required'}), 400
    try:
        pattern = _build_tag_re(tag)
        affected = []
        page_token = None
        while True:
            params = dict(blogId=blog_id, maxResults=50, orderBy='PUBLISHED',
                          status=['LIVE', 'DRAFT'], fetchImages=False)
            if page_token:
                params['pageToken'] = page_token
            r = svc.posts().list(**params).execute()
            for p in r.get('items', []):
                if pattern.search(p.get('content', '')):
                    affected.append({'id': p['id'], 'title': p['title'],
                                     'published': p.get('published', ''),
                                     'url': p.get('url', '')})
            page_token = r.get('nextPageToken')
            if not page_token:
                break
        return jsonify({'affected': affected, 'count': len(affected)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@cleanup_bp.route('/blogger/cleanup/fix-one', methods=['POST'])
@login_required
def blogger_cleanup_fix_one():
    svc = _get_service()
    if not svc:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json() or {}
    blog_id = data.get('blog_id', '')
    post_id = data.get('post_id', '')
    tag = data.get('tag', _DEFAULT_FONTS_TAG).strip()
    if not blog_id or not post_id:
        return jsonify({'error': 'blog_id and post_id required'}), 400
    try:
        p = svc.posts().get(blogId=blog_id, postId=post_id).execute()
        cleaned = _strip_custom_tag(p.get('content', ''), tag)
        body = {'id': post_id, 'title': p['title'], 'content': cleaned}
        if 'labels' in p:
            body['labels'] = p['labels']
        svc.posts().update(blogId=blog_id, postId=post_id, body=body).execute()
        return jsonify({'status': 'fixed', 'title': p['title']})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})
