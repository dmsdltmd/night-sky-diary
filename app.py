"""감정 별자리 (Night Sky Diary) - Streamlit 메인

실행: streamlit run app.py
화면: 오늘의 별(일기 쓰기) / 별자리 지도(탐험) / 이달의 하늘(월간 갤러리)
"""
import datetime as dt
import html

import streamlit as st
import streamlit.components.v1 as components

import analysis as A
import db
import sky
from model import EMO, predict
from samples import SAMPLES

st.set_page_config(page_title="감정 별자리", page_icon="✦", layout="wide")
COL = dict(zip(EMO, sky.COLORS))

# ---------- 공통 스타일 (밤하늘 톤) ----------
# 주의: 아래 스타일 안에는 빈 줄을 넣지 마세요. 빈 줄이 있으면 화면에 코드가 글자로 보여요.
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@300;400;500;700&family=Nanum+Myeongjo:wght@700;800&display=swap" rel="stylesheet">
<style>
:root { --night:#090c1c; --panel:#121633; --panel2:#181d42; --line:rgba(238,240,255,.12); --ink:#eef0ff; --sub:#a6acd3; --faint:#6e74a0; --gold:#e8c472; }
html, body, .stApp, .stMarkdown, button, input, textarea, [data-testid="stSidebar"] { font-family:"Gothic A1","Apple SD Gothic Neo","Malgun Gothic",sans-serif !important; }
.stApp { background: radial-gradient(1200px 500px at 70% -10%, #1a2160 0%, transparent 60%), radial-gradient(900px 400px at 0% 0%, #12183f 0%, transparent 60%), var(--night); }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], footer, #MainMenu { display:none !important; }
.block-container { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 4rem; }
/* 사이드바 */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1130 0%, #090c1c 100%); border-right: 1px solid var(--line); }
.brand { font-family:"Nanum Myeongjo",serif; font-size:22px; font-weight:800; letter-spacing:-.01em; margin:4px 0 2px; }
.brand-sub { color:var(--sub); font-size:12.5px; margin-bottom:18px; }
.side-stat { display:flex; justify-content:space-between; padding:10px 0; border-top:1px solid var(--line); font-size:13px; color:var(--sub); }
.side-stat b { color:var(--ink); font-weight:700; font-variant-numeric:tabular-nums; }
/* 페이지 머리 */
.eyebrow { color:var(--gold); font-size:12px; letter-spacing:.14em; font-weight:500; margin-bottom:6px; }
.hero h1 { font-family:"Nanum Myeongjo",serif !important; font-size:38px !important; font-weight:800 !important; margin:0 !important; padding:0 !important; letter-spacing:-.01em; }
.hero p { color:var(--sub); font-size:14.5px; margin:8px 0 22px; }
/* 입력칸, 버튼 */
.stTextArea textarea { background:var(--panel) !important; border:1px solid var(--line) !important; border-radius:14px !important; font-size:15.5px !important; line-height:1.7 !important; color:var(--ink) !important; }
.stTextArea textarea:focus { border-color:var(--gold) !important; box-shadow:0 0 0 1px var(--gold) !important; }
.stDateInput input, .stTextInput input, [data-baseweb="select"] > div { background:var(--panel) !important; border-radius:10px !important; }
.stButton > button { border-radius:999px; padding:.55rem 1.3rem; font-weight:500; border:1px solid var(--line); background:transparent; width:100%; }
.stButton > button[kind="primary"] { background:var(--gold); color:#1d1606; border:0; font-weight:700; }
.stButton > button[kind="primary"]:hover { background:#f1d38f; color:#1d1606; }
[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(18,22,51,.72); border:1px solid var(--line) !important; border-radius:18px; }
.stRadio [role="radiogroup"] { gap:.35rem .9rem; }
/* 감정 막대 */
.emo-row { display:grid; grid-template-columns:46px 1fr 44px; gap:10px; align-items:center; font-size:14px; margin:7px 0; }
.emo-row i.dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; }
.emo-track { height:8px; background:rgba(238,240,255,.08); border-radius:8px; overflow:hidden; }
.emo-track b { display:block; height:100%; border-radius:8px; }
.emo-pct { text-align:right; color:var(--sub); font-variant-numeric:tabular-nums; }
.note { color:var(--sub); font-size:13px; margin:6px 0 0; }
.label { color:var(--gold); font-size:11.5px; letter-spacing:.12em; font-weight:500; margin:2px 0 10px; }
/* 빈 상태, 최근 기록 */
.empty-sky { height:300px; border-radius:18px; border:1px dashed rgba(238,240,255,.18); display:grid; place-items:center; text-align:center; color:var(--sub); font-size:14px; line-height:1.7;
  background: radial-gradient(circle at 50% 45%, rgba(232,196,114,.08), transparent 55%), #0b0f26; }
.empty-sky b { display:block; font-size:30px; color:var(--gold); font-weight:300; margin-bottom:6px; }
.recent { display:grid; grid-template-columns:10px 54px minmax(0,1fr) auto; gap:12px; align-items:center; padding:11px 0; border-top:1px solid var(--line); font-size:14px; }
.recent i { width:10px; height:10px; border-radius:50%; }
.recent .d { color:var(--sub); font-variant-numeric:tabular-nums; }
.recent .t { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.recent .e { color:var(--sub); font-size:12.5px; }
/* 숫자 카드 */
.cards { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin-bottom:14px; }
.card { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--c,#8b93c9); border-radius:12px; padding:12px 14px; }
.card b { display:block; font-size:24px; font-weight:700; color:var(--c,#eef0ff); line-height:1.15; font-variant-numeric:tabular-nums; }
.card span { color:var(--sub); font-size:12px; }
.delta-up { color:#7fd6a4; } .delta-down { color:#f08a7e; }
.turn { padding:10px 0; border-top:1px solid var(--line); font-size:14px; }
.turn small { color:var(--sub); display:block; margin-top:2px; }
</style>""", unsafe_allow_html=True)


def hero(eyebrow: str, title: str, desc: str):
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{desc}</p></div>',
                unsafe_allow_html=True)


def emotion_bars(probs):
    rows = sorted(zip(EMO, probs), key=lambda t: -t[1])
    st.markdown("".join(
        f'<div class="emo-row"><span><i class="dot" style="background:{COL[e]}"></i>{e}</span>'
        f'<span class="emo-track"><b style="width:{p*100:.1f}%;background:{COL[e]}"></b></span>'
        f'<span class="emo-pct">{round(p*100)}%</span></div>' for e, p in rows), unsafe_allow_html=True)


def top_emotion(e: dict) -> str:
    return e["corrected"] if e.get("corrected") in EMO else EMO[max(range(len(EMO)), key=lambda i: e["probs"][i])]


# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown('<div class="brand">✦ 감정 별자리</div><div class="brand-sub">하루가 별이 되는 감정 일기</div>',
                unsafe_allow_html=True)
    nickname = st.text_input("닉네임", value=st.session_state.get("nickname", ""), max_chars=20,
                             placeholder="내 하늘을 구분할 이름")
    st.session_state["nickname"] = nickname.strip()

NICK = st.session_state["nickname"]

with st.sidebar:
    if NICK:
        mine = db.load_entries(NICK)
        months = len({e["date"][:7] for e in mine})
        st.markdown(f'<div class="side-stat">뜬 별<b>{len(mine)}개</b></div>'
                    f'<div class="side-stat">기록한 달<b>{months}개월</b></div>', unsafe_allow_html=True)
        if db.is_demo():
            st.caption("체험 모드예요. 기록은 이 창에만 잠깐 저장돼요.")
            if st.button("예시 하늘 채우기", help="두 달 치 예시 일기 31개를 실제 모델로 분석해서 채워요"):
                bar = st.progress(0.0, text="예시 일기를 분석하는 중...")
                today = dt.date.today()
                for i, (ago, text) in enumerate(SAMPLES):
                    d = (today - dt.timedelta(days=ago)).isoformat()
                    db.save_entry(NICK, d, text, predict(text), None)
                    bar.progress((i + 1) / len(SAMPLES), text=f"예시 일기를 분석하는 중... {i+1}/{len(SAMPLES)}")
                st.session_state["draft_date"] = None
                st.rerun()


def need_nickname():
    if not NICK:
        st.markdown('<div class="empty-sky"><div><b>✦</b>왼쪽 사이드바에 닉네임을 적으면<br>나만의 밤하늘이 열려요.</div></div>',
                    unsafe_allow_html=True)
        st.stop()


# ---------- 화면 1: 오늘의 별 ----------
def page_write():
    hero("TODAY'S STAR", "오늘의 별", "일기를 쓰면 AI가 섞인 감정을 비율로 읽고, 그 색으로 오늘의 별을 띄워요.")
    need_nickname()

    entries = {e["date"]: e for e in db.load_entries(NICK)}
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        with st.container(border=True):
            day = st.date_input("날짜", value=dt.date.today(), max_value=dt.date.today())
            key = day.isoformat()
            old = entries.get(key)
            if st.session_state.get("draft_date") != key:
                st.session_state["draft_date"] = key
                st.session_state["draft_text"] = old["text"] if old else ""
                st.session_state["draft_probs"] = old["probs"] if old else None
            text = st.text_area("오늘의 일기", key="draft_text", height=190, max_chars=500,
                                placeholder="오늘 있었던 일을 두세 줄로 적어 보세요.\n예) 발표는 끝나서 뿌듯한데 결과가 걱정된다")
            if st.button("감정 분석하기", type="primary"):
                if not text.strip():
                    st.warning("일기를 먼저 적어 주세요.")
                else:
                    with st.spinner("감정을 읽는 중... (처음 한 번은 1~2분)"):
                        st.session_state["draft_probs"] = predict(text.strip())

        recent = sorted(entries.values(), key=lambda e: e["date"], reverse=True)[:4]
        if recent:
            st.markdown('<div class="label" style="margin-top:22px">최근에 뜬 별</div>' + "".join(
                f'<div class="recent"><i style="background:{COL[top_emotion(e)]};box-shadow:0 0 10px {COL[top_emotion(e)]}"></i>'
                f'<span class="d">{e["date"][5:].replace("-", "/")}</span><span class="t">{html.escape(e["text"])}</span>'
                f'<span class="e">{top_emotion(e)}</span></div>' for e in recent), unsafe_allow_html=True)

    with right:
        probs = st.session_state.get("draft_probs")
        if not probs:
            st.markdown('<div class="empty-sky"><div><b>✦</b>일기를 쓰고 <u>감정 분석하기</u>를 누르면<br>여기에 오늘의 별이 떠요.</div></div>',
                        unsafe_allow_html=True)
            return
        ai_top = EMO[max(range(len(EMO)), key=lambda i: probs[i])]
        components.html(sky.star_html(probs, f"{day.month}월 {day.day}일 · {ai_top} {round(max(probs)*100)}%"), height=300)
        with st.container(border=True):
            st.markdown('<div class="label">AI 감정 분석</div>', unsafe_allow_html=True)
            emotion_bars(probs)
            st.markdown(f'<p class="note">AI 확신도 {round(max(probs)*100)}% · 가장 큰 감정은 {ai_top}이에요.</p>',
                        unsafe_allow_html=True)
            options = ["AI 결과 그대로"] + EMO
            default = options.index(old["corrected"]) if old and old.get("corrected") in EMO else 0
            pick = st.radio("내 느낌과 다르다면 골라 주세요", options, index=default, horizontal=True)
            corrected = None if pick in ("AI 결과 그대로", ai_top) else pick
            c1, c2 = st.columns(2)
            if c1.button("별 띄우기 ✦", type="primary"):
                db.save_entry(NICK, key, text.strip(), probs, corrected)
                st.toast(f"{day.month}월 {day.day}일의 별이 떴어요", icon="✦")
                st.rerun()
            if old and c2.button("이 날 기록 지우기"):
                db.delete_entry(NICK, key)
                st.session_state["draft_date"] = None
                st.rerun()


# ---------- 화면 2: 별자리 지도 ----------
def page_map():
    hero("CONSTELLATION MAP", "별자리 지도", "큰 별은 감정, 작은 별은 하루예요. 별을 눌러 그날의 기록으로 들어가 보세요.")
    need_nickname()
    entries = db.load_entries(NICK)
    if not entries:
        st.markdown('<div class="empty-sky"><div><b>✦</b>아직 뜬 별이 없어요.<br>오늘의 별에서 첫 일기를 쓰거나, 사이드바의 예시 하늘 채우기를 눌러 보세요.</div></div>',
                    unsafe_allow_html=True)
        return
    months = sorted({e["date"][:7] for e in entries}, reverse=True)
    c1, _ = st.columns([1, 3])
    scope = c1.selectbox("범위", ["전체 기간"] + months, label_visibility="collapsed")
    shown = entries if scope == "전체 기간" else [e for e in entries if e["date"].startswith(scope)]
    components.html(sky.map_html(shown), height=690)


# ---------- 화면 3: 이달의 하늘 ----------
def page_month():
    hero("MY MONTH IN STARS", "이달의 하늘", "한 달의 감정이 하나의 밤하늘 작품이 돼요.")
    need_nickname()
    entries = db.load_entries(NICK)
    months = sorted({e["date"][:7] for e in entries}, reverse=True) or [dt.date.today().strftime("%Y-%m")]
    c1, _ = st.columns([1, 3])
    ym = c1.selectbox("달", months, format_func=lambda s: f"{s[:4]}년 {int(s[5:])}월", label_visibility="collapsed")
    y, m = int(ym[:4]), int(ym[5:7])
    cur = [e for e in entries if e["date"].startswith(ym)]

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        components.html(sky.poster_html(cur, y, m), height=650)
    if not cur:
        return
    with right:
        py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
        prev = [e for e in entries if e["date"].startswith(f"{py}-{pm:02d}")]
        now_mean = A.month_mean(cur)
        top = EMO[int(now_mean.argmax())]
        mixed = sum(1 for e in cur if sum(v >= .2 for v in A.effective(e)) >= 2)
        st.markdown(f'<div class="cards">'
                    f'<div class="card"><b>{len(cur)}일</b><span>별이 뜬 날</span></div>'
                    f'<div class="card" style="--c:{COL[top]}"><b>{top}</b><span>가장 많이 빛난 감정</span></div>'
                    f'<div class="card" style="--c:#9b8cf5"><b>{mixed}일</b><span>감정이 섞인 날</span></div>'
                    f'<div class="card" style="--c:#7fd6a4"><b>{len(A.turning_points(cur, top=99))}번</b><span>분위기가 바뀐 날</span></div>'
                    f'</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="label">이달의 감정 구성</div>', unsafe_allow_html=True)
            prev_mean = A.month_mean(prev) if prev else None
            rows = []
            for i in sorted(range(len(EMO)), key=lambda i: -now_mean[i]):
                v = now_mean[i] * 100
                d = ""
                if prev_mean is not None:
                    diff = v - prev_mean[i] * 100
                    if abs(diff) >= 0.5:
                        d = f'<span class="{"delta-up" if diff > 0 else "delta-down"}"> {"+" if diff > 0 else ""}{diff:.0f}</span>'
                rows.append(f'<div class="emo-row" style="grid-template-columns:46px 1fr 70px"><span><i class="dot" style="background:{COL[EMO[i]]}"></i>{EMO[i]}</span>'
                            f'<span class="emo-track"><b style="width:{v:.1f}%;background:{COL[EMO[i]]}"></b></span>'
                            f'<span class="emo-pct">{v:.0f}%{d}</span></div>')
            st.markdown("".join(rows), unsafe_allow_html=True)
            if prev:
                st.markdown('<p class="note">초록·빨강 숫자는 지난달과 비교한 변화(%p)예요.</p>', unsafe_allow_html=True)

        tps = A.turning_points(cur)
        st.markdown('<div class="label" style="margin-top:18px">분위기가 바뀐 날</div>', unsafe_allow_html=True)
        if tps:
            st.markdown("".join(
                f'<div class="turn"><b>{int(t["date"][5:7])}월 {int(t["date"][8:])}일</b> · '
                f'<span style="color:{COL[t["from"]]}">{t["from"]}</span> → <span style="color:{COL[t["to"]]}">{t["to"]}</span>'
                f'<small>바로 전 기록과 감정 구성이 {round(t["jsd"]*100)}% 달라졌어요</small></div>' for t in tps),
                unsafe_allow_html=True)
        else:
            st.markdown('<p class="note">이번 달은 감정 구성이 크게 바뀐 날 없이 이어졌어요.</p>', unsafe_allow_html=True)


# ---------- 화면 전환 ----------
nav = st.navigation([
    st.Page(page_write, title="오늘의 별", icon="✍️", url_path="write", default=True),
    st.Page(page_map, title="별자리 지도", icon="🌌", url_path="map"),
    st.Page(page_month, title="이달의 하늘", icon="🖼️", url_path="month"),
])
nav.run()
