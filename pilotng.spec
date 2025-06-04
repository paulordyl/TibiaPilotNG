# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/repositories/actionBar/images', 'src/repositories/actionBar/images'),
        ('src/repositories/battleList/images', 'src/repositories/battleList/images'),
        ('src/repositories/chat/images', 'src/repositories/chat/images'),
        ('src/repositories/gameWindow/images', 'src/repositories/gameWindow/images'),
        ('src/repositories/inventory/images', 'src/repositories/inventory/images'),
        ('src/repositories/radar/images', 'src/repositories/radar/images'),
        ('src/repositories/radar/npys', 'src/repositories/radar/npys'),
        ('src/repositories/refill/images', 'src/repositories/refill/images'),
        ('src/repositories/skills/images', 'src/repositories/skills/images'),
        ('src/repositories/statsBar/images', 'src/repositories/statsBar/images'),
        ('src/repositories/statusBar/images', 'src/repositories/statusBar/images')
    ],
    hiddenimports=[
        'numpy',
        'scipy',
        'customtkinter',
        'cv2',
        'mss',
        'PIL',
        'pytesseract',
        'tcod',
        'cityhash',
        'numba',
        'requests',
        'skimage',
        # Add any other necessary hidden imports here
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pilotng',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pilotng',
)
