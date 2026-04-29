# -*- mode: python ; coding: utf-8 -*-
import os

# Paths resolve from the spec file location so `pyinstaller path/to/Redshale.spec` works from any cwd.
_spec_dir = os.path.dirname(os.path.abspath(SPEC))
# Pin build output next to the spec (overrides CLI defaults that follow the shell cwd).
distpath = os.path.join(_spec_dir, 'dist')
workpath = os.path.join(_spec_dir, 'build')

a = Analysis(
    [os.path.join(_spec_dir, 'src', 'ml_pipeline_studio', 'app.py')],
    pathex=[_spec_dir, os.path.join(_spec_dir, 'src')],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Redshale',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='Redshale',
)
app = BUNDLE(
    coll,
    name='Redshale.app',
    icon=None,
    bundle_identifier=None,
)
