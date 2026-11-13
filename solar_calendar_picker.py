"""태양계·유니버스·리포트 공통 날짜 선택 팝업. AI/DB 로직을 변경하지 않습니다."""
from __future__ import annotations
import calendar
import datetime as dt
import html
import streamlit as st
import analysis

COLORS = ('#ffcf4a','#ff8fb1','#6fd3a8','#9aa6b8','#5b84f0','#b08cf0','#f0645a')
WEEK = ('월','화','수','목','금','토','일')


def shift_month(ym: str, offset: int) -> str:
    y, m = map(int, ym.split('-'))
    total = 12*y+m-1+offset
    new_y, new_m = divmod(total, 12)
    return f'{new_y:04d}-{new_m+1:02d}'


def dominant(entry: dict) -> tuple[str,str]:
    k = int(analysis.effective(entry).argmax())
    return analysis.EMO[k], COLORS[k]


def style(ym, by_date, selected, today):
    pieces = ["""<style>
/* Entire calendar belongs to the Streamlit popover, not the embedded solar iframe. */
div[data-testid="stPopoverBody"]:has(.st-key-solar_picker_root){
 width:min(348px,calc(100vw - 24px))!important;max-width:calc(100vw - 24px)!important;
 padding:12px 13px 11px!important; border-radius:18px!important;
 border:1px solid rgba(175,182,245,.20)!important;
 background:linear-gradient(155deg,#19203e,#0c1229 90%)!important;
 box-shadow:0 22px 70px rgba(0,0,0,.57),inset 0 1px rgba(255,255,255,.055)!important;
 /* The calendar is short enough to show in full on regular screens. */
 height:auto!important;
 max-height:none!important;
 overflow:visible!important;
}
/* Streamlit can impose a second scroll area inside the popover. */
div[data-testid="stPopoverBody"]:has(.st-key-solar_picker_root) [data-testid="stVerticalBlockBorderWrapper"]{
 max-height:none!important;overflow:visible!important;
}
/* On a very short browser window, allow intentional scrolling rather than clipping dates. */
@media(max-height:580px){
 div[data-testid="stPopoverBody"]:has(.st-key-solar_picker_root){
  max-height:calc(100dvh - 96px)!important;
  overflow-y:auto!important;overflow-x:hidden!important;
  overscroll-behavior:contain;
 }
}

.st-key-solar_picker_root [data-testid="stVerticalBlock"]{gap:0!important;}
.st-key-solar_picker_root [data-testid="stElementContainer"]{margin:0!important;}
.st-key-solar_picker_root [data-testid="stHorizontalBlock"]{row-gap:0!important;}
/* Keep six-week months as compact as five-week months. */
.st-key-solar_picker_root [data-testid="stHorizontalBlock"]:has([class*="st-key-solar_cal_day_"]){min-height:30px!important;margin:0!important;padding:0!important;}

.st-key-solar_picker_root [data-testid="stHorizontalBlock"]:has([class*="st-key-solar_cal_day_"]){gap:3px!important;flex-wrap:nowrap!important;}
.st-key-solar_picker_root [data-testid="stHorizontalBlock"]:has([class*="st-key-solar_cal_day_"]) [data-testid="stColumn"]{width:0!important;flex:1 1 0!important;min-width:0!important;}
.st-key-solar_picker_root [data-testid="stVerticalBlockBorderWrapper"]{border:none!important;}
.st-key-solar_picker_root .st-key-solar_prev button,.st-key-solar_picker_root .st-key-solar_next button{
 width:28px!important;min-height:28px!important;height:28px!important;border-radius:10px!important;
 background:#111a37!important;border:1px solid rgba(170,185,241,.16)!important;color:#d7e3ff!important;padding:0!important;
}
.st-key-solar_picker_root .st-key-solar_prev button:hover,.st-key-solar_picker_root .st-key-solar_next button:hover{background:#303d65!important;}
.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button{
 width:100%!important;min-width:0!important;min-height:30px!important;height:30px!important;
 padding:0!important;margin:0!important;background:transparent!important;
 color:#c5cce7!important;border:1px solid transparent!important;
 border-radius:9px!important;font-size:11.5px!important;font-weight:550!important;
 transition:background .15s,border .15s,transform .15s!important;
}
.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button:hover:not(:disabled){background:#2a345c!important;color:#fff!important;border-color:#626fa9!important;}
.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button:disabled{opacity:.24!important;}
.solar-cal-heading{text-align:center;color:#f6f6ff;font-size:13px;font-weight:800;letter-spacing:-.02em;}
.solar-cal-kicker{display:none}
.solar-cal-weekdays{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px;text-align:center;margin:8px 0 4px;color:#8797bd;font-size:10px;font-weight:700;}
.solar-cal-weekdays span:last-child{color:#eaa1b9}
.solar-cal-note{font-size:10px;line-height:1.6;color:#a0aed2;margin-top:11px;padding-top:11px;border-top:1px solid rgba(151,173,235,.13)}
.solar-cal-footer{display:flex;justify-content:space-between;align-items:center;color:#abb8d8;font-size:10px;padding-top:8px;margin-top:5px;border-top:1px solid rgba(151,173,235,.12)}
.solar-cal-footer strong{color:#e6eaff;font-weight:600}
.solar-cal-chip{display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(151,174,233,.19);padding:4px 7px;border-radius:999px;background:rgba(39,51,92,.24)}
.solar-cal-chip i{width:7px;height:7px;background:#78d7ba;border-radius:100%;box-shadow:0 0 10px rgba(105,213,170,.5)}
.solar-day-detail{border-radius:11px;padding:7px 9px;margin-top:6px;background:linear-gradient(130deg,rgba(72,85,137,.25),rgba(22,33,65,.5));border:1px solid rgba(158,180,238,.19);}
.solar-day-detail .date{font-size:11px;font-weight:700;color:#aab8dc;margin-bottom:3px}
.solar-day-detail .mood{font-size:13px;font-weight:800;letter-spacing:-.02em}
.solar-day-detail .note{font-size:10.5px;line-height:1.45;color:#c4cee8;margin-top:3px;overflow-wrap:anywhere;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.st-key-solar_picker_root [class*="st-key-solar_open_"] button{border-radius:10px!important;min-height:31px!important;background:#303d72!important;border:1px solid rgba(181,195,255,.3)!important;color:#f6f5ff!important;font-size:11px!important;font-weight:700!important;}
@media(max-width:440px){div[data-testid="stPopoverBody"]:has(.st-key-solar_picker_root){padding:10px 9px!important}.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button{height:29px!important;min-height:29px!important}}
</style>"""]
    for date, entry in by_date.items():
        _, col = dominant(entry)
        key = date.replace('-', '')
        pieces.append(f'<style>.st-key-solar_picker_root .st-key-solar_cal_day_{key} button{{background:linear-gradient(145deg,{col}28,rgba(22,33,62,.75))!important;color:#f3f4ff!important;border:1px solid {col}80!important;font-weight:750!important;box-shadow:inset 0 -2px 0 {col}95!important;}}</style>')
        # The dot means the day has a record; keep the number legible.
    if selected.startswith(ym + '-'):
        key = selected.replace('-', '')
        pieces.append(f'<style>.st-key-solar_picker_root .st-key-solar_cal_day_{key} button{{outline:2px solid #dbe7ff!important;outline-offset:-3px!important;}}</style>')
    if today.strftime('%Y-%m') == ym:
        key = today.strftime('%Y%m%d')
        pieces.append(f'<style>.st-key-solar_picker_root .st-key-solar_cal_day_{key} button{{border-color:#eacb89!important;}}</style>')
    return ''.join(pieces)


def render_solar_calendar(ym: str, entries: list[dict], on_date_open=None) -> None:
    today = dt.date.today()
    yr, month = map(int, ym.split('-'))
    by_date = {str(e['date']): e for e in entries if str(e.get('date','')).startswith(ym+'-')}
    selected = str(st.session_state.get('solar_selected_date',''))
    if not selected.startswith(ym+'-'):
        selected = ''
    with st.container(key='solar_picker_root'):
        st.markdown(style(ym,by_date,selected,today),unsafe_allow_html=True)
        prev, title, nxt = st.columns([1,4,1],gap='small',vertical_alignment='center')
        with prev.container(key='solar_prev'):
            if st.button('‹',key=f'solar_cal_prev_{ym}',use_container_width=True,help='이전 달'):
                st.session_state['ym']=shift_month(ym,-1)
                st.session_state.pop('solar_selected_date',None)
                st.rerun()
        title.markdown(f'<div class="solar-cal-heading">{yr}년 {month}월</div><div class="solar-cal-kicker">감정 기록 달력</div>',unsafe_allow_html=True)
        with nxt.container(key='solar_next'):
            if st.button('›',key=f'solar_cal_next_{ym}',use_container_width=True,disabled=shift_month(ym,1)>today.strftime('%Y-%m'),help='다음 달'):
                st.session_state['ym']=shift_month(ym,1)
                st.session_state.pop('solar_selected_date',None)
                st.rerun()
        st.markdown('<div class="solar-cal-weekdays">'+''.join(f'<span>{day}</span>' for day in WEEK)+'</div>',unsafe_allow_html=True)
        for week in calendar.monthcalendar(yr,month):
            columns=st.columns(7,gap='small')
            for weekday,day in enumerate(week):
                with columns[weekday]:
                    if not day:
                        st.markdown('<div style="height:30px"></div>',unsafe_allow_html=True)
                        continue
                    date_key=f'{ym}-{day:02d}'
                    entry=by_date.get(date_key)
                    mood=dominant(entry)[0] if entry else '기록 없음'
                    with st.container(key=f'solar_cal_day_{date_key.replace("-", "")}'):
                        if st.button(str(day),key=f'solar_pick_{date_key.replace("-", "")}',help=f'{month}월 {day}일 · {mood}',disabled=dt.date(yr,month,day)>today,use_container_width=True):
                            st.session_state['solar_selected_date']=date_key
                            st.rerun()
        if not selected:
            return
        sdate=dt.date.fromisoformat(selected)
        entry=by_date.get(selected)
        if entry:
            mood,col=dominant(entry)
            body=html.escape(str(entry.get('text') or '기록된 내용이 없어요.')[:75])
            kind='10초 기록' if entry.get('kind')=='quick' else '감정 일기'
            st.markdown(f'<div class="solar-day-detail"><div class="date">{sdate.month}월 {sdate.day}일 · {kind} · <b style="color:{col}">● {html.escape(mood)}</b></div><div class="note">{body}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="solar-day-detail"><div class="date">{sdate.month}월 {sdate.day}일</div><div class="note">아직 남긴 기록이 없는 날이에요.</div></div>',unsafe_allow_html=True)
        if on_date_open is not None:
            with st.container(key=f'solar_open_{selected.replace("-", "")}'):
                if st.button('기록 보기 · 수정' if entry else '이 날짜에 기록하기',key=f'solar_cal_open_{selected.replace("-", "")}',use_container_width=True):
                    on_date_open(sdate)
