import os,shutil,time,json,argparse,sys
from datetime import datetime,timedelta
from pathlib import Path

def cleanup_python_cache():
    base_path=Path.cwd()
    cache_dirs,cache_files=0,0
    for cache_dir in base_path.rglob("__pycache__"):
        if cache_dir.exists()and cache_dir.is_dir():
            try:
                shutil.rmtree(cache_dir);cache_dirs+=1
            except:pass
    for cache_file in base_path.rglob("*.pyc"):
        if cache_file.exists():
            try:
                cache_file.unlink();cache_files+=1
            except:pass
    if cache_dirs>0 or cache_files>0:
        print(f"🧹 Python cache:{cache_dirs} dirs,{cache_files} files cleaned")

def cleanup_storage():
    print("🧹 Cleaning storage...")
    uploads_path=Path("app/static/uploads")
    results_path=Path("app/static/results")
    stats={'uploads_deleted':0,'uploads_space':0,'results_deleted':0,'results_space':0}
    
    if uploads_path.exists():
        cutoff=datetime.now()-timedelta(hours=24)
        for file_path in uploads_path.glob("*"):
            if file_path.is_file():
                try:
                    created=datetime.fromtimestamp(file_path.stat().st_ctime)
                    if created<cutoff:
                        size=file_path.stat().st_size
                        file_path.unlink()
                        stats['uploads_deleted']+=1
                        stats['uploads_space']+=size
                        print(f"  🗑️ Upload:{file_path.name}")
                except:pass
    
    if results_path.exists():
        cutoff=datetime.now()-timedelta(hours=24)
        for dir_path in results_path.glob("*"):
            if dir_path.is_dir():
                try:
                    created=datetime.fromtimestamp(dir_path.stat().st_ctime)
                    if created<cutoff:
                        dir_size=0
                        for f in dir_path.rglob("*"):
                            if f.is_file():
                                dir_size+=f.stat().st_size
                        shutil.rmtree(dir_path)
                        stats['results_deleted']+=1
                        stats['results_space']+=dir_size
                        print(f"  🗑️ Result:{dir_path.name}/")
                except:pass
    
    total_space=(stats['uploads_space']+stats['results_space'])/1024/1024
    print(f"✅ Cleanup:{stats['uploads_deleted']+stats['results_deleted']} items,{total_space:.1f}MB freed")
    return stats

def main():
    parser=argparse.ArgumentParser(description='Cleanup Slice Lemonade storage')
    parser.add_argument('--dry-run',action='store_true',help='Show what would be deleted')
    args=parser.parse_args()
    
    print("🍋 Slice Lemonade Storage Cleanup")
    print("="*50)
    
    if args.dry_run:
        print("📋 DRY RUN - No files will be deleted")
    
    cleanup_python_cache()
    
    if not args.dry_run:
        cleanup_storage()
    else:
        print("📋 Dry run complete - use without --dry-run to actually cleanup")

if __name__=="__main__":
    main()