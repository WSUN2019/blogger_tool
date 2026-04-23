"""Version history routes: /versions/save, /versions/<post_id>, /versions/<post_id>/<ts>"""
import os
from flask import Blueprint, request, jsonify
from config import BASE, login_required

versions_bp = Blueprint('versions', __name__)

VERSIONS_DIR = os.path.join(BASE, 'blog_backup', 'versions')


def _versions_file(post_id: str) -> str:
    return os.path.join(VERSIONS_DIR, f'{post_id}.atom')


def _read_versions(post_id: str) -> list:
    path = _versions_file(post_id)
    if not os.path.exists(path):
        return []
    import xml.etree.ElementTree as ET
    import html as _html_lib
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        versions = []
        for entry in root.findall('atom:entry', ns):
            pub_el = entry.find('atom:published', ns)
            title_el = entry.find('atom:title', ns)
            content_el = entry.find('atom:content', ns)
            versions.append({
                'ts': pub_el.text if pub_el is not None else '',
                'title': title_el.text if title_el is not None else '',
                'content': _html_lib.unescape(content_el.text or '') if content_el is not None else '',
            })
        versions.sort(key=lambda v: v['ts'], reverse=True)
        return versions
    except Exception:
        return []


def _write_versions(post_id: str, versions: list):
    import html as _html_lib
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    lines = ["<?xml version='1.0' encoding='UTF-8'?>",
             "<feed xmlns='http://www.w3.org/2005/Atom'>",
             f"  <id>versions:{post_id}</id>"]
    for v in versions:
        escaped = _html_lib.escape(v['content'])
        lines += [
            "  <entry>",
            f"    <title>{_html_lib.escape(v['title'])}</title>",
            f"    <published>{v['ts']}</published>",
            f"    <content type='html'>{escaped}</content>",
            "  </entry>",
        ]
    lines.append("</feed>")
    with open(_versions_file(post_id), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


@versions_bp.route('/versions/save', methods=['POST'])
@login_required
def versions_save():
    data = request.get_json() or {}
    post_id = data.get('post_id', '').strip()
    title   = data.get('title', '').strip()
    content = data.get('content', '')
    if not post_id:
        return jsonify({'error': 'post_id required'}), 400
    from datetime import timezone, datetime
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    versions = _read_versions(post_id)
    versions.insert(0, {'ts': ts, 'title': title, 'content': content})
    _write_versions(post_id, versions)
    return jsonify({'success': True, 'ts': ts, 'count': len(versions)})


@versions_bp.route('/versions/<post_id>')
@login_required
def versions_list(post_id):
    versions = _read_versions(post_id)
    return jsonify({'versions': [{'ts': v['ts'], 'title': v['title']} for v in versions]})


@versions_bp.route('/versions/<post_id>/<ts>')
@login_required
def versions_get(post_id, ts):
    versions = _read_versions(post_id)
    for v in versions:
        if v['ts'] == ts:
            return jsonify(v)
    return jsonify({'error': 'Not found'}), 404


@versions_bp.route('/versions/<post_id>/<ts>', methods=['DELETE'])
@login_required
def versions_delete(post_id, ts):
    versions = _read_versions(post_id)
    new_versions = [v for v in versions if v['ts'] != ts]
    if len(new_versions) == len(versions):
        return jsonify({'error': 'Not found'}), 404
    _write_versions(post_id, new_versions)
    return jsonify({'success': True, 'count': len(new_versions)})
