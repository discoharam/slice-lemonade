from flask import Flask, request, send_from_directory, Response
from flask_cors import CORS
import os
import atexit
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import threading
import time
import json

# Global storage manager instance
_storage_manager = None

def create_app():
    app = Flask(__name__)
    
    # Configure CORS with specific settings for WaveSurfer
    CORS(app, 
         resources={
             r"/audio/*": {
                 "origins": "*",
                 "methods": ["GET", "HEAD", "OPTIONS"],
                 "allow_headers": ["Range", "Content-Type", "Accept", "Authorization"],
                 "expose_headers": ["Content-Range", "Content-Length", "Content-Type", "X-Audio-Size"],
                 "supports_credentials": False,
                 "max_age": 3600
             },
             r"/api/*": {
                 "origins": "*",
                 "methods": ["GET", "POST", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": False
             }
         })
    
    # CORRECT ABSOLUTE PATHS FOR WINDOWS
    app_root = Path(__file__).parent.absolute()  # Points to backend/app/
    backend_root = app_root.parent.absolute()    # Points to backend/
    
    # Set absolute paths
    upload_folder = backend_root / "app" / "static" / "uploads"
    results_folder = backend_root / "app" / "static" / "results"
    static_folder = backend_root / "app" / "static"
    
    app.config['UPLOAD_FOLDER'] = str(upload_folder)
    app.config['RESULTS_FOLDER'] = str(results_folder)
    app.config['STATIC_FOLDER'] = str(static_folder)
    
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Storage management configuration
    app.config['MAX_STORAGE_GB'] = float(os.environ.get('MAX_STORAGE_GB', 2.0))
    app.config['CLEANUP_INTERVAL_HOURS'] = int(os.environ.get('CLEANUP_INTERVAL_HOURS', 6))
    app.config['UPLOADS_MAX_AGE_HOURS'] = int(os.environ.get('UPLOADS_MAX_AGE_HOURS', 24))
    app.config['RESULTS_MAX_AGE_HOURS'] = int(os.environ.get('RESULTS_MAX_AGE_HOURS', 24))
    app.config['MAX_UPLOAD_FILES'] = int(os.environ.get('MAX_UPLOAD_FILES', 50))
    app.config['MAX_RESULT_DIRS'] = int(os.environ.get('MAX_RESULT_DIRS', 30))
    
    print(f"🎯 CORRECT PATHS CONFIGURED:")
    print(f"   Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"   Results folder: {app.config['RESULTS_FOLDER']}")
    print(f"   Static folder: {app.config['STATIC_FOLDER']}")
    print(f"🔧 Storage limit: {app.config['MAX_STORAGE_GB']}GB")
    print(f"🧹 Cleanup interval: {app.config['CLEANUP_INTERVAL_HOURS']}h")
    
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Initialize storage manager
    global _storage_manager
    _storage_manager = StorageManager(app)
    
    # Flag to track if cleanup has run
    app.config['_cleanup_initialized'] = False
    
    # Flask 2.3+ compatible before request handler
    @app.before_request
    def initialize_on_first_request():
        """Initialize storage management on first request"""
        if not app.config['_cleanup_initialized'] and request.endpoint not in ['static', 'health_check', 'storage_stats', 'storage_health']:
            print("🔧 Initializing smart storage management...")
            
            # Scan existing files
            _storage_manager.scan_storage()
            
            # Perform initial cleanup if needed
            stats = _storage_manager.get_storage_stats()
            used_gb = stats['total_size'] / (1024**3)
            
            if used_gb > app.config['MAX_STORAGE_GB'] * 0.8:
                print(f"⚠️  Storage >80% full ({used_gb:.1f}GB), running cleanup...")
                _storage_manager.cleanup_storage(force=True)
            
            # Start background cleaner
            _storage_manager.start_background_cleaner()
            
            # Clean Python cache
            cleanup_python_cache()
            
            app.config['_cleanup_initialized'] = True
    
    # Register cleanup on shutdown
    def shutdown_cleanup():
        """Cleanup on application shutdown"""
        print("🛑 Application shutting down...")
        if _storage_manager:
            _storage_manager.stop_background_cleaner()
        cleanup_python_cache()
    
    atexit.register(shutdown_cleanup)
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    # Serve static files from app/static
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files with correct path"""
        return send_from_directory(app.config['STATIC_FOLDER'], filename)
    
    # Serve audio files directly for waveform playback - COMPLETELY FIXED
    @app.route('/audio/<job_id>/<stem_name>.<format>')
    def serve_audio(job_id, stem_name, format):
        """Serve audio files with proper headers for waveform playback"""
        # Define file_path
        file_path = os.path.join(app.config['RESULTS_FOLDER'], job_id, f"{stem_name}.{format}")
        
        print(f"🎵 [AUDIO SERVE] Requested: {job_id}/{stem_name}.{format}")
        print(f"📁 [AUDIO SERVE] Path: {file_path}")
        print(f"✅ [AUDIO SERVE] Exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"❌ [AUDIO SERVE] File not found")
            return {"error": f"Audio file {stem_name}.{format} not found for job {job_id}"}, 404
        
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            
            # Determine MIME type
            mime_types = {
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'flac': 'audio/flac'
            }
            
            mime_type = mime_types.get(format.lower(), 'audio/mpeg')
            
            print(f"📊 [AUDIO SERVE] Size: {file_size:,} bytes")
            print(f"📦 [AUDIO SERVE] MIME: {mime_type}")
            
            # Check for range header (WaveSurfer uses this)
            range_header = request.headers.get('Range', None)
            print(f"🎯 [AUDIO SERVE] Range header: {range_header}")
            
            # Handle range requests
            if range_header:
                try:
                    # Parse range header
                    range_ = range_header.replace('bytes=', '').split('-')
                    byte1 = int(range_[0])
                    byte2 = int(range_[1]) if range_[1] else file_size - 1
                    
                    # Ensure byte2 is within bounds
                    if byte2 >= file_size:
                        byte2 = file_size - 1
                    
                    length = byte2 - byte1 + 1
                    
                    print(f"🔧 [AUDIO SERVE] Range: {byte1}-{byte2} (length: {length})")
                    
                    # Create partial response
                    response = Response()
                    response.status_code = 206
                    response.content_type = mime_type
                    response.headers.add('Accept-Ranges', 'bytes')
                    response.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{file_size}')
                    response.headers.add('Content-Length', str(length))
                    
                    # Add CORS headers for WaveSurfer
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    response.headers.add('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
                    response.headers.add('Access-Control-Allow-Headers', 'Range, Content-Type')
                    response.headers.add('Access-Control-Expose-Headers', 'Content-Length, Content-Range')
                    
                    # Stream the file chunk
                    def generate():
                        with open(file_path, 'rb') as f:
                            f.seek(byte1)
                            remaining = length
                            while remaining > 0:
                                chunk = f.read(min(4096, remaining))
                                if not chunk:
                                    break
                                yield chunk
                                remaining -= len(chunk)
                    
                    response.response = generate()
                    return response
                    
                except Exception as e:
                    print(f"⚠️ [AUDIO SERVE] Range error: {e}")
                    # Fall through to full file response
            
            # Full file response
            print(f"🚀 [AUDIO SERVE] Serving full file")
            
            # Use send_file for better performance
            from flask import send_file
            response = send_file(
                file_path,
                mimetype=mime_type,
                as_attachment=False,
                conditional=True
            )
            
            # Set headers for WaveSurfer
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Length'] = str(file_size)
            response.headers['Cache-Control'] = 'public, max-age=3600'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Range, Content-Type'
            response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range'
            response.headers['X-Audio-Size'] = str(file_size)
            response.headers['X-File-Format'] = format.upper()
            
            return response
            
        except Exception as e:
            print(f"❌ [AUDIO SERVE] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Server error: {str(e)}"}, 500
    
    # Add OPTIONS handler for CORS preflight
    @app.route('/audio/<job_id>/<stem_name>.<format>', methods=['OPTIONS'])
    def audio_options(job_id, stem_name, format):
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Range, Content-Type')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response
    
    # Storage management endpoints
    @app.route('/api/storage/stats', methods=['GET'])
    def storage_stats():
        """Get storage statistics"""
        if not _storage_manager:
            return {"error": "Storage manager not initialized"}, 500
        
        return {
            "status": "success",
            "stats": _storage_manager.get_storage_stats(),
            "config": {
                "max_storage_gb": app.config['MAX_STORAGE_GB'],
                "cleanup_interval_hours": app.config['CLEANUP_INTERVAL_HOURS'],
                "uploads_max_age_hours": app.config['UPLOADS_MAX_AGE_HOURS'],
                "results_max_age_hours": app.config['RESULTS_MAX_AGE_HOURS'],
                "uploads_folder": app.config['UPLOAD_FOLDER'],
                "results_folder": app.config['RESULTS_FOLDER']
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @app.route('/api/storage/cleanup', methods=['POST'])
    def trigger_cleanup():
        """Manually trigger storage cleanup"""
        if not _storage_manager:
            return {"error": "Storage manager not initialized"}, 500
        
        report = _storage_manager.cleanup_storage(force=True)
        return {
            "status": "success",
            "message": "Cleanup completed",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    
    @app.route('/api/storage/health', methods=['GET'])
    def storage_health():
        """Check storage health status"""
        if not _storage_manager:
            return {"error": "Storage manager not initialized"}, 500
        
        stats = _storage_manager.get_storage_stats()
        used_gb = stats['total_size'] / (1024**3)
        max_gb = app.config['MAX_STORAGE_GB']
        percent = (used_gb / max_gb) * 100 if max_gb > 0 else 0
        
        status = "healthy"
        if percent > 90:
            status = "critical"
        elif percent > 75:
            status = "warning"
        elif percent > 50:
            status = "ok"
        
        return {
            "status": "success",
            "health": {
                "status": status,
                "used_gb": round(used_gb, 2),
                "max_gb": max_gb,
                "percent": round(percent, 1),
                "files_count": stats['files_count'],
                "dirs_count": stats['dirs_count']
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Simple health endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {
            "status": "healthy",
            "service": "slice-lemonade",
            "storage_initialized": app.config['_cleanup_initialized'],
            "timestamp": datetime.now().isoformat()
        }
    
    # Audio URL test endpoint
    @app.route('/api/test/audio/<job_id>', methods=['GET'])
    def test_audio_urls(job_id):
        """Test audio URLs for a job"""
        results_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
        
        if not os.path.exists(results_dir):
            return {"error": f"Job {job_id} not found"}, 404
        
        files = []
        for file in os.listdir(results_dir):
            if file.endswith(('.mp3', '.wav', '.flac')):
                stem_name, ext = os.path.splitext(file)
                format = ext[1:]  # Remove dot
                files.append({
                    "file": file,
                    "stem": stem_name,
                    "format": format,
                    "url": f"/audio/{job_id}/{stem_name}.{format}",
                    "full_url": f"http://localhost:5000/audio/{job_id}/{stem_name}.{format}",
                    "full_path": os.path.join(results_dir, file),
                    "exists": os.path.exists(os.path.join(results_dir, file)),
                    "size": os.path.getsize(os.path.join(results_dir, file)) if os.path.exists(os.path.join(results_dir, file)) else 0
                })
        
        return {
            "job_id": job_id,
            "files_count": len(files),
            "files": files,
            "directory": results_dir,
            "directory_exists": os.path.exists(results_dir),
            "test_note": "Use the full_url in WaveSurfer for testing"
        }
    
    return app

class StorageManager:
    """Smart storage management with auto-cleanup"""
    
    def __init__(self, app):
        self.app = app
        self.uploads_path = Path(app.config['UPLOAD_FOLDER'])
        self.results_path = Path(app.config['RESULTS_FOLDER'])
        self.cleanup_thread = None
        self.running = False
        self.cleanup_logs = []
        
        # Create storage log directory
        self.logs_path = Path(app.root_path) / ".." / "storage_logs"
        self.logs_path.mkdir(exist_ok=True)
    
    def get_directory_size(self, dir_path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total = 0
        if dir_path.exists() and dir_path.is_dir():
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    try:
                        total += file_path.stat().st_size
                    except:
                        pass
        return total
    
    def scan_storage(self):
        """Scan storage and return statistics"""
        stats = {
            'uploads_size': 0,
            'uploads_count': 0,
            'results_size': 0,
            'results_count': 0,
            'total_size': 0,
            'files_count': 0,
            'dirs_count': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Scan uploads
        if self.uploads_path.exists():
            for file_path in self.uploads_path.glob("*"):
                if file_path.is_file():
                    try:
                        stats['uploads_size'] += file_path.stat().st_size
                        stats['uploads_count'] += 1
                        stats['files_count'] += 1
                    except:
                        pass
        
        # Scan results
        if self.results_path.exists():
            for dir_path in self.results_path.glob("*"):
                if dir_path.is_dir():
                    try:
                        dir_size = self.get_directory_size(dir_path)
                        stats['results_size'] += dir_size
                        stats['results_count'] += 1
                        stats['dirs_count'] += 1
                    except:
                        pass
        
        stats['total_size'] = stats['uploads_size'] + stats['results_size']
        
        # Save scan results
        self.save_scan_log(stats)
        
        return stats
    
    def cleanup_storage(self, force=False):
        """Clean up storage based on configuration"""
        config = self.app.config
        stats_before = self.scan_storage()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'force': force,
            'stats_before': stats_before,
            'uploads_deleted': 0,
            'uploads_space_freed': 0,
            'results_deleted': 0,
            'results_space_freed': 0,
            'errors': []
        }
        
        # Calculate storage usage
        used_gb = stats_before['total_size'] / (1024**3)
        max_gb = config['MAX_STORAGE_GB']
        percent = (used_gb / max_gb) * 100 if max_gb > 0 else 0
        
        print(f"🧹 Storage cleanup: {used_gb:.1f}/{max_gb}GB ({percent:.1f}%)")
        
        # Determine cleanup strategy based on usage
        if percent > 90 or force:
            strategy = "aggressive"
            uploads_max_age = config['UPLOADS_MAX_AGE_HOURS'] // 2
            results_max_age = config['RESULTS_MAX_AGE_HOURS'] // 2
            uploads_max_files = config['MAX_UPLOAD_FILES'] // 2
            results_max_dirs = config['MAX_RESULT_DIRS'] // 2
        elif percent > 75:
            strategy = "moderate"
            uploads_max_age = config['UPLOADS_MAX_AGE_HOURS'] * 3 // 4
            results_max_age = config['RESULTS_MAX_AGE_HOURS'] * 3 // 4
            uploads_max_files = config['MAX_UPLOAD_FILES'] * 3 // 4
            results_max_dirs = config['MAX_RESULT_DIRS'] * 3 // 4
        else:
            strategy = "normal"
            uploads_max_age = config['UPLOADS_MAX_AGE_HOURS']
            results_max_age = config['RESULTS_MAX_AGE_HOURS']
            uploads_max_files = config['MAX_UPLOAD_FILES']
            results_max_dirs = config['MAX_RESULT_DIRS']
        
        print(f"  Strategy: {strategy}")
        print(f"  Uploads: >{uploads_max_age}h, max {uploads_max_files} files")
        print(f"  Results: >{results_max_age}h, max {results_max_dirs} dirs")
        
        # Clean uploads
        if self.uploads_path.exists():
            cutoff = datetime.now() - timedelta(hours=uploads_max_age)
            files = []
            
            # Collect file info
            for file_path in self.uploads_path.glob("*"):
                if file_path.is_file():
                    try:
                        created = datetime.fromtimestamp(file_path.stat().st_ctime)
                        files.append((file_path, created, file_path.stat().st_size))
                    except Exception as e:
                        report['errors'].append(f"Scan {file_path}: {e}")
            
            if files:
                # Sort by creation time (oldest first)
                files.sort(key=lambda x: x[1])
                
                # Delete old files
                for file_path, created, size in files:
                    if created < cutoff:
                        try:
                            file_path.unlink()
                            report['uploads_deleted'] += 1
                            report['uploads_space_freed'] += size
                            print(f"  🗑️  Upload: {file_path.name}")
                        except Exception as e:
                            report['errors'].append(f"Delete {file_path}: {e}")
                
                # Delete excess files if still too many
                remaining = len(files) - report['uploads_deleted']
                if remaining > uploads_max_files:
                    remaining_files = [f for f in files if not (f[1] < cutoff)]
                    remaining_files.sort(key=lambda x: x[1])
                    
                    to_delete = remaining_files[:remaining - uploads_max_files]
                    for file_path, created, size in to_delete:
                        try:
                            file_path.unlink()
                            report['uploads_deleted'] += 1
                            report['uploads_space_freed'] += size
                            print(f"  🗑️  Upload (max): {file_path.name}")
                        except Exception as e:
                            report['errors'].append(f"Delete {file_path}: {e}")
        
        # Clean results
        if self.results_path.exists():
            cutoff = datetime.now() - timedelta(hours=results_max_age)
            dirs = []
            
            # Collect directory info
            for dir_path in self.results_path.glob("*"):
                if dir_path.is_dir():
                    try:
                        created = datetime.fromtimestamp(dir_path.stat().st_ctime)
                        dir_size = self.get_directory_size(dir_path)
                        dirs.append((dir_path, created, dir_size))
                    except Exception as e:
                        report['errors'].append(f"Scan {dir_path}: {e}")
            
            if dirs:
                # Sort by creation time (oldest first)
                dirs.sort(key=lambda x: x[1])
                
                # Delete old directories
                for dir_path, created, size in dirs:
                    if created < cutoff:
                        try:
                            shutil.rmtree(dir_path)
                            report['results_deleted'] += 1
                            report['results_space_freed'] += size
                            print(f"  🗑️  Result: {dir_path.name}/")
                        except Exception as e:
                            report['errors'].append(f"Delete {dir_path}: {e}")
                
                # Delete excess directories if still too many
                remaining = len(dirs) - report['results_deleted']
                if remaining > results_max_dirs:
                    remaining_dirs = [d for d in dirs if not (d[1] < cutoff)]
                    remaining_dirs.sort(key=lambda x: x[1])
                    
                    to_delete = remaining_dirs[:remaining - results_max_dirs]
                    for dir_path, created, size in to_delete:
                        try:
                            shutil.rmtree(dir_path)
                            report['results_deleted'] += 1
                            report['results_space_freed'] += size
                            print(f"  🗑️  Result (max): {dir_path.name}/")
                        except Exception as e:
                            report['errors'].append(f"Delete {dir_path}: {e}")
        
        # Get after stats
        stats_after = self.scan_storage()
        report['stats_after'] = stats_after
        
        # Calculate totals
        total_deleted = report['uploads_deleted'] + report['results_deleted']
        total_space = report['uploads_space_freed'] + report['results_space_freed']
        
        print(f"  ✅ Cleanup: {total_deleted} items, {total_space/1024/1024:.1f}MB freed")
        
        # Save cleanup log
        self.save_cleanup_log(report)
        
        return report
    
    def start_background_cleaner(self):
        """Start background cleanup thread"""
        if self.running:
            return
        
        self.running = True
        
        def cleanup_loop():
            interval = self.app.config['CLEANUP_INTERVAL_HOURS'] * 3600
            
            while self.running:
                try:
                    time.sleep(interval)
                    print(f"\n⏰ Scheduled cleanup started at {datetime.now()}")
                    self.cleanup_storage()
                except Exception as e:
                    print(f"⚠️ Background cleanup error: {e}")
                
                # Save heartbeat log
                self.save_heartbeat()
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        print(f"✅ Background storage cleaner started (interval: {self.app.config['CLEANUP_INTERVAL_HOURS']}h)")
    
    def stop_background_cleaner(self):
        """Stop background cleanup thread"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        print("🛑 Background storage cleaner stopped")
    
    def save_scan_log(self, stats):
        """Save scan results to log file"""
        log_file = self.logs_path / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
        except:
            pass
    
    def save_cleanup_log(self, report):
        """Save cleanup report to log file"""
        log_file = self.logs_path / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        except:
            pass
    
    def save_heartbeat(self):
        """Save heartbeat log"""
        heartbeat = {
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'storage_stats': self.scan_storage()
        }
        
        log_file = self.logs_path / f"heartbeat_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            # Append to daily log
            if log_file.exists():
                with open(log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            if not isinstance(data, list):
                data = []
            
            data.append(heartbeat)
            
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except:
            pass
    
    def get_storage_stats(self):
        """Get current storage statistics"""
        return self.scan_storage()

def cleanup_python_cache():
    """Clean Python cache files"""
    base_path = Path.cwd()
    
    cache_dirs = 0
    cache_files = 0
    
    # Remove __pycache__ directories
    for cache_dir in base_path.rglob("__pycache__"):
        if cache_dir.exists() and cache_dir.is_dir():
            try:
                shutil.rmtree(cache_dir)
                cache_dirs += 1
            except:
                pass
    
    # Remove .pyc files
    for cache_file in base_path.rglob("*.pyc"):
        if cache_file.exists():
            try:
                cache_file.unlink()
                cache_files += 1
            except:
                pass
    
    if cache_dirs > 0 or cache_files > 0:
        print(f"🧹 Python cache: {cache_dirs} dirs, {cache_files} files cleaned")