# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller打包配置文件
生成 onedir 模式，隐藏控制台，带图标
"""

a = Analysis(
    ['gui.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),           # 图标文件
        ('ffmpeg/ffmpeg.exe', '.'),  # FFmpeg可执行文件
    ],
    hiddenimports=[
        'librosa',
        'numpy',
        'scipy',
        'scipy.signal',
        'scipy.ndimage',
        'scipy.sparse',
        'scipy.sparse.linalg',
        'scipy.linalg',
        'sklearn',
        'sklearn.utils',
        'sklearn.utils._cython_blas',
        'audioread',
        'audioread.ffdec',  # FFmpeg解码器
        'joblib',
        'decorator',
        'six',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 不需要matplotlib，节省体积
        'PyQt5',
        'PySide2',
        'tkinter.test',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BPM检测器',           # exe文件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                   # 启用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # 隐藏控制台！
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'             # 应用程序图标！
)

# COLLECT 生成 onedir 模式（文件夹）
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BPM检测器'             # 输出文件夹名
)