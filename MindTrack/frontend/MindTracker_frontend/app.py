import streamlit as st
import sys
import os
import uuid

# Add utils to path for API import
sys.path.append(os.path.dirname(__file__))
try:
    from utils.api import api
    api_available = True
except ImportError:
    api_available = False
    api = None

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="MindTrack", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .big-font {
        font-size:3.5rem;
        font-weight: 700;
        text-align: center;
    }
    .medium-font {
        font-size:1.5rem;
        text-align: center;
        color: #666;
    }
    .habit-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE INIT ----------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "selected_habits" not in st.session_state:
    st.session_state.selected_habits = []
if "habits_saved" not in st.session_state:
    st.session_state.habits_saved = False

    # Ensure backend user exists before saving habits
    # Save using API client signature, add per-habit error messages and rerun the UI after saving

# Clean up invalid session state values
default_habits = ["Drink Water", "Exercise", "Meditate", "Sleep 8h", "Read", "Journal", "Healthy Eating", "Gratitude"]
if st.session_state.selected_habits:
    # Filter out any invalid values that aren't in the default list
    st.session_state.selected_habits = [habit for habit in st.session_state.selected_habits if habit in default_habits]

# ---------- UI ----------
st.markdown('<p class="big-font">🧠 MindTrack</p>', unsafe_allow_html=True)
st.markdown('<p class="medium-font">Build healthy habits. Stay consistent. Track your wellness.</p>', unsafe_allow_html=True)

st.divider()

# ----------- HABIT SETUP SECTION -----------
st.header("📋 Step 1: Choose Your Habits")

# Add reset button if there are issues
if st.session_state.selected_habits and any(habit not in default_habits for habit in st.session_state.selected_habits):
    st.error("⚠️ Invalid habits detected in session. Please reset.")
    if st.button("🔄 Reset All Data", help="Clear all session data and start fresh", type="secondary"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

col1, col2 = st.columns([2, 1])
with col1:
    selected = st.multiselect("Select habits to track:", default_habits, st.session_state.selected_habits)
    # Update session state when selection changes
    if selected != st.session_state.selected_habits:
        st.session_state.selected_habits = selected
        st.session_state.habits_saved = False  # Reset saved status when habits change

with col2:
    st.write("")
    st.write("💡 Tips:")
    st.info("• Select 3-5 habits to start\n• Make them specific and measurable\n• Start small for success")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("➕ Add Custom Habit")
    custom_habit = st.text_input("Enter habit name:", key="custom_habit_input")
    if st.button("➕ Add", use_container_width=True):
        if custom_habit and custom_habit not in selected:
            st.session_state.selected_habits.append(custom_habit)
            st.success(f"✅ Added: {custom_habit}")
            st.rerun()
        elif custom_habit:
            st.warning("Habit already added!")

with col2:
    st.subheader("📊 Your Selected Habits")
    if st.session_state.selected_habits:
        for i, habit in enumerate(st.session_state.selected_habits, 1):
            st.markdown(f'<div class="habit-card"><b>{i}. {habit}</b></div>', unsafe_allow_html=True)
        
        # Save habits button
        if st.button("💾 Save My Habits", use_container_width=True, type="primary"):
            if api_available and st.session_state.user_id:
                try:
                    # Ensure backend user exists (if user_id is local placeholder, try to fetch/create)
                    try:
                        api.get_user(st.session_state.user_id)
                    except Exception:
                        # Create a backend user with a generated name
                        gen_name = f"User_{str(st.session_state.user_id)[:8]}"
                        user_data = api.create_user(name=gen_name, timezone="UTC")
                        st.session_state.user_id = user_data.get("user_id", st.session_state.user_id)

                    with st.spinner("Saving your habits..."):
                        # Save each habit to the backend
                        from datetime import date
                        for habit in st.session_state.selected_habits:
                            try:
                                api.create_habit_entry(
                                    st.session_state.user_id,
                                    habit,
                                    str(date.today()),
                                    status="done",
                                    target_value=1.0,
                                    notes="Initial setup",
                                    mood=5.0,
                                )
                            except Exception as e:
                                st.warning(f"❌ Error saving habit '{habit}': {e}")

                        st.session_state.habits_saved = True
                        st.success(f"✅ Saved {len(st.session_state.selected_habits)} habits!")
                        st.balloons()

                        # Try to refresh saved habits from backend so they are visible on the Home page
                        try:
                            if api_available and st.session_state.user_id:
                                saved = api.get_user_habits(st.session_state.user_id)
                                # Extract unique habit names and store in session for display
                                if saved:
                                    st.session_state.saved_habits = list({e.get("habit_name") for e in saved if e.get("habit_name")})
                                else:
                                    st.session_state.saved_habits = st.session_state.selected_habits.copy()
                        except Exception:
                            # Fallback to local selected habits if backend fetch fails
                            st.session_state.saved_habits = st.session_state.selected_habits.copy()

                        # Refresh the UI so other pages (Dashboard) pick up saved habits
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error saving habits: {str(e)}")
            else:
                st.session_state.habits_saved = True
                st.success("✅ Habits saved locally!")
    
    # ---------- Saved habits preview (backend or local) ----------
    st.markdown("---")
    st.subheader("💾 Saved Habits")
    saved_preview = []
    # Prefer explicit saved_habits set after save, then backend query, then session selected
    if st.session_state.get("saved_habits"):
        saved_preview = st.session_state.get("saved_habits")
    else:
        # Try to fetch from backend if available
        if api_available and st.session_state.get("user_id"):
            try:
                fetched = api.get_user_habits(st.session_state.user_id)
                if fetched:
                    saved_preview = list({e.get("habit_name") for e in fetched if e.get("habit_name")})
            except Exception:
                saved_preview = []
        # Fallback to selected_habits
        if not saved_preview:
            saved_preview = st.session_state.get("selected_habits", [])

    if saved_preview:
        with st.container():
            for i, habit in enumerate(saved_preview, 1):
                st.markdown(f'<div style="font-size:0.95rem; padding:6px 8px; border:1px solid #eee; border-radius:6px; margin-bottom:4px;">{i}. {habit}</div>', unsafe_allow_html=True)
    else:
        st.info("No saved habits yet. Save your selected habits to persist them to the backend.")
    

st.divider()

# ----------- START TRACKING SECTION -----------
st.header("🚀 Step 2: Start Tracking")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="metric-card"><h2>Ready to Begin?</h2><p>Create your account and start your journey!</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎯 Create My Account", use_container_width=True, type="primary"):
        if api_available:
            try:
                with st.spinner("Creating your account..."):
                    user_name = f"User_{uuid.uuid4().hex[:8]}"
                    user_data = api.create_user(name=user_name, timezone="UTC")
                    st.session_state.user_id = user_data.get("user_id") or str(uuid.uuid4())
                    st.success(f"✅ Welcome, {user_name}! Your account is ready.")
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
                st.info("💡 Tip: Start the backend server first!")
                st.session_state.user_id = f"local_{uuid.uuid4().hex[:8]}"
                st.warning("⚠️ Using offline mode")
        else:
            st.session_state.user_id = f"local_{uuid.uuid4().hex[:8]}"
            st.success("✅ Using offline mode")
            st.info("⚠️ Start backend for full features")

with col2:
    if st.session_state.selected_habits and st.session_state.user_id and st.session_state.habits_saved:
        st.success("✅ Everything ready! Click Dashboard in sidebar →")
    elif not st.session_state.selected_habits:
        st.info("👆 Select habits first")
    elif not st.session_state.user_id:
        st.info("👆 Create account first")
    elif not st.session_state.habits_saved:
        st.info("👆 Save your habits first")

if st.session_state.user_id and st.session_state.selected_habits and st.session_state.habits_saved:
    st.success("🎉 Great! You're all set. Navigate to Dashboard in the sidebar to start tracking!")

st.divider()
st.markdown("""
**💡 Getting Started:**
1. ✅ Select your habits
2. ✅ Create your account
3. 📊 Go to Dashboard to track daily
4. 📅 Check Calendar for progress
5. 💡 View Insights for recommendations
""")
