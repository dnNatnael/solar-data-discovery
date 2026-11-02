"""
Plotting utilities for Solar Challenge Dashboard
Provides reusable plotting functions for data visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


# Set styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def create_boxplot(df: pd.DataFrame, metrics: list, title: str = "Metric Comparison") -> go.Figure:
    """
    Create an interactive boxplot for comparing metrics
    
    Args:
        df: Solar dataset DataFrame
        metrics: List of metric columns to plot
        title: Plot title
        
    Returns:
        Plotly Figure object
    """
    # Sample data if dataset is large (keeps boxplot mathematically sound and ultra-fast)
    plot_df = df.sample(min(10000, len(df)), random_state=42) if len(df) > 10000 else df

    # Prepare data for plotting
    data_to_plot = []
    
    for metric in metrics:
        if metric in plot_df.columns:
            data_to_plot.append(
                go.Box(
                    y=plot_df[metric].dropna(),
                    name=metric,
                    boxmean='sd'  # Show mean and standard deviation
                )
            )
    
    fig = go.Figure(data=data_to_plot)
    
    fig.update_layout(
        title=title,
        yaxis_title="Value",
        xaxis_title="Metric",
        showlegend=True,
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_time_series(df: pd.DataFrame, metric: str, title: str = None) -> go.Figure:
    """
    Create an interactive time series plot
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric column to plot
        title: Plot title (auto-generated if None)
        
    Returns:
        Plotly Figure object
    """
    if 'Timestamp' not in df.columns or metric not in df.columns:
        return go.Figure()
    
    if title is None:
        title = f"{metric} Over Time"
    
    # Downsample time series if dataset is large to prevent browser freeze and heavy payloads
    if len(df) > 3000:
        step = max(1, len(df) // 3000)
        plot_df = df.iloc[::step]
    else:
        plot_df = df

    fig = px.line(
        plot_df, 
        x='Timestamp', 
        y=metric,
        title=title,
        labels={'Timestamp': 'Date/Time', metric: f'{metric} Value'}
    )
    
    fig.update_traces(line=dict(color='#1f77b4', width=1.5))
    
    fig.update_layout(
        height=500,
        template="plotly_white",
        hovermode='x unified'
    )
    
    return fig


def create_correlation_heatmap(df: pd.DataFrame, metrics: list = None) -> go.Figure:
    """
    Create a correlation heatmap for numeric columns
    
    Args:
        df: Solar dataset DataFrame
        metrics: List of metrics to include (if None, use all numeric columns)
        
    Returns:
        Plotly Figure object
    """
    if metrics:
        # Filter to only specified metrics that exist
        numeric_cols = [col for col in metrics if col in df.columns]
    else:
        # Use all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return go.Figure()
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Heatmap",
        height=600,
        template="plotly_white"
    )
    
    return fig


def create_scatter_plot(df: pd.DataFrame, x_metric: str, y_metric: str, 
                       color_metric: str = None) -> go.Figure:
    """
    Create an interactive scatter plot
    
    Args:
        df: Solar dataset DataFrame
        x_metric: Metric for x-axis
        y_metric: Metric for y-axis
        color_metric: Optional metric for color coding
        
    Returns:
        Plotly Figure object
    """
    if x_metric not in df.columns or y_metric not in df.columns:
        return go.Figure()
    
    # Sample data to avoid freezing browser with massive point counts
    plot_df = df.sample(min(3000, len(df)), random_state=42) if len(df) > 3000 else df
    
    if color_metric and color_metric in df.columns:
        fig = px.scatter(
            plot_df, 
            x=x_metric, 
            y=y_metric,
            color=color_metric,
            title=f"{y_metric} vs {x_metric}",
            labels={x_metric: x_metric, y_metric: y_metric},
            opacity=0.6
        )
    else:
        fig = px.scatter(
            plot_df, 
            x=x_metric, 
            y=y_metric,
            title=f"{y_metric} vs {x_metric}",
            labels={x_metric: x_metric, y_metric: y_metric},
            opacity=0.6
        )
    
    fig.update_layout(
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_bubble_chart(df: pd.DataFrame, x_metric: str, y_metric: str, 
                       size_metric: str, color_metric: str = None) -> go.Figure:
    """
    Create an interactive bubble chart
    
    Args:
        df: Solar dataset DataFrame
        x_metric: Metric for x-axis
        y_metric: Metric for y-axis
        size_metric: Metric for bubble size
        color_metric: Optional metric for color coding
        
    Returns:
        Plotly Figure object
    """
    required_cols = [x_metric, y_metric, size_metric]
    if not all(col in df.columns for col in required_cols):
        return go.Figure()
    
    # Sample data if too large for performance
    plot_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df
    
    if color_metric and color_metric in df.columns:
        fig = px.scatter(
            plot_df,
            x=x_metric,
            y=y_metric,
            size=size_metric,
            color=color_metric,
            title=f"Bubble Chart: {y_metric} vs {x_metric}",
            labels={x_metric: x_metric, y_metric: y_metric},
            opacity=0.6,
            size_max=30
        )
    else:
        fig = px.scatter(
            plot_df,
            x=x_metric,
            y=y_metric,
            size=size_metric,
            title=f"Bubble Chart: {y_metric} vs {x_metric}",
            labels={x_metric: x_metric, y_metric: y_metric},
            opacity=0.6,
            size_max=30
        )
    
    fig.update_layout(
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_wind_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create wind speed distribution plot
    
    Args:
        df: Solar dataset DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'WS' not in df.columns:
        return go.Figure()
    
    # Sample if large dataset to keep histogram rendering snappy
    plot_df = df.sample(min(20000, len(df)), random_state=42) if len(df) > 20000 else df

    # Create histogram
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=plot_df['WS'].dropna(),
        nbinsx=50,
        name='Wind Speed',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    if 'WSgust' in plot_df.columns:
        fig.add_trace(go.Histogram(
            x=plot_df['WSgust'].dropna(),
            nbinsx=50,
            name='Wind Gust',
            marker_color='orange',
            opacity=0.7
        ))
    
    fig.update_layout(
        title="Wind Speed Distribution",
        xaxis_title="Wind Speed (m/s)",
        yaxis_title="Frequency",
        barmode='overlay',
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_hourly_pattern(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create hourly pattern plot showing average values by hour of day
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric to analyze
        
    Returns:
        Plotly Figure object
    """
    if 'Timestamp' not in df.columns or metric not in df.columns:
        return go.Figure()
    
    # Calculate hourly averages directly without expensive full-dataframe copy
    hourly_avg = df.groupby(df['Timestamp'].dt.hour)[metric].mean().reset_index()
    hourly_avg.columns = ['Hour', metric]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],
        y=hourly_avg[metric],
        mode='lines+markers',
        name=metric,
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"Average {metric} by Hour of Day",
        xaxis_title="Hour of Day",
        yaxis_title=f"Average {metric}",
        height=500,
        template="plotly_white",
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )
    
    return fig


def create_monthly_pattern(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create monthly pattern plot showing average values by month
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric to analyze
        
    Returns:
        Plotly Figure object
    """
    if 'Timestamp' not in df.columns or metric not in df.columns:
        return go.Figure()
    
    # Calculate monthly averages directly without expensive full-dataframe copy
    monthly_avg = df.groupby(df['Timestamp'].dt.month)[metric].mean().reset_index()
    monthly_avg.columns = ['Month', metric]
    
    # Month names for better labeling
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg['MonthName'] = monthly_avg['Month'].apply(lambda x: month_names[int(x)-1])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_avg['MonthName'],
        y=monthly_avg[metric],
        name=metric,
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title=f"Average {metric} by Month",
        xaxis_title="Month",
        yaxis_title=f"Average {metric}",
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_distribution_plot(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create distribution plot (histogram with KDE)
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric to analyze
        
    Returns:
        Plotly Figure object
    """
    if metric not in df.columns:
        return go.Figure()
    
    data = df[metric].dropna()
    if len(data) > 20000:
        data = data.sample(20000, random_state=42)
    
    fig = go.Figure()
    
    # Add histogram
    fig.add_trace(go.Histogram(
        x=data,
        nbinsx=50,
        name='Distribution',
        marker_color='lightblue',
        opacity=0.7,
        histnorm='probability density'
    ))
    
    fig.update_layout(
        title=f"{metric} Distribution",
        xaxis_title=metric,
        yaxis_title="Density",
        height=500,
        template="plotly_white"
    )
    
    return fig
