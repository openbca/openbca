# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('/Users/adam/Repos/openbca/user_interface/Entrypoint.py', '.'), ('excel_input_parsing', 'excel_input_parsing'), ('core/models', 'core/models'), ('core/config.yaml', 'core'), ('user_interface', 'user_interface'), ('model_runners.py', '.'), ('output/.keepme', 'output'), ('.env', '.')]
binaries = []
hiddenimports = ['config.paths.get_streamlit_app_dir', 'streamlit', 'sys', 'model_runners', 'config.env', 'config.paths', 'validation_functions', 'helper_functions', 'figures', 'sql_queries']
datas += copy_metadata('streamlit')
hiddenimports += collect_submodules('sqlglot.dialects')
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sqlmesh')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sqlglot')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('duckdb')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['/var/folders/25/5nbkd4b50l1c7mzmn111cszr0000gn/T/tmpml2jo6uz.py'],
    pathex=['.'],
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
    name='openbca-app',
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
    name='openbca-app',
)
