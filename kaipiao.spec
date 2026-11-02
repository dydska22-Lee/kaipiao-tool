# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：在 GitHub Actions 的 Windows 环境里运行，产出单文件 exe。"""
from PyInstaller.utils.hooks import collect_data_files

# RapidOCR 的 onnx 模型在 pip 包内，显式收集
rapidocr_data = collect_data_files("rapidocr_onnxruntime", includes=["models/*.onnx"])

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("frontend", "frontend"),
        ("resources/template.xlsx", "resources"),
        ("resources/codes.json.gz", "resources"),
    ]
    + rapidocr_data,
    hiddenimports=[
        "rapidocr_onnxruntime",
        "onnxruntime",
        "flask",
        "werkzeug",
        "openpyxl",
        "pdfplumber",
        "PIL",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="开票导入模板小工具",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # 不弹黑窗口，双击即用
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
