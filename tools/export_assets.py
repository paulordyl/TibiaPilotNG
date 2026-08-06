"""Export relevant assets from this repo into tools/imported/current-repo and create a minimal migration JSON.

Usage:
  python3 tools/export_assets.py

What it does:
 - Copies src/repositories/*/images into tools/imported/current-repo/images
 - Searches repo for files with 'waypoint' in name or content and copies them to tools/imported/current-repo/waypoints
 - Creates src/data/imported/current-repo/waypoints.json summarizing found waypoint files
 - Creates a sample waypoint JSON if none found to allow testing the importer UI and headless runner
"""
import os
import shutil
import json

ROOT = os.path.abspath(os.getcwd())
OUT = os.path.join('tools', 'imported', 'current-repo')
IMG_OUT = os.path.join(OUT, 'images')
WAY_OUT = os.path.join(OUT, 'waypoints')
DATA_DIR = os.path.join('src', 'data', 'imported', 'current-repo')

os.makedirs(IMG_OUT, exist_ok=True)
os.makedirs(WAY_OUT, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Copy images under src/repositories/**/images
for dirpath, dirnames, filenames in os.walk(os.path.join('src', 'repositories')):
    if os.path.basename(dirpath).lower() == 'images':
        rel = os.path.relpath(dirpath, os.path.join('src', 'repositories'))
        dest = os.path.join(IMG_OUT, rel)
        os.makedirs(dest, exist_ok=True)
        for f in filenames:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                shutil.copy2(os.path.join(dirpath, f), os.path.join(dest, f))

# Find waypoint files (filename contains waypoint) or files containing 'waypoint' in text
found_waypoints = []
for dirpath, dirnames, filenames in os.walk('.'):
    # skip tools/imported
    if dirpath.startswith('./tools/imported') or dirpath.startswith('tools/imported'):
        continue
    for f in filenames:
        lower = f.lower()
        full = os.path.join(dirpath, f)
        try:
            if 'waypoint' in lower:
                shutil.copy2(full, os.path.join(WAY_OUT, f))
                found_waypoints.append(os.path.relpath(full))
                continue
            # check file content for 'waypoint' keyword for text files
            if lower.endswith(('.json', '.yaml', '.yml', '.txt', '.cfg')):
                with open(full, 'r', errors='ignore') as fh:
                    content = fh.read(65536)
                    if 'waypoint' in content.lower():
                        shutil.copy2(full, os.path.join(WAY_OUT, f))
                        found_waypoints.append(os.path.relpath(full))
        except Exception:
            # skip binary or unreadable
            continue

# create summary JSON in src/data/imported/current-repo/waypoints.json
waypoints_summary = {'found': found_waypoints}
with open(os.path.join(DATA_DIR, 'waypoints.json'), 'w') as fh:
    json.dump(waypoints_summary, fh, indent=2)

# If none found, create a sample waypoint JSON
if not found_waypoints:
    sample = [
        {
            'label': 'sample-start',
            'type': 'walk',
            'coordinate': [100, 100, 7],
            'options': {}
        },
        {
            'label': 'attack-area',
            'type': 'attackClosestCreature',
            'coordinate': [102, 100, 7],
            'options': {}
        }
    ]
    sample_path = os.path.join(DATA_DIR, 'sample_waypoints.json')
    with open(sample_path, 'w') as fh:
        json.dump(sample, fh, indent=2)
    print('No waypoint files found; created sample at', sample_path)
else:
    print('Copied', len(found_waypoints), 'waypoint-related files to', WAY_OUT)

print('Images copied under', IMG_OUT)
print('Waypoints summary written to', os.path.join(DATA_DIR, 'waypoints.json'))
print('Done.')
