"""
Unit tests for data loader, glossary, and universal CSV parsing utilities
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data_loader import (
    validate_file_path,
    standardize_solar_dataframe,
    load_solar_data,
    get_available_metrics,
    get_date_range,
    filter_by_date_range,
    get_summary_statistics,
    get_top_hours,
    discover_local_csv_files,
    get_metric_full_name,
    get_metric_unit,
    get_metric_label,
    get_glossary_dataframe,
    read_csv_flexible,
    METRIC_GLOSSARY,
    GENERAL_SOLAR_TERMS
)


def test_metric_glossary_coverage():
    """Verify that core solar metrics and abbreviations have full names and units defined."""
    core_metrics = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS', 'WSgust', 'BP', 'Precipitation', 'ModA', 'ModB', 'TModA', 'TModB']
    for m in core_metrics:
        assert m in METRIC_GLOSSARY
        assert 'full_name' in METRIC_GLOSSARY[m]
        assert 'unit' in METRIC_GLOSSARY[m]
        assert 'description' in METRIC_GLOSSARY[m]
        assert get_metric_full_name(m) != m
        assert len(get_metric_unit(m)) > 0


def test_get_metric_label():
    """Verify get_metric_label formats abbreviation and full name properly."""
    label_ghi = get_metric_label('GHI')
    assert 'GHI' in label_ghi
    assert 'Global Horizontal Irradiance' in label_ghi
    assert 'W/m²' in label_ghi

    # Unknown metric should fall back to its own name
    assert get_metric_label('custom_sensor_1') == 'custom_sensor_1'


def test_get_glossary_dataframe():
    """Verify glossary dataframe contains expected columns and rows."""
    df_glossary = get_glossary_dataframe(include_general_terms=True)
    assert not df_glossary.empty
    assert set(['Abbreviation', 'Full Name', 'Unit', 'Category', 'Description']).issubset(df_glossary.columns)
    assert 'GHI' in df_glossary['Abbreviation'].values
    assert 'POA' in df_glossary['Abbreviation'].values


def test_validate_file_path(tmp_path):
    """Test file path validation with valid and invalid paths."""
    is_valid, msg = validate_file_path("")
    assert not is_valid

    is_valid, msg = validate_file_path("non_existent_file.csv")
    assert not is_valid

    # Create dummy csv
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("Timestamp,GHI\n2023-01-01 00:00:00,100\n")
    is_valid, msg = validate_file_path(str(csv_file))
    assert is_valid
    assert msg == ""


def test_standardize_solar_dataframe_with_custom_columns():
    """Test standardizing a custom CSV from an arbitrary country/provider."""
    # Test lowercase columns and alternative date column name
    custom_df = pd.DataFrame({
        'date_time': ['2023-01-01 10:00:00', '2023-01-01 11:00:00'],
        'ghi': [450.2, 560.8],
        'temp': [28.4, 29.1],
        'humidity': [45.0, 42.0],
        'wind_speed': [3.5, 4.1],
        'inverter_power_kw': [4.2, 5.1]
    })
    
    std_df = standardize_solar_dataframe(custom_df)
    assert 'Timestamp' in std_df.columns
    assert pd.api.types.is_datetime64_any_dtype(std_df['Timestamp'])
    assert 'GHI' in std_df.columns
    assert 'Tamb' in std_df.columns
    assert 'RH' in std_df.columns
    assert 'WS' in std_df.columns
    assert 'inverter_power_kw' in std_df.columns


def test_standardize_solar_dataframe_separate_ymd():
    """Test handling datasets with separate Year, Month, Day, Hour columns."""
    df_ymd = pd.DataFrame({
        'year': [2023, 2023],
        'month': [5, 5],
        'day': [12, 12],
        'hour': [12, 13],
        'GHI': [800.0, 850.0]
    })
    std_df = standardize_solar_dataframe(df_ymd)
    assert 'Timestamp' in std_df.columns
    assert std_df['Timestamp'].iloc[0] == pd.Timestamp('2023-05-12 12:00:00')


def test_read_csv_flexible_semicolon(tmp_path):
    """Test reading European semicolon-delimited CSV files."""
    csv_file = tmp_path / "european_solar.csv"
    csv_file.write_text("timestamp;GHI;Tamb\n2023-01-01 12:00:00;500.5;24.2\n")
    
    df = read_csv_flexible(str(csv_file))
    assert 'GHI' in df.columns
    assert 'Tamb' in df.columns
    assert len(df) == 1


def test_get_available_metrics():
    """Test dynamic metric discovery with both standard and custom metrics."""
    df = pd.DataFrame({
        'Timestamp': pd.date_range('2023-01-01', periods=3, freq='h'),
        'GHI': [100.0, 200.0, 300.0],
        'Tamb': [20.0, 21.0, 22.0],
        'custom_lux': [1200.0, 2500.0, 3100.0],
        'Comments': [np.nan, np.nan, np.nan],  # All NaN comments should be filtered
        'id': [1, 2, 3]  # id should be ignored
    })
    
    metrics = get_available_metrics(df)
    assert 'GHI' in metrics
    assert 'Tamb' in metrics
    assert 'custom_lux' in metrics
    assert 'Comments' not in metrics
    assert 'id' not in metrics


def test_get_summary_statistics():
    """Test calculation of summary statistics."""
    df = pd.DataFrame({
        'GHI': [100.0, 200.0, 300.0],
        'Tamb': [10.0, 20.0, 30.0]
    })
    summary = get_summary_statistics(df, ['GHI', 'Tamb'])
    assert 'Mean' in summary.columns
    assert summary.loc['GHI', 'Mean'] == 200.0
    assert summary.loc['Tamb', 'Mean'] == 20.0


def test_filter_by_date_range():
    """Test date range filtering."""
    df = pd.DataFrame({
        'Timestamp': pd.date_range('2023-01-01', periods=5, freq='D'),
        'GHI': [10, 20, 30, 40, 50]
    })
    filtered = filter_by_date_range(df, '2023-01-02', '2023-01-04')
    assert len(filtered) == 3


def test_discover_local_csv_files():
    """Test local CSV file discovery in data directory."""
    files = discover_local_csv_files("data")
    assert isinstance(files, list)
    assert len(files) >= 3  # Benin, Sierra Leone, Togo
    assert any('benin' in f for f in files)

