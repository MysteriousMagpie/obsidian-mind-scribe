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

@app.route('/api/message', methods=['POST'])
def message():
    data = request.get_json() or {}
    # Default to 7 days; you could parse data.get('message') for custom days
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
    # Read port from environment (default 5000) so you can override if needed
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
