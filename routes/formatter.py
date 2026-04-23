"""Formatter routes: /api/clean, /api/format, /api/themes, /api/sample"""
from flask import Blueprint, request, jsonify
from config import SAMPLE_FILE, login_required
from blogformat import THEMES, parse_input, render as render_post
from html_utils import _is_html, _html_to_plain, _auto_inject_title
from img_cleaner import clean_html_string as extract_img_tags

formatter_bp = Blueprint('formatter', __name__)


@formatter_bp.route('/api/clean', methods=['POST'])
@login_required
def api_clean():
    data = request.get_json()
    html = data.get('html', '')
    tags = extract_img_tags(html)
    return jsonify({'tags': tags, 'count': len(tags), 'html': '\n'.join(tags)})


@formatter_bp.route('/api/format', methods=['POST'])
@login_required
def api_format():
    data = request.get_json()
    text = data.get('text', '')
    theme_name = data.get('theme', 'navy_gold')
    theme = THEMES.get(theme_name, THEMES['navy_gold'])

    html_stripped = False
    if _is_html(text):
        text = _html_to_plain(text)
        html_stripped = True

    text = _auto_inject_title(text)
    post = parse_input(text)
    html_out = render_post(post, theme)
    return jsonify({'html': html_out, 'html_stripped': html_stripped})


@formatter_bp.route('/api/themes')
@login_required
def api_themes():
    return jsonify({'themes': [
        {'key': k, 'name': v.name, 'primary': v.primary, 'accent': v.accent, 'bg': v.bg}
        for k, v in THEMES.items()
    ]})


@formatter_bp.route('/api/sample')
@login_required
def api_sample():
    with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
        return jsonify({'text': f.read()})
