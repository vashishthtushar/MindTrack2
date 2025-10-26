import streamlit as st
from datetime import time

st.title("⏰ Goals & Reminders")

# Check user
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Please go back and create a demo user first.")
    st.stop()

# Initialize reminders
if "reminders" not in st.session_state:
    st.session_state.reminders = []

# ---------- Add Reminder Form ----------
st.header("Set a new reminder")

with st.form("reminder_form"):
    if "selected_habits" in st.session_state and st.session_state.selected_habits:
        habit = st.selectbox("Select Habit", st.session_state.selected_habits)
    else:
        st.warning("No habits selected. Go back to Home.")
        st.stop()
    target = st.number_input("Target (e.g., minutes, glasses, pages)", min_value=1, value=1)
    frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Custom"])
    reminder_time = st.time_input("Reminder Time", value=time(8, 0))
    enabled = st.checkbox("Enabled", value=True)
    submitted = st.form_submit_button("Save Reminder")
    
    if submitted:
        reminder = {
            "habit": habit,
            "target": target,
            "frequency": frequency,
            "time": str(reminder_time),
            "enabled": enabled
        }
        st.session_state.reminders.append(reminder)
        st.success(f"Reminder set for '{habit}'!")

# ---------- List of Active Reminders ----------
st.header("Active Reminders")

if st.session_state.reminders:
    for idx, r in enumerate(st.session_state.reminders):
        status = "✅ Enabled" if r["enabled"] else "❌ Disabled"
        st.write(f"{idx+1}. {r['habit']} - {r['frequency']} at {r['time']} ({status})")
        if st.button(f"Toggle {idx+1}", key=f"toggle_{idx}"):
            r["enabled"] = not r["enabled"]
            st.experimental_rerun()
else:
    st.info("No reminders set yet.")
