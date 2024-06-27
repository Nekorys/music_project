block_cipher = None

a = Analysis(
    ['main_window.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('awthemes-10.4.0', 'awthemes-10.4.0'),
        ('Additional', 'Additional'),
        ('Songs', 'Songs'),
        ('drive_sync.py', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='my_project',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='my_project',
    collect_subdir=False,
)