# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Desktop\\LegalRiskApp\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\Desktop\\LegalRiskApp\\frontend\\dist', 'frontend\\dist'), ('D:\\Desktop\\LegalRiskApp\\SimHei.ttf', '.'), ('D:\\Desktop\\LegalRiskApp\\favicon.ico', '.')],
    hiddenimports=[],
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
    name='LegalRiskApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\Desktop\\LegalRiskApp\\favicon.ico'],
)
