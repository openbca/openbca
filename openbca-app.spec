# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all modules from packages that might have hidden imports
datas = []
binaries = []
hiddenimports = []

# Collect openpyxl
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect sqlmesh
tmp_ret = collect_all('sqlmesh')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect streamlit
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect sqlglot (required by sqlmesh)
tmp_ret = collect_all('sqlglot')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect duckdb
tmp_ret = collect_all('duckdb')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Add all sqlglot dialects explicitly
hiddenimports += collect_submodules('sqlglot.dialects')

# Add Excel template files
datas += [
    ('nspm/input_templates/OpenBCA Configuration.xlsm', 'nspm/input_templates'),
    ('nspm/input_templates/OpenBCA Program Input.xlsx', 'nspm/input_templates'),
]

# Add logos
datas += [
    ('streamlit_test/logos', 'streamlit_test/logos'),
]

# Add nspm package files
datas += [
    ('nspm/models', 'nspm/models'),
    ('nspm/*', 'nspm'),
]

# Add core package files
datas += [
    ('core/models', 'core/models'),
    ('core/config.yaml', 'core'),
]

# Add config package
datas += [
    ('config', 'config'),
]

# Add streamlit test helper modules
datas += [
    ('streamlit_test/*.py', 'streamlit_test'),
    ('streamlit_test/pages/*.py', 'streamlit_test/pages'),
]

# Add model_runners module (required by streamlit app)
datas += [
    ('model_runners.py', '.'),
]

# Add explicit hidden imports for key dependencies
hiddenimports += [
    'openpyxl.cell._writer',
    'pandas',
    'numpy',
    'sqlmesh.core.model',
    'sqlmesh.core.context',
    'watchdog',
    'tabulate',
    # 'model_runners',
    # 'nspm',
    # 'core',
    # 'streamlit_test',
    # 'validation_functions',
    # 'helper_functions',
    # 'figures',
    # 'sql_queries',
]

a = Analysis(
    ['launcher.py'],
    pathex=["."],
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
    name='openbca-app',
)
