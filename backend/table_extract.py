"""从识别结果 / PDF / Excel 中提取表格行。"""
import io


def boxes_to_grid(items, y_tol_ratio=0.6):
    """把 OCR 文本块按 Y 分组为行、行内按 X 排序。
    返回 {'rows': [[cell_text,...], ...]}，单元格为识别到的文本（不做列对齐假设，
    前端用"手动对应列"让用户指定哪列对应哪个字段）。"""
    if not items:
        return {"rows": []}
    # 每块的中心 y 与高度
    pts = []
    for it in items:
        xs = [p[0] for p in it["box"]]
        ys = [p[1] for p in it["box"]]
        pts.append({
            "text": it["text"],
            "cx": (min(xs) + max(xs)) / 2,
            "cy": (min(ys) + max(ys)) / 2,
            "h": max(ys) - min(ys),
        })
    pts.sort(key=lambda p: p["cy"])
    rows = []
    for p in pts:
        placed = False
        for r in rows:
            # 与行内任一块的 y 重叠即归入该行
            if abs(p["cy"] - r["cy"]) < p["h"] * y_tol_ratio + r["h"] * y_tol_ratio:
                r["cells"].append(p)
                r["cy"] = sum(c["cy"] for c in r["cells"]) / len(r["cells"])
                placed = True
                break
        if not placed:
            rows.append({"cy": p["cy"], "h": p["h"], "cells": [p]})
    grid = []
    for r in rows:
        cells = sorted(r["cells"], key=lambda c: c["cx"])
        grid.append([c["text"] for c in cells])
    return {"rows": grid}


def parse_excel(file_bytes, sheet_index=0, header_row=0):
    """直接读 Excel（openpyxl），返回 {'header': [...], 'rows': [[...]]}。"""
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(file_bytes), data_only=True, read_only=True)
    ws = wb.worksheets[sheet_index]
    header, rows = [], []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        vals = [("" if v is None else str(v).strip()) for v in row]
        # 去掉全空行尾部空列
        while vals and vals[-1] == "":
            vals.pop()
        if not vals:
            continue
        if i == header_row:
            header = vals
        else:
            rows.append(vals)
    return {"header": header, "rows": rows,
            "sheets": wb.sheetnames}


def parse_pdf(file_bytes):
    """PDF：先尝试直接取文本表格（pdfplumber）；取不到则转图片走 OCR。
    返回 {'kind': 'text'|'image', ...}。"""
    import pdfplumber
    out_rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for t in tables:
                for row in t:
                    vals = [("" if v is None else str(v).replace("\n", "").strip()) for v in row]
                    if any(vals):
                        out_rows.append(vals)
    if out_rows:
        return {"kind": "text", "rows": out_rows}
    # 扫描件：转图片 OCR（需要时前端再调 /api/ocr）
    return {"kind": "image", "rows": []}
