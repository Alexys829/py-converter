# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# Use .ico on Windows, no icon on Linux
icon_path = 'pyconverter/resources/icons/app_icon.ico'
if not Path(icon_path).exists():
    icon_path = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pyconverter/resources', 'pyconverter/resources'),
    ],
    hiddenimports=[
        'pyconverter.converters.image',
        'pyconverter.converters.document',
        'pyconverter.converters.data',
        'pyconverter.converters.audio',
        'pyconverter.converters.video',
        'PySide6.QtSvg',
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
    name='pyconverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyconverter',
)
