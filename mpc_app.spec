# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui/*', 'gui'),
        ('utils/*', 'utils'),
        ('trajectory_config.py', '.'),
        ('mpc.py', '.'),
        ('requirements.txt', '.')
    ],
    hiddenimports=[
        'numpy', 
        'scipy', 
        'matplotlib', 
        'tkinter',
        'cvxpy',
        'cvxpy.atoms',
        'cvxpy.expressions',
        'cvxpy.problems',
        'cvxpy.interface',
        'cvxpy.reductions',
        'cvxpy.error',
        'cvxpy.settings',
        'cvxpy.utilities',
        'cvxpy.constraints',
        'cvxpy.lin_ops',
        'clarabel'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MPC_Trajectory_Designer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Changed to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)