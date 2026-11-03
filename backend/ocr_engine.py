"""OCR 引擎：RapidOCR（PaddleOCR 最新模型，onnxruntime 推理）。
识别效果与 PaddleOCR 同源模型一致，体积小、适合打包进 exe。"""
import threading

_engine = None
_lock = threading.Lock()


def get_engine():
    global _engine
    with _lock:
        if _engine is None:
            from rapidocr import RapidOCR
            _engine = RapidOCR()
        return _engine


def ocr_image(image_path):
    """识别图片，返回 [{'text': str, 'score': float, 'box': [[x,y]x4]}, ...]"""
    engine = get_engine()
    out = engine(image_path)
    # 新版 rapidocr(3.x) 返回 RapidOCROutput 对象；旧版返回 (result, elapse) 元组
    if hasattr(out, "txts"):
        boxes = out.boxes if out.boxes is not None else []
        txts = out.txts if out.txts is not None else []
        scores = out.scores if out.scores is not None else []
        items = zip(boxes, txts, scores)
    else:
        result, _ = out
        items = result or []
    ret = []
    for box, text, score in items:
        ret.append({
            "text": text,
            "score": round(float(score), 3),
            "box": [[float(x), float(y)] for x, y in box],
        })
    return ret
