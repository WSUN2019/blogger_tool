"""Config routes: /config/blog-url"""
import os
from flask import Blueprint, request, jsonify
from config import BLOG_URL_FILE, login_required

config_bp = Blueprint('config_routes', __name__)


@config_bp.route('/config/blog-url')
@login_required
def config_get_blog_url():
    url = ''
    if os.path.exists(BLOG_URL_FILE):
        url = open(BLOG_URL_FILE).read().strip()
    return jsonify({'url': url})


@config_bp.route('/config/blog-url', methods=['POST'])
@login_required
def config_save_blog_url():
    url = (request.get_json() or {}).get('url', '').strip()
    os.makedirs(os.path.dirname(BLOG_URL_FILE), exist_ok=True)
    with open(BLOG_URL_FILE, 'w') as f:
        f.write(url)
    return jsonify({'success': True})
