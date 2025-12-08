import os
import sys
from datetime import datetime
from pathlib import Path

def cleanup_on_startup():
    print("🔧 Running pre-startup cleanup...")
    base_path = Path.cwd()
    cache_count = 0
    
    for cache_dir in base_path.rglob("__pycache__"):
        if cache_dir.exists() and cache_dir.is_dir():
            try:
                import shutil
                shutil.rmtree(cache_dir)
                cache_count += 1
            except:
                pass
    
    for cache_file in base_path.rglob("*.pyc"):
        if cache_file.exists():
            try:
                cache_file.unlink()
                cache_count += 1
            except:
                pass
    
    if cache_count > 0:
        print(f"🧹 Cleaned {cache_count} Python cache items")
    
    uploads_path = base_path / "app" / "static" / "uploads"
    results_path = base_path / "app" / "static" / "results"
    
    uploads_path.mkdir(parents=True, exist_ok=True)
    results_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Pre-startup cleanup completed")
    return True

def main():
    print("\n" + "="*60)
    print("🍋 SLICE LEMONADE - SMART PRODUCTION MODE")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    cleanup_on_startup()
    
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        from app import create_app
        
        app = create_app()
        
        print(f"\n📊 Flask Configuration:")
        print(f"  Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"  Results folder: {app.config['RESULTS_FOLDER']}")
        print(f"  Storage limit: {app.config['MAX_STORAGE_GB']}GB")
        print(f"  Cleanup interval: {app.config['CLEANUP_INTERVAL_HOURS']}h")
        
        print(f"\n🚀 Starting server on http://0.0.0.0:5000")
        print("="*60 + "\n")
        
        app.debug = False
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=app.debug)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()