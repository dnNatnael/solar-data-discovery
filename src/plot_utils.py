"""
Plotting utilities for Solar Data Discovery Dashboard
Provides reusable interactive Plotly plotting functions with full metric names and units.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import get_metric_full_name, get_metric_unit, get_metric_label


def create_boxplot(df: pd.DataFrame, metrics: list, title: str = "Metric Distribution Comparison") -> go.Figure:
    """
    Create an interactive boxplot for comparing metrics with full names in hover info
    
    Args:
        df: Solar dataset DataFrame
        metrics: List of metric columns to plot
        title: Plot title
        
    Returns:
        Plotly Figure object
    """
    # Sample data if dataset is large (keeps boxplot mathematically sound and fast)
    plot_df = df.sample(min(10000, len(df)), random_state=42) if len(df) > 10000 else df

    data_to_plot = []
    for metric in metrics:
        if metric in plot_df.columns:
            full_name = get_metric_full_name(metric)
            unit = get_metric_unit(metric)
            display_name = f"{metric} — {full_name}" if full_name != metric else metric
            data_to_plot.append(
                go.Box(
                    y=plot_df[metric].dropna(),
                    name=display_name,
                    boxmean='sd',  # Show mean and standard deviation
                    hovertemplate=f"<b>{metric} ({full_name})</b><br>Value: %{{y:.2f}} {unit}<extra></extra>"
                )
            )
    
    fig = go.Figure(data=data_to_plot)
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#2c3e50")),
        yaxis_title="Value",
        xaxis_title="Metric (Abbreviation & Full Name)",
        showlegend=True,
        height=520,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=80)
    )
    return fig


def create_time_series(df: pd.DataFrame, metric: str, title: str = None) -> go.Figure:
    """
    Create an interactive time series plot with full metric name and unit
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric column to plot
        title: Plot title (auto-generated if None)
        
    Returns:
        Plotly Figure object
    """
    if 'Timestamp' not in df.columns or metric not in df.columns:
        return go.Figure()
    
    full_name = get_metric_full_name(metric)
    unit = get_metric_unit(metric)
    unit_str = f" ({unit})" if unit else ""
    
    if title is None:
        title = f"{metric} — {full_name} Trends Over Time"
    
    # Downsample time series if dataset is large to maintain smooth browser performance
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
        labels={
            'Timestamp': 'Date / Time',
            metric: f"{metric} - {full_name}{unit_str}"
        }
    )
    
    fig.update_traces(
        line=dict(color='#667eea', width=1.5),
        hovertemplate=f"<b>Date/Time:</b> %{{x}}<br><b>{metric} ({full_name}):</b> %{{y:.2f}}{unit_str}<extra></extra>"
    )
    
    fig.update_layout(
        height=520,
        template="plotly_white",
        hovermode='x unified',
        title=dict(font=dict(size=18, color="#2c3e50")),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_correlation_heatmap(df: pd.DataFrame, metrics: list = None) -> go.Figure:
    """
    Create a correlation heatmap for numeric columns with clear labels
    
    Args:
        df: Solar dataset DataFrame
        metrics: List of metrics to include (if None, use all numeric columns)
        
    Returns:
        Plotly Figure object
    """
    if metrics:
        numeric_cols = [col for col in metrics if col in df.columns]
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return go.Figure()
    
    corr_matrix = df[numeric_cols].corr()
    
    # Display labels with abbreviation
    labels = [col for col in corr_matrix.columns]
    hover_texts = []
    for r in corr_matrix.index:
        row_hovers = []
        for c in corr_matrix.columns:
            r_fn = get_metric_full_name(r)
            c_fn = get_metric_full_name(c)
            val = corr_matrix.loc[r, c]
            row_hovers.append(f"<b>{r}</b> ({r_fn}) vs <b>{c}</b> ({c_fn})<br>Correlation: <b>{val:.3f}</b>")
        hover_texts.append(row_hovers)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 11},
        hoverinfo='text',
        hovertext=hover_texts,
        colorbar=dict(title="Pearson Correlation (r)")
    ))
    
    fig.update_layout(
        title=dict(text="Correlation Heatmap Matrix", font=dict(size=18, color="#2c3e50")),
        height=620,
        template="plotly_white",
        margin=dict(l=50, r=50, t=60, b=50)
    )
    return fig


def create_scatter_plot(df: pd.DataFrame, x_metric: str, y_metric: str, 
                       color_metric: str = None) -> go.Figure:
    """
    Create an interactive scatter plot with full metric names
    
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
    
    plot_df = df.sample(min(3000, len(df)), random_state=42) if len(df) > 3000 else df
    
    x_fn = get_metric_full_name(x_metric)
    y_fn = get_metric_full_name(y_metric)
    x_unit = f" ({get_metric_unit(x_metric)})" if get_metric_unit(x_metric) else ""
    y_unit = f" ({get_metric_unit(y_metric)})" if get_metric_unit(y_metric) else ""
    
    title = f"{y_metric} ({y_fn}) vs {x_metric} ({x_fn})"
    labels = {
        x_metric: f"{x_metric} — {x_fn}{x_unit}",
        y_metric: f"{y_metric} — {y_fn}{y_unit}"
    }
    
    if color_metric and color_metric in df.columns:
        c_fn = get_metric_full_name(color_metric)
        labels[color_metric] = f"{color_metric} — {c_fn}"
        fig = px.scatter(
            plot_df, 
            x=x_metric, 
            y=y_metric,
            color=color_metric,
            title=title,
            labels=labels,
            opacity=0.6,
            color_continuous_scale="Viridis"
        )
    else:
        fig = px.scatter(
            plot_df, 
            x=x_metric, 
            y=y_metric,
            title=title,
            labels=labels,
            opacity=0.6
        )
        fig.update_traces(marker=dict(color='#667eea'))
    
    fig.update_layout(
        height=520,
        template="plotly_white",
        title=dict(font=dict(size=18, color="#2c3e50")),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_bubble_chart(df: pd.DataFrame, x_metric: str, y_metric: str, 
                       size_metric: str, color_metric: str = None) -> go.Figure:
    """
    Create an interactive multi-dimensional bubble chart
    
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
    
    plot_df = df.sample(min(1200, len(df)), random_state=42) if len(df) > 1200 else df
    
    # Ensure positive size values for bubbles
    plot_df = plot_df.copy()
    plot_df['size_col'] = plot_df[size_metric].clip(lower=0) + 0.1
    
    x_fn = get_metric_full_name(x_metric)
    y_fn = get_metric_full_name(y_metric)
    s_fn = get_metric_full_name(size_metric)
    
    title = f"Bubble Analysis: {y_metric} vs {x_metric} (Size: {size_metric} - {s_fn})"
    labels = {
        x_metric: f"{x_metric} ({x_fn})",
        y_metric: f"{y_metric} ({y_fn})",
        'size_col': f"Bubble Size: {size_metric}"
    }
    
    if color_metric and color_metric in df.columns:
        c_fn = get_metric_full_name(color_metric)
        labels[color_metric] = f"{color_metric} ({c_fn})"
        fig = px.scatter(
            plot_df,
            x=x_metric,
            y=y_metric,
            size='size_col',
            color=color_metric,
            title=title,
            labels=labels,
            opacity=0.65,
            size_max=32,
            color_continuous_scale="Plasma"
        )
    else:
        fig = px.scatter(
            plot_df,
            x=x_metric,
            y=y_metric,
            size='size_col',
            title=title,
            labels=labels,
            opacity=0.65,
            size_max=32
        )
        fig.update_traces(marker=dict(color='#764ba2'))
    
    fig.update_layout(
        height=520,
        template="plotly_white",
        title=dict(font=dict(size=18, color="#2c3e50")),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_wind_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create wind speed and gust distribution comparison
    
    Args:
        df: Solar dataset DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'WS' not in df.columns:
        return go.Figure()
    
    plot_df = df.sample(min(20000, len(df)), random_state=42) if len(df) > 20000 else df

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=plot_df['WS'].dropna(),
        nbinsx=50,
        name='WS — Wind Speed (m/s)',
        marker_color='#667eea',
        opacity=0.7
    ))
    
    if 'WSgust' in plot_df.columns:
        fig.add_trace(go.Histogram(
            x=plot_df['WSgust'].dropna(),
            nbinsx=50,
            name='WSgust — Wind Gust Speed (m/s)',
            marker_color='#e67e22',
            opacity=0.65
        ))
    
    fig.update_layout(
        title=dict(text="Wind Speed & Gust Velocity Distributions", font=dict(size=18, color="#2c3e50")),
        xaxis_title="Velocity (m/s)",
        yaxis_title="Observation Frequency",
        barmode='overlay',
        height=520,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_hourly_pattern(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create diurnal hourly pattern plot showing 24-hour mean profile
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric to analyze
        
    Returns:
        Plotly Figure object
    """
    if 'Timestamp' not in df.columns or metric not in df.columns:
        return go.Figure()
    
    full_name = get_metric_full_name(metric)
    unit = get_metric_unit(metric)
    unit_str = f" ({unit})" if unit else ""
    
    hourly_avg = df.groupby(df['Timestamp'].dt.hour)[metric].mean().reset_index()
    hourly_avg.columns = ['Hour', metric]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],
        y=hourly_avg[metric],
        mode='lines+markers',
        name=f"{metric} — {full_name}",
        line=dict(color='#667eea', width=2.5),
        marker=dict(size=8, color='#764ba2'),
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Mean %{y:.2f}" + unit_str + "</b><extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text=f"Diurnal Hourly Profile: {metric} — {full_name}", font=dict(size=18, color="#2c3e50")),
        xaxis_title="Hour of Day (00:00 - 23:00)",
        yaxis_title=f"Mean {metric}{unit_str}",
        height=520,
        template="plotly_white",
        xaxis=dict(tickmode='linear', tick0=0, dtick=1, range=[-0.5, 23.5]),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_monthly_pattern(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create seasonal monthly pattern plot showing annual profile
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric to analyze
        
    Returns:
        Plotly Figure object
    """
    if 'Timestamp' not in df.columns or metric not in df.columns:
        return go.Figure()
    
    full_name = get_metric_full_name(metric)
    unit = get_metric_unit(metric)
    unit_str = f" ({unit})" if unit else ""
    
    monthly_avg = df.groupby(df['Timestamp'].dt.month)[metric].mean().reset_index()
    monthly_avg.columns = ['Month', metric]
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg['MonthName'] = monthly_avg['Month'].apply(lambda x: month_names[int(x)-1])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_avg['MonthName'],
        y=monthly_avg[metric],
        name=f"{metric} — {full_name}",
        marker=dict(
            color=monthly_avg[metric],
            colorscale='Purples',
            line=dict(color='#667eea', width=1.5)
        ),
        hovertemplate="<b>%{x}:</b> %{y:.2f}" + unit_str + "<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text=f"Seasonal Monthly Profile: {metric} — {full_name}", font=dict(size=18, color="#2c3e50")),
        xaxis_title="Month",
        yaxis_title=f"Mean {metric}{unit_str}",
        height=520,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_distribution_plot(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create distribution histogram plot with density
    
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
    
    full_name = get_metric_full_name(metric)
    unit = get_metric_unit(metric)
    unit_str = f" ({unit})" if unit else ""
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data,
        nbinsx=50,
        name=f"{metric} — {full_name}",
        marker_color='#667eea',
        opacity=0.75,
        histnorm='probability density'
    ))
    
    fig.update_layout(
        title=dict(text=f"Statistical Distribution: {metric} — {full_name}", font=dict(size=18, color="#2c3e50")),
        xaxis_title=f"{metric} — {full_name}{unit_str}",
        yaxis_title="Probability Density",
        height=520,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig
