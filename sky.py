"""별자리 화면(HTML/JS) 만들기

Python에서 계산한 별 위치·일기 내용을 JSON으로 묶어서 templates/sky.html 안에 넣어요.
별을 누르면 일기가 뜨는 건 전부 JS 안에서 처리돼서 Python과 주고받을 필요가 없어요.
"""
import json
import calendar
from pathlib import Path

import numpy as np
import analysis as A

COLORS = ["#ffcf4a", "#ff8fb1", "#6fd3a8", "#9aa6b8", "#5b84f0", "#b08cf0", "#f0645a"]  # EMO 순서
TEMPLATE = (Path(__file__).parent / "templates" / "sky.html").read_text(encoding="utf-8")
MAP_TEMPLATE = (Path(__file__).parent / "templates" / "sky_map.html").read_text(encoding="utf-8")


def _render(data: dict, height: int, template: str = TEMPLATE) -> str:
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")  # 일기에 </script>가 있어도 안전하게
    return template.replace("__DATA__", js).replace("__HEIGHT__", str(height))


def _stars(entries, X, xy=None, sims=None):
    out = []
    for i, e in enumerate(entries):
        s = {"date": e["date"], "day": int(e["date"][8:10]), "text": e["text"],
             "p": [round(float(v), 4) for v in X[i]], "corrected": e.get("corrected")}
        if xy is not None:
            s["x"], s["y"] = float(xy[i, 0]), float(xy[i, 1])
        if sims is not None:
            s["similar"] = sims[i]
        out.append(s)
    return out


def map_html(entries: list[dict], height: int = 880, extra: dict | None = None) -> str:
    """탐험 화면: 감정이 비슷한 날은 가까이, 비슷한 날끼리 선으로 연결
    extra: 화면 위 숫자 카드에 쓸 값 (예: {"pos_delta": 12.0} = 긍정 감정이 지난달보다 12%p 늘었음)"""
    X = A.matrix(entries)
    dates = [e["date"] for e in entries]
    data = {"mode": "map", "emo": A.EMO, "colors": COLORS, "seed": 7,
            "stars": _stars(entries, X, A.layout(X), A.similar_days(X, dates)),
            # 지도에서는 별마다 가장 비슷한 날 2개까지 이어요 (유사도 0.6 이상)
            "links": A.links(X, threshold=0.6, k=2), "extra": extra or {}}
    return _render(data, height, MAP_TEMPLATE)


def poster_html(entries: list[dict], year: int, month: int, height: int = 640) -> str:
    """월간 포스터: 한 달의 별을 날짜 순서로 잇기"""
    X = A.matrix(entries)
    dates = [e["date"] for e in entries]
    mean = A.month_mean(entries)
    top = int(mean.argmax()) if len(entries) else -1
    sub = f"{len(entries)}일의 별 · 가장 많이 빛난 감정 {A.EMO[top]}" if top >= 0 else "아직 별이 없어요"
    data = {"mode": "poster", "emo": A.EMO, "colors": COLORS, "seed": year * 13 + month,
            "days": calendar.monthrange(year, month)[1], "top": top,
            "title": f"{month}월의 하늘", "subtitle": sub,
            "stars": _stars(entries, X, sims=A.similar_days(X, dates)), "links": []}
    return _render(data, height)


STAR_TEMPLATE = (Path(__file__).parent / "templates" / "star.html").read_text(encoding="utf-8")


def star_html(probs: list[float], label: str = "", height: int = 300) -> str:
    """오늘의 별 미리보기: 감정 비율로 별 하나 그리기"""
    data = {"p": [round(float(v), 4) for v in probs], "colors": COLORS, "label": label}
    return _render(data, height, STAR_TEMPLATE)
