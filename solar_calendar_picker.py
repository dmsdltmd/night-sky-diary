"""감정의 궤적: 태양계·유니버스·리포트 공통 중앙 달력.

기존 오른쪽 앵커 팝업 대신 st.dialog 안에서 사용합니다.
DB 및 AI 분석 코드는 변경하지 않습니다.
"""
from __future__ import annotations

import calendar
import datetime as dt
import html

import streamlit as st
import analysis

COLORS = ('#ffcf4a', '#ff8fb1', '#6fd3a8', '#9aa6b8', '#5b84f0', '#b08cf0', '#f0645a')
WEEK = ('월', '화', '수', '목', '금', '토', '일')


def shift_month(ym: str, offset: int) -> str:
    year, month = map(int, ym.split('-'))
    total = 12 * year + month - 1 + offset
    next_year, next_month = divmod(total, 12)
    return f'{next_year:04d}-{next_month + 1:02d}'


def dominant(entry: dict) -> tuple[str, str]:
    idx = int(analysis.effective(entry).argmax())
    return analysis.EMO[idx], COLORS[idx]


def _refresh_dialog():
    """Re-render only the open dialog, keeping its month navigation visible."""
    st.rerun(scope='fragment')


def style(ym: str, by_date: dict, selected: str, today: dt.date) -> str:
    css = ["""<style>
/* Centered dialog: no anchored popover or extra tall overlay covering the side card. */
div[role="dialog"]:has(.st-key-solar_picker_root){
  width:min(420px,calc(100vw - 24px))!important;
  max-width:calc(100vw - 24px)!important;
  border-radius:22px!important;
  border:1px solid rgba(177,183,245,.22)!important;
  background:linear-gradient(155deg,#19213f 0%,#101630 62%,#0c1127 100%)!important;
  box-shadow:0 26px 90px rgba(1,3,17,.65)!important;
}
/* Streamlit may wrap the dialog differently in different releases. */
[data-testid="stDialog"]:has(.st-key-solar_picker_root) [data-testid="stVerticalBlock"]{gap:0!important}
.st-key-solar_picker_root [data-testid="stVerticalBlock"]{gap:0!important}
.st-key-solar_picker_root [data-testid="stElementContainer"]{margin:0!important}
.st-key-solar_picker_root [data-testid="stVerticalBlockBorderWrapper"]{border:none!important;box-shadow:none!important}
.st-key-solar_picker_root [data-testid="stHorizontalBlock"]:has([class*="st-key-solar_cal_day_"]){
  gap:3px!important;flex-wrap:nowrap!important;min-height:36px!important;margin:0!important;padding:0!important;
}
.st-key-solar_picker_root [data-testid="stHorizontalBlock"]:has([class*="st-key-solar_cal_day_"]) [data-testid="stColumn"]{
  width:0!important;flex:1 1 0!important;min-width:0!important;
}
.st-key-solar_picker_root .st-key-solar_prev button,.st-key-solar_picker_root .st-key-solar_next button{
  min-width:32px!important;min-height:32px!important;height:32px!important;
  border-radius:10px!important;background:#141b39!important;
  border:1px solid rgba(172,183,242,.23)!important;color:#dce4ff!important;padding:0!important;
}
.st-key-solar_picker_root .st-key-solar_prev button:hover,.st-key-solar_picker_root .st-key-solar_next button:hover{
  background:#2d3865!important;
}
.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button{
  width:100%!important;min-width:0!important;min-height:33px!important;height:33px!important;
  padding:0!important;margin:0!important;border-radius:10px!important;
  background:transparent!important;border:1px solid transparent!important;
  color:#cbd2ec!important;font-size:12px!important;font-weight:550!important;
  transition:background .14s,border .14s!important;
}
.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button:hover:not(:disabled){
  background:#29365e!important;border-color:#7885bc!important;color:#fff!important;
}
.st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button:disabled{opacity:.28!important}
.solar-cal-heading{text-align:center;color:#f5f5ff;font-size:15px;font-weight:800;letter-spacing:-.03em;line-height:2}
.solar-cal-weekdays{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px;text-align:center;
  padding:10px 0 7px;color:#98a5cb;font-size:10px;font-weight:750;}
.solar-cal-weekdays span:last-child{color:#eba3bd}
.solar-cal-footer{display:flex;align-items:center;justify-content:space-between;gap:7px;
  margin-top:10px;padding:10px 1px 4px;border-top:1px solid rgba(161,173,241,.15);
  color:#b9c3e2;font-size:10px;}
.solar-cal-footer strong{color:#e9ecff;font-weight:750}
.solar-cal-chip{display:inline-flex;align-items:center;gap:6px;color:#bcc8e8}
.solar-cal-chip i{width:7px;height:7px;border-radius:50%;background:#78d7ba;box-shadow:0 0 9px rgba(105,213,170,.48)}
.solar-cal-empty{font-size:11px;color:#a6b2d6;text-align:center;padding:8px 2px 0}
.solar-day-detail{margin-top:9px;padding:11px 12px;border-radius:12px;border:1px solid rgba(162,175,236,.19);
  background:linear-gradient(130deg,rgba(68,79,136,.23),rgba(21,31,63,.48))}
.solar-day-detail .date{color:#d8ddf6;font-size:11px;font-weight:800}
.solar-day-detail .note{color:#b9c8e5;font-size:11px;line-height:1.5;margin-top:6px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
.st-key-solar_picker_root [class*="st-key-solar_open_"] button,
.st-key-solar_picker_root .st-key-solar_change_month button{
  border-radius:11px!important;min-height:34px!important;width:100%!important;
  background:rgba(113,104,205,.25)!important;color:#f5f3ff!important;
  border:1px solid rgba(171,163,255,.39)!important;font-size:11px!important;font-weight:750!important;
}
.st-key-solar_picker_root .st-key-solar_change_month button{
  background:rgba(36,47,83,.54)!important;color:#bfc8e9!important;
  border-color:rgba(160,171,221,.22)!important;
}
@media(max-width:480px){
  .st-key-solar_picker_root [class*="st-key-solar_cal_day_"] button{min-height:32px!important;height:32px!important}
  .st-key-solar_picker_root [data-testid="stHorizontalBlock"]:has([class*="st-key-solar_cal_day_"]){min-height:34px!important}
}
</style>"""]
    # Apply record-day colors with higher specificity than the general button rule.
    for date, entry in by_date.items():
        _, color = dominant(entry)
        key = date.replace('-', '')
        css.append(
            f'<style>.st-key-solar_picker_root .st-key-solar_cal_day_{key} button{{'
            f'background:linear-gradient(145deg,{color}2e,rgba(23,33,65,.71))!important;'
            f'border:1px solid {color}91!important;color:#f7f7ff!important;'
            f'box-shadow:inset 0 -2px 0 {color}b3!important;font-weight:750!important;'
            f'}}</style>'
        )
    if selected.startswith(ym + '-'):
        css.append(
            f'<style>.st-key-solar_picker_root .st-key-solar_cal_day_{selected.replace("-", "")} button{{'
            f'outline:2px solid #e5eaff!important;outline-offset:-3px!important;}}</style>'
        )
    if today.strftime('%Y-%m') == ym:
        css.append(
            f'<style>.st-key-solar_picker_root .st-key-solar_cal_day_{today.strftime("%Y%m%d")} button{{'
            f'border-color:#eacb89!important;}}</style>'
        )
    return ''.join(css)


def render_solar_calendar(ym: str, entries: list[dict], on_date_open=None) -> None:
    """Call this from a st.dialog; fragment reruns keep the dialog open."""
    today = dt.date.today()
    # Navigation inside the modal does not change the underlying page until confirmed.
    view_ym = st.session_state.get('calendar_view_month') or ym
    try:
        year, month = map(int, view_ym.split('-'))
        if year < 1900 or year > today.year or (year == today.year and month > today.month):
            raise ValueError('Invalid month')
        dt.date(year, month, 1)
    except (ValueError, TypeError, AttributeError):
        view_ym = ym
        year, month = map(int, view_ym.split('-'))
        st.session_state['calendar_view_month'] = view_ym

    by_date = {str(e['date']): e for e in entries if str(e.get('date', '')).startswith(view_ym + '-')}
    selected = str(st.session_state.get('solar_selected_date', ''))
    if not selected.startswith(view_ym + '-'):
        selected = ''

    with st.container(key='solar_picker_root'):
        st.markdown(style(view_ym, by_date, selected, today), unsafe_allow_html=True)
        prev, heading, nxt = st.columns([1, 4, 1], gap='small', vertical_alignment='center')
        with prev.container(key='solar_prev'):
            if st.button('‹', key=f'calendar_prev_{view_ym}', help='이전 달', use_container_width=True,
                         disabled=year == 1900 and month == 1):
                st.session_state['calendar_view_month'] = shift_month(view_ym, -1)
                st.session_state.pop('solar_selected_date', None)
                _refresh_dialog()
        heading.markdown(f'<div class="solar-cal-heading">{year}년 {month}월</div>', unsafe_allow_html=True)
        with nxt.container(key='solar_next'):
            if st.button('›', key=f'calendar_next_{view_ym}', help='다음 달', use_container_width=True,
                         disabled=view_ym >= today.strftime('%Y-%m')):
                st.session_state['calendar_view_month'] = shift_month(view_ym, 1)
                st.session_state.pop('solar_selected_date', None)
                _refresh_dialog()

        st.markdown('<div class="solar-cal-weekdays">' + ''.join(f'<span>{day}</span>' for day in WEEK) + '</div>',
                    unsafe_allow_html=True)
        for week in calendar.monthcalendar(year, month):
            cols = st.columns(7, gap='small')
            for weekday, day in enumerate(week):
                with cols[weekday]:
                    if not day:
                        st.markdown('<div style="height:33px"></div>', unsafe_allow_html=True)
                        continue
                    key = f'{view_ym}-{day:02d}'
                    entry = by_date.get(key)
                    mood = dominant(entry)[0] if entry else '기록 없음'
                    with st.container(key=f'solar_cal_day_{key.replace("-", "")}'):
                        if st.button(str(day), key=f'calendar_pick_{key.replace("-", "")}',
                                     help=f'{month}월 {day}일 · {mood}',
                                     disabled=dt.date(year, month, day) > today, use_container_width=True):
                            st.session_state['solar_selected_date'] = key
                            _refresh_dialog()

        st.markdown(
            f'<div class="solar-cal-footer"><span class="solar-cal-chip"><i></i> 색이 있는 날 = 기록한 날'
            f'</span><strong>{len(by_date)}일 기록</strong></div>', unsafe_allow_html=True
        )
        if selected:
            selected_day = dt.date.fromisoformat(selected)
            entry = by_date.get(selected)
            if entry:
                mood, color = dominant(entry)
                text = html.escape(str(entry.get('text') or '기록된 내용이 없어요.')[:100])
                kind = '빠른 기록' if entry.get('kind') == 'quick' else '감정 일기'
                st.markdown(
                    f'<div class="solar-day-detail"><div class="date">{selected_day.month}월 {selected_day.day}일 · '
                    f'{kind} · <span style="color:{color}">● {html.escape(mood)}</span></div>'
                    f'<div class="note">{text}</div></div>', unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="solar-day-detail"><div class="date">{selected_day.month}월 {selected_day.day}일'
                    '</div><div class="note">아직 일기를 남기지 않은 날이에요.</div></div>', unsafe_allow_html=True
                )
            if on_date_open is not None:
                with st.container(key=f'solar_open_{selected.replace("-", "")}'):
                    if st.button('기록 보기 · 수정' if entry else '이 날짜에 일기 쓰기',
                                 key=f'calendar_open_{selected.replace("-", "")}', use_container_width=True):
                        on_date_open(selected_day)
        else:
            st.markdown('<div class="solar-cal-empty">날짜를 누르면 그날의 감정과 일기를 확인할 수 있어요.</div>',
                        unsafe_allow_html=True)

        if view_ym != ym:
            with st.container(key='solar_change_month'):
                if st.button(f'{year}년 {month}월 화면 보기', key=f'calendar_show_month_{view_ym}',
                             use_container_width=True):
                    st.session_state['ym'] = view_ym
                    st.session_state.pop('solar_selected_date', None)
                    st.rerun()  # Full rerun closes the dialog and changes the main page month.
