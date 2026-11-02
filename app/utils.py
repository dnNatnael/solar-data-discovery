"""
App utilities for Solar Data Discovery Dashboard
Re-exports core functions from src.data_loader and src.plot_utils
"""

from src.data_loader import (
    load_solar_data,
    standardize_solar_dataframe,
    get_available_metrics,
    get_date_range,
    filter_by_date_range,
    get_summary_statistics,
    get_top_hours,
    read_csv_flexible,
    discover_local_csv_files,
    get_metric_full_name,
    get_metric_unit,
    get_metric_category,
    get_metric_description,
    get_metric_label,
    get_glossary_dataframe,
    METRIC_GLOSSARY,
    GENERAL_SOLAR_TERMS,
    METRIC_ALIASES
)

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

