from __future__ import annotations 

import argparse
import shutil 
from pathlib import Path
from datetime import datetime
from typing import Optional


IMG_EXT = {".jpg", ".png", ".jpeg"}
VIDEO_EXT = {".mov", ".mp4"}

def file_kind(path: Path) -> Optional[str]:
    ext = path.suffix.lower()
    if ext in IMG_EXT:
        return "image"
    if ext in VIDEO_EXT: 
        return "video"
    return None 

# 3 safe_mkdir: create directory if it doesn't exist
def safe_mkdir(p:Path) -> None:     
    p.mkdir(parents = True, exist_ok = True)

def get_file(p:Path) -> datetime: 
    ts = p.stat().st_mtime
    return datetime.fromtimestamp(ts)

def next_available_path(dest_dir: Path, prefix: str, dt: datetime, ext: str) -> Path:
    for counter in range (1, 10_000): 
        name = f"{prefix}_{dt:%Y%m%d}_{counter:03d}{ext.lower()}"
        potential = dest_dir / name
        if not potential.exists():
            return potential
    raise RuntimeError("Too many filename collisions")

def main() -> int: 
    parser = argparse.ArgumentParser(description="Organize images/videos")
    parser.add_argument("--src", required = True)
    parser.add_argument("--dest", required = True)
    parser.add_argument("--dry-run", action = "store_true")
    parser.add_argument("--recursive", action = "store_true")
    parser.add_argument("--debug", action ="store_true")
    args = parser.parse_args()
    
    src = Path(args.src).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve()

    if not src.exists() or not src.is_dir():
        print(f"Error: src is not a folder: {src}")
        return 2 
    
    images_dir = dest / "images"
    videos_dir = dest / "videos"
    safe_mkdir(images_dir)
    safe_mkdir(videos_dir)

    files = src.rglob("*") if args.recursive else src.iterdir()
    
    moved = 0 
    skipped = 0 

    for f in files: 
        if not f.is_file(): 
            continue 
        
        kind = file_kind(f)
        if args.debug:
            print("debug:",f.name, "kind=", kind)
        
        if kind is None: 
            skipped += 1
            continue

        dt = get_file(f)

        if kind == "image":
            dest_dir = images_dir
            prefix = "IMG"
        else:
            dest_dir = videos_dir
            prefix = "VID"  

        target = next_available_path(dest_dir, prefix, dt, f.suffix)

        if args.dry_run:
            print(f"[DRY] MOVE: {f.name} -> {target}")
            continue

        shutil.move(str(f),str(target))
        print(f"MOVED {f.name} -> {target.name}")
        moved += 1

    print("\nSummary")
    print("Moved:", moved)
    print("Skipped:", skipped)
    return 0 
if __name__ == "__main__":
    raise SystemExit(main())
    

