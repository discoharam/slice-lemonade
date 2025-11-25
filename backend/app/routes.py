from flask import Blueprint, request, jsonify, send_file, current_app
import os
import uuid
from datetime import datetime
from .separator import AudioSeparator

main = Blueprint('main', __name__)
separator = AudioSeparator()

@main.route('/')
def home():
    return jsonify({
        "message": "🍋 Slice Lemonade API",
        "version": "1.0.0",
        "status": "running"
    })

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "slice-lemonade",
        "timestamp": datetime.utcnow().isoformat()
    })

@main.route('/api/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    allowed_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({"error": f"File type {file_ext} not supported"}), 400
    
    job_id = str(uuid.uuid4())
    
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, f"{job_id}_{file.filename}")
        file.save(file_path)
        
        print(f"🎯 Starting separation for job: {job_id}")
        result = separator.separate_audio(file_path, job_id)
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Separation error: {str(e)}")
        return jsonify({
            "job_id": job_id,
            "status": "error",
            "error": str(e)
        }), 500

@main.route('/api/download/<job_id>/<track_name>')
def download_track(job_id, track_name):
    results_folder = current_app.config['RESULTS_FOLDER']
    file_path = os.path.join(results_folder, job_id, f"{track_name}.wav")
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"{track_name}.wav")
    else:
        return jsonify({"error": "File not found"}), 404

@main.route('/api/jobs/<job_id>/status')
def job_status(job_id):
    results_folder = current_app.config['RESULTS_FOLDER']
    job_folder = os.path.join(results_folder, job_id)
    
    if os.path.exists(job_folder):
        tracks = [f for f in os.listdir(job_folder) if f.endswith('.wav')]
        return jsonify({
            "job_id": job_id,
            "status": "completed",
            "tracks": [os.path.splitext(t)[0] for t in tracks],
            "available_tracks": tracks
        })
    else:
        return jsonify({
            "job_id": job_id,
            "status": "processing",
            "message": "Job is still processing or doesn't exist"
        })