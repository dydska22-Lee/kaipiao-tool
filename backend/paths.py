"""打包友好的路径：开发时用源码目录，打包后用 sys._MEIPASS。"""
import os
import sys


def base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


FRONTEND_DIR = os.path.join(base_dir(), "frontend")
TEMPLATE_XLSX = os.path.join(base_dir(), "resources", "template.xlsx")
CODES_JSON = os.path.join(base_dir(), "resources", "codes.json.gz")
