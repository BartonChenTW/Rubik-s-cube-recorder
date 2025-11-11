"""
Visualization utilities for Rubik's Cube Recorder
Creates charts and visual statistics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def create_time_chart(df):
    """
    Create a line chart showing solve times over time
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
    """
    if df.empty:
        st.info("No data to display")
        return
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Create the figure
    fig = go.Figure()
    
    # Add the main time series line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['time'],
        mode='lines+markers',
        name='Solve Time',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=6)
    ))
    
    # Add moving average if enough data
    if len(df) >= 5:
        df['ma5'] = df['time'].rolling(window=5, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ma5'],
            mode='lines',
            name='5-solve Moving Average',
            line=dict(color='#4ECDC4', width=2, dash='dash')
        ))
    
    # Add personal best line
    pb = df['time'].min()
    fig.add_hline(
        y=pb,
        line_dash="dot",
        line_color="green",
        annotation_text=f"Personal Best: {pb:.2f}s",
        annotation_position="right"
    )
    
    # Update layout
    fig.update_layout(
        title="Solve Time Progression",
        xaxis_title="Date",
        yaxis_title="Time (seconds)",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_statistics_cards(df):
    """
    Create metric cards showing key statistics
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
    """
    if df.empty:
        st.info("No data available")
        return
    
    times = df['time'].values
    
    # Calculate statistics
    best_time = times.min()
    worst_time = times.max()
    avg_time = times.mean()
    median_time = pd.Series(times).median()
    
    # Calculate Ao5, Ao12, Ao100
    ao5 = calculate_average_of(times, 5)
    ao12 = calculate_average_of(times, 12)
    ao100 = calculate_average_of(times, 100)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏆 Personal Best",
            value=f"{best_time:.2f}s",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📊 Average",
            value=f"{avg_time:.2f}s",
            delta=f"{avg_time - best_time:.2f}s" if best_time else None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="📈 Median",
            value=f"{median_time:.2f}s"
        )
    
    with col4:
        st.metric(
            label="📉 Worst",
            value=f"{worst_time:.2f}s"
        )
    
    # Second row - Averages
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Ao5",
            value=f"{ao5:.2f}s" if ao5 else "N/A"
        )
    
    with col2:
        st.metric(
            label="Ao12",
            value=f"{ao12:.2f}s" if ao12 else "N/A"
        )
    
    with col3:
        st.metric(
            label="Ao100",
            value=f"{ao100:.2f}s" if ao100 else "N/A"
        )
    
    with col4:
        st.metric(
            label="Total Solves",
            value=f"{len(times)}"
        )


def calculate_average_of(times, n):
    """
    Calculate average of n (removing best and worst)
    
    Args:
        times (array): Array of times
        n (int): Number of solves to average
    
    Returns:
        float: Average time, or None if not enough data
    """
    if len(times) < n:
        return None
    
    last_n = times[-n:]
    # Remove best and worst
    trimmed = sorted(last_n)[1:-1]
    return float(sum(trimmed) / len(trimmed))


def create_distribution_chart(df):
    """
    Create a histogram showing the distribution of solve times
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
    """
    if df.empty:
        st.info("No data to display")
        return
    
    fig = px.histogram(
        df,
        x='time',
        nbins=30,
        title='Distribution of Solve Times',
        labels={'time': 'Time (seconds)', 'count': 'Frequency'},
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Time (seconds)",
        yaxis_title="Number of Solves"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_cube_type_comparison(df):
    """
    Create a box plot comparing times across different cube types
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
    """
    if df.empty:
        st.info("No data to display")
        return
    
    fig = px.box(
        df,
        x='cube_type',
        y='time',
        title='Solve Times by Cube Type',
        labels={'cube_type': 'Cube Type', 'time': 'Time (seconds)'},
        color='cube_type',
        points="all"
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Cube Type",
        yaxis_title="Time (seconds)"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_progress_heatmap(df):
    """
    Create a heatmap showing solve activity over time
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
    """
    if df.empty:
        st.info("No data to display")
        return
    
    # Extract date and create daily aggregation
    df = df.copy()
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_counts = df.groupby('date').size().reset_index(name='count')
    
    # Create calendar heatmap data
    fig = px.density_heatmap(
        daily_counts,
        x='date',
        y=[1] * len(daily_counts),  # Single row
        z='count',
        title='Solve Activity Calendar',
        color_continuous_scale='Reds',
        labels={'count': 'Solves'}
    )
    
    fig.update_layout(
        showlegend=True,
        height=200,
        yaxis=dict(visible=False),
        xaxis_title="Date"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_improvement_chart(df):
    """
    Create a chart showing improvement over time (rolling averages)
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
    """
    if df.empty or len(df) < 5:
        st.info("Need at least 5 solves to show improvement trend")
        return
    
    df = df.sort_values('timestamp').copy()
    
    # Calculate rolling averages
    df['ao5'] = df['time'].rolling(window=5, min_periods=5).apply(
        lambda x: sorted(x)[1:-1].mean() if len(x) >= 5 else None
    )
    
    if len(df) >= 12:
        df['ao12'] = df['time'].rolling(window=12, min_periods=12).apply(
            lambda x: sorted(x)[1:-1].mean() if len(x) >= 12 else None
        )
    
    # Create figure
    fig = go.Figure()
    
    # Add Ao5
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['ao5'],
        mode='lines',
        name='Ao5',
        line=dict(color='#FF6B6B', width=2)
    ))
    
    # Add Ao12 if available
    if 'ao12' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ao12'],
            mode='lines',
            name='Ao12',
            line=dict(color='#4ECDC4', width=2)
        ))
    
    fig.update_layout(
        title="Improvement Trend (Rolling Averages)",
        xaxis_title="Date",
        yaxis_title="Time (seconds)",
        hovermode='x unified',
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_session_stats(df, session_duration_minutes=60):
    """
    Display statistics for the current solving session
    
    Args:
        df (pd.DataFrame): DataFrame containing solve records
        session_duration_minutes (int): Duration to consider as current session
    """
    if df.empty:
        st.info("No solves in current session")
        return
    
    # Get recent solves within session duration
    cutoff_time = datetime.now() - timedelta(minutes=session_duration_minutes)
    session_df = df[pd.to_datetime(df['timestamp']) >= cutoff_time]
    
    if session_df.empty:
        st.info(f"No solves in the last {session_duration_minutes} minutes")
        return
    
    st.subheader(f"Current Session ({len(session_df)} solves)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Session Best", f"{session_df['time'].min():.2f}s")
    
    with col2:
        st.metric("Session Average", f"{session_df['time'].mean():.2f}s")
    
    with col3:
        st.metric("Session Solves", len(session_df))
