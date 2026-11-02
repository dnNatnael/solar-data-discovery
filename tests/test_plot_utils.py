"""
Unit tests for plotting functions with metric abbreviations and full descriptive text
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.plot_utils import (
    create_boxplot,
    create_time_series,
    create_correlation_heatmap,
    create_scatter_plot,
    create_bubble_chart,
    create_wind_distribution,
    create_hourly_pattern,
    create_monthly_pattern,
    create_distribution_plot
)


@pytest.fixture
def sample_solar_df():
    """Create a sample solar dataframe for testing plots."""
    dates = pd.date_range('2023-01-01', periods=48, freq='h')
    df = pd.DataFrame({
        'Timestamp': dates,
        'GHI': np.linspace(0, 800, 48),
        'DNI': np.linspace(0, 900, 48),
        'DHI': np.linspace(0, 200, 48),
        'Tamb': np.linspace(20, 35, 48),
        'RH': np.linspace(40, 80, 48),
        'WS': np.linspace(1, 10, 48),
        'WSgust': np.linspace(2, 15, 48)
    })
    return df


def test_create_boxplot(sample_solar_df):
    """Test creating boxplot with full metric name labels."""
    fig = create_boxplot(sample_solar_df, ['GHI', 'Tamb'])
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    # Verify full name appears in boxplot trace names
    trace_names = [trace.name for trace in fig.data]
    assert any('Global Horizontal Irradiance' in name for name in trace_names)


def test_create_time_series(sample_solar_df):
    """Test creating time series with full metric title and labels."""
    fig = create_time_series(sample_solar_df, 'GHI')
    assert isinstance(fig, go.Figure)
    assert 'GHI' in fig.layout.title.text
    assert 'Global Horizontal Irradiance' in fig.layout.title.text


def test_create_correlation_heatmap(sample_solar_df):
    """Test creating correlation heatmap."""
    fig = create_correlation_heatmap(sample_solar_df, ['GHI', 'DNI', 'Tamb'])
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == 'heatmap'


def test_create_scatter_plot(sample_solar_df):
    """Test creating scatter plot with full names."""
    fig = create_scatter_plot(sample_solar_df, 'GHI', 'Tamb', color_metric='WS')
    assert isinstance(fig, go.Figure)
    assert 'Tamb' in fig.layout.title.text
    assert 'GHI' in fig.layout.title.text


def test_create_bubble_chart(sample_solar_df):
    """Test creating multi-dimensional bubble chart."""
    fig = create_bubble_chart(sample_solar_df, 'GHI', 'Tamb', size_metric='WS', color_metric='RH')
    assert isinstance(fig, go.Figure)


def test_create_wind_distribution(sample_solar_df):
    """Test creating wind speed and gust distribution."""
    fig = create_wind_distribution(sample_solar_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_create_hourly_pattern(sample_solar_df):
    """Test creating diurnal hourly pattern."""
    fig = create_hourly_pattern(sample_solar_df, 'GHI')
    assert isinstance(fig, go.Figure)
    assert 'Hourly' in fig.layout.title.text or 'Diurnal' in fig.layout.title.text


def test_create_monthly_pattern(sample_solar_df):
    """Test creating seasonal monthly pattern."""
    fig = create_monthly_pattern(sample_solar_df, 'GHI')
    assert isinstance(fig, go.Figure)
    assert 'Monthly' in fig.layout.title.text or 'Seasonal' in fig.layout.title.text


def test_create_distribution_plot(sample_solar_df):
    """Test creating distribution plot."""
    fig = create_distribution_plot(sample_solar_df, 'GHI')
    assert isinstance(fig, go.Figure)
    assert 'GHI' in fig.layout.title.text

