"""开票导入模板小工具 · 本地后端。双击 exe 启动后在本机浏览器中使用，数据不出本机。"""
import io
import os
import tempfile

from flask import Flask, jsonify, request, send_file, send_from_directory

from backend.ocr_engine import ocr_image
from backend.table_extract import boxes_to_grid, parse_excel, parse_pdf
from backend.taxcodes import search as code_search, guess as code_guess
from backend.exporter import export_rows
from backend.paths import FRONTEND_DIR

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/ocr", methods=["POST"])
def api_ocr():
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "msg": "没有文件"}), 400
    suffix = os.path.splitext(f.filename or "")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        f.save(tmp.name)
        path = tmp.name
    try:
        items = ocr_image(path)
    finally:
        os.unlink(path)
    grid = boxes_to_grid(items)
    return jsonify({"ok": True, "items": items, "grid": grid["rows"]})


@app.route("/api/parse", methods=["POST"])
def api_parse():
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "msg": "没有文件"}), 400
    data = f.read()
    name = (f.filename or "").lower()
    try:
        if name.endswith((".xlsx", ".xls")):
            r = parse_excel(data)
            return jsonify({"ok": True, "kind": "excel", **r})
        if name.endswith(".pdf"):
            r = parse_pdf(data)
            return jsonify({"ok": True, **r})
        return jsonify({"ok": False, "msg": "不支持的文件类型"}), 400
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "msg": f"解析失败：{e}"}), 500


@app.route("/api/codes")
def api_codes():
    q = request.args.get("q", "")
    return jsonify({"ok": True, "items": code_search(q)})


@app.route("/api/guess", methods=["POST"])
def api_guess():
    name = (request.json or {}).get("name", "")
    hit = code_guess(name)
    return jsonify({"ok": True, "item": hit})


@app.route("/api/export", methods=["POST"])
def api_export():
    rows = (request.json or {}).get("rows", [])
    # 基础校验：项目名称必填、金额必填、编码须为19位数字
    problems = []
    for i, r in enumerate(rows, 1):
        if not (r.get("name") or "").strip():
            problems.append(f"第{i}行缺项目名称")
        if not (r.get("amount") or "").strip():
            problems.append(f"第{i}行缺金额")
        code = (r.get("code") or "").strip()
        if code and (len(code) != 19 or not code.isdigit()):
            problems.append(f"第{i}行编码不是19位数字")
    if problems:
        return jsonify({"ok": False, "msg": "请先修正：\n" + "\n".join(problems)}), 400
    data = export_rows(rows)
    return send_file(io.BytesIO(data),
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="发票开具项目信息导入模板.xlsx")


def main():
    # 本机启动，自动打开浏览器
    import threading
    import webbrowser
    port = 18742
    threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}/")).start()
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
