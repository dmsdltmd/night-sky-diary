"""Emotion Trace: home UI style and time-capsule page entry point."""
import streamlit as st

# Preserve the existing homepage styling; only the capsule page is replaced.
HOME_STYLE = """<style>
.st-key-et_explore [data-testid="stVerticalBlockBorderWrapper"]{background:linear-gradient(150deg,rgba(30,37,75,.87),rgba(12,19,43,.97))!important;border:1px solid rgba(171,171,244,.18)!important;border-radius:19px!important;box-shadow:0 14px 35px rgba(3,5,23,.16),inset 0 1px 0 rgba(255,255,255,.05)!important}
.st-key-et_explore [data-testid="stPageLink"] a{background:rgba(129,122,232,.10)!important}
.st-key-et_explore [data-testid="stPageLink"] a:hover{background:rgba(140,129,239,.22)!important}
.quick-result{box-shadow:0 20px 42px rgba(5,8,31,.20),inset 0 1px 0 rgba(255,255,255,.07)!important}
.arrive{border-radius:14px}
</style>"""


def render_home_theme() -> None:
    st.markdown(HOME_STYLE, unsafe_allow_html=True)


def render_capsule_theme() -> None:
    """Called by app.py's existing page_capsule; no app.py changes required.

    Render the replacement page, then intentionally halt the legacy page body.
    The sidebar was already built before nav.run() invokes this function.
    """
    from emotion_capsule_page import render_capsule_page

    render_capsule_page()
    st.stop()
