# 📊 Solar Challenge Dashboard - Technical Documentation

## Overview

This document provides detailed technical information about the Streamlit dashboard implementation for the Solar Challenge Week 0 project.

## Architecture

### Component Structure

```
Dashboard Architecture
├── app/main.py                 # Main Streamlit application
├── src/data_loader.py          # Data loading & preprocessing
├── src/plot_utils.py           # Visualization functions
└── .streamlit/config.toml      # Streamlit configuration
```

### Design Principles

1. **Modularity**: Reusable functions separated into utility modules
2. **Performance**: Data caching with `@st.cache_data` decorator
3. **User Experience**: Intuitive sidebar navigation and tabbed interface
4. **Flexibility**: Support for both file upload and local file loading
5. **Production-Ready**: Error handling, validation, and graceful failures

## Module Documentation

### src/data_loader.py

#### Functions

**`validate_file_path(file_path: str) -> Tuple[bool, str]`**
- Validates file existence and extension (.csv, .txt, .tsv)
- Returns validation status and error message

**`read_csv_flexible(file_or_path: Any) -> pd.DataFrame`**
- Reads CSV files with automatic fallback for comma, semicolon (European), or tab delimiters
- Robust against different text encodings (UTF-8, Latin1)

**`standardize_solar_dataframe(df: pd.DataFrame, parse_dates: bool = True) -> pd.DataFrame`**
- Standardizes any arbitrary solar dataset worldwide
- Auto-detects timestamp columns (timestamp, datetime, date_time, date, time, dt, epoch, or separate Year/Month/Day columns)
- Maps common lowercase and alias names to standard metric abbreviations (GHI, DNI, DHI, Tamb, RH, WS, etc.)

**`load_solar_data(file_path: str, parse_dates: bool = True) -> Optional[pd.DataFrame]`**
- Loads CSV file with flexible parsing and standardization
- Raises descriptive errors

**`get_available_metrics(df: pd.DataFrame) -> list`**
- Returns list of available numeric solar and meteorological metrics
- Prioritizes standard solar metrics first and dynamically includes any custom numeric sensor columns

**`discover_local_csv_files(directory: str = "data") -> list`**
- Scans and returns all CSV files present in the `data/` folder and subdirectories

**`get_metric_full_name(metric: str) -> str`**
- Returns the full descriptive text for any metric abbreviation (e.g. `GHI` -> `Global Horizontal Irradiance`)

**`get_metric_unit(metric: str) -> str`**
- Returns measurement unit string (e.g. `W/m²`, `°C`, `m/s`, `%`)

**`get_metric_label(metric: str) -> str`**
- Formats metric with abbreviation, full name, and unit for UI selectboxes

**`get_glossary_dataframe() -> pd.DataFrame`**
- Returns comprehensive DataFrame of abbreviations, full names, units, and definitions

**`get_date_range(df: pd.DataFrame) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]`**
- Extracts min and max dates from dataset
- Returns None if timestamp column missing

**`filter_by_date_range(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame`**
- Filters data between date range
- Returns original dataframe if no timestamp column

**`get_summary_statistics(df: pd.DataFrame, metrics: list) -> pd.DataFrame`**
- Calculates comprehensive statistics (Mean, Median, Std Dev, Min, Max, Count)
- Returns formatted statistics dataframe

**`get_top_hours(df: pd.DataFrame, metric: str, top_n: int = 10) -> pd.DataFrame`**
- Returns top N records for specified metric
- Used for peak hours analysis

### src/plot_utils.py

#### Visualization Functions

**`create_boxplot(df, metrics, title)`**
- Interactive Plotly boxplot
- Supports multiple metrics comparison
- Shows mean and standard deviation

**`create_time_series(df, metric, title)`**
- Line plot for temporal analysis
- Unified hover mode for better UX
- Customizable styling

**`create_correlation_heatmap(df, metrics)`**
- Heatmap showing correlation matrix
- Color-coded values (-1 to 1)
- Annotated with correlation coefficients

**`create_scatter_plot(df, x_metric, y_metric, color_metric)`**
- 2D or 3D scatter plots
- Optional color coding by third metric
- Interactive tooltips

**`create_bubble_chart(df, x_metric, y_metric, size_metric, color_metric)`**
- Multi-dimensional visualization
- Bubble size represents third dimension
- Sampling for large datasets (>1000 records)

**`create_wind_distribution(df)`**
- Histogram for wind speed analysis
- Overlay of wind speed and gust
- Frequency distribution

**`create_hourly_pattern(df, metric)`**
- Average values by hour of day
- Identifies daily patterns
- Linear time axis

**`create_monthly_pattern(df, metric)`**
- Average values by month
- Seasonal trend identification
- Bar chart visualization

**`create_distribution_plot(df, metric)`**
- Histogram with probability density
- Shows data distribution shape
- Useful for identifying normality

## Dashboard Features

### 1. Data Loading Options

#### File Upload
```python
# User uploads CSV directly through Streamlit widget
uploaded_file = st.sidebar.file_uploader("Upload cleaned CSV file", type=['csv'])
```

**Advantages:**
- No local file path needed
- Works in Streamlit Cloud
- Easy for non-technical users

#### Local Path
```python
# User specifies file path
file_path = st.sidebar.text_input("File path for {country}:")
df = load_data_cached(file_path)
```

**Advantages:**
- Faster for local development
- Supports large files
- Reusable paths

### 2. Interactive Widgets

#### Sidebar Controls
- **Radio buttons**: Data source selection
- **Selectbox**: Country/dataset selection
- **Text input**: Custom file paths
- **Multiselect**: Metric selection
- **Checkbox**: Date filter toggle
- **Date input**: Date range selection

#### Main Content
- **Tabs**: Organized content sections
- **Selectbox**: Metric-specific visualizations
- **Radio**: Pattern type selection
- **Slider**: Row count control
- **Checkbox**: Display options
- **Download button**: CSV export

### 3. Caching Strategy

```python
@st.cache_data
def load_data_cached(file_path: str):
    """Cache data loading for better performance"""
    try:
        return load_solar_data(file_path)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None
```

**Benefits:**
- Prevents redundant file reads
- Faster interaction
- Reduced memory usage
- Automatic cache invalidation

### 4. Error Handling

The dashboard implements comprehensive error handling:

```python
# File validation
is_valid, error_msg = validate_file_path(file_path)
if not is_valid:
    raise FileNotFoundError(error_msg)

# Graceful failures
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.sidebar.error(f"❌ Error loading file: {str(e)}")
```

## Customization Guide

### Adding New Metrics

1. **Add to `data_loader.py`:**
```python
potential_metrics = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS', 'WSgust', 
                    'YourNewMetric']  # Add here
```

2. **Create visualization function in `plot_utils.py`:**
```python
def create_your_plot(df: pd.DataFrame, metric: str) -> go.Figure:
    # Your plotting logic
    fig = go.Figure()
    # ... configure plot
    return fig
```

3. **Add to dashboard in `app/main.py`:**
```python
with tab_new:
    st.header("Your New Analysis")
    fig = create_your_plot(df, selected_metric)
    st.plotly_chart(fig, use_container_width=True)
```

### Changing Color Scheme

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"        # Your primary color
backgroundColor = "#FFFFFF"      # Background
secondaryBackgroundColor = "#F0F0F0"  # Sidebar
textColor = "#262730"           # Text color
```

### Adding New Tab

```python
# In app/main.py
tab1, tab2, ..., tab_new = st.tabs([
    "📊 Overview", 
    # ... existing tabs
    "🆕 Your New Tab"
])

with tab_new:
    st.header("Your Analysis")
    # Your code here
```

## Performance Optimization

### 1. Data Sampling
For large datasets (>1M rows), consider sampling:
```python
if len(df) > 1_000_000:
    df_sample = df.sample(n=100_000, random_state=42)
else:
    df_sample = df
```

### 2. Lazy Loading
Load visualizations only when tabs are active:
```python
with tab_specific:
    if st.button("Generate Heavy Visualization"):
        fig = create_heavy_plot(df)
        st.plotly_chart(fig)
```

### 3. Reduce Plot Complexity
```python
# Sample data for scatter plots
plot_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df
```

## Deployment Best Practices

### 1. Requirements Management
Keep `requirements.txt` minimal and version-pinned:
```txt
streamlit==1.28.0
pandas==2.1.0
plotly==5.17.0
```

### 2. Memory Management
- Use `@st.cache_data` for expensive operations
- Clear cache when needed: `st.cache_data.clear()`
- Monitor app memory in Streamlit Cloud

### 3. Security
- Never commit API keys or credentials
- Use `st.secrets` for sensitive data
- Validate all user inputs

### 4. User Experience
- Show loading spinners for long operations
- Provide clear error messages
- Add help text to widgets
- Include usage instructions

## Testing Locally

### Quick Test
```bash
# Navigate to project root
cd solar-challenge-week0

# Run dashboard
streamlit run app/main.py

# Open browser at http://localhost:8501
```

### Test with Sample Data
```python
# Create minimal test CSV
import pandas as pd
import numpy as np

dates = pd.date_range('2024-01-01', periods=100, freq='H')
test_data = pd.DataFrame({
    'Timestamp': dates,
    'GHI': np.random.uniform(0, 1000, 100),
    'DNI': np.random.uniform(0, 900, 100),
    'DHI': np.random.uniform(0, 500, 100),
    'Tamb': np.random.uniform(20, 35, 100)
})
test_data.to_csv('data/test_data.csv', index=False)
```

## Troubleshooting

### Common Issues

**Issue: Import Error**
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Ensure you're running from project root and sys.path is configured correctly.

**Issue: Date Parsing Fails**
```
ValueError: time data doesn't match format
```
**Solution:** Check timestamp format in CSV. Use `errors='coerce'` in `pd.to_datetime()`.

**Issue: Empty Plot**
```
Plot shows but no data visible
```
**Solution:** Verify metric names match column names exactly (case-sensitive).

**Issue: Memory Error in Streamlit Cloud**
```
MemoryError: Unable to allocate array
```
**Solution:** Implement data sampling or increase app resources.

## Advanced Features

### 1. Multi-File Comparison
```python
# Load multiple datasets
dfs = {
    'Benin': load_solar_data('data/benin.csv'),
    'Togo': load_solar_data('data/togo.csv')
}

# Compare side by side
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(create_time_series(dfs['Benin'], 'GHI'))
with col2:
    st.plotly_chart(create_time_series(dfs['Togo'], 'GHI'))
```

### 2. Export Functionality
```python
# Already implemented in Data Table tab
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="solar_data_filtered.csv",
    mime="text/csv"
)
```

### 3. Real-time Data Updates
```python
# Auto-refresh every 60 seconds
import time

placeholder = st.empty()
while True:
    with placeholder.container():
        df = load_latest_data()
        st.plotly_chart(create_time_series(df, 'GHI'))
    time.sleep(60)
```

## Resources

### Official Documentation
- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### Community
- [Streamlit Forum](https://discuss.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)

### Support
For issues specific to this dashboard, please open an issue on GitHub or contact the development team.

---

**Last Updated:** November 2024  
**Version:** 1.0.0  
**Maintainer:** 10 Academy KAIM Team
