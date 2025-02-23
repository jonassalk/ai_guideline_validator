from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pypdf import PdfReader
import docx
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the app
CORS(app)

# Configuration for file upload
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Set the app config for uploads folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
import os
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to validate PDF file
def is_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            print("Number of pages:", len(reader.pages))  # Access the pages directly
            return len(reader.pages) > 0  # If the PDF has at least one page
    except Exception as e:
        print(f"An error occurred in validating PDF: {e}")
        return False

# Helper function to validate DOCX file
def is_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return len(doc.paragraphs) > 0  # If the DOCX has at least one paragraph
    except Exception:
        return False

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file securely
        file.save(file_path)
        
        # Check if it's a valid PDF or DOCX
        if filename.lower().endswith('.pdf') and not is_pdf(file_path):
            print(file_path)
            os.remove(file_path)
            return jsonify({'message': 'Invalid PDF file'}), 400
        
        if filename.lower().endswith(('.doc', '.docx')) and not is_docx(file_path):
            os.remove(file_path)
            return jsonify({'message': 'Invalid DOCX file'}), 400
        
        return jsonify({'message': 'File uploaded successfully'}), 200
    
    else:
        return jsonify({'message': 'Allowed file types are pdf, docx'}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)
