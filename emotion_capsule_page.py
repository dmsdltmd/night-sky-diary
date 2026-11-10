"""EMOTION TRACE | Time Capsule — focused, single-file redesign.

Drop-in replacement for emotion_capsule_page.py. The existing
emotion_visual_theme.render_capsule_theme() calls render_capsule_page().
This file does NOT change app.py, db.py, the ML model, or the database schema.
"""
from __future__ import annotations

import datetime as dt
import html
import math
from typing import Any

import streamlit as st

import analysis as A
import db

EMOTIONS = A.EMO
COLORS = ("#ffcf4a", "#ff8fb1", "#6fd3a8", "#9aa6b8", "#5b84f0", "#b08cf0", "#f0645a")
MILESTONES = (7, 14, 30)

# One-time styles. All bespoke classes are capsule-prefixed; Streamlit widget
# styling is restricted to the capsule container so other pages are unaffected.
STYLES = r"""<style>
.et-cap-shell{font-family:'Gothic A1','Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#f5f4ff}
.et-cap-intro{position:relative;overflow:hidden;min-height:168px;padding:26px 34px 24px;border-radius:22px;border:1px solid rgba(173,183,243,.22);background:radial-gradient(ellipse at 79% 17%,rgba(130,99,209,.19),transparent 48%),linear-gradient(122deg,#151a34,#11172f 54%,#121330);box-shadow:0 16px 45px rgba(2,5,24,.18);margin-bottom:18px}
.et-cap-intro::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.32;background-image:radial-gradient(1px 1px at 16% 26%,#fff 95%,transparent),radial-gradient(1px 1px at 69% 78%,#e1c9ff 95%,transparent),radial-gradient(1px 1px at 92% 24%,#fff 95%,transparent);background-size:151px 123px,213px 179px,269px 211px}
.et-cap-intro-content{position:relative;z-index:2;max-width:77%}
.et-cap-overline{display:flex;align-items:center;gap:8px;font-size:9.5px;letter-spacing:.21em;font-weight:700;color:#c1b2f2}
.et-cap-overline i{font-size:13px;color:#ffd6ab;font-style:normal}
.et-cap-intro h1{font-size:clamp(24px,2.35vw,31px);font-weight:800;letter-spacing:-.06em;line-height:1.47;color:#fff;margin:11px 0 7px}
.et-cap-intro h1 em{font-style:normal;color:#f2cfdb}
.et-cap-intro p{max-width:700px;font-size:13px;line-height:1.8;color:#abb7d5;margin:0}
.et-cap-next{display:inline-flex;align-items:center;gap:9px;padding:7px 11px;margin-top:13px;background:rgba(195,174,244,.085);border:1px solid rgba(190,175,240,.16);border-radius:99px;font-size:11.5px;color:#c3c9e1;max-width:100%;flex-wrap:wrap}
.et-cap-next b{color:#f2e3ff;font-weight:700}
.et-cap-next-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#ffd0b1;box-shadow:0 0 10px rgba(255,194,154,.55)}
.et-cap-art{position:absolute;right:5%;top:50%;transform:translateY(-50%);width:170px;height:148px;z-index:1;pointer-events:none}
.et-cap-art svg{width:100%;height:100%;filter:drop-shadow(0 10px 24px rgba(178,114,201,.12))}
.et-cap-eyebrow{font-size:10px;letter-spacing:.14em;font-weight:700;color:#b3bde2}
.et-cap-section{display:flex;align-items:center;gap:9px;margin:16px 0 13px}
.et-cap-section strong{font-size:17px;letter-spacing:-.045em;color:#f9f5ff}
.et-cap-section span{font-size:11px;color:#a3aecf}
.et-cap-empty{min-height:205px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:9px;text-align:center;background:linear-gradient(140deg,rgba(30,34,70,.58),rgba(16,22,47,.67));border:1px solid rgba(171,177,233,.16);border-radius:20px;padding:30px 18px;margin:5px 0 12px}
.et-cap-empty-icon{display:grid;place-items:center;height:56px;width:66px;margin-bottom:5px}
.et-cap-empty-icon svg{height:49px;width:60px}
.et-cap-empty strong{font-size:15px;color:#fff;font-weight:700;letter-spacing:-.02em}
.et-cap-empty p{font-size:13px;line-height:1.85;margin:0;color:#aebad6;max-width:500px}
.et-cap-hint{font-size:11px;line-height:1.7;color:#a1accb;margin:0 0 11px}
.et-cap-letter{position:relative;overflow:hidden;padding:26px 27px 23px;border-radius:20px;border:1px solid rgba(216,191,242,.24);background:radial-gradient(ellipse at 100% 0,rgba(126,94,177,.13),transparent 46%),linear-gradient(150deg,#24243d,#1c223c 63%,#171d35);box-shadow:0 17px 35px rgba(1,4,21,.18)}
.et-cap-letter:before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:.82}
.et-cap-letter-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.et-cap-letter-top b{font-size:11px;color:#ebc7d7;letter-spacing:.14em;font-weight:700}
.et-cap-letter-top span{font-size:10px;color:#c1c4df}
.et-cap-letter-date{color:#aeb8d6;font-size:11px;margin:8px 0 16px}
.et-cap-letter-body{font-family:'Nanum Myeongjo','Malgun Gothic',serif;white-space:pre-wrap;overflow-wrap:anywhere;font-size:16px;line-height:2.05;color:#fff6fa;padding:21px 0;min-height:104px;border-top:1px solid rgba(205,194,243,.13);border-bottom:1px solid rgba(205,194,243,.13)}
.et-cap-bar-label{margin:18px 0 8px;font-size:11px;color:#b9bfdb}
.et-cap-bar{display:flex;gap:3px;width:100%;height:7px;border-radius:10px;overflow:hidden;background:rgba(255,255,255,.06)}
.et-cap-bar i{display:block;height:100%;min-width:0;border-radius:3px}
.et-cap-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.et-cap-tags span{display:flex;align-items:center;gap:5px;border-radius:99px;border:1px solid rgba(200,195,241,.16);background:rgba(255,255,255,.03);padding:6px 10px;color:#d7d9ed;font-size:10px}
.et-cap-tags span i{display:block;width:6px;height:6px;border-radius:50%;background:var(--tone)}
.et-cap-compare{background:linear-gradient(155deg,rgba(31,37,72,.92),rgba(18,24,49,.92));border:1px solid rgba(173,184,236,.19);border-radius:20px;padding:21px 18px}
.et-cap-compare h3{font-size:15px;color:#f4f3ff;letter-spacing:-.03em;margin:0 0 5px}
.et-cap-compare p{font-size:11px;line-height:1.8;color:#a6b4d1;margin:0}
.et-cap-two{display:grid;grid-template-columns:1fr 29px 1fr;align-items:center;gap:5px;margin:24px 0 19px}
.et-cap-person{text-align:center;min-width:0}
.et-cap-orb{display:block;width:57px;height:57px;border-radius:50%;margin:0 auto 11px;background:radial-gradient(circle at 32% 27%,rgba(255,255,255,.92),var(--tone) 23%,color-mix(in srgb,var(--tone) 57%,#151f3c) 57%,#10162d 95%);box-shadow:0 0 0 6px color-mix(in srgb,var(--tone) 10%,transparent),0 0 23px color-mix(in srgb,var(--tone) 23%,transparent),inset -7px -8px 12px rgba(3,8,23,.48)}
.et-cap-orb.is-empty{background:radial-gradient(circle at 35% 29%,#b7c0d8,#3a466a 59%,#111a34);opacity:.36;box-shadow:none}
.et-cap-person b{display:block;font-size:12px;color:#f5f5ff}.et-cap-person small{display:block;font-size:10px;color:#95a5c7;margin-top:4px}
.et-cap-arrow{text-align:center;color:#ad9ace;font-size:20px;margin-top:-23px}
.et-cap-similarity{border-top:1px solid rgba(171,184,233,.14);padding-top:16px;font-size:12px;line-height:1.8;color:#b6c1dc;text-align:center}
.et-cap-similarity strong{color:#e9d4fa;font-size:18px;font-weight:800}
.et-cap-smallnote{font-size:10px;color:#93a2c5;line-height:1.7;margin-top:8px;text-align:center}
.et-cap-reply-label{margin:18px 0 10px}.et-cap-reply-label b{display:block;font-size:14px;color:#f6efff}.et-cap-reply-label small{display:block;color:#adb5d2;font-size:11px;margin-top:3px}
.et-cap-upcoming{display:flex;align-items:center;gap:13px;padding:14px 16px;margin:0 0 10px;border:1px solid rgba(163,177,226,.17);background:linear-gradient(130deg,rgba(32,39,72,.69),rgba(18,25,51,.74));border-radius:15px}
.et-cap-upcoming-icon{display:grid;place-items:center;flex:0 0 37px;height:37px;border:1px solid rgba(239,209,170,.23);background:rgba(242,211,173,.08);border-radius:12px;color:#f2d3b7;font-size:18px}
.et-cap-upcoming-body{min-width:0;flex:1}.et-cap-upcoming-body b{display:block;color:#f7f5ff;font-size:12px;margin-bottom:4px}.et-cap-upcoming-body small{display:block;font-size:10.5px;color:#a3b0d0;line-height:1.6}
.et-cap-days{white-space:nowrap;border-radius:20px;border:1px solid rgba(213,192,243,.22);padding:6px 9px;font-size:11px;font-weight:700;color:#ead4ef}
.et-cap-thread{border:1px solid rgba(178,180,235,.16);border-radius:16px;padding:16px;background:rgba(21,27,54,.5);display:grid;gap:13px;margin:9px 0 14px}
.et-cap-bubble{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.9;padding:14px 16px;border-radius:14px;color:#eff0ff}
.et-cap-bubble small{display:block;color:#abb7d6;margin-bottom:7px;font-size:10.5px}
.et-cap-bubble.old{max-width:92%;background:rgba(79,83,133,.25);border:1px solid rgba(178,179,244,.14);border-bottom-left-radius:4px}
.et-cap-bubble.new{max-width:92%;justify-self:end;background:rgba(122,98,194,.26);border:1px solid rgba(204,174,243,.21);border-bottom-right-radius:4px}
/* Scope widget cosmetics to the time-capsule container only. */
.st-key-et_cap_root [data-testid='stTabs'] [data-baseweb='tab-list']{gap:7px;background:rgba(19,24,49,.35);border:1px solid rgba(172,171,227,.13);border-radius:13px;padding:4px}
.st-key-et_cap_root [data-testid='stTabs'] button[data-baseweb='tab']{border-radius:9px!important;color:#b5bed8!important;padding:9px 14px!important;font-size:12px!important;font-weight:600!important;white-space:nowrap!important}
.st-key-et_cap_root [data-testid='stTabs'] button[data-baseweb='tab'][aria-selected='true']{color:#fff!important;background:rgba(128,111,202,.3)!important}
.st-key-et_cap_root [data-testid='stTabs'] [data-baseweb='tab-highlight']{display:none!important}
.st-key-et_cap_root textarea{background:#151c38!important;border:1px solid rgba(175,174,231,.28)!important;border-radius:12px!important;color:#f7f4ff!important}
.st-key-et_cap_root [data-testid='stForm']{border:1px solid rgba(187,174,240,.16)!important;border-radius:15px!important;background:rgba(31,34,67,.36)!important}
@media(max-width:780px){.et-cap-intro{padding:22px 20px;min-height:164px}.et-cap-intro-content{max-width:84%}.et-cap-art{width:130px;right:1%;opacity:.58}.et-cap-letter{padding:21px 20px}.et-cap-intro h1{font-size:25px}}
@media(max-width:530px){.et-cap-intro-content{max-width:100%}.et-cap-art{right:-32px;width:125px;opacity:.23}.et-cap-intro h1{font-size:23px}.et-cap-intro p{font-size:11px;max-width:85%}.et-cap-next{font-size:10.5px}.et-cap-upcoming{padding:11px}.et-cap-days{font-size:10px}.st-key-et_cap_root [data-testid='stTabs'] button[data-baseweb='tab']{font-size:11px!important;padding:8px 9px!important}}
</style>"""


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _effective(entry: dict) -> list[float]:
    """Use the project's corrected-emotion rule for every display/compare."""
    return [max(0.0, float(x)) for x in A.effective(entry)]


def _dominant(entry: dict) -> int:
    p = _effective(entry)
    return max(range(len(EMOTIONS)), key=lambda i: p[i])


def _short_date(date: dt.date | str) -> str:
    if isinstance(date, str):
        date = dt.date.fromisoformat(date[:10])
    return f"{date.month}월 {date.day}일"


def _due_entries(entries: list[dict], today: dt.date) -> list[dict]:
    """One un-replied entry per source date; no duplicate 7/14/30 letters."""
    out = []
    for entry in entries:
        try:
            date = dt.date.fromisoformat(str(entry['date'])[:10])
        except (KeyError, ValueError, TypeError):
            continue
        age = (today - date).days
        if age < 7 or entry.get('reply'):
            continue
        fresh = any(0 <= age - m < 7 for m in MILESTONES)
        out.append({**entry, 'age': age, 'fresh': fresh, 'today': age in MILESTONES})
    return sorted(out, key=lambda x: (not x['today'], not x['fresh'], -dt.date.fromisoformat(str(x['date'])[:10]).toordinal()))


def _upcoming_entries(entries: list[dict], today: dt.date) -> list[dict]:
    """Future 7, 14 and 30-day arrivals for un-replied source entries."""
    out = []
    for entry in entries:
        if entry.get('reply'):
            continue
        try:
            recorded = dt.date.fromisoformat(str(entry['date'])[:10])
        except (KeyError, ValueError, TypeError):
            continue
        age = (today - recorded).days
        if age < 0:
            continue
        for milestone in MILESTONES:
            if milestone > age:
                arriving = recorded + dt.timedelta(days=milestone)
                out.append({'entry': entry, 'arrival': arriving, 'milestone': milestone, 'days': (arriving - today).days})
    return sorted(out, key=lambda x: (x['days'], x['milestone'], x['entry']['date']))


def _envelope_svg() -> str:
    return '''<svg viewBox="0 0 220 180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="capPaper" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f5d5d0"/><stop offset=".56" stop-color="#d8aaba"/><stop offset="1" stop-color="#9f8ec4"/></linearGradient><linearGradient id="capFold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f9ded7"/><stop offset="1" stop-color="#b88aaf"/></linearGradient></defs><ellipse cx="113" cy="92" rx="98" ry="43" fill="none" stroke="#b5a1de" stroke-opacity=".34" stroke-width="1.3" transform="rotate(-24 113 92)"/><ellipse cx="112" cy="92" rx="84" ry="64" fill="none" stroke="#d9bdd8" stroke-opacity=".13" stroke-width="1" transform="rotate(20 112 92)"/><rect x="53" y="55" width="120" height="85" rx="10" fill="url(#capPaper)" transform="rotate(-6 113 97)"/><path d="M56 58 L113 106 L172 58" fill="none" stroke="#ffe5db" stroke-opacity=".8" stroke-width="1.7" transform="rotate(-6 113 97)"/><path d="M53 136L106 98M171 136L122 98" fill="none" stroke="#a16f9c" stroke-opacity=".35" transform="rotate(-6 113 97)"/><path d="M54 132L105 98Q113 92 121 98L173 132Q173 141 162 141H65Q54 141 54 132Z" fill="url(#capFold)" transform="rotate(-6 113 97)"/><circle cx="115" cy="107" r="10" fill="#ba8398" stroke="#f1c2b5" stroke-width="1.2"/><path d="M115 101l3 6-3 6-3-6Z" fill="#ffe4cc"/><circle cx="30" cy="74" r="2" fill="#fff0e6"/><circle cx="194" cy="122" r="2" fill="#c4e7ff"/></svg>'''


def _header(next_item: dict | None) -> None:
    if next_item:
        upcoming_text = f"다음 편지 · {_short_date(next_item['arrival'])} (D-{next_item['days']})"
    else:
        upcoming_text = "새 기록을 남기면 7일 뒤 첫 편지가 도착해요"
    st.markdown(f'''<div class="et-cap-shell"><section class="et-cap-intro">
<div class="et-cap-intro-content"><div class="et-cap-overline"><i>✦</i> EMOTION TRACE · TIME CAPSULE</div>
<h1>과거의 마음이, <em>오늘의 나에게.</em></h1>
<p>오늘 남긴 기록이 7·14·30일 뒤 편지가 되어 돌아와요. 그때의 나를 읽고, 지금의 마음으로 답장해 보세요.</p>
<div class="et-cap-next"><span class="et-cap-next-dot"></span><b>{_esc(upcoming_text)}</b></div></div>
<div class="et-cap-art">{_envelope_svg()}</div></section></div>''', unsafe_allow_html=True)


def _empty(title: str, description: str) -> None:
    st.markdown(f'''<div class="et-cap-empty"><div class="et-cap-empty-icon">{_envelope_svg()}</div><strong>{_esc(title)}</strong><p>{_esc(description)}</p></div>''', unsafe_allow_html=True)


def _home_link(label: str) -> None:
    """Reuse the existing navigation without altering app.py."""
    try:
        import __main__
        pages = getattr(__main__, 'PAGES', None)
        if isinstance(pages, dict) and 'home' in pages:
            st.page_link(pages['home'], label=f'✦ {label}')
            return
    except Exception:
        pass
    st.caption('왼쪽 메뉴의 홈에서 오늘의 감정을 기록할 수 있어요.')


def _letter_card(entry: dict) -> None:
    recorded = dt.date.fromisoformat(str(entry['date'])[:10])
    probs = _effective(entry)
    ranked = sorted(range(len(EMOTIONS)), key=lambda i: -probs[i])
    dominant = ranked[0]
    body = _esc(entry.get('text') or '기록된 글이 없어요.')
    bar = ''.join(f'<i style="width:{p * 100:.4f}%;background:{COLORS[i]}"></i>' for i, p in enumerate(probs))
    tags = ''.join(f'<span><i style="--tone:{COLORS[i]}"></i>{_esc(EMOTIONS[i])} {round(probs[i] * 100)}%</span>' for i in ranked[:3])
    age = entry['age']
    label = f'{age}일 전의 편지'
    arrival_note = '오늘 도착' if entry['today'] else '도착한 편지'
    st.markdown(f'''<article class="et-cap-letter" style="--accent:{COLORS[dominant]}">
<div class="et-cap-letter-top"><b>LETTER FROM THE PAST</b><span>{arrival_note}</span></div>
<div class="et-cap-letter-date">{_esc(label)} · {recorded.year}년 {recorded.month}월 {recorded.day}일</div>
<div class="et-cap-letter-body">{body}</div><div class="et-cap-bar-label">그날의 감정</div>
<div class="et-cap-bar">{bar}</div><div class="et-cap-tags">{tags}</div></article>''', unsafe_allow_html=True)


def _comparison(entry: dict, entries: list[dict], today: dt.date) -> None:
    past = _effective(entry)
    past_index = max(range(7), key=lambda i: past[i])
    current_entry = next((e for e in entries if str(e.get('date', ''))[:10] == today.isoformat()), None)
    current = _effective(current_entry) if current_entry else None
    now_index = max(range(7), key=lambda i: current[i]) if current else None
    if current:
        dot = sum(a * b for a, b in zip(past, current))
        norm1 = math.sqrt(sum(a * a for a in past))
        norm2 = math.sqrt(sum(b * b for b in current))
        similarity = round(100 * dot / max(norm1 * norm2, 1e-9))
        result = f'감정 비율이 <strong>{similarity}%</strong> 비슷해요.'
        sub = '당시와 오늘 기록의 AI 감정 비율 기준이에요.'
        now_orb = f'<span class="et-cap-orb" style="--tone:{COLORS[now_index]}"></span>'
        now_name = EMOTIONS[now_index]
    else:
        result = '오늘의 감정은 아직 기록되지 않았어요.'
        sub = '홈에서 오늘의 마음을 남기면 비교할 수 있어요.'
        now_orb = '<span class="et-cap-orb is-empty"></span>'
        now_name = '기록 전'
    st.markdown(f'''<div class="et-cap-compare"><h3>그때와 지금</h3><p>마음이 어떻게 달라졌는지 살펴봐요.</p>
<div class="et-cap-two"><div class="et-cap-person"><span class="et-cap-orb" style="--tone:{COLORS[past_index]}"></span><b>{_esc(EMOTIONS[past_index])}</b><small>{_short_date(entry['date'])}</small></div>
<div class="et-cap-arrow">⟶</div><div class="et-cap-person">{now_orb}<b>{_esc(now_name)}</b><small>오늘</small></div></div>
<div class="et-cap-similarity">{result}</div><div class="et-cap-smallnote">{_esc(sub)}</div></div>''', unsafe_allow_html=True)
    if current_entry is None:
        _home_link('오늘의 감정 기록하기')


def _inbox(nickname: str, entries: list[dict], today: dt.date, due: list[dict], upcoming: list[dict]) -> None:
    old = any(not x['fresh'] for x in due)
    show_old = st.toggle('지난 편지도 함께 보기', value=False, key='et_cap_show_old') if old else False
    letters = due if show_old else [x for x in due if x['fresh']]
    if not letters:
        if due:
            message = '오래된 편지가 남아 있어요. 위의 지난 편지 보기를 켜면 열어볼 수 있어요.'
        elif upcoming:
            message = f'다음 편지는 {_short_date(upcoming[0]["arrival"])}에 도착해요.'
        else:
            message = '오늘의 감정을 기록하면 7일 뒤 첫 편지가 도착해요.'
        _empty('아직 도착한 편지가 없어요', message)
        _home_link('오늘의 마음 기록하기')
        return

    st.markdown('<div class="et-cap-section"><strong>도착한 편지</strong><span>어느 날의 마음을 열어볼까요?</span></div>', unsafe_allow_html=True)
    def label(i: int) -> str:
        e = letters[i]
        mood = EMOTIONS[_dominant(e)]
        status = '오늘 도착 · ' if e['today'] else ''
        return f'{status}{_short_date(e["date"])} · {e["age"]}일 전 · {mood}'
    # Selection is indexed by each file's unique date; the field is only a UI switch.
    pick = st.selectbox('열어볼 편지', options=list(range(len(letters))), format_func=label, key='et_cap_letter_pick', label_visibility='collapsed')
    entry = letters[pick]
    left, right = st.columns([1.42, 1], gap='medium')
    with left:
        _letter_card(entry)
        st.markdown('<div class="et-cap-reply-label"><b>지금의 내가, 그때의 나에게</b><small>답장은 보관함에서 다시 읽고 수정할 수 있어요.</small></div>', unsafe_allow_html=True)
        with st.form(key=f'et_cap_reply_form_{entry["date"]}', border=True):
            answer = st.text_area('답장', placeholder='그때의 나에게 전하고 싶은 말을 적어 보세요.', max_chars=500, height=112, key=f'et_cap_reply_input_{entry["date"]}')
            sent = st.form_submit_button('답장 보내기 ✉', type='primary', use_container_width=True)
            if sent:
                if not answer.strip():
                    st.warning('답장 내용을 먼저 적어 주세요.')
                else:
                    try:
                        db.save_reply(nickname, entry['date'], answer.strip(), today.isoformat())
                    except Exception:
                        st.error('답장을 저장하지 못했어요. 다시 시도해 주세요.')
                    else:
                        st.toast('답장이 보관함에 저장됐어요.', icon='💌')
                        st.rerun()
    with right:
        _comparison(entry, entries, today)


def _scheduled(upcoming: list[dict]) -> None:
    if not upcoming:
        _empty('기다리는 편지가 없어요', '새 기록을 남기면 7일·14일·30일 뒤에 다시 만나볼 수 있어요.')
        _home_link('오늘의 마음 기록하기')
        return
    st.markdown('<div class="et-cap-section"><strong>기다리는 편지</strong><span>기록한 날을 기준으로 도착일을 계산해요.</span></div>', unsafe_allow_html=True)
    # Filter only when it materially helps; keep short lists free of extra controls.
    selected = '전체' if len(upcoming) <= 8 else st.selectbox('도착 시점', ('전체','7일','14일','30일'), key='et_cap_upcoming_filter')
    shown = upcoming if selected == '전체' else [x for x in upcoming if x['milestone'] == int(selected[:-1])]
    for item in shown[:12]:
        date = item['entry']['date']
        mood = EMOTIONS[_dominant(item['entry'])]
        st.markdown(f'''<div class="et-cap-upcoming"><span class="et-cap-upcoming-icon">✉</span>
<div class="et-cap-upcoming-body"><b>{_short_date(item['arrival'])} 도착 · {item['milestone']}일의 편지</b>
<small>{_short_date(date)}에 남긴 { _esc(mood) }의 마음</small></div><span class="et-cap-days">D-{item['days']}</span></div>''', unsafe_allow_html=True)
    if len(shown) > 12:
        st.caption(f'가까운 12건만 표시하고 있어요. 외에 {len(shown) - 12}건이 더 예정돼 있어요.')
    st.caption('한 기록은 7·14·30일 뒤에 차례로 돌아옵니다. 별도 편지를 저장하지는 않아요.')


def _history(nickname: str, entries: list[dict], today: dt.date) -> None:
    replied = sorted([e for e in entries if e.get('reply')], key=lambda e: e.get('reply_at') or '', reverse=True)
    if not replied:
        _empty('아직 주고받은 편지가 없어요', '도착한 편지에 답장하면 이곳에서 다시 읽고 수정할 수 있어요.')
        return
    st.markdown('<div class="et-cap-section"><strong>답장 보관함</strong><span>과거와 현재의 마음을 함께 간직해요.</span></div>', unsafe_allow_html=True)
    view_all = st.toggle('모든 답장 보기', key='et_cap_history_all') if len(replied) > 5 else False
    for e in (replied if view_all else replied[:5]):
        mood = EMOTIONS[_dominant(e)]
        reply_date = str(e.get('reply_at') or today.isoformat())[:10]
        heading = f'{_short_date(e["date"])}의 편지 · {mood} · 답장 {_short_date(reply_date)}'
        with st.expander(heading, expanded=False):
            st.markdown(f'''<div class="et-cap-thread"><div class="et-cap-bubble old"><small>{_short_date(e['date'])} · 과거의 나</small>{_esc(e.get('text') or '')}</div>
<div class="et-cap-bubble new"><small>{_short_date(reply_date)} · 지금의 나</small>{_esc(e.get('reply') or '')}</div></div>''', unsafe_allow_html=True)
            with st.form(f'et_cap_edit_form_{e["date"]}', border=False):
                changed = st.text_area('답장 수정하기', value=e.get('reply') or '', height=95, max_chars=500, key=f'et_cap_edit_{e["date"]}')
                if st.form_submit_button('수정한 답장 저장'):
                    if not changed.strip():
                        st.warning('답장을 비워둘 수는 없어요.')
                    else:
                        try:
                            db.save_reply(nickname, e['date'], changed.strip(), today.isoformat())
                        except Exception:
                            st.error('수정 내용을 저장하지 못했어요.')
                        else:
                            st.toast('답장을 수정했어요.', icon='💌')
                            st.rerun()
    if len(replied) > 5 and not view_all:
        st.caption(f'최근 5건을 표시했어요. 나머지 {len(replied)-5}건도 위에서 확인할 수 있어요.')


def render_capsule_page() -> None:
    """Called from emotion_visual_theme.render_capsule_theme in existing app.py."""
    nickname = str(st.session_state.get('nickname') or '').strip()
    if not nickname:
        st.warning('홈에서 닉네임을 먼저 입력해 주세요.')
        return
    entries = db.load_entries(nickname)
    today = dt.date.today()  # Keep date behavior aligned with existing app.py
    due = _due_entries(entries, today)
    upcoming = _upcoming_entries(entries, today)
    fresh_count = sum(bool(e['fresh']) for e in due)
    replies_count = sum(bool(e.get('reply')) for e in entries)
    with st.container(key='et_cap_root'):
        st.markdown(STYLES, unsafe_allow_html=True)
        _header(upcoming[0] if upcoming else None)
        inbox, scheduled, history = st.tabs([
            f'✉ 도착한 편지 {fresh_count}',
            f'◷ 기다리는 편지 {len(upcoming)}',
            f'↗ 답장 보관함 {replies_count}',
        ])
        with inbox:
            _inbox(nickname, entries, today, due, upcoming)
        with scheduled:
            _scheduled(upcoming)
        with history:
            _history(nickname, entries, today)
