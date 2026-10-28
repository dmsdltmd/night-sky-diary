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
    }


def load_entries(nickname: str) -> list[dict]:
    """날짜순으로 정렬된 일기 목록"""
    c = _client()
    if c is None:
        box = st.session_state.setdefault("demo_db", {})
        return sorted(box.get(nickname, {}).values(), key=lambda e: e["date"])
    res = c.table("diaries").select("*").eq("nickname", nickname).order("entry_date").execute()
    return [_row_to_entry(r) for r in res.data]


def save_entry(nickname: str, date: str, text: str, probs: list[float], corrected: str | None):
    """같은 날짜에 이미 있으면 덮어써요"""
    c = _client()
    if c is None:
        box = st.session_state.setdefault("demo_db", {}).setdefault(nickname, {})
        box[date] = {"date": date, "text": text, "probs": list(probs), "corrected": corrected}
        return
    row = {"nickname": nickname, "entry_date": date, "content": text, "corrected": corrected}
    row.update({c_: round(float(p), 4) for c_, p in zip(COLS, probs)})
    c.table("diaries").upsert(row, on_conflict="nickname,entry_date").execute()


def delete_entry(nickname: str, date: str):
    c = _client()
    if c is None:
        st.session_state.setdefault("demo_db", {}).get(nickname, {}).pop(date, None)
        return
    c.table("diaries").delete().eq("nickname", nickname).eq("entry_date", date).execute()
