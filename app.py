"""감정 별자리 (Night Sky Diary) - Streamlit 메인

실행: streamlit run app.py
화면: 오늘의 별(일기 쓰기) / 별자리 지도(탐험) / 이달의 하늘(월간 포스터)
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

# 주의: 아래 스타일 안에는 빈 줄을 넣지 마세요. 빈 줄이 있으면 화면에 코드가 글자로 보여요.
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@300;400;500;700&family=Nanum+Myeongjo:wght@700;800&family=Dancing+Script:wght@500&display=swap" rel="stylesheet">
<style>
:root { --night:#070918; --panel:rgba(17,20,48,.78); --line:rgba(150,160,255,.16); --line-hi:rgba(170,160,255,.42); --ink:#eef0ff; --sub:#a3a8cf; --faint:#6b7099; --gold:#ffcf6a; --violet:#9b8cff; }
html, body, .stApp, .stMarkdown, button, input, textarea, [data-testid="stSidebar"] { font-family:"Gothic A1","Apple SD Gothic Neo","Malgun Gothic",sans-serif !important; }
.stApp { background: radial-gradient(1100px 520px at 75% -12%, #1b1f5e 0%, transparent 60%), radial-gradient(900px 500px at 10% 110%, #1a1048 0%, transparent 60%), var(--night); }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], footer, #MainMenu { display:none !important; }
.block-container { max-width: 1360px; padding-top: 1.6rem; padding-bottom: 3rem; }
/* ----- 사이드바 ----- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0c0f2c 0%, #080a1e 100%); border-right: 1px solid var(--line); min-width: 280px !important; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top: .5rem; }
.brand { display:flex; gap:12px; align-items:center; padding:4px 2px 18px; border-bottom:1px solid var(--line); margin-bottom:14px; }
.brand svg { width:38px; height:38px; flex:none; }
.brand b { display:block; font-size:20px; font-weight:700; letter-spacing:-.01em; color:#e9e6ff; }
.brand span { font-size:11.5px; color:var(--sub); }
[class*="st-key-nav_"] a { border-radius:12px !important; padding:12px 14px !important; border:1px solid transparent; margin:2px 0; }
[class*="st-key-nav_"] a:hover { background: rgba(155,140,255,.08) !important; }
[class*="st-key-nav_"] a p { font-size:15px !important; font-weight:500; color:#e8e9f8 !important; line-height:1.35; }
[class*="st-key-nav_"] a p::after { display:block; font-size:11.5px; font-weight:400; color:var(--sub); margin-top:2px; }
.st-key-nav_write a p::after { content:"일기 쓰기 & 감정 분석"; }
.st-key-nav_map a p::after { content:"나의 감정 별자리 탐험"; }
.st-key-nav_month a p::after { content:"월간 감정 포스터"; }
[class*="st-key-nav_"] a span[data-testid="stIconMaterial"] { font-size:24px !important; color:#c7bdff !important; margin-right:6px; }
.side-label { color:var(--sub); font-size:12.5px; font-weight:500; margin:18px 2px 10px; padding-top:16px; border-top:1px solid var(--line); }
.rec { display:grid; grid-template-columns:10px 1fr auto; gap:12px; align-items:center; font-size:12.5px; padding:6px 2px; color:#d8daf0; }
.rec i { width:9px; height:9px; border-radius:50%; }
.rec span:last-child { color:var(--sub); }
.quote { font-family:"Dancing Script", cursive; font-size:19px; line-height:1.45; color:#a99cf0; transform:rotate(-6deg); margin:46px 0 10px 8px; opacity:.9; }
.quote small { display:block; font-size:16px; margin:6px 0 0 70px; color:#8f84e0; }
[data-testid="stSidebar"] .stTextInput input { background: rgba(255,255,255,.04) !important; border-radius:10px !important; }
/* ----- 페이지 머리 ----- */
.head { display:flex; gap:14px; align-items:center; }
.head svg { width:42px; height:42px; flex:none; }
.head h1 { font-size:28px !important; font-weight:700 !important; margin:0 !important; padding:0 !important; color:#f0eeff; letter-spacing:-.01em; }
.head p { margin:2px 0 0; font-size:13.5px; color:var(--sub); }
.month-pill { display:flex; align-items:center; justify-content:center; gap:8px; height:42px; border:1px solid var(--line); border-radius:12px; background:var(--panel); font-size:14px; font-weight:500; font-variant-numeric:tabular-nums; }
.st-key-mnav .stButton > button { height:42px; border-radius:12px; padding:0; background:var(--panel); border:1px solid var(--line); font-size:18px; }
/* ----- 입력칸, 버튼 ----- */
.stTextArea textarea { background:rgba(10,12,32,.75) !important; border:1px solid var(--line) !important; border-radius:14px !important; font-size:15.5px !important; line-height:1.7 !important; color:var(--ink) !important; }
.stTextArea textarea:focus { border-color:var(--violet) !important; box-shadow:0 0 0 1px var(--violet) !important; }
.stDateInput input, [data-baseweb="select"] > div { background:rgba(10,12,32,.75) !important; border-radius:10px !important; }
.stButton > button { border-radius:999px; padding:.55rem 1.3rem; font-weight:500; border:1px solid var(--line); background:transparent; width:100%; }
.stButton > button[kind="primary"] { background:linear-gradient(135deg,#ffd98a,#f2b84b); color:#21180a; border:0; font-weight:700; box-shadow:0 6px 20px rgba(255,200,100,.18); }
.stButton > button[kind="primary"]:hover { filter:brightness(1.06); color:#21180a; }
[data-testid="stVerticalBlockBorderWrapper"] { background:var(--panel); border:1px solid var(--line) !important; border-radius:16px; }
.stRadio [role="radiogroup"] { gap:.35rem .9rem; }
/* ----- 감정 막대, 카드 ----- */
.emo-row { display:grid; grid-template-columns:52px 1fr 44px; gap:10px; align-items:center; font-size:14px; margin:7px 0; }
.emo-row i.dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; }
.emo-track { height:8px; background:rgba(238,240,255,.08); border-radius:8px; overflow:hidden; }
.emo-track b { display:block; height:100%; border-radius:8px; }
.emo-pct { text-align:right; color:var(--sub); font-variant-numeric:tabular-nums; }
.note { color:var(--sub); font-size:13px; margin:6px 0 0; }
.label { color:#d8dbf2; font-size:13px; font-weight:500; margin:2px 0 10px; }
.empty-sky { min-height:300px; border-radius:16px; border:1px dashed rgba(170,160,255,.25); display:grid; place-items:center; text-align:center; color:var(--sub); font-size:14px; line-height:1.7; padding:24px;
  background: radial-gradient(circle at 50% 45%, rgba(155,140,255,.12), transparent 55%), rgba(10,12,32,.6); }
.empty-sky b { display:block; font-size:30px; color:var(--gold); font-weight:300; margin-bottom:6px; }
.recent { display:grid; grid-template-columns:10px 54px minmax(0,1fr) auto; gap:12px; align-items:center; padding:11px 0; border-top:1px solid var(--line); font-size:14px; }
.recent i { width:10px; height:10px; border-radius:50%; }
.recent .d { color:var(--sub); font-variant-numeric:tabular-nums; }
.recent .t { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.recent .e { color:var(--sub); font-size:12.5px; }
.cards { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin-bottom:14px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:14px 16px; }
.card b { display:block; font-size:24px; font-weight:700; color:var(--c,#eef0ff); line-height:1.2; font-variant-numeric:tabular-nums; }
.card span { color:var(--sub); font-size:12px; }
.delta-up { color:#7fe0a6; } .delta-down { color:#ff8f86; }
.turn { padding:10px 0; border-top:1px solid var(--line); font-size:14px; }
.turn small { color:var(--sub); display:block; margin-top:2px; }
</style>""", unsafe_allow_html=True)

ICON = {
    "logo": '<svg viewBox="0 0 40 40" fill="none" stroke="#b9adff" stroke-width="1.6" stroke-linejoin="round"><path d="M20 4l4.2 10.2L35 16l-8.4 7.2L29 34l-9-5.6L11 34l2.4-10.8L5 16l10.8-1.8z"/><circle cx="31" cy="7" r="1.2" fill="#b9adff"/><circle cx="7" cy="30" r="1" fill="#b9adff"/></svg>',
    "write": '<svg viewBox="0 0 40 40" fill="none" stroke="#c7bdff" stroke-width="1.6"><path d="M20 4l13 7.5v15L20 34 7 26.5v-15z"/><path d="M20 13l2 4.5 4.8.5-3.6 3.2 1 4.8L20 23.6 15.8 26l1-4.8-3.6-3.2 4.8-.5z"/></svg>',
    "map": '<svg viewBox="0 0 40 40" fill="none" stroke="#c7bdff" stroke-width="1.6" stroke-linecap="round"><path d="M20 6l2.4 7.6L30 16l-7.6 2.4L20 26l-2.4-7.6L10 16l7.6-2.4z"/><path d="M31 25l1 3 3 1-3 1-1 3-1-3-3-1 3-1zM9 27l.8 2.2L12 30l-2.2.8L9 33l-.8-2.2L6 30l2.2-.8z"/></svg>',
    "month": '<svg viewBox="0 0 40 40" fill="none" stroke="#c7bdff" stroke-width="1.6"><rect x="7" y="7" width="26" height="26" rx="4"/><path d="M7 26l7-7 6 6 4-4 9 9"/><circle cx="26" cy="15" r="2.4"/></svg>',
}


def emotion_bars(probs):
    rows = sorted(zip(EMO, probs), key=lambda t: -t[1])
    st.markdown("".join(
        f'<div class="emo-row"><span><i class="dot" style="background:{COL[e]}"></i>{e}</span>'
        f'<span class="emo-track"><b style="width:{p*100:.1f}%;background:{COL[e]}"></b></span>'
        f'<span class="emo-pct">{round(p*100)}%</span></div>' for e, p in rows), unsafe_allow_html=True)


def top_emotion(e: dict) -> str:
    return e["corrected"] if e.get("corrected") in EMO else EMO[max(range(len(EMO)), key=lambda i: e["probs"][i])]


def month_options(entries):
    cur = dt.date.today().strftime("%Y-%m")
    return sorted({e["date"][:7] for e in entries} | {cur}, reverse=True)


def header(icon: str, title: str, desc: str, months: list[str] | None = None):
    """왼쪽: 아이콘 + 제목 + 설명 / 오른쪽: 달 이동 (‹ 2026년 10월 ›)"""
    left, right = st.columns([3, 1.15], vertical_alignment="center")
    left.markdown(f'<div class="head">{ICON[icon]}<div><h1>{title}</h1><p>{desc}</p></div></div>', unsafe_allow_html=True)
    if not months:
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        return None
    ym = st.session_state.get("ym")
    if ym not in months:
        ym = months[0]
    i = months.index(ym)
    with right.container(key="mnav"):
        a, b, c = st.columns([1, 3.4, 1], gap="small")
        if a.button("‹", key="m_prev", disabled=i == len(months) - 1, help="이전 달"):
            st.session_state["ym"] = months[i + 1]; st.rerun()
        b.markdown(f'<div class="month-pill">📅 {ym[:4]}년 {int(ym[5:])}월</div>', unsafe_allow_html=True)
        if c.button("›", key="m_next", disabled=i == 0, help="다음 달"):
            st.session_state["ym"] = months[i - 1]; st.rerun()
    st.session_state["ym"] = ym
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    return ym


def need_nickname():
    if not st.session_state.get("nickname"):
        st.markdown('<div class="empty-sky"><div><b>✦</b>왼쪽에 <u>내 하늘 이름</u>을 적으면<br>나만의 밤하늘이 열려요.</div></div>',
                    unsafe_allow_html=True)
        st.stop()


# ---------- 화면 1: 오늘의 별 ----------
def page_write():
    header("write", "오늘의 별", "일기를 쓰면 AI가 섞인 감정을 비율로 읽고, 그 색으로 오늘의 별을 띄워요")
    need_nickname()
    nick = st.session_state["nickname"]
    entries = {e["date"]: e for e in db.load_entries(nick)}
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
            text = st.text_area("오늘의 일기", key="draft_text", height=210, max_chars=500,
                                placeholder="오늘 있었던 일을 두세 줄로 적어 보세요.\n예) 발표는 끝나서 뿌듯한데 결과가 걱정된다")
            if st.button("감정 분석하기", type="primary"):
                if not text.strip():
                    st.warning("일기를 먼저 적어 주세요.")
                else:
                    with st.spinner("감정을 읽는 중... (처음 한 번은 1~2분)"):
                        st.session_state["draft_probs"] = predict(text.strip())

    with right:
        probs = st.session_state.get("draft_probs")
        if not probs:
            st.markdown('<div class="empty-sky" style="min-height:420px"><div><b>✦</b>일기를 쓰고 <u>감정 분석하기</u>를 누르면<br>여기에 오늘의 별이 떠요.</div></div>',
                        unsafe_allow_html=True)
            return
        ai_top = EMO[max(range(len(EMO)), key=lambda i: probs[i])]
        components.html(sky.star_html(probs, f"{day.month}월 {day.day}일 · {ai_top} {round(max(probs)*100)}%"), height=300)
        with st.container(border=True):
            st.markdown('<div class="label">감정 비율</div>', unsafe_allow_html=True)
            emotion_bars(probs)
            st.markdown(f'<p class="note">AI 확신도 {round(max(probs)*100)}% · 가장 큰 감정은 {ai_top}이에요.</p>',
                        unsafe_allow_html=True)
            options = ["AI 결과 그대로"] + EMO
            default = options.index(old["corrected"]) if old and old.get("corrected") in EMO else 0
            pick = st.radio("내 느낌과 다르다면 골라 주세요", options, index=default, horizontal=True)
            corrected = None if pick in ("AI 결과 그대로", ai_top) else pick
            c1, c2 = st.columns(2)
            if c1.button("별 띄우기 ✦", type="primary"):
                db.save_entry(nick, key, text.strip(), probs, corrected)
                st.toast(f"{day.month}월 {day.day}일의 별이 떴어요", icon="✨")
                st.rerun()
            if old and c2.button("이 날 기록 지우기"):
                db.delete_entry(nick, key)
                st.session_state["draft_date"] = None
                st.rerun()


# ---------- 화면 2: 별자리 지도 ----------
def page_map():
    nick = st.session_state.get("nickname", "")
    entries = db.load_entries(nick) if nick else []
    ym = header("map", "별자리 지도", "감정이 비슷했던 날은 가까이, 서로 다른 감정은 또 다른 별빛으로", month_options(entries))
    need_nickname()
    y, m = int(ym[:4]), int(ym[5:])
    cur = [e for e in entries if e["date"].startswith(ym)]
    py_, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    prev = [e for e in entries if e["date"].startswith(f"{py_}-{pm:02d}")]
    a, b = A.positive_share(cur), A.positive_share(prev)
    extra = {"pos_delta": (a - b) if a is not None and b is not None else None}
    components.html(sky.map_html(cur, height=880, extra=extra), height=890)


# ---------- 화면 3: 이달의 하늘 ----------
def page_month():
    nick = st.session_state.get("nickname", "")
    entries = db.load_entries(nick) if nick else []
    ym = header("month", "이달의 하늘", "한 달의 감정이 하나의 밤하늘 작품이 돼요", month_options(entries))
    need_nickname()
    y, m = int(ym[:4]), int(ym[5:])
    cur = [e for e in entries if e["date"].startswith(ym)]

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        components.html(sky.poster_html(cur, y, m), height=650)
    if not cur:
        return
    with right:
        py_, pm = (y, m - 1) if m > 1 else (y - 1, 12)
        prev = [e for e in entries if e["date"].startswith(f"{py_}-{pm:02d}")]
        now_mean = A.month_mean(cur)
        top = EMO[int(now_mean.argmax())]
        mixed = sum(1 for e in cur if sum(v >= .2 for v in A.effective(e)) >= 2)
        st.markdown(f'<div class="cards">'
                    f'<div class="card"><b>{len(cur)}일</b><span>별이 뜬 날</span></div>'
                    f'<div class="card" style="--c:{COL[top]}"><b>{top}</b><span>가장 많이 빛난 감정</span></div>'
                    f'<div class="card" style="--c:#b3a6ff"><b>{mixed}일</b><span>감정이 섞인 날</span></div>'
                    f'<div class="card" style="--c:#7fe0a6"><b>{len(A.turning_points(cur, top=99))}번</b><span>분위기가 바뀐 날</span></div>'
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
                rows.append(f'<div class="emo-row" style="grid-template-columns:52px 1fr 70px"><span><i class="dot" style="background:{COL[EMO[i]]}"></i>{EMO[i]}</span>'
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


# ---------- 화면 목록 (기본 메뉴는 숨기고 사이드바에 직접 그려요) ----------
PAGES = {
    "write": st.Page(page_write, title="오늘의 별", icon=":material/hexagon:", url_path="write", default=True),
    "map": st.Page(page_map, title="별자리 지도", icon=":material/auto_awesome:", url_path="map"),
    "month": st.Page(page_month, title="이달의 하늘", icon=":material/wallpaper:", url_path="month"),
}
nav = st.navigation(list(PAGES.values()), position="hidden")
current = next(k for k, p in PAGES.items() if p.title == nav.title)

# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown(f'<div class="brand">{ICON["logo"]}<div><b>감정 별자리</b><span>나의 감정이 모여, 별이 되는 곳</span></div></div>',
                unsafe_allow_html=True)
    st.markdown(f'<style>.st-key-nav_{current} a {{ background:linear-gradient(135deg,rgba(120,100,255,.28),rgba(80,70,200,.14)) !important;'
                f' border-color:rgba(170,160,255,.45) !important; box-shadow:0 0 22px rgba(130,110,255,.18); }}</style>',
                unsafe_allow_html=True)
    for k, p in PAGES.items():
        with st.container(key=f"nav_{k}"):
            st.page_link(p)

    nickname = st.text_input("내 하늘 이름", value=st.session_state.get("nickname", ""), max_chars=20,
                             placeholder="닉네임을 적어 주세요")
    st.session_state["nickname"] = nickname.strip()
    nick = st.session_state["nickname"]

    if nick:
        mine = db.load_entries(nick)
        recent = sorted(mine, key=lambda e: e["date"], reverse=True)[:5]
        st.markdown('<div class="side-label">최근 기록</div>' + ("".join(
            f'<div class="rec"><i style="background:{COL[top_emotion(e)]};box-shadow:0 0 8px {COL[top_emotion(e)]}"></i>'
            f'<span>{e["date"].replace("-", ".")}</span><span>{top_emotion(e)}</span></div>' for e in recent)
            or '<p class="note">아직 기록이 없어요.</p>'), unsafe_allow_html=True)
        if db.is_demo():
            st.caption("체험 모드예요. 기록은 이 창에만 잠깐 저장돼요.")
            if st.button("예시 하늘 채우기", help="두 달 치 예시 일기 31개를 실제 모델로 분석해서 채워요"):
                bar = st.progress(0.0, text="예시 일기를 분석하는 중...")
                today = dt.date.today()
                for i, (ago, text) in enumerate(SAMPLES):
                    db.save_entry(nick, (today - dt.timedelta(days=ago)).isoformat(), text, predict(text), None)
                    bar.progress((i + 1) / len(SAMPLES), text=f"예시 일기를 분석하는 중... {i+1}/{len(SAMPLES)}")
                st.session_state["draft_date"] = None
                st.rerun()

    st.markdown('<div class="quote">Every emotion<br>&nbsp;&nbsp;is a star,<br>And you are<br>&nbsp;the universe.<small>✧</small></div>',
                unsafe_allow_html=True)

nav.run()
