"""감정 별자리 (Night Sky Diary) - Streamlit 메인

실행: streamlit run app.py
화면: 오늘의 별(일기 쓰기) / 별자리 지도(탐험) / 이달의 하늘(월간 갤러리)
"""
import datetime as dt
import calendar

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import analysis as A
import db
import sky
from model import EMO, predict

st.set_page_config(page_title="감정 별자리", page_icon="✦", layout="wide")

# ---------- 공통 스타일 ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@300;500;700&family=Nanum+Myeongjo:wght@700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stMarkdown, .stTextArea textarea { font-family: "Gothic A1", "Apple SD Gothic Neo", sans-serif; }
h1, h2, h3 { font-family: "Nanum Myeongjo", serif !important; }
.stApp { background: radial-gradient(120% 50% at 50% -10%, #10153a 0%, transparent 70%), #090c1c; }
.emo-row { display:grid; grid-template-columns:40px 1fr 44px; gap:8px; align-items:center; font-size:14px; margin:4px 0; }
.emo-track { height:9px; background:rgba(238,240,255,.08); border-radius:9px; overflow:hidden; }
.emo-track i { display:block; height:100%; border-radius:9px; }
.emo-pct { text-align:right; color:#a6acd3; font-variant-numeric:tabular-nums; }
.note { color:#a6acd3; font-size:13px; }
</style>""", unsafe_allow_html=True)


def emotion_bars(probs):
    rows = sorted(zip(EMO, probs, sky.COLORS), key=lambda t: -t[1])
    html = "".join(
        f'<div class="emo-row"><span>{e}</span><span class="emo-track"><i style="width:{p*100:.1f}%;background:{c}"></i></span>'
        f'<span class="emo-pct">{round(p*100)}%</span></div>' for e, p, c in rows)
    st.markdown(html, unsafe_allow_html=True)


# ---------- 사이드바: 닉네임 ----------
with st.sidebar:
    st.markdown("### ✦ 감정 별자리")
    nickname = st.text_input("닉네임", value=st.session_state.get("nickname", ""), max_chars=20,
                             placeholder="내 하늘을 구분할 이름")
    st.session_state["nickname"] = nickname.strip()
    if db.is_demo():
        st.info("체험 모드예요. 기록은 이 브라우저 창에만 잠깐 저장돼요.")

NICK = st.session_state["nickname"]


def need_nickname():
    if not NICK:
        st.warning("왼쪽 사이드바에 닉네임을 먼저 적어 주세요.")
        st.stop()


# ---------- 화면 1: 오늘의 별 ----------
def page_write():
    st.title("오늘의 별")
    st.caption("일기를 쓰면 AI가 섞인 감정을 비율로 읽고, 그 색으로 오늘의 별을 띄워요.")
    need_nickname()

    entries = {e["date"]: e for e in db.load_entries(NICK)}
    day = st.date_input("날짜", value=dt.date.today(), max_value=dt.date.today())
    key = day.isoformat()
    old = entries.get(key)

    # 날짜가 바뀌면 그날 기록을 불러와요
    if st.session_state.get("draft_date") != key:
        st.session_state["draft_date"] = key
        st.session_state["draft_text"] = old["text"] if old else ""
        st.session_state["draft_probs"] = old["probs"] if old else None

    text = st.text_area("오늘의 일기", key="draft_text", height=150, max_chars=500,
                        placeholder="예) 발표는 끝나서 뿌듯한데 결과가 걱정된다")

    if st.button("감정 분석하기", type="primary", disabled=not text.strip()):
        with st.spinner("감정을 읽는 중..."):
            st.session_state["draft_probs"] = predict(text.strip())

    probs = st.session_state.get("draft_probs")
    if not probs:
        return

    st.subheader("AI 감정 분석")
    emotion_bars(probs)
    ai_top = EMO[max(range(len(EMO)), key=lambda i: probs[i])]
    st.markdown(f'<p class="note">AI 확신도 {round(max(probs)*100)}% · 가장 큰 감정은 {ai_top}이에요.</p>',
                unsafe_allow_html=True)

    options = ["AI 결과 그대로"] + EMO
    default = options.index(old["corrected"]) if old and old.get("corrected") in EMO else 0
    pick = st.radio("내 느낌과 다르다면 골라 주세요", options, index=default, horizontal=True)
    corrected = None if pick == "AI 결과 그대로" or pick == ai_top else pick

    c1, c2 = st.columns([1, 1])
    if c1.button("별 띄우기 ✦", type="primary", use_container_width=True):
        db.save_entry(NICK, key, text.strip(), probs, corrected)
        st.success(f"{day.month}월 {day.day}일의 별이 떴어요. 별자리 지도에서 확인해 보세요.")
    if old and c2.button("이 날 기록 지우기", use_container_width=True):
        db.delete_entry(NICK, key)
        st.session_state["draft_date"] = None
        st.rerun()


# ---------- 화면 2: 별자리 지도 ----------
def page_map():
    st.title("별자리 지도")
    st.caption("별 하나가 하루예요. 감정 구성이 비슷한 날은 가까이 놓이고 은은한 선으로 이어져요.")
    need_nickname()
    entries = db.load_entries(NICK)
    if not entries:
        st.info("아직 뜬 별이 없어요. '오늘의 별'에서 첫 일기를 써 보세요.")
        return

    months = sorted({e["date"][:7] for e in entries}, reverse=True)
    scope = st.selectbox("범위", ["전체 기간"] + months)
    shown = entries if scope == "전체 기간" else [e for e in entries if e["date"].startswith(scope)]
    components.html(sky.map_html(shown), height=690)

    groups = A.co_occurring(shown)
    if groups:
        st.markdown("**자주 함께 온 감정**")
        for a, b, n in groups[:3]:
            st.markdown(f"- {a} + {b} : {n}일")


# ---------- 화면 3: 이달의 하늘 ----------
def page_month():
    st.title("이달의 하늘")
    st.caption("한 달의 감정이 하나의 밤하늘 작품이 돼요.")
    need_nickname()
    entries = db.load_entries(NICK)
    months = sorted({e["date"][:7] for e in entries}, reverse=True) or [dt.date.today().strftime("%Y-%m")]
    ym = st.selectbox("달", months)
    y, m = int(ym[:4]), int(ym[5:7])
    cur = [e for e in entries if e["date"].startswith(ym)]
    components.html(sky.poster_html(cur, y, m), height=650)
    if not cur:
        return

    # 지난달과 비교
    py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    prev = [e for e in entries if e["date"].startswith(f"{py}-{pm:02d}")]
    now_mean = A.month_mean(cur)
    df = pd.DataFrame({"감정": EMO, "이번 달(%)": (now_mean * 100).round(1)})
    if prev:
        df["지난달(%)"] = (A.month_mean(prev) * 100).round(1)
        df["변화(%p)"] = (df["이번 달(%)"] - df["지난달(%)"]).round(1)
    st.subheader("감정 구성")
    st.dataframe(df, hide_index=True, use_container_width=True)

    tps = A.turning_points(cur)
    st.subheader("분위기가 바뀐 날")
    if tps:
        for t in tps:
            st.markdown(f"- **{t['date']}** : {t['from']} → {t['to']} (변화 정도 {t['jsd']})")
    else:
        st.markdown('<p class="note">이번 달은 감정 구성이 크게 바뀐 날 없이 이어졌어요.</p>', unsafe_allow_html=True)


# ---------- 화면 전환 ----------
nav = st.navigation([
    st.Page(page_write, title="오늘의 별", icon="✍️", url_path="write", default=True),
    st.Page(page_map, title="별자리 지도", icon="🌌", url_path="map"),
    st.Page(page_month, title="이달의 하늘", icon="🖼️", url_path="month"),
])
nav.run()
