import streamlit as st
import pandas as pd
import pytz
import math
import textwrap
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# 1) Page config must be the first Streamlit call
st.set_page_config(
    page_title="Neon Time Comparator",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Constants
UTC = timezone.utc
ALL_TIMEZONES = pytz.all_timezones

# 2) Inject custom CSS
def load_css():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');
      html, body, [class*="st-"] { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; }
      h1 {
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        font-size: 2.8rem !important;
        text-shadow: 0 0 10px rgba(102,204,255,0.7);
        background: linear-gradient(90deg, #00dbde, #fc00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
        padding-bottom: 20px;
      }
      .clock-card {
        background: rgba(10,15,30,0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(102,204,255,0.2);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        height: 420px;
      }
      .clock-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,150,255,0.3);
        border: 1px solid rgba(102,204,255,0.4);
      }
      .timezone-name {
        font-size: 1.4rem;
        font-weight: 600;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 8px rgba(102,204,255,0.5);
        margin-bottom: 20px;
        word-wrap: break-word;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .digital-clock {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 2px;
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 10px rgba(0,200,255,0.8);
        color: #00ccff;
        margin-top: 25px;
      }
      .date-display {
        font-size: 1rem;
        opacity: 0.9;
        text-shadow: 0 0 5px rgba(255,255,255,0.5);
      }
      .stDataFrame { background-color: transparent; }
      .stDataFrame table {
        background: rgba(10,15,30,0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(102,204,255,0.2);
      }
      .stDataFrame th {
        background: rgba(0,100,200,0.2);
        color: #fff !important;
        font-weight: 600;
        text-shadow: 0 0 8px rgba(102,204,255,0.3);
      }
      .stDataFrame td { color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# 3) SVG analog clock generator
def create_analog_clock_svg(dt):
    hour_angle   = (dt.hour % 12 + dt.minute / 60) * 30
    minute_angle = (dt.minute + dt.second / 60) * 6
    second_angle = dt.second * 6

    # build the numbers via a single-line f-string inside join
    numbers_svg = ''.join([
        f'<text x="{100 + 80 * math.sin(math.radians(i*30))}" '
        f'y="{100 - 80 * math.cos(math.radians(i*30))}" '
        'fill="#00ccff" font-size="16" font-family="Orbitron" '
        'text-anchor="middle" alignment-baseline="middle" '
        'style="text-shadow:0 0 10px #00ccff;">'
        f'{i if i != 0 else 12}</text>'
        for i in range(1, 13)
    ])

    return f"""
    <svg width="180" height="180" viewBox="0 0 200 200"
         style="background: rgba(0,0,0,0.3); border-radius:50%;
                border:2px solid rgba(102,204,255,0.3);
                box-shadow: inset 0 0 20px rgba(0,0,0,0.5), 0 0 20px rgba(0,150,255,0.2);">
      {numbers_svg}
      <line x1="100" y1="100"
            x2="{100 + 50 * math.sin(math.radians(hour_angle))}"
            y2="{100 - 50 * math.cos(math.radians(hour_angle))}"
            stroke="#fff" stroke-width="6" stroke-linecap="round"
            style="filter:drop-shadow(0 0 3px #fff)" />
      <line x1="100" y1="100"
            x2="{100 + 70 * math.sin(math.radians(minute_angle))}"
            y2="{100 - 70 * math.cos(math.radians(minute_angle))}"
            stroke="#00ccff" stroke-width="4" stroke-linecap="round"
            style="filter:drop-shadow(0 0 3px #00ccff)" />
      <line x1="100" y1="100"
            x2="{100 + 80 * math.sin(math.radians(second_angle))}"
            y2="{100 - 80 * math.cos(math.radians(second_angle))}"
            stroke="#ff00aa" stroke-width="2" stroke-linecap="round"
            style="filter:drop-shadow(0 0 4px #ff00aa)" />
      <circle cx="100" cy="100" r="6" fill="#ff00aa"
              style="filter:drop-shadow(0 0 5px #ff00aa)" />
    </svg>
    """

# 4) Main app
def main():
    # auto-refresh every second
    st_autorefresh(interval=1000, key="clock_autorefresh")

    load_css()

    # initialize session state
    if 'selected_timezones' not in st.session_state:
        st.session_state.selected_timezones = [
            'America/Denver',
            'America/Los_Angeles',
            'America/Argentina/Buenos_Aires',
            'Europe/Rome',
            'Asia/Tokyo'
        ]
    if 'to_remove' not in st.session_state:
        st.session_state.to_remove = None

    # handle "Remove" clicks
    if st.session_state.to_remove:
        st.session_state.selected_timezones.remove(st.session_state.to_remove)
        st.session_state.to_remove = None
        st.experimental_rerun()

    st.title("🌎 Neon Time Comparator")

    # timezone selector
    st.header("Add a New Timezone")
    c1, c2 = st.columns([3, 1])
    with c1:
        selected_tz = st.selectbox(
            "Search for a city, state, or country…",
            options=ALL_TIMEZONES,
            index=ALL_TIMEZONES.index('America/New_York'),
            label_visibility="collapsed",
            key="tz_selector"
        )
    with c2:
        if st.button("Add Timezone", use_container_width=True):
            if selected_tz not in st.session_state.selected_timezones:
                st.session_state.selected_timezones.append(selected_tz)
                st.experimental_rerun()
            else:
                st.toast(f"{selected_tz} is already in the list.", icon="⚠️")

    st.markdown("---")

    if not st.session_state.selected_timezones:
        st.info("Add a timezone to get started.")
        return

    # world clocks
    st.header("World Clocks")
    utc_now = datetime.now(UTC)
    cols = st.columns(len(st.session_state.selected_timezones))
    for idx, tz in enumerate(st.session_state.selected_timezones):
        with cols[idx]:
            local = utc_now.astimezone(pytz.timezone(tz))
            st.markdown(f"""
                <div class="clock-card">
                  <div class="timezone-name">{tz.replace('_',' ')}</div>
                  {create_analog_clock_svg(local)}
                  <div class="digital-clock">{local.strftime('%H:%M:%S')}</div>
                  <div class="date-display">{local.strftime('%A, %B %d, %Y')}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Remove", key=f"remove_{tz}", use_container_width=True):
                st.session_state.to_remove = tz
                st.experimental_rerun()

    # summary table
    st.markdown("---")
    st.header("At a Glance Summary")
    base = st.session_state.selected_timezones[0]
    base_dt = utc_now.astimezone(pytz.timezone(base)).utcoffset().total_seconds() / 3600

    data = []
    for tz in st.session_state.selected_timezones:
        dt = utc_now.astimezone(pytz.timezone(tz))
        offset = dt.utcoffset().total_seconds() / 3600
        diff = offset - base_dt
        data.append({
            "Location": tz.replace('_', ' '),
            "Current Time": dt.strftime('%H:%M:%S'),
            "Date": dt.strftime('%Y-%m-%d'),
            "Difference": "Base" if tz == base else f"{diff:+.1f}h".replace('.0h','h')
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
