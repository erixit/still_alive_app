import streamlit as st
import sqlite3
from datetime import datetime
import calendar
import pandas as pd
from streamlit_calendar import calendar as st_calendar

st.set_page_config(page_title="Still Alive", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Database setup
DB_FILE = "still_alive.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            username TEXT NOT NULL,
            activity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, username)
        )
    ''')
    conn.commit()
    conn.close()

def get_month_checkins(year, month):
    """Get all check-ins for a specific month"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    month_start = f"{year}-{month:02d}-01"
    month_end = f"{year}-{month:02d}-31"
    
    c.execute('''
        SELECT DATE(date) as check_date, username, activity
        FROM checkins
        WHERE DATE(date) BETWEEN ? AND ?
        ORDER BY check_date, username
    ''', (month_start, month_end))
    
    results = c.fetchall()
    conn.close()
    
    # Convert to dict for easy lookup
    checkins = {}
    for date_str, username, activity in results:
        day = int(date_str.split('-')[2])
        if day not in checkins:
            checkins[day] = {}
        checkins[day][username] = activity
    
    return checkins

def check_in(day, username, year, month, activity):
    """Record or update a check-in"""
    date_str = f"{year}-{month:02d}-{day:02d}"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Check if user already checked in
    c.execute('''
        SELECT id FROM checkins
        WHERE date = ? AND username = ?
    ''', (date_str, username))
    
    existing = c.fetchone()
    
    if existing:
        # Update existing check-in
        c.execute('''
            UPDATE checkins
            SET activity = ?
            WHERE date = ? AND username = ?
        ''', (activity if activity else None, date_str, username))
    else:
        # Insert new check-in
        c.execute('''
            INSERT INTO checkins (date, username, activity)
            VALUES (?, ?, ?)
        ''', (date_str, username, activity if activity else None))
    
    conn.commit()
    conn.close()

def get_day_checkins(day, year, month):
    """Get all check-ins for a specific day"""
    date_str = f"{year}-{month:02d}-{day:02d}"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT username, activity
        FROM checkins
        WHERE date = ?
        ORDER BY username
    ''', (date_str,))
    
    results = c.fetchall()
    conn.close()
    return results

def get_all_checkins():
    """Get all check-ins for display"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT DATE(date) as date, username, activity
        FROM checkins
        ORDER BY date DESC
    ''')
    results = c.fetchall()
    conn.close()
    return results

# Initialize database
init_db()

# Login Section
if not st.session_state.logged_in:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        username = st.selectbox("Select your name:", ["You", "Brother"])
        if st.button("Login"):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
else:
    # Main App header in compact form
    col_welcome, col_logout = st.columns([4, 1])
    with col_welcome:
        st.write(f"**Still Alive** — Welcome, {st.session_state.username}! 👋")
    with col_logout:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    now = datetime.now()
    year = now.year
    month = now.month
    
    # Get all check-ins for this month
    checkins = get_month_checkins(year, month)
    
    # Color mapping for users
    user_colors = {
        "You": "#FF6B6B",
        "Brother": "#4ECDC4"
    }

    events = []
    for day, users in checkins.items():
        for user, activity in users.items():
            title = user if not activity else f"{user}: {activity}"
            events.append({
                "title": title,
                "start": f"{year}-{month:02d}-{day:02d}",
                "end": f"{year}-{month:02d}-{day:02d}",
                "color": user_colors.get(user, "#888888")
            })

    # Stabilize options and events to prevent infinite reruns
    if "calendar_options" not in st.session_state:
        st.session_state.calendar_options = {
            "initialView": "dayGridMonth",
            "headerToolbar": {
                "left": "prev,next prevYear,nextYear today",
                "center": "title",
                "right": ""
            },
            "selectable": False,
            "editable": False,
            "height": 500,
            "dayCellClassNames": "fc-day-no-highlight"
        }

    if "calendar_events" not in st.session_state or st.session_state.calendar_events != events:
        st.session_state.calendar_events = events

    # Use columns to center the calendar and reduce its width to ~75%
    _, col_cal, _ = st.columns([1, 6, 1])

    with col_cal:
        # Legend
        st.markdown(f"<div>Legend: <span style='color:{user_colors['You']}'>●</span> You &nbsp;&nbsp; <span style='color:{user_colors['Brother']}'>●</span> Brother</div>", unsafe_allow_html=True)
        try:
            # Limit callbacks to prevent 'eventsSet' from triggering infinite reruns
            st_calendar(
                events=st.session_state.calendar_events,
                options=st.session_state.calendar_options,
                key="calendar",
                callbacks=[]
            )
        except Exception:
            st.info("Streamlit calendar not available — showing the styled grid above instead.")

    st.markdown("---")

    # Writable single-line check-in form
    col_date, col_form = st.columns([1, 3])
    
    with col_date:
        # Date picker outside form so it triggers re-run
        # Remove the `value` argument. The `key` will preserve the state across reruns,
        # and the widget will correctly default to today's date on the first load.
        form_date = st.date_input("Date", key="form_date_picker")
        
        # Fetch existing message for selected date and user
        existing_msg = ""
        existing_activity = get_day_checkins(form_date.day, form_date.year, form_date.month)
        for user, activity in existing_activity:
            if user == st.session_state.username:
                existing_msg = activity if activity else ""
                break
    
    with col_form:
        # Form for message and submission
        with st.form(key="quick_checkin", clear_on_submit=False):
            # Message input inside form
            form_msg = st.text_input("Message (optional)", value=existing_msg)

            col_chk, col_submit = st.columns([1, 1])
            with col_chk:
                # The hardcoded `value=True` was a primary cause of the infinite loop
                # as it fought with Streamlit's state management. Removing it allows
                # the widget to behave correctly, defaulting to unchecked.
                form_alive = st.checkbox("I'm alive")
            with col_submit:
                submitted = st.form_submit_button("Save", use_container_width=True)

    if submitted:
        # If user unchecked 'I'm alive' treat as deletion of check-in
        if form_alive:
            check_in(form_date.day, st.session_state.username, form_date.year, form_date.month, form_msg)
            st.success(f"Saved check-in for {form_date.strftime('%Y-%m-%d')}")
        else:
            # Remove existing check-in for this user/date if exists
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('DELETE FROM checkins WHERE date = ? AND username = ?', (form_date.strftime('%Y-%m-%d'), st.session_state.username))
            conn.commit()
            conn.close()
            st.info(f"Removed check-in for {form_date.strftime('%Y-%m-%d')}")
        # An explicit st.rerun() is not needed here and can cause loops.
        # Streamlit automatically reruns the script after a form submission.
