"""OCR 引擎：RapidOCR（PaddleOCR 模型家族的轻量版，onnxruntime 推理）。
识别效果与 PaddleOCR 同源模型一致，体积小、适合打包进 exe。"""
import threading

_engine = None
_lock = threading.Lock()


def get_engine():
    global _engine
    with _lock:
        if _engine is None:
            from rapidocr_onnxruntime import RapidOCR
            _engine = RapidOCR()
        return _engine


def ocr_image(image_path):
    """识别图片，返回 [{'text': str, 'score': float, 'box': [[x,y]x4]}, ...]"""
    engine = get_engine()
    result, _ = engine(image_path)
    out = []
    if result:
        for box, text, score in result:
            out.append({
                "text": text,
                "score": round(float(score), 3),
                "box": [[float(x), float(y)] for x, y in box],
            })
    return out
