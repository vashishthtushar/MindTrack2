import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

st.title("📅 Calendar & Streaks")

# Check user
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Please go back and create a demo user first.")
    st.stop()

# Initialize habit history storage
if "habit_history" not in st.session_state:
    st.session_state.habit_history = {}  # {"YYYY-MM-DD": {"habit_name": status, ...}}

# Add today's dashboard entries to history (simulate daily save)
if "habit_entries" in st.session_state:
    today = str(date.today())
    st.session_state.habit_history[today] = st.session_state.habit_entries.copy()

# ---------- Generate month calendar ----------
today = date.today()
start_month = today.replace(day=1)
days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day

# Prepare data for heatmap
heatmap_data = []
for day in range(1, days_in_month + 1):
    day_str = today.replace(day=day).isoformat()
    if day_str in st.session_state.habit_history:
        entries = st.session_state.habit_history[day_str]
        done_count = sum(1 for s in entries.values() if s=="Done")
        total_count = len(entries)
        completion_rate = done_count / total_count if total_count else 0
    else:
        completion_rate = 0
    heatmap_data.append({"day": day, "completion": completion_rate})

df = pd.DataFrame(heatmap_data)

# Plotly heatmap
fig = px.imshow(
    [df['completion']],  # single row
    labels=dict(x="Day of Month", color="Completion"),
    x=df['day'],
    y=["Progress"],
    color_continuous_scale=["red", "yellow", "green"],
    text_auto=True
)
fig.update_yaxes(showticklabels=False)

st.plotly_chart(fig, use_container_width=True)

# ---------- Day Details ----------
st.subheader("Select a day to view details")
selected_day = st.number_input("Day:", min_value=1, max_value=days_in_month, value=today.day)

selected_date = today.replace(day=selected_day).isoformat()
if selected_date in st.session_state.habit_history:
    st.write("Habits for", selected_date)
    for habit, status in st.session_state.habit_history[selected_date].items():
        st.write(f"- {habit}: {status}")
else:
    st.info("No entries for this day yet.")
