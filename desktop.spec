# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Collect all resources (binaries, data, hiddenimports) for clr_loader and pythonnet
datas_clr, binaries_clr, hiddenimports_clr = collect_all('clr_loader')
datas_pn, binaries_pn, hiddenimports_pn = collect_all('pythonnet')

combined_datas = [('templates', 'templates'), ('static', 'static')] + datas_clr + datas_pn
combined_binaries = binaries_clr + binaries_pn
combined_hiddenimports = ['clr'] + hiddenimports_clr + hiddenimports_pn

a = Analysis(
    ['desktop.py'],
    pathex=[],
    binaries=combined_binaries,
    datas=combined_datas,
    hiddenimports=combined_hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabling UPX compression to avoid DLL loading/corruption issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
