"""
Data loading utilities for Solar Challenge Dashboard
Provides functions to load and validate solar dataset CSV files
"""

import pandas as pd
import os
from pathlib import Path
from typing import Optional, Tuple


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate if the file exists and is a CSV file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "No file path provided"
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File does not exist: {file_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    if path.suffix.lower() not in ['.csv', '.txt']:
        return False, f"File must be a CSV file, got: {path.suffix}"
    
    return True, ""


def standardize_solar_dataframe(df: pd.DataFrame, parse_dates: bool = True) -> pd.DataFrame:
    """
    Standardize timestamp column names and parse dates to support any solar dataset
    
    Args:
        df: Input DataFrame
        parse_dates: Whether to parse the timestamp column as datetime
        
    Returns:
        Standardized DataFrame
    """
    df = df.copy()
    
    # Auto-detect timestamp column if 'Timestamp' is not directly present
    if 'Timestamp' not in df.columns:
        date_candidates = ['timestamp', 'datetime', 'date_time', 'date', 'time', 'dt', 'Date', 'DateTime', 'Time']
        for col in date_candidates:
            if col in df.columns:
                df = df.rename(columns={col: 'Timestamp'})
                break
    
    # Parse timestamp if it exists and parse_dates is True
    if parse_dates and 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    
    return df


def load_solar_data(file_path: str, parse_dates: bool = True) -> Optional[pd.DataFrame]:
    """
    Load solar dataset from CSV file with proper parsing
    
    Args:
        file_path: Path to the CSV file
        parse_dates: Whether to parse the Timestamp column as datetime
        
    Returns:
        DataFrame with solar data, or None if loading fails
    """
    is_valid, error_msg = validate_file_path(file_path)
    
    if not is_valid:
        raise FileNotFoundError(error_msg)
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        return standardize_solar_dataframe(df, parse_dates=parse_dates)
    
    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")


def get_available_metrics(df: pd.DataFrame) -> list:
    """
    Get list of available numeric metrics from the dataframe.
    Prioritizes standard solar metrics first, and automatically includes
    any other numeric measurement columns so any CSV can be analyzed.
    
    Args:
        df: Solar dataset DataFrame
        
    Returns:
        List of metric column names
    """
    # Standard solar metrics
    priority_metrics = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS', 'WSgust', 
                        'ModA', 'ModB', 'BP', 'Precipitation']
    
    # Priority columns present in dataframe
    available = [col for col in priority_metrics if col in df.columns]
    
    # Also discover any other numeric metrics (e.g., from other weather stations or countries)
    ignored_cols = {'id', 'index', 'unnamed: 0', 'year', 'month', 'day', 'hour'}
    other_numeric = [
        col for col in df.select_dtypes(include=['number']).columns 
        if col not in available and col.lower() not in ignored_cols
    ]
    
    return available + other_numeric


def get_date_range(df: pd.DataFrame) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """
    Get the date range from the dataset
    
    Args:
        df: Solar dataset DataFrame
        
    Returns:
        Tuple of (min_date, max_date)
    """
    if 'Timestamp' not in df.columns:
        return None, None
    
    try:
        min_date = df['Timestamp'].min()
        max_date = df['Timestamp'].max()
        return min_date, max_date
    except:
        return None, None


def filter_by_date_range(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    """
    Filter dataframe by date range
    
    Args:
        df: Solar dataset DataFrame
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        Filtered DataFrame
    """
    if 'Timestamp' not in df.columns:
        return df
    
    mask = (df['Timestamp'] >= pd.to_datetime(start_date)) & \
           (df['Timestamp'] <= pd.to_datetime(end_date))
    
    return df[mask]


def get_summary_statistics(df: pd.DataFrame, metrics: list) -> pd.DataFrame:
    """
    Calculate summary statistics for selected metrics
    
    Args:
        df: Solar dataset DataFrame
        metrics: List of metric columns to analyze
        
    Returns:
        DataFrame with summary statistics
    """
    stats_dict = {}
    
    for metric in metrics:
        if metric in df.columns:
            stats_dict[metric] = {
                'Mean': df[metric].mean(),
                'Median': df[metric].median(),
                'Std Dev': df[metric].std(),
                'Min': df[metric].min(),
                'Max': df[metric].max(),
                'Count': df[metric].count()
            }
    
    stats_df = pd.DataFrame(stats_dict).T
    return stats_df


def get_top_hours(df: pd.DataFrame, metric: str, top_n: int = 10) -> pd.DataFrame:
    """
    Get top N hours with highest values for a given metric
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric column to analyze
        top_n: Number of top records to return
        
    Returns:
        DataFrame with top N records
    """
    if metric not in df.columns or 'Timestamp' not in df.columns:
        return pd.DataFrame()
    
    top_df = df.nlargest(top_n, metric)[['Timestamp', metric]].copy()
    top_df.reset_index(drop=True, inplace=True)
    
    return top_df
