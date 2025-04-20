# app.py - Complete standalone Flask application for malaria analysis

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import random
import io
import sys

# For PDF handling - uncomment if you have PyMuPDF installed
# import fitz

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Utility Functions
def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_images_from_pdf(pdf_path):
    """
    Extract images from a PDF file
    
    Note: This is a placeholder. Uncomment the PyMuPDF code for actual implementation.
    """
    # Placeholder for image extraction
    # In a real implementation with PyMuPDF installed:
    """
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            images.append({
                "page": page_num,
                "index": img_index,
                "bytes": image_bytes
            })
    
    return images
    """
    
    # For now, just return a simulated number of images
    return [{"page": 0, "index": i, "bytes": b"placeholder"} for i in range(random.randint(1, 5))]

def analyze_image_for_malaria(image_data):
    """
    Simulate malaria detection on an image
    
    In a real implementation, this would use a trained ML model
    """

    return {
        "parasite_detected": random.choice([True, False]),
        "parasite_type": random.choice(["P. falciparum", "P. vivax", "P. ovale", "P. malariae"]) if random.random() > 0.3 else None,
        "confidence": random.uniform(0.7, 0.99)
    }

def analyze_malaria_pdf(pdf_path):
    """Process a PDF file and analyze for malaria"""
    try:
        # Extract images from the PDF
        images = extract_images_from_pdf(pdf_path)
        
        if not images:
            return {
                "diagnosis": "Inconclusive",
                "error": "No images found in PDF"
            }
        
        # Analyze each image for malaria parasites
        image_results = []
        for image in images:
            result = analyze_image_for_malaria(image["bytes"])
            image_results.append(result)
        
        # Aggregate results for final diagnosis
        positive_count = sum(1 for r in image_results if r["parasite_detected"])
        total_count = len(image_results)
        
        # Make a diagnosis based on results
        if positive_count > 0:
            # Get detected parasite types
            parasites = [r["parasite_type"] for r in image_results 
                        if r["parasite_detected"] and r["parasite_type"]]
            unique_parasites = list(set(parasites))
            
            # Calculate average confidence
            confidences = [r["confidence"] for r in image_results if r["parasite_detected"]]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "diagnosis": "Positive",
                "parasites_detected": unique_parasites,
                "confidence": avg_confidence,
                "parasite_count": positive_count,
                "images_analyzed": total_count
            }
        else:
            return {
                "diagnosis": "Negative",
                "confidence": 0.85,  # Placeholder confidence for negative result
                "parasite_count": 0,
                "images_analyzed": total_count
            }
            
    except Exception as e:
        # Log the error (in a real application, use a proper logger)
        print(f"Error analyzing PDF: {str(e)}", file=sys.stderr)
        raise

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "Malaria analyzer API is running"}), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_pdf():
    """Endpoint to upload and analyze a malaria PDF"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser might submit an empty file
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename to prevent security issues
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        try:
            # Process the PDF with the AI model
            results = analyze_malaria_pdf(filepath)
            
            # Return analysis results
            return jsonify({
                'success': True,
                'results': results
            }), 200
            
        except Exception as e:
            return jsonify({
                'error': f'Analysis failed: {str(e)}'
            }), 500
    
    return jsonify({'error': 'File type not allowed. Please upload a PDF file.'}), 400

# Main entry point
if __name__ == '__main__':
    print(f"Starting malaria analyzer API server on http://localhost:8000")
    print(f"Upload directory: {app.config['UPLOAD_FOLDER']}")
    app.run(debug=True, host='0.0.0.0', port=8000)
