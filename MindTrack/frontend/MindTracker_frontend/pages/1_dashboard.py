import streamlit as st
from datetime import date, datetime
import sys
import os

# Add utils to path for API import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from utils.api import api
    api = api
except ImportError:
    api = None

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-card {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .habit-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Today's Dashboard")

# Check if user exists
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("⚠️ Please go back to Home and create an account first.")
    st.stop()

# Initialize session state
if "habit_entries" not in st.session_state:
    st.session_state.habit_entries = {}

today = str(date.today())

# Initialize streaks
if "streaks" not in st.session_state:
    st.session_state.streaks = {"current": 0, "best": 0, "last_completed": None}

def update_streaks():
    all_done = all(status == "Done" for status in st.session_state.habit_entries.values())
    if all_done:
        st.session_state.streaks["current"] += 1
        if st.session_state.streaks["current"] > st.session_state.streaks["best"]:
            st.session_state.streaks["best"] = st.session_state.streaks["current"]
        st.session_state.streaks["last_completed"] = today
    else:
        st.session_state.streaks["current"] = 0

# Badge milestones
milestones = [3, 7, 14, 30]
current_streak = st.session_state.streaks["current"]

if current_streak in milestones:
    st.balloons()
    st.success(f"🏆 Congrats! {current_streak}-day streak!")

# Load habits from backend or session state
def load_user_habits():
    """Load user's habits from backend or session state"""
    if api and st.session_state.user_id:
        try:
            # Try to get habits from backend
            habits_data = api.get_user_habits(st.session_state.user_id)
            if habits_data:
                # Extract unique habit names
                habit_names = list(set([entry.get('habit_name') for entry in habits_data]))
                return habit_names
        except Exception as e:
            st.warning(f"Could not load habits from backend: {e}")
    # Fallback to session state
    return st.session_state.get('selected_habits', [])

# Load habits early so metrics can use them
user_habits = load_user_habits()

# Progress metrics
done_count = sum(1 for s in st.session_state.habit_entries.values() if s == "Done")
total_count = max(1, len(user_habits))
completion_rate = int((done_count / total_count) * 100) if total_count > 0 else 0

# Display metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📈 Completion", f"{done_count}/{total_count}", f"{completion_rate}%")

with col2:
    st.metric("🔥 Current Streak", f"{current_streak} days")

with col3:
    st.metric("🏆 Best Streak", f"{st.session_state.streaks['best']} days")

st.divider()

# Main content
subheader = st.subheader(f"📅 {today}")

# Check if we have habits
if not user_habits:
    st.warning("⚠️ No habits found. Please go back to Home and select habits first.")
    st.info("💡 Make sure to save your habits after selecting them!")
    st.stop()

# Progress bar
if total_count > 0:
    st.progress(completion_rate / 100)

# Debug helper: show raw habits from backend
with st.expander("⚙️ Debug: Raw habits (backend)"):
    # Display most recent save errors (if any) to help debug failing saves
    last_errors = st.session_state.get("last_save_errors")
    if last_errors:
        st.markdown("**Last save errors:**")
        for err in last_errors:
            # Show the error in a collapsible area for readability
            title = err.split(':', 1)[0] if ':' in err else err
            with st.expander(title):
                st.write(err)

    if st.button("Fetch raw habits from backend"):
        try:
            raw = api.get_user_habits(st.session_state.user_id) if api else []
            st.write(raw)
        except Exception as e:
            st.error(f"Could not fetch raw habits: {e}")

st.markdown("---")

# Habit tracking section
st.markdown("### 🎯 Track Your Habits")

for idx, habit in enumerate(user_habits):
    st.markdown(f'<div class="habit-item"><strong>📌 {habit}</strong></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Done", key=f"done_{idx}", use_container_width=True):
            st.session_state.habit_entries[habit] = "Done"
            # Save to backend
            if api and st.session_state.user_id:
                try:
                    from datetime import date
                    # Call API with positional/keyword args matching the client signature
                    try:
                        api.create_habit_entry(
                            st.session_state.user_id,
                            habit,
                            str(date.today()),
                            status="done",
                            target_value=1.0,
                            notes="Completed via dashboard",
                            mood=5.0,
                        )
                    except Exception as e:
                        st.warning(f"Could not save to backend: {e}")
                except Exception as e:
                    st.warning(f"Could not save to backend: {e}")
            st.rerun()
    
    with col2:
        if st.button("🟡 Partial", key=f"partial_{idx}", use_container_width=True):
            st.session_state.habit_entries[habit] = "Partial"
            # Save to backend
            if api and st.session_state.user_id:
                try:
                    from datetime import date
                    try:
                        api.create_habit_entry(
                            st.session_state.user_id,
                            habit,
                            str(date.today()),
                            status="partial",
                            target_value=0.5,
                            notes="Partially completed via dashboard",
                            mood=3.0,
                        )
                    except Exception as e:
                        st.warning(f"Could not save to backend: {e}")
                except Exception as e:
                    st.warning(f"Could not save to backend: {e}")
            st.rerun()
    
    with col3:
        if st.button("❌ Missed", key=f"missed_{idx}", use_container_width=True):
            st.session_state.habit_entries[habit] = "Missed"
            # Save to backend
            if api and st.session_state.user_id:
                try:
                    from datetime import date
                    try:
                        api.create_habit_entry(
                            st.session_state.user_id,
                            habit,
                            str(date.today()),
                            status="missed",
                            target_value=0.0,
                            notes="Missed via dashboard",
                            mood=1.0,
                        )
                    except Exception as e:
                        st.warning(f"Could not save to backend: {e}")
                except Exception as e:
                    st.warning(f"Could not save to backend: {e}")
            st.rerun()
    
    # Show current status
    if habit in st.session_state.habit_entries:
        status = st.session_state.habit_entries[habit]
        if status == "Done":
            st.success(f"✅ {habit}: Completed!")
        elif status == "Partial":
            st.info(f"🟡 {habit}: Partially done")
        elif status == "Missed":
            st.error(f"❌ {habit}: Missed")

st.markdown("---")

# Save button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("💾 Save Progress", use_container_width=True, type="primary"):
        if api:
            try:
                # Ensure backend user exists before saving progress
                try:
                    api.get_user(st.session_state.user_id)
                except Exception:
                    gen_name = f"User_{str(st.session_state.user_id)[:8]}"
                    user_data = api.create_user(name=gen_name, timezone="UTC")
                    st.session_state.user_id = user_data.get("user_id", st.session_state.user_id)

                # Save to backend per habit and collect errors
                errors = []
                for habit, status in st.session_state.habit_entries.items():
                    status_value = status.lower().replace(" ", "_")
                    try:
                        api.create_habit_entry(
                            st.session_state.user_id,
                            habit,
                            today,
                            status=status_value,
                        )
                    except Exception as e:
                        errors.append(f"{habit}: {e}")

                update_streaks()

                # Check for badges
                try:
                    badge_result = api.check_and_award_badges(st.session_state.user_id)
                    if badge_result.get("awarded_count", 0) > 0:
                        st.balloons()
                        st.success(f"🎉 You earned {badge_result['awarded_count']} new badge(s)!")
                except Exception:
                    pass

                if errors:
                    st.error("Failed to save some items:")
                    for err in errors:
                        st.markdown(f"- {err}")
                    # Store last save errors so the debug expander can display them
                    st.session_state.last_save_errors = errors
                else:
                    st.success("✅ Progress saved successfully!")
                    # Refresh UI so dashboard reflects new entries
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to save: {str(e)}")
                st.info("💡 Start backend: cd backend && uvicorn app.main:app --reload")
        else:
            update_streaks()
            st.success("✅ Progress saved locally!")

# Quick stats at bottom
st.markdown("---")
st.markdown("### 📊 Quick Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Today", today.split("-")[2])

with col2:
    habits_total = len(st.session_state.get('selected_habits', user_habits))
    st.metric("Total Habits", habits_total)

with col3:
    completed_today = done_count
    st.metric("Completed", completed_today)

with col4:
    remaining = total_count - done_count
    st.metric("Remaining", remaining)
