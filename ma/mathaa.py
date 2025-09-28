import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime, timedelta
import time
import os
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Math Learning Dashboard",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MATH DATABASE ---
math_data = {
    "Algebra": [
        {"type": "solve", "question": "If $3x + 7 = 19$, what is $x$?", "answer": "4", "points": 10, "image": "algebra_graph.png"},
        {"type": "simplify", "question": "Simplify: $5(2x - 3) - 4x$", "answer": "6x-15", "points": 15, "image": None},
        {"type": "solve", "question": "Solve for $y$: $\\frac{y}{2} - 5 = 1$", "answer": "12", "points": 10, "image": None},
        {"type": "factor", "question": "Factor: $x^2 - 9$", "answer": "(x-3)(x+3)", "points": 15, "image": None},
        {"type": "solve", "question": "Solve the quadratic equation: $x^2 - 5x + 6 = 0$", "answer": "2,3", "points": 20, "image": None}
    ],
    "Geometry": [
        {"type": "area", "question": "What is the area of a rectangle with length 8 and width 4? (Number only)", "answer": "32", "points": 10, "image": "rectangle_diagram.png"},
        {"type": "perimeter", "question": "Find the perimeter of a triangle with sides 5, 12, and 13. (Number only)", "answer": "30", "points": 10, "image": "triangle_diagram.png"},
        {"type": "angle", "question": "If two angles of a triangle are $60^{\\circ}$ and $40^{\\circ}$, what is the third angle? (Number only)", "answer": "80", "points": 15, "image": None},
        {"type": "volume", "question": "What is the volume of a cube with side length 3? (Number only)", "answer": "27", "points": 15, "image": "cube_diagram.png"},
        {"type": "area", "question": "What is the area of a circle with radius 7? (Use π and round to 2 decimals)", "answer": "153.94", "points": 20, "image": "circle_diagram.png"}
    ],
    "Trigonometry": [
        {"type": "ratio", "question": "The definition of $\\cos(\\theta)$ is: (Adjacent/Hypotenuse, Opposite/Hypotenuse, Opposite/Adjacent)", "answer": "Adjacent/Hypotenuse", "points": 20, "image": "trig_triangle.png"},
        {"type": "value", "question": "What is the value of $\\sin(30^{\\circ})$? (Fraction: 1/2 or decimal: 0.5)", "answer": "0.5", "points": 25, "image": None},
        {"type": "value", "question": "What is the value of $\\tan(45^{\\circ})$? (Number only)", "answer": "1", "points": 25, "image": None},
        {"type": "identity", "question": "What is the Pythagorean identity? ($\\sin^2(\\theta) + \\cos^2(\\theta)$ = ?)", "answer": "1", "points": 30, "image": None}
    ],
    "Calculus": [
        {"type": "derivative", "question": "Find the derivative of $f(x) = 3x^2 + 2x - 5$", "answer": "6x+2", "points": 25, "image": None},
        {"type": "integral", "question": "Find the integral of $2x$ with respect to $x$", "answer": "x^2", "points": 25, "image": None},
        {"type": "limit", "question": "Find the limit: $\\lim_{x \\to 2} (x^2 + 3)$", "answer": "7", "points": 20, "image": None}
    ],
    "Statistics": [
        {"type": "mean", "question": "Find the mean of: 5, 7, 9, 11, 13", "answer": "9", "points": 15, "image": None},
        {"type": "probability", "question": "What is the probability of getting heads when flipping a fair coin? (Fraction or decimal)", "answer": "0.5", "points": 15, "image": None}
    ]
}

# --- DAILY MATH CHALLENGES ---
daily_math_challenges = {
    "Monday": {"topic": "Algebra", "task": "Solve 3 algebra problems"},
    "Tuesday": {"topic": "Geometry", "task": "Complete 2 geometry exercises"},
    "Wednesday": {"topic": "Trigonometry", "task": "Master trigonometric identities"},
    "Thursday": {"topic": "Calculus", "task": "Practice derivatives and integrals"},
    "Friday": {"topic": "Statistics", "task": "Solve probability problems"},
    "Saturday": {"topic": "Mixed", "task": "Challenge yourself with mixed problems"},
    "Sunday": {"topic": "Review", "task": "Review all math topics learned this week"}
}

# --- UTILITY FUNCTIONS ---

def get_daily_challenge():
    """Get today's daily math challenge"""
    today = datetime.now().strftime("%A")
    return daily_math_challenges.get(today, {"topic": "General", "task": "Practice math problems today!"})

def update_streak():
    """Update the daily streak counter"""
    today = datetime.now().date()
    last_date = st.session_state.user_data['last_activity_date']
    
    if last_date:
        last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
        if today == last_date + timedelta(days=1):
            st.session_state.user_data['daily_streak'] += 1
            check_achievements()
        elif today > last_date + timedelta(days=1):
            st.session_state.user_data['daily_streak'] = 1
    else:
        st.session_state.user_data['daily_streak'] = 1
    
    st.session_state.user_data['last_activity_date'] = today.strftime("%Y-%m-%d")

def add_points(points):
    """Add points and check for level up"""
    st.session_state.user_data['points'] += points
    
    # Record points for graphing
    st.session_state.user_data['points_history'].append({
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'points_gained': points,
        'total_points': st.session_state.user_data['points']
    })
    
    # Level up every 100 points
    new_level = st.session_state.user_data['points'] // 100 + 1
    if new_level > st.session_state.user_data['level']:
        st.session_state.user_data['level'] = new_level
        st.balloons()
        st.sidebar.success(f"🎉 Level Up! You are now Level {new_level}!")
    check_achievements()

def check_achievements():
    """Check and unlock math achievements"""
    achievements = st.session_state.user_data['achievements']
    points = st.session_state.user_data['points']
    streak = st.session_state.user_data['daily_streak']
    math_problems = st.session_state.user_data['math_problems_completed']
    total_math_problems = sum(math_problems.values())
    
    # Point-based achievements
    if points >= 50 and "50_points" not in achievements:
        achievements.append("50_points")
        st.sidebar.success("🏆 Achievement Unlocked: 50 Points!")
    
    if points >= 100 and "100_points" not in achievements:
        achievements.append("100_points")
        st.sidebar.success("🏆 Achievement Unlocked: Century Scorer!")
    
    # Streak-based achievements
    if streak >= 3 and "3_day_streak" not in achievements:
        achievements.append("3_day_streak")
        st.sidebar.success("🏆 Achievement Unlocked: 3-Day Streak!")
    
    if streak >= 7 and "7_day_streak" not in achievements:
        achievements.append("7_day_streak")
        st.sidebar.success("🏆 Achievement Unlocked: Weekly Warrior!")
    
    # Math-specific achievements
    if total_math_problems >= 10 and "10_math_problems" not in achievements:
        achievements.append("10_math_problems")
        st.sidebar.success("🏆 Achievement Unlocked: Math Beginner!")
    
    if total_math_problems >= 25 and "25_math_problems" not in achievements:
        achievements.append("25_math_problems")
        st.sidebar.success("🏆 Achievement Unlocked: Math Enthusiast!")
    
    if total_math_problems >= 50 and "50_math_problems" not in achievements:
        achievements.append("50_math_problems")
        st.sidebar.success("🏆 Achievement Unlocked: Math Master!")

def save_user_data():
    """Save user data to JSON file"""
    try:
        with open('math_user_data.json', 'w') as f:
            json.dump(st.session_state.user_data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_user_data():
    """Load user data from JSON file"""
    try:
        if os.path.exists('math_user_data.json'):
            with open('math_user_data.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return None

# --- INITIALIZE SESSION STATE ---
if 'user_data' not in st.session_state:
    # Try to load existing data
    loaded_data = load_user_data()
    if loaded_data:
        st.session_state.user_data = loaded_data
    else:
        st.session_state.user_data = {
            'current_grade': 'Grade 7',
            'student_name': '',
            'daily_streak': 0,
            'last_activity_date': None,
            'points': 0,
            'level': 1,
            'daily_challenges_completed': [],
            'achievements': [],
            'points_history': [],
            'math_problems_completed': {},
            'math_quiz_history': []
        }

if 'math_quiz' not in st.session_state:
    st.session_state.math_quiz = {'active': False, 'current_topic': None, 'question': None, 'user_answer': ''}

# --- SIDEBAR (USER PROFILE & MENU) ---
st.sidebar.title("📐 Math Learning Center")
st.sidebar.markdown("---")

# Student Profile Section
st.sidebar.subheader("👤 Student Profile")
if not st.session_state.user_data.get('student_name', ''):
    name = st.sidebar.text_input("Enter Your Name:", key="name_input")
    if name and name.strip():
        st.session_state.user_data['student_name'] = name.strip()
        save_user_data()
        st.rerun()
else:
    st.sidebar.write(f"**Student:** {st.session_state.user_data['student_name']}")

grade = st.sidebar.selectbox("Select Your Grade", ["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"])
st.session_state.user_data['current_grade'] = grade

st.sidebar.markdown(f"**Level:** {st.session_state.user_data['level']}")
st.sidebar.markdown(f"**Points:** {st.session_state.user_data['points']}")
st.sidebar.markdown(f"**Streak:** {st.session_state.user_data['daily_streak']} days")

# Main menu - Math focused only
menu_options = ["🏠 Dashboard", "📐 Math Practice", "📊 Progress Report", "🏆 Achievement Board"]

if 'menu' not in st.session_state:
    st.session_state.menu = menu_options[0]

menu = st.sidebar.selectbox("📋 Select Menu", menu_options, 
                           index=menu_options.index(st.session_state.menu),
                           key="menu_selector")

st.session_state.menu = menu

# Save data button
if st.sidebar.button("💾 Save Progress"):
    save_user_data()
    st.sidebar.success("Progress saved successfully!")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Practice daily to improve your math skills!")

# --- MAIN CONTENT AREA ---

# Dashboard
if menu == "🏠 Dashboard":
    st.title("🎯 Math Learning Dashboard")
    st.success(f"Welcome back, **{st.session_state.user_data.get('student_name', 'Student')}**! You're currently in **{grade}**.")
    
    # Daily challenge card
    challenge = get_daily_challenge()
    
    col1, col2, col3 = st.columns([2,1,1])
    
    with col1:
        st.subheader("📅 Today's Math Challenge")
        st.info(f"**Topic:** {challenge['topic']}")
        st.info(f"**Task:** {challenge['task']}")
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str not in st.session_state.user_data['daily_challenges_completed']:
            if st.button("Start Today's Challenge", type="primary"):
                st.session_state.user_data['daily_challenges_completed'].append(today_str)
                add_points(10)
                update_streak()
                save_user_data()
                st.success("+10 points! Challenge started. Complete math problems in the Math Practice section.")
        else:
            st.success("You've already started today's challenge!")

    # Quick stats
    st.subheader("📈 Math Progress Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_math_problems = sum(st.session_state.user_data['math_problems_completed'].values())
        st.metric("Problems Solved", total_math_problems)
    
    with col2:
        math_topics = len(st.session_state.user_data['math_problems_completed'])
        st.metric("Topics Practiced", math_topics)
    
    with col3:
        st.metric("Total Points", st.session_state.user_data['points'])
    
    with col4:
        st.metric("Current Level", st.session_state.user_data['level'])

    # Recent activity
    st.subheader("📝 Recent Math Activity")
    if st.session_state.user_data['math_quiz_history']:
        recent_activities = st.session_state.user_data['math_quiz_history'][-5:]  # Last 5 activities
        for activity in reversed(recent_activities):
            st.write(f"✅ **{activity['topic']}**: {activity['question_type']} - {activity['result']} (+{activity['points']} points) - {activity['timestamp']}")
    else:
        st.info("No math activities recorded yet. Start practicing!")

# Math Practice
elif menu == "📐 Math Practice":
    st.title("📐 Math Practice: Algebra, Geometry, Trigonometry, Calculus & Statistics")
    st.info("Test your skills in various mathematical fields. Type your answer (numbers only for calculations, or the requested term).")
    st.markdown("---")
    
    # Topic selection
    math_topics = list(math_data.keys())
    selected_topic = st.selectbox("Select a Math Topic:", math_topics)
    
    st.subheader(f"Practice Problems in {selected_topic}")

    # Display topic statistics
    topic_count = st.session_state.user_data['math_problems_completed'].get(selected_topic, 0)
    st.write(f"**Problems solved in {selected_topic}:** {topic_count}")

    # Button to start a new quiz
    if st.button(f"Generate New {selected_topic} Problem", type="primary"):
        problem = random.choice(math_data[selected_topic])
        st.session_state.math_quiz['active'] = True
        st.session_state.math_quiz['current_topic'] = selected_topic
        st.session_state.math_quiz['question'] = problem
        st.session_state.math_quiz['user_answer'] = ''
        
    st.markdown("---")
    
    # Active Quiz Logic
    if st.session_state.math_quiz['active']:
        problem = st.session_state.math_quiz['question']
        
        st.subheader(f"Question: ({problem['type'].capitalize()})")
        
        # IMAGE Placeholder for Math Diagrams/Graphs
        if problem['image']:
            st.info(f"**Diagram:** Imagine a {problem['image']} diagram here to help solve the problem.")
        
        # Use st.latex for math formulas
        st.latex(problem['question']) 
        
        # Input field for user answer
        user_input = st.text_input("Your Answer:", key="math_answer_input").strip()

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Submit Answer", type="primary"):
                # Normalize answers for comparison (remove spaces and convert to lowercase)
                correct_answer = problem['answer'].replace(" ", "").lower()
                submitted_answer = user_input.replace(" ", "").lower()
                
                if submitted_answer == correct_answer:
                    st.success(f"✅ Correct! You earned **{problem['points']}** points.")
                    add_points(problem['points'])
                    update_streak() 
                    
                    # Update math problems completed count
                    topic = st.session_state.math_quiz['current_topic']
                    st.session_state.user_data['math_problems_completed'][topic] = \
                        st.session_state.user_data['math_problems_completed'].get(topic, 0) + 1
                    
                    # Record successful attempt
                    st.session_state.user_data['math_quiz_history'].append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'topic': topic,
                        'question_type': problem['type'],
                        'result': 'Correct',
                        'points': problem['points']
                    })
                    
                    result = "Correct"
                else:
                    st.error(f"❌ Incorrect. The correct answer was: **{problem['answer']}**")
                    
                    # Record failed attempt
                    st.session_state.user_data['math_quiz_history'].append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'topic': st.session_state.math_quiz['current_topic'],
                        'question_type': problem['type'],
                        'result': 'Incorrect',
                        'points': 0
                    })
                    result = "Incorrect"
                
                # Save data after each attempt
                save_user_data()
                
                # Reset quiz state for a new question
                st.session_state.math_quiz['active'] = False
                st.session_state.math_quiz['user_answer'] = ''
                time.sleep(2)
                st.rerun()

# Progress Report (INCLUDES GRAPHS AND PIE CHART)
elif menu == "📊 Progress Report":
    st.title("📊 Your Math Learning Progress")
    
    # 1. Overall Stats
    total_math_problems = sum(st.session_state.user_data['math_problems_completed'].values())
    math_topics_attempted = len(st.session_state.user_data['math_problems_completed'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Problems Solved", total_math_problems)
    with col2:
        st.metric("Topics Practiced", math_topics_attempted)
    with col3:
        st.metric("Total Points", st.session_state.user_data['points'])
    with col4:
        st.metric("Current Level", st.session_state.user_data['level'])
    
    st.markdown("---")

    # 2. Points History Graph (Line Chart)
    st.subheader("⭐ Points Progress Over Time")
    
    if st.session_state.user_data['points_history']:
        # Convert history to DataFrame
        points_df = pd.DataFrame(st.session_state.user_data['points_history'])
        points_df['date'] = pd.to_datetime(points_df['date']).dt.date
        
        # Group by date for plotting total points
        daily_points_df = points_df.groupby('date').last().reset_index()
        
        # Line chart for total points over time
        st.line_chart(daily_points_df, x='date', y='total_points', use_container_width=True)
        st.caption("Total points accumulated over time")
    else:
        st.info("No points history yet. Complete math problems to start tracking!")

    st.markdown("---")
    
    # 3. Math Problem Distribution (Pie Chart)
    st.subheader("📐 Math Topic Distribution")
    
    math_completed = st.session_state.user_data['math_problems_completed']
    
    if math_completed:
        math_df = pd.DataFrame(list(math_completed.items()), columns=['Topic', 'Problems Completed'])
        
        # Use Plotly for a better Pie Chart visualization
        fig = px.pie(math_df, 
                     values='Problems Completed', 
                     names='Topic', 
                     title='Distribution of Completed Math Problems by Topic',
                     color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No math problems completed yet. Try the Math Practice section!")

    st.markdown("---")

    # 4. Daily Activity Heatmap (Simplified)
    st.subheader("📅 Recent Activity Timeline")
    
    if st.session_state.user_data['math_quiz_history']:
        # Get last 10 activities
        recent_activities = st.session_state.user_data['math_quiz_history'][-10:]
        
        for activity in reversed(recent_activities):
            status_icon = "✅" if activity['result'] == 'Correct' else "❌"
            st.write(f"{status_icon} **{activity['timestamp']}** - {activity['topic']} ({activity['question_type']}) - {activity['result']}")
    else:
        st.info("No recent math activities. Start practicing to see your timeline!")

# Achievement Board
elif menu == "🏆 Achievement Board":
    st.title("🏆 Math Achievement Board")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📐 Math Problems")
        total_problems = sum(st.session_state.user_data['math_problems_completed'].values())
        
        if total_problems >= 1:
            st.success("✅ First Problem Solved")
        if total_problems >= 10:
            st.success("✅ Math Beginner (10 problems)")
        if total_problems >= 25:
            st.success("✅ Math Enthusiast (25 problems)")
        if total_problems >= 50:
            st.success("✅ Math Master (50 problems)")
        else:
            st.info(f"Solve {50 - total_problems} more problems to become a Math Master!")
    
    with col2:
        st.subheader("🔥 Streaks")
        streak = st.session_state.user_data['daily_streak']
        
        if streak >= 1:
            st.success("✅ Daily Learner")
        if streak >= 3:
            st.success("✅ 3-Day Streak")
        if streak >= 7:
            st.success("✅ Weekly Warrior")
        else:
            st.info(f"Keep practicing for {7 - streak} more days for Weekly Warrior!")
    
    with col3:
        st.subheader("⭐ Points")
        points = st.session_state.user_data['points']
        
        if points >= 50:
            st.success("✅ 50 Points")
        if points >= 100:
            st.success("✅ Century Scorer")
        if points >= 500:
            st.success("✅ Math Power Player")
        else:
            st.info(f"Earn {500 - points} more points for the Power Player achievement!")
    
    st.markdown("---")
    st.subheader("🎯 Topic Mastery")
    
    math_completed = st.session_state.user_data['math_problems_completed']
    for topic in math_data.keys():
        count = math_completed.get(topic, 0)
        if count >= 5:
            st.success(f"✅ {topic} Explorer (5+ problems)")
        elif count >= 1:
            st.info(f"⏳ {topic} Beginner ({count}/5 problems)")
        else:
            st.write(f"🔲 {topic} (Not started)")

# Footer
st.markdown("---")
st.markdown("### 🚀 Continue Your Math Learning Journey!")
st.markdown("*Practice daily to see amazing progress in mathematics!*")

# Custom CSS for light blue background and math-themed colors
st.markdown("""
<style>
    .stApp {
        background-color: #e0f7fa;
    }
    h1 {
        color: #1E90FF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)