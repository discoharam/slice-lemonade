Write-Host "🔧 RESTORING MISSING BACKEND FILES..." -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Yellow

cd "C:\DEV\Slice Lemonade\backend"

# 1. Create run.py
@'
from app import create_app
import os, sys
from pathlib import Path

app = create_app()
if __name__ == "__main__":
    print("\n🍋 SLICE LEMONADE BACKEND")
    print("="*50)
    print(f"📁 Uploads: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Results: {app.config['RESULTS_FOLDER']}")
    print(f"💾 Storage: {app.config['MAX_STORAGE_GB']}GB limit")
    print("="*50)
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    print(f"🚀 Starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
