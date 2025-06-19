import os
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
import markdown

# Import and configure Obsidian Agent modules (installed via pip editable)
try:
    from agent.config import config
    from agent.summarizer import process_observation_notes, generate_weekly_review_markdown
    from agent.writer import ensure_vault_structure
except ImportError as e:
    raise ImportError(f"Failed to import Obsidian Agent modules: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Welcome to the Obsidian Agent API!"

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/message', methods=['POST'])
def message():
    data = request.get_json() or {}
    user_message = data.get('message', '')
    date_range = data.get('dateRange', 7)
    # Support 'all' as a special value for all time
    if date_range == 'all':
        days = 3650  # 10 years, effectively 'all time'
    else:
        try:
            days = int(date_range)
        except Exception:
            days = 7
    try:
        config.validate()
        ensure_vault_structure()
        processed = process_observation_notes(days)
        markdown_content = generate_weekly_review_markdown(processed)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    html_preview = markdown.markdown(markdown_content)
    return jsonify({
        'response': markdown_content,
        'preview': html_preview,
    })

if __name__ == '__main__':
    # Read port from environment 
    port = int(os.environ.get('FLASK_PORT', 5100))
    app.run(debug=True, host='0.0.0.0', port=port)
