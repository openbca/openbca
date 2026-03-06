# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT

# Collect all modules from packages that might have hidden imports
datas = []
binaries = []
hiddenimports = []

# List of packages to collect (add any additional packages that are part of the app)
package_list = ['openpyxl', 'sqlmesh', 'streamlit', 'sqlglot', 'duckdb', 'config']

# Collect all specified packages and their dependencies
for package in package_list:
    collected_data, collected_binaries, collected_hiddenimports = collect_all(package)
    datas += collected_data
    binaries += collected_binaries
    hiddenimports += collected_hiddenimports

# Add all sqlglot dialects explicitly
hiddenimports += collect_submodules('sqlglot.dialects')

# Add Excel template files
datas += [
    ('nspm/input_templates/OpenBCA Configuration.xlsm', 'nspm/input_templates'),
    ('nspm/input_templates/OpenBCA Program Input.xlsx', 'nspm/input_templates'),
]

# Add Output directory for generated files
datas += [
    ('output/.keepme', 'output'),
]

# Add .env file if it exists
datas += [
    ('.env', '.'),
]

# Add nspm sqlmesh files and additional helper modules
datas += [
    ('nspm/models', 'nspm/models'),
    ('nspm/config.yaml', 'nspm'),
    ('nspm/*.py', 'nspm'),
]

# Add core sqlmesh files
datas += [
    ('core/models', 'core/models'),
    ('core/config.yaml', 'core'),
]

# Add streamlit test app files, including logos
datas += [
    ('user_interface/*.py', 'user_interface'),
    ('user_interface/pages/*.py', 'user_interface/pages'),
    ('user_interface/logos', 'user_interface/logos'),
]

# Add model_runners module (required by streamlit app)
datas += [
    ('model_runners.py', '.'),
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
