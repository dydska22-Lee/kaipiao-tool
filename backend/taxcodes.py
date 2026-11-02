"""税收分类编码库：4205 条，提供按名称/编码搜索与模糊匹配。"""
import gzip
import json

from backend.paths import CODES_JSON

_CODES = None


def _load():
    global _CODES
    if _CODES is None:
        with gzip.open(CODES_JSON, "rt", encoding="utf-8") as f:
            # 紧凑格式：[code, name, cat, leaf]
            _CODES = [{"code": c[0], "name": c[1], "cat": c[2], "leaf": bool(c[3])}
                      for c in json.load(f)]
    return _CODES


def search(keyword, limit=20):
    """按名称或编码关键字搜索，末级编码优先。"""
    codes = _load()
    kw = (keyword or "").strip()
    if not kw:
        return []
    is_digit = kw[:1].isdigit()
    hits = []
    for c in codes:
        if is_digit:
            if c["code"].startswith(kw):
                hits.append((0, c))
        else:
            if kw in c["name"]:
                hits.append((0, c))
            elif kw in (c["cat"] or ""):
                hits.append((1, c))
        if len(hits) >= limit * 3:
            break
    # 名称命中优先于类别/说明命中；末级优先，其次名称短的优先
    hits = [c for _, c in sorted(hits, key=lambda t: (t[0], 0 if t[1]["leaf"] else 1, len(t[1]["name"])))]
    return hits[:limit]


def guess(name):
    """按商品名猜编码：取名称包含商品关键词的末级编码，得分最高的1个。"""
    codes = _load()
    nm = (name or "").strip()
    if not nm:
        return None
    # 切出可能的关键词：去掉数字字母型号，保留中文词
    import re
    keywords = [k for k in re.findall(r"[\u4e00-\u9fa5]{2,}", nm)]
    best, best_score = None, 0
    for c in codes:
        if not c["leaf"]:
            continue
        score = 0
        for kw in keywords:
            if kw in c["name"]:
                score += len(kw) * 2
        if c["name"] in nm or nm in c["name"]:
            score += 10
        if score > best_score:
            best, best_score = c, score
    return best
