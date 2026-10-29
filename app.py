"""감정의 궤적 (EMOTION TRACE) - Streamlit 메인

실행: streamlit run app.py
화면: 홈(오늘의 별) / 감정 태양계 / 감정 유니버스 / 우주의 기록(월간 리포트)
"""
import calendar
import datetime as dt
import html

import streamlit as st
import streamlit.components.v1 as components

import analysis as A
import db
import quotes
import sky
from model import EMO, predict
from samples import SAMPLES

st.set_page_config(page_title="감정의 궤적", page_icon="✦", layout="wide")
COL = dict(zip(EMO, sky.COLORS))
WEEK = "월화수목금토일"

# 주의: 아래 스타일 안에는 빈 줄을 넣지 마세요. 빈 줄이 있으면 화면에 코드가 글자로 보여요.
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@300;400;500;700&family=Nanum+Myeongjo:wght@700;800&display=swap" rel="stylesheet">
<style>
:root { --night:#070a1d; --card:rgba(16,20,46,.82); --line:rgba(140,150,255,.15); --line-hi:rgba(165,155,255,.42); --ink:#eef0ff; --sub:#a3a8cf; --faint:#6b7099; --violet:#8b7bff; --gold:#ffcf6a; }
html, body, .stApp, .stMarkdown, button, input, textarea, [data-testid="stSidebar"] { font-family:"Gothic A1","Apple SD Gothic Neo","Malgun Gothic",sans-serif !important; }
.stApp { background: radial-gradient(1100px 520px at 75% -12%, #18205a 0%, transparent 60%), radial-gradient(900px 480px at 5% 108%, #170f44 0%, transparent 60%), var(--night); }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], footer, #MainMenu { display:none !important; }
.block-container { max-width: 1380px; padding-top: 1.3rem; padding-bottom: 3rem; }
/* ----- 사이드바 ----- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b0e2a 0%, #070919 100%); border-right: 1px solid var(--line); min-width: 250px !important; max-width: 260px !important; }
.brand { display:flex; gap:12px; align-items:center; padding:2px 2px 22px; }
.brand svg { width:34px; height:34px; flex:none; }
.brand b { display:block; font-size:18px; font-weight:700; color:#ecebff; }
.brand span { font-size:9.5px; color:var(--faint); letter-spacing:.26em; }
[class*="st-key-nav_"] a { border-radius:10px !important; padding:10px 14px !important; margin:1px 0; border:1px solid transparent; }
[class*="st-key-nav_"] a:hover { background: rgba(139,123,255,.08) !important; }
[class*="st-key-nav_"] a p { font-size:14px !important; color:#d9dbf2 !important; }
[class*="st-key-nav_"] a span[data-testid="stIconMaterial"] { font-size:20px !important; color:#b9b0ff !important; margin-right:8px; }
.side-gap { height: 34vh; }
.st-key-side_bottom .stButton > button, .st-key-side_bottom [data-testid="stPopover"] button { border:0 !important; background:transparent !important; justify-content:flex-start; padding:.45rem .9rem; color:#c3c7e6; font-weight:400; }
.st-key-side_bottom .stButton > button:hover, .st-key-side_bottom [data-testid="stPopover"] button:hover { background: rgba(255,255,255,.04) !important; }
/* ----- 페이지 머리 ----- */
.head h1 { font-size:26px !important; font-weight:700 !important; margin:0 !important; padding:0 !important; color:#f2f0ff; display:flex; align-items:baseline; gap:12px; }
.head h1 small { margin-left:12px; font-size:14px; font-weight:400; color:var(--sub); }
.head p { margin:6px 0 0; font-size:13px; color:var(--sub); line-height:1.6; }
.user-chip { display:flex; align-items:center; justify-content:flex-end; gap:9px; font-size:13px; color:#d6d9f2; }
.user-chip i { width:30px; height:30px; border-radius:50%; display:grid; place-items:center; font-style:normal; background:linear-gradient(135deg,#8b7bff,#5b84f0); color:#fff; font-size:12px; font-weight:700; }
.st-key-mnav [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:.5rem; align-items:center; }
.st-key-mnav [data-testid="stColumn"] { min-width:0 !important; }
.st-key-mpill { border:1px solid var(--line); border-radius:10px; background:var(--card); padding:0 4px; }
.st-key-mpill [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:0; align-items:center; }
.st-key-mpill button, .st-key-mpill button:disabled, .st-key-mpill button:hover { height:36px; border:0 !important; background:transparent !important; box-shadow:none !important; padding:0; font-size:16px; color:#c9cdf0; }
.st-key-mpill button:disabled { color:#3d4270 !important; }
.st-key-mpill [data-testid="stMarkdownContainer"], .st-key-mpill .stMarkdown { margin:0 !important; }
.st-key-all_rec, .st-key-all_rec [data-testid="stButton"], .st-key-all_rec button { width:100% !important; }
.month-pill { display:flex; align-items:center; justify-content:center; height:36px; font-size:13px; font-weight:500; font-variant-numeric:tabular-nums; white-space:nowrap; }
.month-pill span { color:var(--faint); margin-left:8px; font-size:11px; }
.cal { display:grid; place-items:center; height:38px; border:1px solid var(--line); border-radius:10px; background:var(--card); font-size:15px; }
.st-key-more [data-testid="stPopover"] button { border:0 !important; background:transparent !important; color:var(--sub); width:auto; padding:.3rem .6rem; }
.st-key-save .stButton > button { width:auto; padding:.4rem 1.6rem; float:right; }
.trail { position:relative; display:grid; grid-template-columns:repeat(7,minmax(0,1fr)); text-align:center; padding-top:2px; }
.trail::before { content:""; position:absolute; left:7%; right:7%; top:15px; height:1px; background:linear-gradient(90deg, transparent, rgba(165,155,255,.35), transparent); }
.trail div { position:relative; display:grid; justify-items:center; gap:5px; font-size:11px; color:var(--sub); font-variant-numeric:tabular-nums; }
.trail i { width:22px; height:22px; border-radius:50%; background:radial-gradient(circle at 34% 30%, #ffffff 0%, var(--c) 32%, var(--c2) 78%, #0a0c24 100%); box-shadow:0 0 14px var(--c); }
.trail i.off { background:#0b0e26; box-shadow:none; border:1px dashed rgba(165,155,255,.3); }
.trail b { font-weight:500; color:var(--c); font-size:11.5px; margin-top:-2px; }
/* ----- 입력칸, 버튼, 카드 ----- */
.stTextArea textarea { background:rgba(8,10,28,.55) !important; border:1px solid var(--line) !important; border-radius:12px !important; font-size:14.5px !important; line-height:1.75 !important; color:var(--ink) !important; }
.stTextArea textarea:focus { border-color:var(--violet) !important; box-shadow:0 0 0 1px var(--violet) !important; }
.stDateInput input, .stTextInput input, [data-baseweb="select"] > div { background:rgba(8,10,28,.55) !important; border-radius:10px !important; }
.stButton > button, [data-testid="stPopover"] button { border-radius:999px; padding:.45rem 1.1rem; font-weight:500; border:1px solid var(--line-hi); background:transparent; width:100%; }
.stButton > button[kind="primary"], .stFormSubmitButton > button { background:linear-gradient(135deg,#9a8cff,#6f5ef0) !important; color:#fff !important; border:0 !important; font-weight:700; box-shadow:0 6px 22px rgba(120,100,255,.26); border-radius:999px; width:100%; }
.stButton > button[kind="primary"]:hover { filter:brightness(1.08); color:#fff; }
[data-testid="stVerticalBlockBorderWrapper"] { background:var(--card); border:1px solid var(--line) !important; border-radius:16px; }
.ctitle { font-size:14px; font-weight:700; color:#eceaff; margin:0 0 10px; }
.note { color:var(--sub); font-size:12.5px; }
/* 최근 7일 */
.week { display:grid; grid-template-columns:repeat(7,minmax(0,1fr)); gap:6px; text-align:center; }
.week div { display:grid; justify-items:center; gap:6px; font-size:11.5px; color:var(--sub); font-variant-numeric:tabular-nums; }
.week i { width:26px; height:26px; border-radius:50%; background:radial-gradient(circle at 34% 30%, #ffffff 0%, var(--c) 32%, var(--c2) 78%, #0a0c24 100%); box-shadow:0 0 14px var(--c); }
.week i.off { background:rgba(255,255,255,.05); box-shadow:none; border:1px dashed rgba(165,155,255,.25); }
.week b { font-weight:500; color:var(--c); font-size:12px; }
/* 로그인 */
.welcome { text-align:center; padding:26px 10px 8px; }
.welcome svg { width:54px; height:54px; }
.welcome h2 { font-size:28px !important; margin:10px 0 4px !important; }
.welcome p { color:var(--sub); font-size:13.5px; margin:0 0 6px; }
/* 기록 보관함 */
.rec2 { display:grid; grid-template-columns:62px minmax(0,1fr); gap:10px; padding:7px 0; font-size:12.5px; border-bottom:1px solid rgba(140,150,255,.08); }
.rec2 b { font-weight:500; white-space:nowrap; font-variant-numeric:tabular-nums; }
.rec2 span { color:#cfd2ec; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.arc { display:grid; grid-template-columns:96px minmax(0,1fr); gap:16px; padding:14px 4px; border-top:1px solid var(--line); }
.arc .d b { display:block; font-size:15px; font-variant-numeric:tabular-nums; }
.arc .d small { color:var(--faint); font-size:11.5px; }
.arc .pill { display:inline-block; font-size:11.5px; padding:2px 9px; border-radius:99px; margin-right:6px; }
.arc .mix { display:flex; gap:2px; height:5px; margin:8px 0; max-width:260px; }
.arc .mix i { display:block; border-radius:3px; }
.arc p { margin:0; font-size:13.5px; line-height:1.7; color:#d6d9f0; }
</style>""", unsafe_allow_html=True)

LOGO = ('<svg viewBox="0 0 40 40" fill="none"><path d="M20 3l2.6 13.4L36 20l-13.4 2.6L20 37l-2.6-14.4L4 20l13.4-3.6z" fill="url(#lg)" opacity=".95"/>'
        '<path d="M20 9l1.3 9.7L31 20l-9.7 1.3L20 31l-1.3-9.7L9 20l9.7-1.3z" fill="#fff" opacity=".55"/>'
        '<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cfc6ff"/><stop offset="1" stop-color="#7f8cff"/></linearGradient></defs></svg>')


# ---------- 공통 도우미 ----------
def top_emotion(e: dict) -> str:
    return e["corrected"] if e.get("corrected") in EMO else EMO[max(range(len(EMO)), key=lambda i: e["probs"][i])]


def month_options(entries):
    cur = dt.date.today().strftime("%Y-%m")
    return sorted({e["date"][:7] for e in entries} | {cur}, reverse=True)


def header(title: str, desc: str, months=None, pill=None, small: str = ""):
    """왼쪽: 제목 + 설명 / 오른쪽: 달 이동(‹ 2026년 10월 ›) 또는 사용자 이름"""
    left, right = st.columns([2.4, 1.15], vertical_alignment="center")
    left.markdown(f'<div class="head"><h1>{title}{f"<small>{small}</small>" if small else ""}</h1><p>{desc}</p></div>', unsafe_allow_html=True)
    nick = st.session_state.get("nickname", "")
    ym = None
    if months:
        ym = st.session_state.get("ym")
        if ym not in months:
            ym = months[0]
        i = months.index(ym)
        with right.container(key="mnav"):
            box, cal = st.columns([5, 1], gap="small", vertical_alignment="center")
            with box.container(key="mpill"):
                a, b, c = st.columns([1, 5, 1], gap="small", vertical_alignment="center")
                if a.button("‹", key="m_prev", disabled=i == len(months) - 1, help="이전 달"):
                    st.session_state["ym"] = months[i + 1]; st.rerun()
                b.markdown(f'<div class="month-pill">{(pill or (lambda s: f"{s[:4]}년 {int(s[5:])}월"))(ym)}<span>▾</span></div>', unsafe_allow_html=True)
                if c.button("›", key="m_next", disabled=i == 0, help="다음 달"):
                    st.session_state["ym"] = months[i - 1]; st.rerun()
            cal.markdown('<div class="cal">📅</div>', unsafe_allow_html=True)
        st.session_state["ym"] = ym
    elif nick:
        right.markdown(f'<div class="user-chip">{html.escape(nick)}님 <i>{html.escape(nick[:1])}</i></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    return ym


def login_card():
    """닉네임이 없으면 시작 화면"""
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.container(border=True):
            st.markdown(f'<div class="welcome">{LOGO}<h2>감정의 궤적</h2><p>나의 감정이 모여, 나만의 궤도가 되다.</p></div>', unsafe_allow_html=True)
            with st.form("login", border=False):
                name = st.text_input("내 하늘 이름", max_chars=20, placeholder="닉네임을 적어 주세요")
                if st.form_submit_button("시작하기") and name.strip():
                    st.session_state["nickname"] = name.strip()
                    st.rerun()
            st.markdown('<p class="note" style="text-align:center">이름으로 내 기록을 구분해요. 다음에도 같은 이름으로 들어오면 돼요.</p>', unsafe_allow_html=True)
    st.stop()


def nick_or_login() -> str:
    nick = st.session_state.get("nickname", "")
    if not nick:
        login_card()
    return nick


# ---------- 화면 1: 홈 (오늘의 별) ----------
def page_home():
    nick = nick_or_login()
    entries = {e["date"]: e for e in db.load_entries(nick)}
    today = dt.date.today()

    # 어느 날의 일기인지 (기본: 오늘, '⋯'에서 다른 날로 바꿀 수 있어요)
    day = st.session_state.get("day", today)
    key = day.isoformat()
    old = entries.get(key)
    if st.session_state.get("draft_date") != key:
        st.session_state["draft_date"] = key
        st.session_state["draft_text"] = old["text"] if old else ""
        st.session_state["draft_fix"] = old.get("corrected") if old else None
    probs = old["probs"] if old else None

    q, by = quotes.pick(EMO, probs, day)
    sub = "당신의 감정이 모여 오늘도 특별한 궤적을 만들었어요." if old else "오늘의 감정을 기록하고, 나만의 궤도를 이어가 보세요."
    components.html(sky.hero_html(f"{day.year}년 {day.month}월 {day.day}일 {WEEK[day.weekday()]}요일", q, by, sub, probs, user=nick), height=320)

    c1, c2 = st.columns([1, 1.25], gap="medium")
    with c1:
        with st.container(border=True, height=245):
            st.markdown('<div class="ctitle">오늘의 감정 비율</div>', unsafe_allow_html=True)
            components.html(sky.donut_html(probs), height=172)
    with c2:
        with st.container(border=True, height=245):
            st.markdown('<div class="ctitle">오늘의 일기</div>', unsafe_allow_html=True)
            text = st.text_area("일기", key="draft_text", height=110, max_chars=500, label_visibility="collapsed",
                                placeholder="오늘 있었던 일과 그때의 마음을 편하게 적어 보세요.")
            l, r = st.columns([1, 1], vertical_alignment="center")
            with l.container(key="more"):
                with st.popover("⋯", help="다른 날짜, 감정 수정, 지우기"):
                    new_day = st.date_input("날짜", value=day, max_value=today)
                    if new_day != day:
                        st.session_state["day"] = new_day; st.rerun()
                    fix = st.session_state.get("draft_fix")
                    pick = st.radio("내 느낌과 가장 가까운 감정", ["AI 결과 그대로"] + EMO, index=(EMO.index(fix) + 1) if fix in EMO else 0)
                    new_fix = None if pick == "AI 결과 그대로" else pick
                    if new_fix != fix:
                        st.session_state["draft_fix"] = new_fix
                        if old:
                            db.save_entry(nick, key, old["text"], old["probs"], new_fix)
                        st.rerun()
                    if old and st.button("이 날 기록 지우기"):
                        db.delete_entry(nick, key)
                        st.session_state["draft_date"] = None
                        st.rerun()
            with r.container(key="save"):
                if st.button("저장하기", type="primary"):
                    if not text.strip():
                        st.warning("일기를 먼저 적어 주세요.")
                    else:
                        with st.spinner("AI가 감정을 읽는 중..."):
                            p = old["probs"] if old and old["text"] == text.strip() else predict(text.strip())
                        db.save_entry(nick, key, text.strip(), p, st.session_state.get("draft_fix"))
                        st.toast(f"{day.month}월 {day.day}일의 행성이 생겼어요", icon="✨")
                        st.rerun()

    # 최근 감정 기록 (최근 7일)
    cells = []
    for i in range(6, -1, -1):
        d = today - dt.timedelta(days=i)
        e = entries.get(d.isoformat())
        if e:
            t = top_emotion(e)
            order = sorted(range(len(EMO)), key=lambda k: -e["probs"][k])
            c2_ = COL[EMO[order[1]]] if EMO[order[0]] == t else COL[EMO[order[0]]]
            cells.append(f'<div style="--c:{COL[t]};--c2:{c2_}"><i></i>{d.month}.{d.day:02d}<b>{t}</b></div>')
        else:
            cells.append(f'<div style="--c:#6b7099"><i class="off"></i>{d.month}.{d.day:02d}<b>-</b></div>')
    with st.container(border=True):
        st.markdown('<div class="ctitle">오늘의 감정 기록</div><div class="trail">' + "".join(cells) + "</div>", unsafe_allow_html=True)


# ---------- 화면 2: 감정 태양계 ----------
def page_solar():
    nick = nick_or_login()
    entries = db.load_entries(nick)
    ym = header("감정 태양계", "일곱 개의 감정 행성이 만들어 가는 나만의 우주를 탐험해 보세요", month_options(entries))
    cur = [e for e in entries if e["date"].startswith(ym)]
    components.html(sky.solar_html(cur, f"{ym[:4]}년 {int(ym[5:])}월", height=600), height=610)


# ---------- 화면 3: 감정 유니버스 ----------
def range_label(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:])
    return f"{y}년 {m}월 1일 - {m}월 {calendar.monthrange(y, m)[1]}일"


def page_universe():
    nick = nick_or_login()
    entries = db.load_entries(nick)
    ym = header("감정 유니버스", "당신의 감정이 만들어 낸 데이터의 별들을 탐험해 보세요. 비슷한 감정을 가진 날들이 서로 연결되어 있어요.",
                month_options(entries), pill=range_label)
    cur = [e for e in entries if e["date"].startswith(ym)]
    components.html(sky.universe_html(cur, height=640), height=650)


# ---------- 화면 4: 우주의 기록 (월간 리포트) ----------
def page_archive():
    nick = nick_or_login()
    entries = db.load_entries(nick)
    ym = st.session_state.get("ym") or dt.date.today().strftime("%Y-%m")
    ym = header("월간 리포트", "지난 한 달, 당신의 감정이 그린 궤적을 돌아보세요", month_options(entries),
                small=f"{ym[:4]}년 {int(ym[5:])}월")
    y, m = int(ym[:4]), int(ym[5:])
    cur = [e for e in entries if e["date"].startswith(ym)]
    components.html(sky.report_html(cur, y, m, part="top"), height=290)
    if not cur:
        return
    l, r = st.columns([2, 1], gap="medium")
    with l:
        components.html(sky.report_html(cur, y, m, part="bottom"), height=315)
    with r:
        with st.container(border=True, height=313):
            st.markdown('<div class="ctitle">최근 일기</div>' + "".join(
                f'<div class="rec2"><b>{int(e["date"][5:7])}월 {int(e["date"][8:])}일</b><span>{html.escape(e["text"])}</span></div>'
                for e in sorted(cur, key=lambda e: e["date"], reverse=True)[:5]), unsafe_allow_html=True)
            if st.button("전체 기록 보기", key="all_rec"):
                st.session_state["show_all"] = not st.session_state.get("show_all", False)
    if not st.session_state.get("show_all"):
        return
    with st.container(border=True):
        st.markdown('<div class="ctitle">전체 기록</div>', unsafe_allow_html=True)
        a, b = st.columns([2, 1])
        q = a.text_input("검색", placeholder="일기 내용으로 찾기 (예: 발표)", label_visibility="collapsed")
        f = b.selectbox("감정", ["모든 감정"] + EMO, label_visibility="collapsed")
        rows = sorted(entries, key=lambda e: e["date"], reverse=True)
        if q.strip():
            rows = [e for e in rows if q.strip() in e["text"]]
        if f != "모든 감정":
            rows = [e for e in rows if top_emotion(e) == f]
        st.markdown(f'<p class="note">{len(rows)}개의 기록</p>', unsafe_allow_html=True)
        out = []
        for e in rows[:60]:
            d = dt.date.fromisoformat(e["date"])
            t = top_emotion(e)
            order = sorted(range(len(EMO)), key=lambda i: -e["probs"][i])
            mix = "".join(f'<i style="flex:{e["probs"][i]:.3f};background:{COL[EMO[i]]}"></i>' for i in order if e["probs"][i] >= .01)
            out.append(f'<div class="arc"><div class="d"><b>{d.month}월 {d.day}일</b><small>{d.year} · {WEEK[d.weekday()]}요일</small></div>'
                       f'<div><span class="pill" style="background:{COL[t]}26;color:{COL[t]}">{t}</span>'
                       f'<span class="note">{" · ".join(f"{EMO[i]} {round(e["probs"][i]*100)}%" for i in order[:3])}</span>'
                       f'<div class="mix">{mix}</div><p>{html.escape(e["text"])}</p></div></div>')
        st.markdown("".join(out) or '<p class="note">찾는 기록이 없어요.</p>', unsafe_allow_html=True)


# ---------- 화면 목록 (기본 메뉴는 숨기고 사이드바에 직접 그려요) ----------
PAGES = {
    "home": st.Page(page_home, title="홈", icon=":material/home:", url_path="home", default=True),
    "solar": st.Page(page_solar, title="감정 태양계", icon=":material/trip_origin:", url_path="solar"),
    "universe": st.Page(page_universe, title="감정 유니버스", icon=":material/hub:", url_path="universe"),
    "archive": st.Page(page_archive, title="우주의 기록", icon=":material/article:", url_path="archive"),
}
nav = st.navigation(list(PAGES.values()), position="hidden")
current = next(k for k, p in PAGES.items() if p.title == nav.title)

with st.sidebar:
    st.markdown(f'<div class="brand">{LOGO}<div><b>감정의 궤적</b><span>EMOTION TRACE</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<style>.st-key-nav_{current} a {{ background:linear-gradient(135deg,rgba(139,123,255,.3),rgba(90,80,210,.14)) !important;'
                f' border-color:rgba(165,155,255,.4) !important; }} .st-key-nav_{current} a p {{ color:#fff !important; font-weight:700; }}</style>',
                unsafe_allow_html=True)
    for k, p in PAGES.items():
        with st.container(key=f"nav_{k}"):
            st.page_link(p)
    st.markdown('<div class="side-gap"></div>', unsafe_allow_html=True)
    nick = st.session_state.get("nickname", "")
    with st.container(key="side_bottom"):
        with st.popover("⚙  설정", width="stretch"):
            if nick:
                st.markdown(f"**{html.escape(nick)}**님의 하늘")
                mine = db.load_entries(nick)
                st.caption(f"지금까지 {len(mine)}개의 기록")
            if db.is_demo():
                st.caption("체험 모드예요. 기록은 이 창에만 잠깐 저장돼요.")
                if nick and st.button("예시 기록 채우기", help="두 달 치 예시 일기 31개를 실제 모델로 분석해서 채워요"):
                    bar = st.progress(0.0, text="예시 일기를 분석하는 중...")
                    today = dt.date.today()
                    for i, (ago, text) in enumerate(SAMPLES):
                        db.save_entry(nick, (today - dt.timedelta(days=ago)).isoformat(), text, predict(text), None)
                        bar.progress((i + 1) / len(SAMPLES), text=f"예시 일기를 분석하는 중... {i+1}/{len(SAMPLES)}")
                    st.session_state["draft_date"] = None
                    st.rerun()
        if nick and st.button("⏻  로그아웃"):
            for k in ("nickname", "draft_date", "draft_text", "draft_fix", "day", "ym"):
                st.session_state.pop(k, None)
            st.rerun()

nav.run()
