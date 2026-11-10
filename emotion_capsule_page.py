"""EMOTION TRACE — Time Capsule v4.

Capsule-only presentation. It uses existing diary / reply schema and leaves
existing AI, Supabase, and other pages untouched.
"""
from __future__ import annotations

import datetime as dt
import html
import math
from typing import Any

import streamlit as st

import analysis as A
import db

EMO = A.EMO
COLORS = ["#ffcf4a", "#ff8fb1", "#6fd3a8", "#9aa6b8", "#5b84f0", "#b08cf0", "#f0645a"]
MILESTONES = (7, 14, 30)

CAPSULE_CSS = r'''<style>
/* Capsule page only: prefixes avoid modifying Home, Solar and Universe. */
.et-cap-wrap{width:100%;font-family:'Gothic A1','Malgun Gothic',sans-serif;color:#f5f2ff}
.et-cap-hero{position:relative;overflow:hidden;min-height:276px;padding:36px 43px 33px;border:1px solid rgba(185,168,244,.25);border-radius:27px;background:radial-gradient(ellipse at 74% 58%,rgba(87,60,159,.40),transparent 45%),radial-gradient(ellipse at 19% 80%,rgba(40,95,137,.19),transparent 58%),linear-gradient(128deg,#15192e 0%,#171833 48%,#100f28 100%);box-shadow:0 26px 60px rgba(4,5,22,.24),inset 0 1px rgba(255,255,255,.075);margin:0 0 19px}
.et-cap-hero::before{content:'';position:absolute;inset:0;pointer-events:none;opacity:.45;background-image:radial-gradient(1px 1px at 12% 21%,#fff 99%,transparent),radial-gradient(1px 1px at 38% 70%,#d6bdff 99%,transparent),radial-gradient(1.5px 1.5px at 75% 23%,#bde9f4 99%,transparent),radial-gradient(1px 1px at 93% 71%,#fff 99%,transparent);background-size:202px 162px,268px 216px,324px 252px,175px 203px}
.et-cap-hero::after{content:'';position:absolute;width:500px;height:500px;right:-100px;top:-152px;border:1px solid rgba(208,187,255,.10);border-radius:50%;box-shadow:0 0 0 56px rgba(160,138,235,.035),0 0 0 130px rgba(160,138,235,.025);pointer-events:none}
.et-cap-hero-content{position:relative;z-index:2;max-width:60%}
.et-cap-kicker{font-size:10px;letter-spacing:.27em;color:#cab9ff;font-weight:700;margin-bottom:19px}
.et-cap-hero h1{font-size:clamp(27px,3.05vw,42px);letter-spacing:-.055em;line-height:1.43;font-weight:800;margin:0;color:#fff}
.et-cap-hero h1 em{font-style:normal;background:linear-gradient(93deg,#ffe7c3,#c9b5ff 60%,#aeeaf0);-webkit-background-clip:text;background-clip:text;color:transparent}
.et-cap-hero p{font-size:12.5px;color:#b9bbd5;line-height:1.95;max-width:440px;margin:13px 0 20px}
.et-cap-pills{display:flex;align-items:center;flex-wrap:wrap;gap:7px}
.et-cap-pills span{padding:7px 11px;font-size:11px;color:#e5daf7;border:1px solid rgba(205,190,253,.19);background:rgba(220,204,255,.07);border-radius:99px}
.et-cap-pills .et-cap-pills-label{border:0;padding-left:0;background:none;color:#a4abc9}
.et-cap-hero-art{position:absolute;right:4%;top:0;width:41%;height:100%;z-index:1;display:flex;justify-content:center;align-items:center;filter:drop-shadow(0 9px 30px rgba(175,114,252,.13))}
.et-cap-hero-art svg{width:min(100%,380px);height:auto;overflow:visible;animation:et-float 7s ease-in-out infinite}
@keyframes et-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
.et-cap-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin-bottom:24px}
.et-cap-stat{position:relative;border:1px solid rgba(185,170,239,.15);background:linear-gradient(142deg,rgba(34,37,76,.72),rgba(17,21,43,.84));border-radius:17px;padding:17px 18px;min-width:0;overflow:hidden}
.et-cap-stat::before{content:'';position:absolute;top:0;left:20px;right:20px;height:1px;background:linear-gradient(90deg,transparent,var(--tone),transparent);opacity:.52}
.et-cap-stat .et-cap-stat-num{font-size:23px;letter-spacing:-.055em;font-weight:800;line-height:1.5;color:#fff}
.et-cap-stat .et-cap-stat-head{color:#a9afd1;font-size:11px;margin-top:3px;line-height:1.6}
.et-cap-stat .et-cap-stat-sub{color:var(--tone);font-size:10px;margin-top:7px}
.et-cap-section-kicker{display:flex;align-items:center;gap:9px;font-size:10px;letter-spacing:.2em;color:#c0b4e2;font-weight:700;margin:12px 0 12px}
.et-cap-section-kicker::before{content:'';display:block;width:17px;height:1px;background:#b6a4f3}
.et-cap-stages{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:17px}
.et-cap-stage{position:relative;display:flex;gap:12px;align-items:center;border:1px solid rgba(174,179,239,.15);border-radius:15px;padding:12px 15px;background:rgba(17,22,48,.52)}
.et-cap-stage i{font-style:normal;width:34px;height:34px;display:grid;place-items:center;flex:none;border-radius:50%;color:#ffe2ad;border:1px solid rgba(255,220,172,.37);box-shadow:inset 0 0 17px rgba(255,213,154,.08);font-size:14px}
.et-cap-stage b{display:block;font-size:12px;color:#f6f3ff}.et-cap-stage small{display:block;margin-top:3px;font-size:10px;color:#9ba7c8}
.et-cap-stage::after{content:'';position:absolute;right:-8px;top:50%;width:5px;border-top:1px dashed rgba(203,194,255,.35)}.et-cap-stage:last-child::after{display:none}
.et-cap-headline{margin:14px 0 13px}.et-cap-headline b{display:block;font-size:19px;letter-spacing:-.04em;color:#f9f5ff}.et-cap-headline span{display:block;color:#9ba8c9;font-size:11px;line-height:1.8;margin-top:3px}
.et-cap-letter{position:relative;overflow:hidden;border:1px solid rgba(214,183,246,.27);border-radius:23px;background:radial-gradient(ellipse at 0 100%,rgba(90,65,126,.24),transparent 55%),linear-gradient(151deg,#25253c,#191c36 56%,#17192f);padding:31px 33px 27px;box-shadow:0 22px 46px rgba(3,5,17,.17)}
.et-cap-letter::before{content:'';position:absolute;top:0;right:0;width:200px;height:200px;transform:translate(45%,-44%);border:1px solid rgba(229,206,251,.12);border-radius:50%;box-shadow:0 0 0 23px rgba(223,193,255,.035),0 0 0 54px rgba(223,193,255,.02)}
.et-cap-letter-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.et-cap-letter-top span{color:#d7c2fa;letter-spacing:.17em;font-weight:700;font-size:9px}
.et-cap-seal{display:grid;place-items:center;height:39px;width:39px;border-radius:50%;border:1px solid rgba(249,211,175,.44);color:#ffdeaf;font-size:18px;background:radial-gradient(circle,rgba(248,189,142,.21),rgba(248,189,142,.03));transform:rotate(-13deg)}
.et-cap-letter-date{color:#b5b2d4;font-size:11px;margin:3px 0 22px}.et-cap-letter-body{white-space:pre-wrap;overflow-wrap:anywhere;font-family:'Nanum Myeongjo','Malgun Gothic',serif;font-size:clamp(15px,1.3vw,18px);font-weight:500;line-height:2.0;color:#fff6fa;min-height:120px;border-top:1px solid rgba(201,179,226,.15);border-bottom:1px solid rgba(201,179,226,.15);padding:23px 0 22px}
.et-cap-letter-foot{display:flex;justify-content:space-between;align-items:center;gap:10px;color:#aeb5d4;font-size:10.5px;margin:17px 0 13px}
.et-cap-mixture{display:flex;gap:3px;width:100%;height:7px;overflow:hidden;border-radius:9px;background:#343553}.et-cap-mixture i{height:100%;border-radius:4px;flex-grow:0;min-width:1px}
.et-cap-feelings{display:flex;flex-wrap:wrap;gap:7px;margin-top:15px}.et-cap-feelings span{border:1px solid rgba(214,203,255,.14);border-radius:99px;padding:5px 9px;font-size:10px;color:#d0c8ea;background:rgba(255,255,255,.035)}
.et-cap-feelings i{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:6px;background:var(--c)}
.et-cap-panel{border:1px solid rgba(183,179,244,.21);border-radius:22px;padding:24px 21px 22px;background:radial-gradient(circle at 55% 27%,rgba(96,67,156,.22),transparent 62%),linear-gradient(153deg,#1c2442,#13192f 70%);height:100%}
.et-cap-panel-kicker{font-size:9px;font-weight:700;letter-spacing:.19em;color:#aeb9f5}.et-cap-panel h3{font-size:19px;letter-spacing:-.04em;color:#fff;margin:7px 0 5px}.et-cap-panel p{font-size:11px;line-height:1.9;color:#aab5d2;margin:0 0 17px}
.et-cap-compare-orbs{display:flex;align-items:center;justify-content:space-between;gap:4px;margin:18px auto 17px}
.et-cap-person{flex:1;text-align:center;min-width:0}.et-cap-person .et-cap-orb{width:67px;height:67px;display:block;border-radius:50%;margin:0 auto 10px;background:radial-gradient(circle at 34% 30%,rgba(255,255,255,.95),var(--c) 17%,color-mix(in srgb,var(--c) 58%,#171b3e) 55%,#10132c 100%);box-shadow:0 0 0 7px color-mix(in srgb,var(--c) 10%,transparent),0 0 36px color-mix(in srgb,var(--c) 21%,transparent),inset -8px -10px 14px rgba(8,12,30,.6);border:1px solid color-mix(in srgb,var(--c) 60%,#cfd2e9)}
.et-cap-person .et-cap-orb.et-cap-orb-empty{opacity:.32;box-shadow:0 0 0 7px rgba(185,170,232,.1);background:radial-gradient(circle at 33% 30%,#9da3c2,#303a61 55%,#10152b)}
.et-cap-person b{display:block;color:#e7e6ff;font-size:12px}.et-cap-person small{font-size:10px;color:#9da9cd}.et-cap-connector{display:flex;align-items:center;justify-content:center;color:#baa7ec;font-size:19px;min-width:30px;margin-top:-30px}
.et-cap-sim{padding:13px 14px;border:1px solid rgba(173,174,239,.15);background:rgba(14,22,48,.60);border-radius:13px;text-align:center;font-size:11px;color:#b9c3de;line-height:1.85}.et-cap-sim strong{color:#fff;font-size:15px}
.et-cap-insight{padding-top:14px;margin-top:14px;border-top:1px solid rgba(175,181,244,.16);font-size:10.5px;color:#aab4d5;line-height:1.95}
.et-cap-reply-intro{margin-top:18px;padding:13px 15px 9px;border:1px solid rgba(194,173,243,.15);background:linear-gradient(125deg,rgba(69,54,113,.15),rgba(15,20,44,.15));border-radius:16px 16px 0 0}.et-cap-reply-intro b{display:block;color:#f3e9ff;font-size:12px}.et-cap-reply-intro span{display:block;color:#9cabc9;font-size:10.5px;line-height:1.65;margin:5px 0}
.et-cap-empty{display:flex;justify-content:center;align-items:center;text-align:center;flex-direction:column;gap:11px;padding:45px 24px;border:1px solid rgba(174,175,230,.18);border-radius:21px;background:radial-gradient(circle at center,rgba(95,72,146,.14),transparent 60%),rgba(19,24,49,.6);min-height:215px}.et-cap-empty-orb{width:63px;height:56px;border:1px solid rgba(243,203,161,.4);border-radius:12px;display:grid;place-items:center;transform:rotate(-5deg);font-size:27px;color:#ffd8b4;background:linear-gradient(135deg,rgba(152,123,173,.25),rgba(59,52,106,.22));box-shadow:0 0 32px rgba(184,146,237,.1)}.et-cap-empty b{font-size:15px;color:#f2efff}.et-cap-empty p{font-size:11px;color:#aab3d0;line-height:1.9;margin:0;max-width:490px}
.et-cap-mail{display:flex;gap:13px;align-items:center;border:1px solid rgba(171,181,239,.18);background:linear-gradient(120deg,rgba(30,36,68,.68),rgba(19,23,47,.84));border-radius:16px;padding:13px 16px;margin-bottom:10px}.et-cap-mail-icon{flex:none;width:45px;height:45px;display:grid;place-items:center;border-radius:14px;color:#fce6cd;background:linear-gradient(160deg,rgba(228,196,167,.2),rgba(141,106,205,.15));border:1px solid rgba(220,198,233,.16);font-size:22px}.et-cap-mail-body{flex:1;min-width:0}.et-cap-mail b{display:block;color:#f2f0ff;font-size:12px}.et-cap-mail small{display:block;font-size:10.5px;color:#9faacc;margin-top:5px;line-height:1.5}.et-cap-mail-badge{white-space:nowrap;font-size:11px;color:#f8dda9;border:1px solid rgba(230,199,149,.27);padding:5px 9px;border-radius:99px;background:rgba(231,192,127,.06)}
.et-cap-history{border:1px solid rgba(192,183,244,.17);border-radius:18px;background:rgba(15,20,45,.39);padding:18px;margin-bottom:8px}.et-cap-history-head{font-size:10px;color:#b4bbd7;letter-spacing:.12em;margin-bottom:13px}.et-cap-thread{display:grid;gap:13px}.et-cap-bubble{padding:17px 18px;border-radius:16px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.95;color:#e8e7f4}.et-cap-bubble small{display:block;color:#aeb8d5;font-size:10px;letter-spacing:.04em;margin-bottom:9px}.et-cap-bubble.past{max-width:91%;background:linear-gradient(140deg,rgba(71,77,130,.43),rgba(30,37,74,.5));border:1px solid rgba(172,183,247,.17);border-bottom-left-radius:4px}.et-cap-bubble.present{max-width:91%;justify-self:end;background:linear-gradient(125deg,rgba(126,99,198,.39),rgba(104,84,165,.22));border:1px solid rgba(200,171,245,.27);border-bottom-right-radius:4px}
/* Only capsule page Streamlit controls */
[data-testid='stMainBlockContainer'] .st-key-et_cap_reply textarea{background:#171b38!important;border-color:rgba(182,172,243,.26)!important;color:#f5efff!important;border-radius:13px!important}
[data-testid='stMainBlockContainer'] .st-key-et_cap_reply [data-testid='stForm']{border-color:rgba(178,170,239,.19);border-radius:17px;background:rgba(26,29,61,.55)}
.stTabs [data-baseweb='tab-list']{gap:6px;background:rgba(16,20,42,.48);padding:5px;border:1px solid rgba(160,164,228,.13);border-radius:15px}
.stTabs button[data-baseweb='tab']{color:#aeb8d4!important;border-radius:10px;padding:10px 15px!important;font-size:12px!important;font-weight:600!important}
.stTabs button[data-baseweb='tab'][aria-selected='true']{color:#fff!important;background:linear-gradient(140deg,rgba(128,115,204,.34),rgba(73,91,148,.24))!important}
@media(max-width:900px){.et-cap-hero{padding:31px}.et-cap-hero-content{max-width:64%}.et-cap-hero-art{width:43%;right:0}.et-cap-hero h1{font-size:30px}.et-cap-stat{padding:13px 14px}}
@media(max-width:650px){.et-cap-hero{min-height:270px;padding:26px 23px}.et-cap-hero-content{max-width:100%}.et-cap-hero-art{width:180px;right:-37px;top:26px;opacity:.37}.et-cap-hero h1{font-size:27px}.et-cap-hero p{max-width:86%;font-size:11.5px}.et-cap-summary{gap:6px}.et-cap-stat{padding:12px 9px}.et-cap-stat .et-cap-stat-num{font-size:16px}.et-cap-stat .et-cap-stat-head{font-size:9px}.et-cap-stat .et-cap-stat-sub{font-size:9px}.et-cap-stages{gap:5px}.et-cap-stage{display:block;text-align:center;padding:10px 5px}.et-cap-stage i{margin:0 auto 7px}.et-cap-stage b{font-size:11px}.et-cap-stage small{font-size:9px}.et-cap-letter{padding:21px 20px}.et-cap-panel{padding:21px 17px}.et-cap-mail{padding:12px 10px}.et-cap-mail-icon{width:37px;height:38px}.et-cap-mail-badge{padding:5px 7px;font-size:10px}}
@media(prefers-reduced-motion:reduce){.et-cap-hero-art svg{animation:none}}
</style>'''


def _safe(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _effective(entry: dict) -> list[float]:
    return [max(0.0, float(x)) for x in A.effective(entry)]


def _main(entry: dict) -> int:
    return max(range(len(EMO)), key=lambda i: _effective(entry)[i])


def _pretty_date(date: str) -> str:
    d = dt.date.fromisoformat(date)
    return f"{d.month}월 {d.day}일"


def _due_list(entries: list[dict], today: dt.date) -> list[dict]:
    """Unreplied letters that have actually arrived at least 7 days ago."""
    out = []
    for e in entries:
        try:
            age = (today - dt.date.fromisoformat(e['date'])).days
        except (KeyError, ValueError):
            continue
        if e.get('reply') or age < 7:
            continue
        fresh = any(0 <= age - m < 7 for m in MILESTONES)
        out.append({**e, 'age': age, 'fresh': fresh, 'today': age in MILESTONES})
    return sorted(out, key=lambda x: (not x['today'], not x['fresh'], -dt.date.fromisoformat(x['date']).toordinal()))


def _upcoming(entries: list[dict], today: dt.date) -> list[dict]:
    out = []
    for e in entries:
        if e.get('reply'):
            continue
        try:
            recorded = dt.date.fromisoformat(e['date'])
            age = (today - recorded).days
        except (KeyError, ValueError):
            continue
        if age < 0:
            continue
        for milestone in MILESTONES:
            if milestone > age:
                arrive = recorded + dt.timedelta(days=milestone)
                out.append({'entry':e,'milestone':milestone,'arrival':arrive,'days':(arrive-today).days})
    return sorted(out, key=lambda x: (x['days'], x['milestone'], x['entry']['date']))


def _preview_art() -> str:
    """Vector artwork stays crisp, needs no image files or external requests."""
    return '''<div class="et-cap-hero-art" aria-hidden="true">
<svg viewBox="0 0 420 310" role="img" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="etAura"><stop stop-color="#b9a0ff" stop-opacity=".31"/><stop offset=".55" stop-color="#8361df" stop-opacity=".12"/><stop offset="1" stop-color="#8361df" stop-opacity="0"/></radialGradient>
<linearGradient id="etPaper" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f2d1c7"/><stop offset=".43" stop-color="#d8a9ba"/><stop offset="1" stop-color="#ae88bb"/></linearGradient>
<linearGradient id="etFold" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#f7dcd3"/><stop offset="1" stop-color="#b68fae"/></linearGradient>
<linearGradient id="etRing" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#eacda8" stop-opacity=".78"/><stop offset=".55" stop-color="#c3b4f8" stop-opacity=".22"/><stop offset="1" stop-color="#9ce2ec" stop-opacity=".65"/></linearGradient>
<filter id="etGlow"><feGaussianBlur stdDeviation="9"/></filter></defs>
<circle cx="216" cy="150" r="159" fill="url(#etAura)"/>
<g transform="rotate(-23 211 157)" fill="none" stroke="url(#etRing)" stroke-width="1.2"><ellipse cx="211" cy="157" rx="176" ry="69"/><ellipse cx="211" cy="157" rx="133" ry="116" opacity=".36"/><ellipse cx="211" cy="157" rx="186" ry="103" opacity=".16"/></g>
<circle cx="58" cy="134" r="3" fill="#dbceff"/><circle cx="345" cy="79" r="3" fill="#ffdfa9"/><circle cx="339" cy="248" r="2" fill="#bde3ff"/>
<g fill="none" stroke="#ecddff" stroke-width="1" opacity=".56"><path d="M56 124v20M46 134h20"/><path d="M343 70v18M335 79h16"/><path d="M339 240v16M331 248h16"/></g>
<g transform="translate(0 -3) rotate(-6 211 171)">
<rect x="128" y="111" width="172" height="119" rx="15" fill="#be98c2" opacity=".28" filter="url(#etGlow)"/>
<rect x="125" y="105" width="172" height="119" rx="14" fill="url(#etPaper)" stroke="#f6e2dc" stroke-opacity=".54"/>
<path d="M130 112 L211 169 L292 112" fill="none" stroke="#fff2e3" stroke-opacity=".78" stroke-width="2"/>
<path d="M129 217 L201 165 M293 217 L219 165" fill="none" stroke="#9d709d" stroke-opacity=".57" stroke-width="2"/>
<path d="M125 213 L204 160 Q211 156 218 160 L297 213 Q297 224 284 224 H138 Q125 224 125 213Z" fill="url(#etFold)"/>
<circle cx="211" cy="177" r="19" fill="#5a477c" opacity=".25" filter="url(#etGlow)"/>
<circle cx="211" cy="177" r="15" fill="#c48b90" stroke="#f6d0b2" stroke-width="1.1"/>
<path d="M210 169l4 6-4 8-4-8Z" fill="#ffe0c3" opacity=".93"/>
</g>
<path d="M80 226q73 57 162 29" stroke="#e2caff" stroke-opacity=".27" stroke-dasharray="3 8" fill="none"/>
</svg></div>'''


def _header(fresh: int, replied: int, next_item: dict | None) -> None:
    when = f"{_pretty_date(next_item['arrival'].isoformat())} · D-{next_item['days']}" if next_item else "첫 기록을 남겨보세요"
    st.markdown(CAPSULE_CSS, unsafe_allow_html=True)
    st.markdown('''<div class="et-cap-wrap"><div class="et-cap-hero"><div class="et-cap-hero-content">
<div class="et-cap-kicker">EMOTION TRACE &nbsp; / &nbsp; LETTERS THROUGH TIME</div>
<h1>시간을 건너,<br><em>마음이 도착하는 곳.</em></h1>
<p>어제의 마음이 편지가 되어 돌아와요. 그때의 나를 만나고, 지금의 나로 답장해 보세요.</p>
<div class="et-cap-pills"><span class="et-cap-pills-label">편지가 돌아오는 시간</span><span>7일</span><span>14일</span><span>30일</span></div>
</div>''' + _preview_art() + '</div></div>', unsafe_allow_html=True)
    stats=[(f'{fresh}통','최근 도착한 편지','지금 읽어볼 마음','#f5d29f'),(f'{replied}통','주고받은 편지','나와 나의 대화','#c4b0ff'),(when,'다음 편지 도착','시간의 우편함','#98dde4')]
    st.markdown('<div class="et-cap-summary">'+''.join(f'<div class="et-cap-stat" style="--tone:{col}"><div class="et-cap-stat-num">{_safe(value)}</div><div class="et-cap-stat-head">{_safe(label)}</div><div class="et-cap-stat-sub">{_safe(sub)}</div></div>' for value,label,sub,col in stats)+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="et-cap-section-kicker">YOUR LETTERS, IN TIME</div><div class="et-cap-stages">'+''.join(f'<div class="et-cap-stage"><i>{sym}</i><div><b>{days}일의 편지</b><small>{note}</small></div></div>' for sym,days,note in [('✦',7,'첫 번째 마주침'),('◈',14,'조금 먼 마음'),('✧',30,'한 달 뒤의 나')])+'</div>',unsafe_allow_html=True)


def _empty(title:str,caption:str)->None:
    st.markdown(f'<div class="et-cap-empty"><div class="et-cap-empty-orb">✉</div><b>{_safe(title)}</b><p>{_safe(caption)}</p></div>',unsafe_allow_html=True)


def _letter_card(x: dict)->None:
    date=dt.date.fromisoformat(x['date'])
    p=_effective(x)
    order=sorted(range(len(EMO)),key=lambda i:-p[i])
    tags=''.join(f'<span><i style="--c:{COLORS[i]}"></i>{EMO[i]} {round(p[i]*100)}%</span>' for i in order[:3])
    mix=''.join(f'<i style="width:{max(.1,p[i]*100):.3f}%;background:{COLORS[i]}"></i>' for i in range(7))
    text=_safe(x.get('text') or '이날 남긴 글이 없어요.')
    date_text=f'{date.year}년 {date.month}월 {date.day}일'
    now_tag=' · 오늘 도착' if x['today'] else ''
    st.markdown(f'''<div class="et-cap-letter"><div class="et-cap-letter-top"><span>LETTER FROM THE PAST</span><span class="et-cap-seal">✦</span></div>
<div class="et-cap-letter-date">{x['age']}일 전의 나 &nbsp; · &nbsp; {date_text}{now_tag}</div>
<div class="et-cap-letter-body">{text}</div>
<div class="et-cap-letter-foot"><span>그날 마음에 남은 감정들</span><span>7가지 감정</span></div><div class="et-cap-mixture">{mix}</div>
<div class="et-cap-feelings">{tags}</div></div>''',unsafe_allow_html=True)


def _compare_card(x: dict, all_entries:list[dict], today:dt.date)->None:
    past=_effective(x);past_idx=max(range(7),key=lambda i:past[i]);date=_pretty_date(x['date'])
    now=next((e for e in all_entries if e.get('date')==today.isoformat()),None)
    cur=_effective(now) if now is not None else [0.0]*7
    cur_idx=max(range(7),key=lambda i:cur[i]) if now is not None else -1
    orb_now=f'<span class="et-cap-orb" style="--c:{COLORS[cur_idx]}"></span>' if now is not None else '<span class="et-cap-orb et-cap-orb-empty"></span>'
    orb_past=f'<span class="et-cap-orb" style="--c:{COLORS[past_idx]}"></span>'
    if now is not None:
        dot=sum(a*b for a,b in zip(past,cur));norm1=math.sqrt(sum(a*a for a in past));norm2=math.sqrt(sum(b*b for b in cur));score=round(100*dot/max(1e-9,norm1*norm2))
        headline=f'감정 비율 유사도 <strong>{score}%</strong>'
        hint='가장 큰 감정은 달라졌어요.' if past_idx!=cur_idx else '가장 큰 감정은 같아요.'
    else:
        headline='오늘의 마음을 <strong>기록해 주세요</strong>'
        hint='오늘 기록이 생기면 그때와 지금의 마음을 비교할 수 있어요.'
    same=sum(1 for e in all_entries if e.get('date','')>x['date'] and e.get('date','')<=today.isoformat() and _main(e)==past_idx)
    st.markdown(f'''<div class="et-cap-panel"><div class="et-cap-panel-kicker">THEN &amp; NOW</div><h3>그때와 지금의 나</h3>
<p>같은 사람이지만 서로 다른 시간의 마음을 비교해요.</p>
<div class="et-cap-compare-orbs"><div class="et-cap-person">{orb_past}<b>{EMO[past_idx]}</b><small>{_safe(date)}</small></div>
<div class="et-cap-connector">⟶</div><div class="et-cap-person">{orb_now}<b>{EMO[cur_idx] if now is not None else '아직 빈자리'}</b><small>오늘</small></div></div>
<div class="et-cap-sim">{headline}<br><span>{_safe(hint)}</span></div>
<div class="et-cap-insight">그날 이후 <b>{EMO[past_idx]}</b>이(가) 가장 컸던 날은 <b>{same}일</b> 더 있었어요.<br>※ 감정 분석 비율을 바탕으로 한 참고 정보예요.</div></div>''',unsafe_allow_html=True)
    if now is None:
        _home_link('오늘의 감정을 기록하러 가기')


def _home_link(label:str)->None:
    """Use the existing st.Page object, with a safe fallback in preview/tests."""
    try:
        import __main__
        pages=getattr(__main__,'PAGES',{})
        if isinstance(pages,dict) and 'home' in pages:
            st.page_link(pages['home'],label=f'✦ {label}')
            return
    except Exception:
        pass
    st.caption('왼쪽 메뉴의 홈에서 오늘의 감정을 기록할 수 있어요.')


def _inbox(nick:str, entries:list[dict], today:dt.date, due:list[dict])->None:
    st.markdown('<div class="et-cap-headline"><b>나에게 도착한 편지</b><span>도착한 마음을 열고, 그때의 나에게 답장해 보세요.</span></div>',unsafe_allow_html=True)
    show_all=st.toggle('지난 편지도 함께 보기',key='et_cap_show_old',help='답장하지 않은 7일 이상 된 기록까지 볼 수 있어요.')
    letters=due if show_all else [x for x in due if x['fresh']]
    if not letters:
        nxt=_upcoming(entries,today)
        info=f"다음 편지는 {_pretty_date(nxt[0]['arrival'].isoformat())}에 도착할 예정이에요." if nxt else '오늘 기록을 남기면 7일 뒤 첫 편지가 찾아와요.'
        _empty('아직 열어볼 편지가 없어요',info)
        _home_link('오늘의 마음 남기기')
        return
    def _label(i:int)->str:
        x=letters[i];m=EMO[_main(x)];tag='오늘 도착 · ' if x['today'] else ''
        return f'{tag}{_pretty_date(x["date"])} · {x["age"]}일 전 · {m}'
    pick=st.selectbox('어느 날의 편지를 열어볼까요?',options=range(len(letters)),format_func=_label,index=0,key='et_cap_letter_pick')
    x=letters[pick];left,right=st.columns([1.48,1],gap='medium')
    with left:
        _letter_card(x)
        st.markdown('<div class="et-cap-reply-intro"><b>지금의 내가, 그때의 나에게</b><span>그때 미처 하지 못한 말을 적어 보세요. 답장은 보관함에 남아요.</span></div>',unsafe_allow_html=True)
        with st.container(key='et_cap_reply'):
            with st.form(key=f'et_cap_reply_form_{x["date"]}',border=True):
                reply=st.text_area('답장 내용',placeholder='그때의 나는 어떤 마음이었을까? 지금은 어떤 말을 전해주고 싶나요?',max_chars=500,height=130,label_visibility='collapsed')
                submitted=st.form_submit_button('그때의 나에게 답장 보내기  ✉',type='primary',use_container_width=True)
                if submitted:
                    if not reply.strip():st.warning('답장 내용을 적어 주세요.')
                    else:
                        try:
                            db.save_reply(nick,x['date'],reply.strip(),today.isoformat())
                        except Exception:
                            st.error('답장을 저장하지 못했어요. 다시 시도해 주세요.')
                        else:
                            st.toast('답장이 보관함에 도착했어요.',icon='💌')
                            st.rerun()
    with right:
        _compare_card(x,entries,today)


def _scheduled(entries:list[dict],today:dt.date,upcoming:list[dict])->None:
    st.markdown('<div class="et-cap-headline"><b>시간의 우편함</b><span>지금은 잠들어 있는 마음들. 정해진 날짜가 되면 편지가 도착해요.</span></div>',unsafe_allow_html=True)
    t1,t2=st.columns([1.8,1.0],vertical_alignment='center')
    with t2:
        milestone=st.selectbox('도착 시점',('전체 보기','7일 뒤','14일 뒤','30일 뒤'),label_visibility='collapsed',key='et_cap_eta_filter')
    if milestone!='전체 보기':
        m=int(milestone.split('일')[0]);items=[x for x in upcoming if x['milestone']==m]
    else:items=upcoming
    if not items:
        _empty('예정된 편지가 아직 없어요','오늘의 감정을 기록하면 7일 · 14일 · 30일 뒤에 차례로 만나볼 수 있어요.')
        _home_link('새로운 기록 남기기')
        return
    count=len(items)
    st.caption(f'다가올 편지 {count}건 · 가장 가까운 도착일 {_pretty_date(items[0]["arrival"].isoformat())}')
    for item in items[:14]:
        e=item['entry'];m=EMO[_main(e)];caption=f'{_pretty_date(e["date"])}에 남긴 기록 · {m}의 마음'
        st.markdown(f'''<div class="et-cap-mail"><div class="et-cap-mail-icon">✉</div><div class="et-cap-mail-body"><b>{_pretty_date(item['arrival'].isoformat())} 도착 예정 · {item['milestone']}일의 편지</b><small>{_safe(caption)}</small></div><div class="et-cap-mail-badge">D-{item['days']}</div></div>''',unsafe_allow_html=True)
    if count>14:st.caption(f'가까운 14건을 먼저 보여드리고 있어요. 이 밖에도 {count-14}건의 편지가 예정되어 있어요.')
    st.caption('※ 기존 일기가 일정 시간이 지나 편지가 되는 기능입니다. 별도 메시지를 새로 저장하지는 않아요.')


def _history(nick:str, entries:list[dict],today:dt.date)->None:
    replied=sorted([e for e in entries if e.get('reply')],key=lambda e:e.get('reply_at') or '',reverse=True)
    st.markdown('<div class="et-cap-headline"><b>우리가 주고받은 편지</b><span>과거의 내가 남긴 마음과 지금의 내가 건넨 답장을 함께 보관해요.</span></div>',unsafe_allow_html=True)
    if not replied:
        _empty('아직 답장한 편지가 없어요','도착한 편지에 답장하면 두 시점의 대화가 여기에 쌓여요.')
        return
    see_all=st.toggle('모든 답장 보기',key='et_cap_history_all')
    shown=replied if see_all else replied[:5]
    for x in shown:
        mood=EMO[_main(x)];answerdate=x.get('reply_at') or today.isoformat()
        answerlabel=_pretty_date(answerdate[:10]) if answerdate else '최근'
        heading=f'{_pretty_date(x["date"])} · {mood} · 답장 {_safe(answerlabel)}'
        with st.expander(heading,expanded=False):
            st.markdown(f'''<div class="et-cap-history"><div class="et-cap-history-head">A CONVERSATION THROUGH TIME</div><div class="et-cap-thread">
<div class="et-cap-bubble past"><small>{_pretty_date(x['date'])} · 과거의 나 · {_safe(mood)}</small>{_safe(x.get('text') or '')}</div>
<div class="et-cap-bubble present"><small>{_safe(answerlabel)} · 지금의 나</small>{_safe(x.get('reply') or '')}</div>
</div></div>''',unsafe_allow_html=True)
            with st.form(f'et_cap_edit_form_{x["date"]}',border=False):
                updated=st.text_area('답장 다시 쓰기',value=x.get('reply') or '',max_chars=500,height=100,key=f'et_cap_edit_input_{x["date"]}')
                if st.form_submit_button('수정한 답장 저장',use_container_width=False):
                    if not updated.strip():st.warning('내용을 지우려면 먼저 새로운 답장 문구를 적어 주세요.')
                    else:
                        try:db.save_reply(nick,x['date'],updated.strip(),today.isoformat())
                        except Exception:st.error('답장을 수정하지 못했어요.')
                        else:
                            st.toast('답장이 수정됐어요.',icon='💌');st.rerun()
    if not see_all and len(replied)>5:st.caption(f'최근 5개의 대화를 보여드려요. 남은 {len(replied)-5}개도 위에서 확인할 수 있어요.')


def render_capsule_page() -> None:
    nick=str(st.session_state.get('nickname') or '').strip()
    # Existing page calls nick_or_login() first, so this should always be set.
    if not nick:
        st.warning('먼저 홈에서 닉네임을 입력해 주세요.')
        return
    entries=db.load_entries(nick)
    today=dt.date.today()  # Match the rest of the existing app's date convention.
    due=_due_list(entries,today)
    upcoming=_upcoming(entries,today)
    answered=sum(bool(e.get('reply')) for e in entries)
    fresh=sum(x['fresh'] for x in due)
    _header(fresh,answered,upcoming[0] if upcoming else None)
    inbox,scheduled,history=st.tabs([f'✉ 도착한 편지  {fresh}', f'◷ 기다리는 편지  {len(upcoming)}', f'↗ 답장 보관함  {answered}'])
    with inbox:_inbox(nick,entries,today,due)
    with scheduled:_scheduled(entries,today,upcoming)
    with history:_history(nick,entries,today)
