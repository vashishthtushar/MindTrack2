import streamlit as st

st.title("⚙️ Settings & Profile")

# Check user
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Please go back and create a demo user first.")
    st.stop()

st.header("Manage Habits")

# Initialize selected habits if not present
if "selected_habits" not in st.session_state:
    st.session_state.selected_habits = []

# Show current habits
st.subheader("Current Habits")
for idx, habit in enumerate(st.session_state.selected_habits):
    col1, col2 = st.columns([3,1])
    with col1:
        new_name = st.text_input(f"Rename '{habit}'", value=habit, key=f"rename_{idx}")
        if new_name != habit:
            st.session_state.selected_habits[idx] = new_name
    with col2:
        if st.button(f"❌ Delete", key=f"delete_{idx}"):
            st.session_state.selected_habits.pop(idx)
            st.experimental_rerun()

# Add new habit
st.subheader("Add New Habit")
new_habit = st.text_input("New habit name")
if st.button("➕ Add Habit"):
    if new_habit:
        st.session_state.selected_habits.append(new_habit)
        st.success(f"Added habit: {new_habit}")
        st.experimental_rerun()

# Reset demo user
st.divider()
st.header("Reset Demo Data")
if st.button("🗑 Reset Demo User"):
    keys_to_clear = ["user_id", "selected_habits", "habit_entries", "habit_history", "streaks", "reminders"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Demo user and all data cleared. Restart the app to create a new demo user.")

# Privacy note
st.divider()
st.caption("🔒 All data stored locally in this demo. No personal data is uploaded.")
