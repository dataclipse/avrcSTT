# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_all

pkg1_binaries, pkg1_datas, pkg1_hiddenimports = collect_all('sv_ttk')
pkg2_binaries, pkg2_datas, pkg2_hiddenimports = collect_all('whisper')

binaries = pkg1_binaries + pkg2_binaries
datas = pkg1_datas + pkg2_datas
hiddenimports = pkg1_hiddenimports + pkg2_hiddenimports

a = Analysis(
    ['avrcSTT.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='avrcSTT',
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
    name='avrcSTT',
)
