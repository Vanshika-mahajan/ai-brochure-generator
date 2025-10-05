from flask import Flask, request, jsonify, render_template, send_from_directory
from brochure_logic import create_brochure_from_url
import os

app = Flask(__name__)

# This will store the generated PDFs
OUTPUT_FOLDER = 'output'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the brochure generation
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    print(f"Received request to generate brochure for: {url}")
    # Run your main logic
    filename = create_brochure_from_url(url)
    
    if filename:
        return jsonify({'download_url': f'/download/{filename}'})
    else:
        return jsonify({'error': 'Failed to generate brochure. Check the console for details.'}), 500

# Route to download the generated PDF
@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)