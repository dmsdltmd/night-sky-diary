"""일기 저장/불러오기

- Supabase 키(secrets)가 있으면 Supabase에 저장해요.
- 키가 없으면 '체험 모드': 브라우저 세션 안에만 저장돼요. (새로고침하면 사라짐)
"""
import streamlit as st

COLS = ["joy", "flutter", "calm", "tired", "sad", "anxious", "angry"]  # EMO 순서와 같음


@st.cache_resource
def _client():
    try:
        url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    except Exception:
        return None
    from supabase import create_client
    return create_client(url, key)


def is_demo() -> bool:
    return _client() is None


def _row_to_entry(r: dict) -> dict:
    return {
        "date": str(r["entry_date"]),
        "text": r["content"],
        "probs": [float(r[c] or 0) for c in COLS],
        "corrected": r.get("corrected"),
        "kind": r.get("kind") or "diary",          # diary = 일기, quick = 10초 기록
        "reply": r.get("reply"),                   # 타임캡슐 답장
        "reply_at": str(r["reply_at"]) if r.get("reply_at") else None,
    }


def load_entries(nickname: str) -> list[dict]:
    """날짜순으로 정렬된 일기 목록"""
    c = _client()
    if c is None:
        box = st.session_state.setdefault("demo_db", {})
        return sorted(box.get(nickname, {}).values(), key=lambda e: e["date"])
    res = c.table("diaries").select("*").eq("nickname", nickname).order("entry_date").execute()
    return [_row_to_entry(r) for r in res.data]


def save_entry(nickname: str, date: str, text: str, probs: list[float], corrected: str | None, kind: str = "diary"):
    """같은 날짜에 이미 있으면 덮어써요 (답장은 그대로 남겨요)"""
    c = _client()
    if c is None:
        box = st.session_state.setdefault("demo_db", {}).setdefault(nickname, {})
        prev = box.get(date, {})
        box[date] = {"date": date, "text": text, "probs": list(probs), "corrected": corrected, "kind": kind,
                     "reply": prev.get("reply"), "reply_at": prev.get("reply_at")}
        return
    row = {"nickname": nickname, "entry_date": date, "content": text, "corrected": corrected, "kind": kind}
    row.update({c_: round(float(p), 4) for c_, p in zip(COLS, probs)})
    c.table("diaries").upsert(row, on_conflict="nickname,entry_date").execute()


def delete_entry(nickname: str, date: str):
    c = _client()
    if c is None:
        st.session_state.setdefault("demo_db", {}).get(nickname, {}).pop(date, None)
        return
    c.table("diaries").delete().eq("nickname", nickname).eq("entry_date", date).execute()


def save_reply(nickname: str, date: str, reply: str | None, reply_at: str | None):
    """타임캡슐: 지난 기록에 지금의 내가 남긴 답장 저장 (None이면 지우기)"""
    c = _client()
    if c is None:
        e = st.session_state.setdefault("demo_db", {}).get(nickname, {}).get(date)
        if e is not None:
            e["reply"], e["reply_at"] = reply, reply_at
        return
    c.table("diaries").update({"reply": reply, "reply_at": reply_at}).eq("nickname", nickname).eq("entry_date", date).execute()
