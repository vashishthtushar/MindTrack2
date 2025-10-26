import streamlit as st
import sys
import os

# Add utils to path for API import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from utils.api import api
    api_available = True
except ImportError:
    api_available = False
    api = None

st.title("💡 Insights")

# Check user
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Please go back and create a demo user first.")
    st.stop()

# Initialize habit history
if "habit_history" not in st.session_state:
    st.session_state.habit_history = {}

# Get insights from backend if available
insights = []

if api_available:
    try:
        # Get comprehensive insights from backend
        backend_insights = api.get_insights(st.session_state.user_id, days=30)
        
        # Convert backend insights to display format
        if backend_insights.get("recommendations"):
            for rec in backend_insights["recommendations"]:
                insights.append({
                    "title": rec.get("title", "Insight"),
                    "body": rec.get("body", ""),
                    "why": f"Confidence: {rec.get('confidence', 'medium').upper()}",
                    "action": "View Details"
                })
        
        # Display completion rate
        completion_rate = backend_insights.get("completion_rate", 0)
        st.metric("Overall Completion Rate", f"{completion_rate*100:.1f}%")
        
        # Display habit streaks
        if backend_insights.get("habit_streaks"):
            st.subheader("🔥 Your Streaks")
            for habit, streak_info in list(backend_insights["habit_streaks"].items())[:5]:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{habit}**")
                with col2:
                    st.metric("Current", f"{streak_info.get('current_streak', 0)} days")
                with col3:
                    st.metric("Best", f"{streak_info.get('max_streak', 0)} days")
        
        # Display recent badges
        if backend_insights.get("recent_badges"):
            st.subheader("🏆 Recent Badges")
            for badge in backend_insights["recent_badges"][:3]:
                st.info(f"**{badge.get('name', 'Badge')}** - {badge.get('description', '')}")
    except Exception as e:
        st.warning(f"Could not fetch insights from backend: {str(e)}")
        st.info("💡 Make sure the backend API is running on http://localhost:8000")
        insights = []  # Fall back to demo insights

# If no backend insights, use demo insights
if not insights:
    # Demo logic to generate insights based on habit history
    missed_count = 0
    for day_entries in st.session_state.habit_history.values():
        missed_count += sum(1 for s in day_entries.values() if s != "Done")
    
    if missed_count > 0:
        insights.append({
            "title": "Focus on completing missed habits",
            "body": f"You have {missed_count} incomplete habits this month. Completing them boosts consistency!",
            "why": "Consistency increases habit formation probability.",
            "action": "Add to Today"
        })
    
    # Example static insight
    insights.append({
        "title": "Keep your streak going!",
        "body": "You are on a current streak — try completing all habits today to maintain it.",
        "why": "Streaks motivate daily engagement.",
        "action": "Add to Today"
    })

# Display insights
for insight in insights:
    with st.expander(f"💡 {insight['title']}"):
        st.write(insight['body'])
        st.caption(f"Why: {insight['why']}")
        if st.button(insight['action'], key=insight['title']):
            st.success(f"Action '{insight['action']}' applied to today's dashboard!")

