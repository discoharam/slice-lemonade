from app import create_app
import os
import sys
from pathlib import Path

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🍋 SLICE LEMONADE BACKEND - PRODUCTION READY")
    print("="*60)
    
    import shutil
    cache_dirs = 0
    for cache_dir in Path.cwd().rglob("__pycache__"):
        if cache_dir.is_dir():
            try:
                shutil.rmtree(cache_dir)
                cache_dirs += 1
            except:
                pass
    
    if cache_dirs > 0:
        print(f"🧹 Cleaned {cache_dirs} Python cache directories")
    
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Results folder: {app.config['RESULTS_FOLDER']}")
    print(f"💾 Storage limit: {app.config['MAX_STORAGE_GB']}GB")
    print(f"🔧 Auto-cleanup: Every {app.config['CLEANUP_INTERVAL_HOURS']} hours")
    print("="*60)
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting server on http://0.0.0.0:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)