"""Automatically import exported assets into src/data/imported/current-repo and migrate waypoint files into reviewable JSON.

Usage:
  python3 tools/import_and_migrate.py

This will:
 - Copy tools/imported/current-repo/images -> src/data/imported/current-repo/images
 - For each file under tools/imported/current-repo/waypoints:
    - if JSON/YAML, copy to src/data/imported/current-repo/
    - if .py or unknown, create a placeholder JSON describing the source and add to migrated_waypoints.json
 - Create src/data/imported/current-repo/migrated_waypoints.json with an array of waypoint objects (either actual or placeholders)

This is conservative: it doesn't try to execute or deeply parse python waypoint scripts. It produces reviewable JSON suitable for loading by the importer UI.
"""
import os
import shutil
import json

SRC = os.path.join('src', 'data', 'imported', 'current-repo')
TOOLS_IN = os.path.join('tools', 'imported', 'current-repo')
IMG_IN = os.path.join(TOOLS_IN, 'images')
WAY_IN = os.path.join(TOOLS_IN, 'waypoints')

os.makedirs(SRC, exist_ok=True)
os.makedirs(os.path.join(SRC, 'images'), exist_ok=True)

migrated = []

# copy images
if os.path.isdir(IMG_IN):
    for dirpath, dirnames, files in os.walk(IMG_IN):
        rel = os.path.relpath(dirpath, IMG_IN)
        destdir = os.path.join(SRC, 'images', rel) if rel != '.' else os.path.join(SRC, 'images')
        os.makedirs(destdir, exist_ok=True)
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                shutil.copy2(os.path.join(dirpath, f), os.path.join(destdir, f))

# migrate waypoints
if os.path.isdir(WAY_IN):
    for f in sorted(os.listdir(WAY_IN)):
        full = os.path.join(WAY_IN, f)
        name, ext = os.path.splitext(f)
        try:
            if ext.lower() in ('.json', '.yaml', '.yml'):
                shutil.copy2(full, os.path.join(SRC, f))
                # try to load JSON/YAML as list
                try:
                    with open(full, 'r') as fh:
                        data = json.load(fh)
                        if isinstance(data, list):
                            migrated.extend(data)
                        else:
                            # wrap non-list data
                            migrated.append({'label': name, 'type': 'imported', 'content': data})
                except Exception:
                    # If can't parse, add a placeholder referencing file
                    migrated.append({'label': name, 'type': 'imported-file', 'source': full})
            elif ext.lower() == '.py':
                # create placeholder entry referencing the script
                migrated.append({'label': name, 'type': 'script-ref', 'source': full, 'note': 'Review Python waypoint script and convert manually if desired.'})
                # also copy script for review
                shutil.copy2(full, os.path.join(SRC, f))
            else:
                # unknown file types: copy and reference
                shutil.copy2(full, os.path.join(SRC, f))
                migrated.append({'label': name, 'type': 'unknown', 'source': full})
        except Exception as e:
            print('Skipping', full, 'due to', e)

# write migrated_waypoints.json
out_path = os.path.join(SRC, 'migrated_waypoints.json')
with open(out_path, 'w') as fh:
    json.dump(migrated, fh, indent=2)

print('Migrated', len(migrated), 'waypoint entries to', out_path)
print('Images copied to', os.path.join(SRC, 'images'))
print('Done.')
