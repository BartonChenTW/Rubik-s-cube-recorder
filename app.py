"""
Rubik's Cube Recorder - Streamlit Application
Record your solving times and algorithms for different Rubik's cube patterns
"""

import warnings
warnings.filterwarnings('ignore', message='.*pyarrow.*')

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components
from datetime import datetime
from utils.mongo_data_manager import MongoDataManager
from utils.visualizations import create_time_chart, create_statistics_cards

# Page configuration
st.set_page_config(
    page_title="Rubik's Cube Recorder",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lazy initialize MongoDB data manager
@st.cache_resource
def get_data_manager():
    return MongoDataManager()

data_manager = get_data_manager()

# Cache algorithms to avoid DB hits on every rerun
@st.cache_data(ttl=300)
def get_algorithms_cached():
    return data_manager.load_algorithms()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    /* Big timer control buttons */
    div[data-testid="column"]:has(button[key="start_timer"]) button,
    div[data-testid="column"]:has(button[key="stop_timer"]) button,
    div[data-testid="column"]:has(button[key="reset_timer"]) button {
        height: 120px !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
        border-radius: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🧊 Rubik\'s Cube Recorder</div>', unsafe_allow_html=True)

# Sidebar - Player Profile
st.sidebar.title("👤 Player Profile")

# Initialize player name in session state
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""

player_name = st.sidebar.text_input(
    "Your Name",
    value=st.session_state.player_name,
    placeholder="Enter your name",
    help="This will be saved with your solve records"
)

if player_name != st.session_state.player_name:
    st.session_state.player_name = player_name

# Display welcome message if name is set
if st.session_state.player_name:
    st.sidebar.success(f"Welcome, {st.session_state.player_name}! 🎉")
else:
    st.sidebar.info("👋 Enter your name above")

st.sidebar.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page:",
    ["Record New Solve", "View Records", "Statistics"]
)

# ===== RECORD NEW SOLVE PAGE =====
if page == "Record New Solve":
    st.header("⏱️ Record New Solve")
    
    # Initialize session state for timer
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = 0.0
    if 'recorded_time' not in st.session_state:
        st.session_state.recorded_time = 0.0
    
    # Stopwatch section
    st.subheader("⏱️ Stopwatch Timer")
    
    # Add custom CSS for big buttons
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button,
        div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
            height: 150px !important;
            font-size: 3rem !important;
            font-weight: bold !important;
            border-radius: 20px !important;
            padding: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    timer_col1, timer_col2, timer_col3 = st.columns([2, 1, 1])
    
    with timer_col1:
        # Display timer (client-side JS updates without reruns)
        # Use UTC to avoid timezone issues between server and client
        from datetime import timezone
        
        if st.session_state.timer_running and st.session_state.start_time:
            # Calculate display time server-side for initial render
            time_display = (datetime.now(timezone.utc) - st.session_state.start_time).total_seconds()
            base_offset = 0.0  # Always start from 0 when running
        else:
            time_display = float(st.session_state.recorded_time or 0.0)
            base_offset = time_display

        # Render a JS-driven timer that updates in the browser
        running_js = 'true' if st.session_state.timer_running and st.session_state.start_time else 'false'
        start_iso = st.session_state.start_time.isoformat() if st.session_state.start_time else None
        components.html(
            f"""
            <div id="timerDisplay" style="color:#FF6B6B; font-size: 4rem; font-weight: bold;">{time_display:.2f}s</div>
            <script>
            (function(){{
                const running = {running_js};
                const startISO = {json.dumps(start_iso)};
                const base = {base_offset:.6f};
                const el = document.getElementById('timerDisplay');
                let currentElapsedSeconds = base;
                function fmt(ms){{ return (ms/1000).toFixed(2) + 's'; }}
                if (running && startISO) {{
                    const t0 = new Date(startISO).getTime();
                    const baseMs = base * 1000;
                    let rafId;
                    function tick(){{
                        const now = Date.now();
                        const elapsedMs = (now - t0) + baseMs;
                        currentElapsedSeconds = elapsedMs / 1000;
                        el.textContent = fmt(elapsedMs);
                        rafId = window.requestAnimationFrame(tick);
                    }}
                    tick();
                    window.addEventListener('beforeunload', ()=>{{ if (rafId) cancelAnimationFrame(rafId); }});
                }} else {{
                    el.textContent = fmt(base*1000);
                }}
                // Store current elapsed time for Python to read
                window.timerElapsedSeconds = function() {{ return currentElapsedSeconds; }};
            }})();
            </script>
            """,
            height=100,
        )
    
    with timer_col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if not st.session_state.timer_running:
            if st.button("▶️\nStart", key="start_timer", use_container_width=True, type="primary"):
                from datetime import timezone
                st.session_state.timer_running = True
                st.session_state.start_time = datetime.now(timezone.utc)
                st.session_state.elapsed_time = 0.0
                st.session_state.recorded_time = 0.0
                st.rerun()
        else:
            if st.button("⏹️\nStop", key="stop_timer", use_container_width=True, type="primary"):
                from datetime import timezone
                st.session_state.timer_running = False
                # Compute elapsed based on start_time (server-side calculation as fallback)
                if st.session_state.start_time:
                    # Use elapsed_time which includes any accumulated time from pauses
                    server_elapsed = (datetime.now(timezone.utc) - st.session_state.start_time).total_seconds()
                    st.session_state.recorded_time = st.session_state.elapsed_time + server_elapsed
                else:
                    st.session_state.recorded_time = float(st.session_state.recorded_time or 0.0)
                st.rerun()
    
    with timer_col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if st.button("🔄\nReset", key="reset_timer", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.elapsed_time = 0.0
            st.session_state.recorded_time = 0.0
            st.rerun()
    
    # No auto-refresh needed; timer updates client-side without reruns
    
    st.markdown("---")

    # Only render Solve Details and DB-bound widgets when timer is NOT running
    if st.session_state.timer_running:
        st.subheader("Solve Details")
        st.info("Timer is running. Stop the timer to enter details and save.")
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Solve Details")

            # Input fields - use recorded time as default
            solve_time = st.number_input(
                "Solve Time (seconds)",
                min_value=0.0,
                max_value=999.99,
                value=float(st.session_state.recorded_time) if st.session_state.recorded_time > 0 else 0.0,
                step=0.01,
                format="%.2f",
                help="Enter your solving time in seconds (or use stopwatch above)"
            )

            cube_type = st.selectbox(
                "Cube Type",
                ["3x3", "2x2", "4x4", "5x5", "Pyraminx", "Megaminx", "Skewb", "Square-1"],
                help="Select the type of cube"
            )

            # Algorithm/Method selection
            st.markdown("#### Method/Algorithm Used")

            # Load existing algorithms (cached to avoid repeated DB calls during timer reruns)
            algorithms = get_algorithms_cached()
            algorithm_names = [algo['name'] for algo in algorithms] if algorithms else []

            # Create options list
            method_options = ["None", "Add new method..."] + algorithm_names

            selected_method = st.selectbox(
                "Select method",
                options=method_options,
                help="Choose the method/algorithm you used, or add a new one"
            )

            # If "Add new method" is selected, show input field
            new_method_name = None
            if selected_method == "Add new method...":
                new_method_name = st.text_input(
                    "New method name",
                    placeholder="e.g., CFOP, Roux, ZZ, Beginner's Method",
                    help="Enter the name of the method you used"
                )
                if new_method_name:
                    selected_method = new_method_name

            scramble = st.text_area(
                "Scramble",
                placeholder="R U R' U' F2 D...",
                help="Enter the scramble sequence used"
            )

            notes = st.text_area(
                "Notes (Optional)",
                placeholder="Any observations or comments about this solve...",
                help="Add any notes about this solve"
            )

        with col2:
            st.subheader("Quick Info")
            if st.session_state.player_name:
                st.info(f"**Player:** {st.session_state.player_name}")
            st.info(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
            st.info(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")

            if solve_time > 0:
                st.success(f"**Time:** {solve_time:.2f}s")

        # Submit button
        if st.button("💾 Save Solve", type="primary"):
            if solve_time > 0:
                # Determine final method name
                final_method = "None"
                if selected_method and selected_method != "None" and selected_method != "Add new method...":
                    final_method = selected_method

                    # If it's a new method, add it to algorithms
                    if new_method_name and new_method_name == selected_method:
                        algorithm = {
                            "name": new_method_name,
                            "notation": "",
                            "category": "Method",
                            "notes": f"Added from solve record on {datetime.now().strftime('%Y-%m-%d')}",
                            "date_added": datetime.now()
                        }
                        data_manager.add_algorithm(algorithm)
                        # Invalidate cached algorithms so the new one appears immediately
                        try:
                            get_algorithms_cached.clear()
                        except Exception:
                            pass

                record = {
                    "timestamp": datetime.now(),
                    "player_name": st.session_state.player_name if st.session_state.player_name else "Anonymous",
                    "time": solve_time,
                    "cube_type": cube_type,
                    "method": final_method,
                    "scramble": scramble,
                    "notes": notes
                }
                data_manager.add_solve(record)
                st.success("✅ Solve recorded successfully!")

                st.balloons()
            else:
                st.error("⚠️ Please enter a valid solve time!")

# ===== VIEW RECORDS PAGE =====
elif page == "View Records":
    st.header("📋 Your Solve Records")
    
    # Load data
    df = data_manager.load_data()
    
    if not df.empty:
        # Filters - Row 1
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Player name filter
            if 'player_name' in df.columns:
                players = df['player_name'].unique().tolist()
                player_filter = st.multiselect(
                    "Filter by Player",
                    options=players,
                    default=players
                )
            else:
                player_filter = None
        
        with col2:
            cube_filter = st.multiselect(
                "Filter by Cube Type",
                options=df['cube_type'].unique(),
                default=df['cube_type'].unique()
            )
        
        with col3:
            # Method filter
            if 'method' in df.columns:
                methods = df['method'].unique().tolist()
                method_filter = st.multiselect(
                    "Filter by Method",
                    options=methods,
                    default=methods
                )
            else:
                method_filter = None
        
        # Filters - Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            sort_options = ["timestamp", "time", "cube_type"]
            if 'player_name' in df.columns:
                sort_options.append("player_name")
            if 'method' in df.columns:
                sort_options.append("method")
            
            sort_by = st.selectbox(
                "Sort by",
                sort_options,
                index=0
            )
        
        with col2:
            sort_order = st.radio(
                "Order",
                ["Descending", "Ascending"],
                horizontal=True
            )
        
        # Filter and sort data
        filtered_df = df[df['cube_type'].isin(cube_filter)]
        if player_filter is not None and 'player_name' in df.columns:
            filtered_df = filtered_df[filtered_df['player_name'].isin(player_filter)]
        if method_filter is not None and 'method' in df.columns:
            filtered_df = filtered_df[filtered_df['method'].isin(method_filter)]
        ascending = sort_order == "Ascending"
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
        
        # Display statistics
        st.subheader("📊 Quick Stats")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Solves", len(filtered_df))
        with col2:
            st.metric("Best Time", f"{filtered_df['time'].min():.2f}s" if not filtered_df.empty else "N/A")
        with col3:
            st.metric("Average Time", f"{filtered_df['time'].mean():.2f}s" if not filtered_df.empty else "N/A")
        with col4:
            st.metric("Latest Time", f"{filtered_df.iloc[0]['time']:.2f}s" if not filtered_df.empty else "N/A")
        
        # Display table
        st.subheader("All Records")
        
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['time'] = display_df['time'].apply(lambda x: f"{x:.2f}s")
        
        # Use st.write with pandas DataFrame to avoid pyarrow dependency
        st.write(display_df.to_html(index=False), unsafe_allow_html=True)
        
        # Delete records
        if st.checkbox("Show delete options"):
            record_to_delete = st.number_input(
                "Enter row number to delete (0-based index)",
                min_value=0,
                max_value=len(filtered_df)-1,
                step=1
            )
            if st.button("🗑️ Delete Record", type="secondary"):
                data_manager.delete_solve(record_to_delete)
                st.success("Record deleted!")
                st.rerun()
    else:
        st.info("📝 No records yet. Start by recording your first solve!")

# ===== STATISTICS PAGE =====
elif page == "Statistics":
    st.header("📈 Statistics & Analysis")
    
    df = data_manager.load_data()
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Player filter
            if 'player_name' in df.columns:
                players = ["All"] + list(df['player_name'].unique())
                selected_player = st.selectbox("Select Player", players)
            else:
                selected_player = "All"
        
        with col2:
            # Cube type selector
            cube_types = ["All"] + list(df['cube_type'].unique())
            selected_cube = st.selectbox("Select Cube Type", cube_types)
        
        # Filter data
        analysis_df = df.copy()
        
        if selected_player != "All" and 'player_name' in df.columns:
            analysis_df = analysis_df[analysis_df['player_name'] == selected_player]
        
        if selected_cube != "All":
            analysis_df = analysis_df[analysis_df['cube_type'] == selected_cube]
        
        if not analysis_df.empty:
            # Statistics cards
            create_statistics_cards(analysis_df)
            
            # Time progression chart
            st.subheader("⏱️ Time Progression")
            create_time_chart(analysis_df)
            
            # Distribution by cube type
            st.subheader("🧊 Solves by Cube Type")
            cube_counts = df['cube_type'].value_counts()
            fig_cubes = go.Figure(data=[
                go.Bar(x=cube_counts.index, y=cube_counts.values, marker_color='#1f77b4')
            ])
            fig_cubes.update_layout(
                xaxis_title="Cube Type",
                yaxis_title="Number of Solves",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_cubes, use_container_width=True)
            
            # Personal records
            st.subheader("🏆 Personal Records")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Best Times by Cube Type**")
                best_times = df.groupby('cube_type')['time'].min().sort_values()
                best_times_df = best_times.apply(lambda x: f"{x:.2f}s").to_frame(name='Best Time')
                st.write(best_times_df.to_html(), unsafe_allow_html=True)
            
            with col2:
                st.write("**Average Times by Cube Type**")
                avg_times = df.groupby('cube_type')['time'].mean().sort_values()
                avg_times_df = avg_times.apply(lambda x: f"{x:.2f}s").to_frame(name='Average Time')
                st.write(avg_times_df.to_html(), unsafe_allow_html=True)
        else:
            st.warning("No data available for the selected cube type.")
    else:
        st.info("📝 No data available yet. Record some solves first!")

# ===== ALGORITHMS PAGE =====
elif page == "Algorithms":
    st.header("🧩 Algorithm Library")
    
    st.info("📚 Save and organize your favorite algorithms for different patterns")
    
    # Load algorithms
    algorithms = data_manager.load_algorithms()
    
    # Add new algorithm section
    with st.expander("➕ Add New Algorithm", expanded=False):
        algo_name = st.text_input("Pattern Name", placeholder="e.g., T-Perm, OLL 21")
        algo_notation = st.text_area("Algorithm", placeholder="R U R' U' R' F R2 U' R' U' R U R' F'")
        algo_category = st.selectbox(
            "Category",
            ["PLL", "OLL", "F2L", "CMLL", "ZBLL", "Winter Variation", "Other"]
        )
        algo_notes = st.text_area("Notes (Optional)", placeholder="Tips for execution, finger tricks, etc.")
        
        if st.button("💾 Save Algorithm"):
            if algo_name and algo_notation:
                algorithm = {
                    "name": algo_name,
                    "notation": algo_notation,
                    "category": algo_category,
                    "notes": algo_notes,
                    "date_added": datetime.now()
                }
                data_manager.add_algorithm(algorithm)
                st.success("✅ Algorithm saved!")
                st.rerun()
            else:
                st.error("⚠️ Please fill in the pattern name and algorithm!")
    
    # Display algorithms
    if algorithms:
        st.subheader("📖 Your Algorithm Library")
        
        # Filter by category
        categories = list(set([algo['category'] for algo in algorithms]))
        selected_category = st.selectbox("Filter by Category", ["All"] + categories)
        
        # Display algorithms
        for i, algo in enumerate(algorithms):
            if selected_category == "All" or algo['category'] == selected_category:
                with st.expander(f"🔹 {algo['name']} ({algo['category']})"):
                    st.code(algo['notation'], language="text")
                    if algo.get('notes'):
                        st.write("**Notes:**", algo['notes'])
                    st.caption(f"Added: {algo['date_added'].strftime('%Y-%m-%d')}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_algo_{i}"):
                        data_manager.delete_algorithm(i)
                        st.success("Algorithm deleted!")
                        st.rerun()
    else:
        st.info("No algorithms saved yet. Add your first one above!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "**Rubik's Cube Recorder** helps you track your solving progress, "
    "record your times, and organize your algorithm library. "
    "\n\nBuilt with ❤️ using Streamlit"
)
