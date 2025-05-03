from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS  # Import Flask-CORS
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename
from main import main as process_pdf
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration with absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'outputs')
ALLOWED_EXTENSIONS = {'pdf'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# In-memory task storage
# In a production app, use a database instead
tasks = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def background_process(task_id, filepath, custom_prompt=None):
    """Process the PDF in a background thread"""
    try:
        # Update task status to processing
        tasks[task_id]['status'] = 'PROCESSING'
        
        # Call the main processing function
        output_filename = process_pdf(filepath)
        
        if output_filename:
            # Update task status to complete
            tasks[task_id]['status'] = 'COMPLETED'
            tasks[task_id]['result'] = {
                'audio_url': f'/audio/{os.path.basename(output_filename)}',
                'message': 'PDF processed successfully'
            }
        else:
            # Update task status to failed
            tasks[task_id]['status'] = 'FAILED'
            tasks[task_id]['result'] = {
                'error': 'Processing failed'
            }
    except Exception as e:
        # Update task status to failed with error message
        tasks[task_id]['status'] = 'FAILED'
        tasks[task_id]['result'] = {
            'error': str(e)
        }

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Castify - Convert PDFs to Podcasts</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .form-container { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Castify - Convert PDFs to Podcasts</h1>
            <div class="form-container">
                <h2>Upload a PDF</h2>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".pdf" required>
                    <textarea name="prompt" rows="4" cols="50" placeholder="Optional: Custom prompt for your podcast. Leave blank for default."></textarea>
                    <br><br>
                    <input type="submit" value="Generate Podcast">
                </form>
            </div>
        </body>
    </html>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Generate a unique filename
        filename = task_id + '_' + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get custom prompt if provided
        prompt = request.form.get('prompt', None)
        
        # Initialize task data
        tasks[task_id] = {
            'id': task_id,
            'status': 'PENDING',
            'filename': filename,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'result': None
        }
        
        # Start processing in a background thread
        thread = threading.Thread(
            target=background_process, 
            args=(task_id, filepath, prompt)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'task_id': task_id,
            'status_url': f'/status/{task_id}'
        })
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/status/<task_id>')
def task_status(task_id):
    task = tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    response = {
        'id': task_id,
        'status': task['status'],
        'created_at': task['created_at']
    }
    
    # Add result data if available
    if task['result']:
        response['result'] = task['result']
    
    return jsonify(response)

@app.route('/audio/<filename>')
def get_audio(filename):
    """Serve audio files from the output directory"""
    try:
        # Check if the file exists
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        print(f"Looking for file at: {file_path}")
        if not os.path.exists(file_path):
            return jsonify({'error': f"File {filename} not found at {file_path}"}), 404
            
        # Return the file with the correct MIME type
        return send_from_directory(
            OUTPUT_FOLDER, 
            filename, 
            mimetype='audio/mpeg', 
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': f"Error serving audio file: {str(e)}"}), 500

@app.route('/audio-test')
def audio_test():
    """List audio files and provide test links"""
    files = []
    try:
        for file in os.listdir(OUTPUT_FOLDER):
            if True:
                files.append({
                    'filename': file,
                    'url': f'/audio/{file}',
                    'size': os.path.getsize(os.path.join(OUTPUT_FOLDER, file))
                })
        return jsonify({
            'output_dir': os.path.abspath(OUTPUT_FOLDER),
            'file_count': len(files),
            'files': files
        })
    except Exception as e:
        return jsonify({'error': f"Error listing audio files: {str(e)}"}), 500

@app.route('/tasks')
def list_tasks():
    """Get a list of all tasks (for monitoring purposes)"""
    return jsonify({
        'tasks': list(tasks.values())
    })
    
@app.route('/outputs')
def list_outputs():
    """List all output files"""
    files = os.listdir(OUTPUT_FOLDER)
    return jsonify({'files': files})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
