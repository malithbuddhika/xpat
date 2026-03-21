# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'shiboken6',
]

datas = collect_data_files('PySide6', includes=['plugins/platforms', 'plugins/imageformats'])

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.Qt3D',
        'PySide6.QtQml',
        'PySide6.QtNetwork',
        'PySide6.QtPrintSupport',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.QtLocationIot',
        'PySide6.QtVirtualKeyboard',
        'numpy',
        'scipy',
        'PIL',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='xpat_worker_tool',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='xpat_worker_tool',
)
app = BUNDLE(
    coll,
    name='xpat_worker_tool.app',
    icon=None,
    bundle_identifier=None,
)
