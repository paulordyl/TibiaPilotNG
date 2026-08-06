"""Importer scaffold: clone an external tibiabotNG repo and extract likely assets (waypoints, images, configs).

Usage:
  python3 tools/import_tibiabot.py <git_url>

This is conservative: it will not overwrite project files automatically. It copies found assets into tools/imported/<repo-name>/ so you can review and approve manual merge.
"""
import sys
import os
import shutil
import subprocess
from urllib.parse import urlparse

OUT_DIR = os.path.join('tools', 'imported')


def run(cmd, cwd=None):
    print('>', ' '.join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def clone_repo(url):
    parsed = urlparse(url)
    name = os.path.splitext(os.path.basename(parsed.path))[0]
    dest = os.path.join(OUT_DIR, name)
    if os.path.exists(dest):
        print('Already cloned at', dest)
        return dest
    os.makedirs(OUT_DIR, exist_ok=True)
    run(['git', 'clone', '--depth', '1', url, dest])
    return dest


def find_assets(repo_path):
    assets = {'waypoints': [], 'images': [], 'configs': []}
    for root, dirs, files in os.walk(repo_path):
        for f in files:
            if f.lower().endswith(('.json', '.yaml', '.yml', '.txt')) and 'way' in f.lower():
                assets['waypoints'].append(os.path.join(root, f))
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                assets['images'].append(os.path.join(root, f))
            if f.lower().endswith(('.cfg', '.ini', '.conf')) or 'config' in f.lower():
                assets['configs'].append(os.path.join(root, f))
    return assets


def copy_assets(found, repo_name):
    target = os.path.join(OUT_DIR, repo_name)
    out_assets = os.path.join(target, 'extracted')
    os.makedirs(out_assets, exist_ok=True)
    for k, paths in found.items():
        dest_dir = os.path.join(out_assets, k)
        os.makedirs(dest_dir, exist_ok=True)
        for p in paths:
            shutil.copy2(p, dest_dir)
    return out_assets


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 tools/import_tibiabot.py <git_url>')
        sys.exit(1)
    url = sys.argv[1]
    repo_path = clone_repo(url)
    name = os.path.splitext(os.path.basename(repo_path))[0]
    found = find_assets(repo_path)
    print('Found assets:')
    for k, v in found.items():
        print(f'  {k}: {len(v)}')
    copied = copy_assets(found, name)
    print('Copied assets to', copied)
    print('Review files and manually merge into src/ as appropriate.')
