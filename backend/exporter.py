"""导出：把明细行填入广东电子税务局导入模板（sheet1，A-H 列，从第 4 行起）。
直接在用户模板文件副本上写，保留原模板的说明、约束、下拉选项和其他 sheet。"""
import io

from backend.paths import TEMPLATE_XLSX

# 列映射：目标字段 -> 模板列
COLS = {"name": "A", "code": "B", "spec": "C", "unit": "D",
        "qty": "E", "price": "F", "amount": "G", "rate": "H"}
START_ROW = 4


def export_rows(rows):
    """rows: [{'name','code','spec','unit','qty','price','amount','rate'}, ...]
    返回 xlsx 二进制。"""
    from openpyxl import load_workbook
    wb = load_workbook(TEMPLATE_XLSX)
    ws = wb["Sheet1"] if "Sheet1" in wb.sheetnames else wb.worksheets[0]
    # 先清空旧数据区（第4行起，A-H列），保留样式
    for r in range(START_ROW, ws.max_row + 1):
        empty = True
        for col in "ABCDEFGH":
            if ws[f"{col}{r}"].value not in (None, ""):
                empty = False
                break
        if empty and r > START_ROW + len(rows) + 5:
            break
        for col in "ABCDEFGH":
            ws[f"{col}{r}"].value = None
    for i, row in enumerate(rows):
        r = START_ROW + i
        for field, col in COLS.items():
            v = (row.get(field) or "").strip()
            if v == "":
                continue
            ws[f"{col}{r}"] = v
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
