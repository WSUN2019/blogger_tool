"""Gemini routes: /api/gemini-status, /api/save-gemini-key, /api/save-gemini-model, /api/smart-format"""
import os
from flask import Blueprint, request, jsonify
from config import GEMINI_KEY_FILE, GEMINI_MODEL_FILE, login_required
from blogformat import THEMES, parse_input, render as render_post
from gemini_client import (GEMINI_MODELS, GEMINI_PROMPT,
                           _get_gemini_key, _get_gemini_model)

gemini_bp = Blueprint('gemini', __name__)


@gemini_bp.route('/api/gemini-status')
@login_required
def api_gemini_status():
    return jsonify({
        'configured': bool(_get_gemini_key()),
        'model': _get_gemini_model(),
        'models': GEMINI_MODELS,
    })


@gemini_bp.route('/api/save-gemini-model', methods=['POST'])
@login_required
def api_save_gemini_model():
    model_id = (request.get_json() or {}).get('model', '').strip()
    valid_ids = {m['id'] for m in GEMINI_MODELS}
    if model_id not in valid_ids:
        return jsonify({'error': 'Invalid model'}), 400
    os.makedirs(os.path.dirname(GEMINI_MODEL_FILE), exist_ok=True)
    with open(GEMINI_MODEL_FILE, 'w') as f:
        f.write(model_id)
    return jsonify({'success': True, 'model': model_id})


@gemini_bp.route('/api/save-gemini-key', methods=['POST'])
@login_required
def api_save_gemini_key():
    key = (request.get_json() or {}).get('key', '').strip()
    os.makedirs(os.path.dirname(GEMINI_KEY_FILE), exist_ok=True)
    with open(GEMINI_KEY_FILE, 'w') as f:
        f.write(key)
    return jsonify({'success': True})


@gemini_bp.route('/api/smart-format', methods=['POST'])
@login_required
def api_smart_format():
    data = request.get_json()
    text = data.get('text', '').strip()
    theme_name = data.get('theme', 'navy_gold')
    model_id = data.get('model', '').strip() or _get_gemini_model()
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    api_key = _get_gemini_key()
    if not api_key:
        return jsonify({'error': 'no_key'}), 400

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_id,
            contents=GEMINI_PROMPT + text,
        )
        structured = response.text.strip()

        if structured.startswith('```'):
            lines = structured.splitlines()
            start = 1
            end = len(lines) - 1 if lines[-1].strip() == '```' else len(lines)
            structured = '\n'.join(lines[start:end]).strip()

        theme = THEMES.get(theme_name, THEMES['navy_gold'])
        post = parse_input(structured)
        html_out = render_post(post, theme)
        return jsonify({'html': html_out, 'structured_text': structured, 'model': model_id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
