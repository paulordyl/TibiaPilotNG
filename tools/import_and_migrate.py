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
                # attempt a best-effort static parse of common waypoint scripts to extract coordinates and type
                try:
                    with open(full, 'r', errors='ignore') as fh:
                        txt = fh.read()
                    import re
                    coords = None
                    # find patterns like [123, 456, 7] or (123,456,7)
                    m = re.search(r"\[?\(\s*(\d{1,4})\s*,\s*(\d{1,4})\s*,\s*(\d{1,2})\s*\)?\]?", txt)
                    if m:
                        try:
                            x = int(m.group(1)); y = int(m.group(2)); z = int(m.group(3))
                            # quick sanity check for coordinate ranges
                            if 0 <= x <= 2000 and 0 <= y <= 2000 and 0 <= z <= 15:
                                coords = [x, y, z]
                        except Exception:
                            coords = None

                    # extract hotkeys or slots like hotkey = 'f' or hotkey: 'f' or slot = 1
                    options = {}
                    # find patterns hotkey[:] =? 'x' or "x"
                    hotkey_m = re.search(r"hotkey\s*[:=]\s*['\"]([\w\d]+)['\"]", txt, re.IGNORECASE)
                    if hotkey_m:
                        options['hotkey'] = hotkey_m.group(1)
                    slot_m = re.search(r"slot\s*[:=]\s*(\d{1,3})", txt, re.IGNORECASE)
                    if slot_m:
                        options['slot'] = int(slot_m.group(1))

                    # detect directions (north/east/south/west) or numeric directions
                    dir_m = re.search(r"(north|south|east|west|up|down|left|right|direction)[:=\s]+([\w\d]+)", txt, re.IGNORECASE)
                    if dir_m:
                        options['direction_hint'] = dir_m.group(2)
                    # find explicit direction numbers (0-7)
                    numdir = re.search(r"direction\s*[:=]\s*(\d)", txt, re.IGNORECASE)
                    if numdir:
                        try:
                            options['direction'] = int(numdir.group(1))
                        except Exception:
                            pass

                    # guess type from filename or script content
                    guessed_type = None
                    lname = name.lower()
                    if 'walk' in lname or 'walkto' in lname:
                        guessed_type = 'walk'
                    elif 'rope' in lname:
                        guessed_type = 'useRope'
                    elif 'shovel' in lname:
                        guessed_type = 'useShovel'
                    elif 'ladder' in lname:
                        guessed_type = 'useLadder'
                    elif 'opendoor' in lname or 'open' in lname:
                        guessed_type = 'openDoor'
                    elif 'rightclickuse' in lname or 'use' in lname:
                        guessed_type = 'use'
                    elif 'rightclickdirection' in lname or 'direction' in lname:
                        guessed_type = 'rightClickDirection'
                    elif 'setnext' in lname:
                        guessed_type = 'setNextWaypoint'
                    else:
                        # inspect content for hints
                        lowtxt = txt.lower()
                        if 'walkto' in lowtxt or 'walk to' in lowtxt:
                            guessed_type = 'walk'
                        elif 'rope' in lowtxt:
                            guessed_type = 'useRope'
                        elif 'shovel' in lowtxt:
                            guessed_type = 'useShovel'
                        elif 'ladder' in lowtxt:
                            guessed_type = 'useLadder'
                        elif 'open' in lowtxt:
                            guessed_type = 'openDoor'

                    waypoint = {'label': name, 'type': guessed_type or 'imported-script', 'options': options}
                    if coords is not None:
                        waypoint['coordinate'] = coords
                    else:
                        waypoint['coordinate'] = None

                    # copy script for review
                    shutil.copy2(full, os.path.join(SRC, f))

                    # write per-script converted JSON to src for easy loading
                    converted_name = f"{name}.converted.json"
                    converted_path = os.path.join(SRC, converted_name)
                    with open(converted_path, 'w') as outfh:
                        json.dump([waypoint], outfh, indent=2)

                    migrated.append(waypoint)
                except Exception as e:
                    # fallback to placeholder
                    migrated.append({'label': name, 'type': 'script-ref', 'source': full, 'note': 'Review Python waypoint script and convert manually if desired.'})
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
