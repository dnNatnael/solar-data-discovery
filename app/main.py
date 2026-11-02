"""
Solar Challenge Interactive Dashboard
10 Academy KAIM Week 0 - Bonus Task

A production-ready Streamlit dashboard for visualizing solar radiation data
from Benin, Sierra Leone, and Togo.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import (
    load_solar_data, 
    get_available_metrics, 
    get_date_range,
    filter_by_date_range,
    get_summary_statistics,
    get_top_hours
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

# Page configuration
st.set_page_config(
    page_title="Solar Challenge Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for responsive and modern styling
st.markdown("""
    <style>
    /* Main Header Styling */
    .main-header {
        font-size: clamp(1.8rem, 4vw, 2.8rem);
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
    }
    
    /* Sub Header */
    .sub-header {
        font-size: clamp(0.9rem, 2vw, 1.2rem);
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Responsive Containers */
    .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem 1rem;
        }
    }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    section[data-testid="stSidebar"] .css-1d391kg {
        padding: 1rem;
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding: 10px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e2e6;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Info Boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #667eea;
        padding: 1rem;
        background-color: #f8f9ff;
    }
    
    /* Download Button Styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric Widgets */
    div[data-testid="stMetricValue"] {
        font-size: clamp(1.2rem, 3vw, 2rem);
        font-weight: 700;
    }
    
    /* Responsive Tables */
    .dataframe {
        font-size: clamp(0.75rem, 1.5vw, 0.9rem);
    }
    
    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 12px;
        margin-top: 2rem;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #f8f9ff;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Plot Containers */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Radio Buttons */
    .stRadio > label {
        font-weight: 600;
        color: #333;
    }
    
    /* Select Boxes */
    .stSelectbox > label {
        font-weight: 600;
        color: #333;
    }
    
    /* Mobile Responsive */
    @media (max-width: 640px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 0.85rem;
            padding: 8px 12px;
        }
        
        .main-header {
            font-size: 1.8rem;
        }
        
        .sub-header {
            font-size: 0.9rem;
        }
    }
    
    /* Smooth Animations */
    * {
        transition: background-color 0.2s ease, color 0.2s ease;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data_cached(file_path: str):
    """Cache data loading for better performance"""
    try:
        return load_solar_data(file_path)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


@st.cache_data
def convert_df_to_csv(data: pd.DataFrame) -> bytes:
    """Cache CSV conversion so it is not re-computed on every rerun"""
    return data.to_csv(index=False).encode('utf-8')


def main():
    """Main application function"""
    
    # Header with improved responsive design
    st.markdown('''
        <div class="main-header">☀️ Solar Challenge Dashboard</div>
        <div class="sub-header">Interactive Analysis of Solar Radiation Data from West Africa</div>
    ''', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Dashboard Configuration")
    st.sidebar.markdown("---")
    
    # Country/Dataset selection
    st.sidebar.subheader("📍 Select Dataset")
    
    # Option to upload file or use local path
    data_source = st.sidebar.radio(
        "Data Source:",
        ["Upload CSV File", "Use Local Path"],
        help="Choose how to load your dataset"
    )
    
    df = None
    
    if data_source == "Upload CSV File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload cleaned CSV file",
            type=['csv'],
            help="Upload your cleaned solar dataset CSV file"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                st.sidebar.success("✅ File loaded successfully!")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading file: {str(e)}")
    
    else:  # Use Local Path
        # Predefined country paths (user can modify)
        country = st.sidebar.selectbox(
            "Select Country:",
            ["Benin", "Sierra Leone", "Togo", "Custom Path"],
            help="Select a predefined country or use a custom path"
        )
        
        # Smart candidate paths (support both data/cleaned/ and data/ raw files)
        country_candidates = {
            "Benin": ["data/benin-malanville.csv", "data/cleaned/benin_clean.csv"],
            "Sierra Leone": ["data/sierraleone-bumbuna.csv", "data/cleaned/sierra_leone_clean.csv"],
            "Togo": ["data/togo-dapaong_qc.csv", "data/cleaned/togo_clean.csv"]
        }
        
        def resolve_default_path(c_name):
            for p in country_candidates.get(c_name, []):
                if Path(p).exists():
                    return p
            return country_candidates.get(c_name, [""])[0]
        
        if country == "Custom Path":
            file_path = st.sidebar.text_input(
                "Enter file path:",
                placeholder="path/to/your/file.csv",
                help="Enter the full or relative path to your CSV file"
            )
        else:
            file_path = st.sidebar.text_input(
                f"File path for {country}:",
                value=resolve_default_path(country),
                help="Update this path to match your local file location"
            )
        
        if file_path:
            if st.sidebar.button("📂 Load Data"):
                df = load_data_cached(file_path)
                if df is not None:
                    st.sidebar.success("✅ Data loaded successfully!")
    
    # Main content area
    if df is None:
        st.info("👈 Please load a dataset using the sidebar to get started!")
        
        # Display instructions
        with st.expander("📖 How to Use This Dashboard", expanded=True):
            st.markdown("""
            ### Getting Started
            
            1. **Load Your Data**: Use the sidebar to either:
               - Upload a CSV file directly, or
               - Specify a local file path to your cleaned dataset
            
            2. **Configure Filters**: Once data is loaded, you can:
               - Select metrics to analyze (GHI, DNI, DHI, etc.)
               - Filter by date range
               - Choose visualization options
            
            3. **Explore Visualizations**: Navigate through different tabs to view:
               - Boxplot comparisons
               - Time series analysis
               - Statistical summaries
               - Correlation patterns
               - And much more!
            
            ### Expected Data Format
            Your CSV file should contain columns such as:
            - `Timestamp`: Date and time of measurements
            - `GHI`: Global Horizontal Irradiance
            - `DNI`: Direct Normal Irradiance
            - `DHI`: Diffuse Horizontal Irradiance
            - `Tamb`: Ambient Temperature
            - `RH`: Relative Humidity
            - `WS`: Wind Speed
            - `WSgust`: Wind Gust Speed
            
            ### Note
            This dashboard is designed for the 10 Academy KAIM Week 0 Solar Challenge.
            It supports analysis of solar radiation data from Benin, Sierra Leone, and Togo.
            """)
        
        return
    
    # Data loaded successfully - show metrics selector
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Select Metrics")
    
    available_metrics = get_available_metrics(df)
    
    if not available_metrics:
        st.error("❌ No valid metrics found in the dataset!")
        return
    
    # Multi-select for metrics
    selected_metrics = st.sidebar.multiselect(
        "Choose metrics to analyze:",
        available_metrics,
        default=available_metrics[:3] if len(available_metrics) >= 3 else available_metrics,
        help="Select one or more metrics for analysis"
    )
    
    # Date range filter
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Date Range Filter")
    
    min_date, max_date = get_date_range(df)
    
    if min_date and max_date:
        use_date_filter = st.sidebar.checkbox("Enable date filter", value=False)
        
        if use_date_filter:
            date_range = st.sidebar.date_input(
                "Select date range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                df = filter_by_date_range(df, date_range[0], date_range[1])
                st.sidebar.info(f"📊 Filtered to {len(df):,} records")
    
    # Display basic dataset info
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Dataset Info")
    st.sidebar.write(f"**Records**: {len(df):,}")
    st.sidebar.write(f"**Columns**: {len(df.columns)}")
    if min_date and max_date:
        st.sidebar.write(f"**Date Range**: {min_date.date()} to {max_date.date()}")
    
    # Main dashboard content with tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "📈 Time Series", 
        "🔍 Detailed Analysis",
        "🌡️ Patterns",
        "🔗 Correlations",
        "📋 Data Table"
    ])
    
    with tab1:
        st.header("📊 Overview & Summary Statistics")
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        else:
            # Summary statistics with responsive layout
            col1, col2 = st.columns([2, 1], gap="large")
            
            with col1:
                st.markdown("### 📈 Statistical Summary")
                summary_df = get_summary_statistics(df, selected_metrics)
                st.dataframe(
                    summary_df.style.format("{:.2f}").background_gradient(cmap='Blues', subset=['Mean']),
                    width="stretch",
                    height=400
                )
            
            with col2:
                st.markdown("### ⚡ Quick Metrics")
                metrics_to_show = selected_metrics[:4] if len(selected_metrics) >= 4 else selected_metrics
                for metric in metrics_to_show:
                    if metric in df.columns:
                        mean_val = df[metric].mean()
                        max_val = df[metric].max()
                        delta_pct = ((mean_val / max_val) * 100) if max_val != 0 else 0
                        st.metric(
                            label=f"**{metric}**",
                            value=f"{mean_val:.2f}",
                            delta=f"{delta_pct:.1f}% of max",
                            delta_color="normal"
                        )
            
            # Boxplot comparison with enhanced styling
            st.markdown("---")
            st.markdown("### 📊 Distribution Comparison")
            st.markdown("*Compare the statistical distribution of selected metrics*")
            fig_box = create_boxplot(df, selected_metrics, "Metric Distribution Comparison")
            st.plotly_chart(fig_box, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
    
    with tab2:
        st.header("📈 Time Series Analysis")
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        else:
            # Metric selector for time series
            metric_for_ts = st.selectbox(
                "Select metric for time series:",
                selected_metrics,
                help="Choose which metric to display over time"
            )
            
            if metric_for_ts:
                # Time series plot with enhanced presentation
                st.markdown(f"### 📈 {metric_for_ts} Trends Over Time")
                fig_ts = create_time_series(df, metric_for_ts)
                st.plotly_chart(fig_ts, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
                # Top/Peak hours in columns
                st.markdown("---")
                col_left, col_right = st.columns([1, 1], gap="large")
                
                with col_left:
                    st.markdown(f"### 🏆 Top 10 Peak Hours")
                    top_df = get_top_hours(df, metric_for_ts, top_n=10)
                    if not top_df.empty:
                        st.dataframe(
                            top_df.style.format({metric_for_ts: "{:.2f}"}).highlight_max(axis=0, color='lightgreen'),
                            width="stretch",
                            height=400
                        )
                    else:
                        st.info("No timestamp data available for peak hours analysis.")
                
                with col_right:
                    st.markdown("### 📊 Key Statistics")
                    if metric_for_ts in df.columns:
                        stats_container = st.container()
                        with stats_container:
                            metric_data = df[metric_for_ts].dropna()
                            st.metric("Maximum", f"{metric_data.max():.2f}")
                            st.metric("Average", f"{metric_data.mean():.2f}")
                            st.metric("Minimum", f"{metric_data.min():.2f}")
                            st.metric("Std Dev", f"{metric_data.std():.2f}")
    
    with tab3:
        st.header("🔍 Detailed Analysis")
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        else:
            analysis_type = st.selectbox(
                "Select analysis type:",
                ["Distribution", "Scatter Plot", "Bubble Chart", "Wind Analysis"]
            )
            
            if analysis_type == "Distribution":
                metric = st.selectbox("Select metric:", selected_metrics, key="dist_metric")
                st.markdown(f"### 📊 {metric} Distribution Analysis")
                st.info("💡 This histogram shows how frequently different values occur in the dataset.")
                fig = create_distribution_plot(df, metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            elif analysis_type == "Scatter Plot":
                col1, col2, col3 = st.columns(3)
                with col1:
                    x_metric = st.selectbox("X-axis:", selected_metrics, key="scatter_x")
                with col2:
                    y_metric = st.selectbox("Y-axis:", selected_metrics, index=min(1, len(selected_metrics)-1), key="scatter_y")
                with col3:
                    color_option = st.selectbox("Color by:", ["None"] + selected_metrics, key="scatter_color")
                
                color_metric = None if color_option == "None" else color_option
                st.markdown(f"### 🔵 Scatter Analysis: {y_metric} vs {x_metric}")
                st.info("💡 Explore the relationship between two metrics. Points show individual measurements.")
                fig = create_scatter_plot(df, x_metric, y_metric, color_metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            elif analysis_type == "Bubble Chart":
                if len(selected_metrics) < 3:
                    st.warning("⚠️ Please select at least 3 metrics for bubble chart.")
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        x_metric = st.selectbox("X-axis:", selected_metrics, key="bubble_x")
                    with col2:
                        y_metric = st.selectbox("Y-axis:", selected_metrics, index=min(1, len(selected_metrics)-1), key="bubble_y")
                    with col3:
                        size_metric = st.selectbox("Size:", selected_metrics, index=min(2, len(selected_metrics)-1), key="bubble_size")
                    
                    color_option = st.selectbox("Color by:", ["None"] + selected_metrics, key="bubble_color")
                    color_metric = None if color_option == "None" else color_option
                    
                    st.markdown("### 🫧 Multi-Dimensional Bubble Chart")
                    st.info("💡 Bubble size represents the third metric. Larger bubbles indicate higher values.")
                    fig = create_bubble_chart(df, x_metric, y_metric, size_metric, color_metric)
                    st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            elif analysis_type == "Wind Analysis":
                if 'WS' in df.columns:
                    st.markdown("### 🌬️ Wind Speed & Gust Analysis")
                    st.info("💡 Compare wind speed and gust distributions to understand wind patterns.")
                    fig = create_wind_distribution(df)
                    st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                    
                    # Additional wind statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Avg Wind Speed", f"{df['WS'].mean():.2f} m/s")
                    with col2:
                        st.metric("Max Wind Speed", f"{df['WS'].max():.2f} m/s")
                    with col3:
                        if 'WSgust' in df.columns:
                            st.metric("Max Gust", f"{df['WSgust'].max():.2f} m/s")
                else:
                    st.warning("⚠️ Wind speed data (WS) not available in the dataset.")
    
    with tab4:
        st.header("🌡️ Temporal Patterns")
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        elif 'Timestamp' not in df.columns:
            st.warning("⚠️ Timestamp column not found in the dataset.")
        else:
            metric = st.selectbox("Select metric for pattern analysis:", selected_metrics, key="pattern_metric")
            
            pattern_type = st.radio(
                "Pattern type:",
                ["Hourly Pattern", "Monthly Pattern"],
                horizontal=True
            )
            
            if pattern_type == "Hourly Pattern":
                st.markdown(f"### ⏰ Hourly Pattern: {metric}")
                st.info("💡 This chart shows the average values across all days for each hour of the day.")
                fig = create_hourly_pattern(df, metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            else:  # Monthly Pattern
                st.markdown(f"### 📅 Monthly Pattern: {metric}")
                st.info("💡 This chart shows the average values for each month in the dataset.")
                fig = create_monthly_pattern(df, metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
    
    with tab5:
        st.header("🔗 Correlation Analysis")
        
        if len(selected_metrics) < 2:
            st.warning("⚠️ Please select at least 2 metrics for correlation analysis.")
        else:
            st.markdown("### 🔗 Correlation Matrix Heatmap")
            st.info("💡 Correlation values range from -1 to 1. Values closer to 1 indicate strong positive correlation, while values closer to -1 indicate strong negative correlation.")
            fig_corr = create_correlation_heatmap(df, selected_metrics)
            st.plotly_chart(fig_corr, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            # Show strongest correlations
            st.markdown("---")
            st.markdown("### 🎯 Key Correlations")
            corr_matrix = df[selected_metrics].corr()
            
            # Get top correlations
            correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    correlations.append({
                        'Metric 1': corr_matrix.columns[i],
                        'Metric 2': corr_matrix.columns[j],
                        'Correlation': corr_matrix.iloc[i, j]
                    })
            
            if correlations:
                corr_df = pd.DataFrame(correlations)
                corr_df = corr_df.sort_values('Correlation', ascending=False, key=abs)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🔺 Strongest Positive")
                    st.dataframe(
                        corr_df.head(5).style.format({'Correlation': '{:.3f}'}).background_gradient(cmap='Greens'),
                        width="stretch"
                    )
                with col2:
                    st.markdown("#### 🔻 Strongest Negative")
                    st.dataframe(
                        corr_df.tail(5).style.format({'Correlation': '{:.3f}'}).background_gradient(cmap='Reds'),
                        width="stretch"
                    )
    
    with tab6:
        st.header("📋 Raw Data Table")
        
        st.markdown("### 📊 Dataset Preview")
        st.info("💡 Explore your data directly. Use the controls below to customize the view.")
        
        # Display controls with better spacing
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            num_rows = st.slider("Number of rows to display:", 5, 100, 20)
        with col2:
            show_all_cols = st.checkbox("Show all columns", value=False)
        with col3:
            st.metric("Total Rows", f"{len(df):,}")
        
        # Display data
        if show_all_cols:
            st.dataframe(df.head(num_rows), width="stretch")
        else:
            display_cols = ['Timestamp'] + selected_metrics if 'Timestamp' in df.columns else selected_metrics
            display_cols = [col for col in display_cols if col in df.columns]
            st.dataframe(df[display_cols].head(num_rows), width="stretch")
        
        # Download option with enhanced presentation
        st.markdown("---")
        st.markdown("### 📥 Export Data")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            Download the filtered dataset in CSV format for further analysis.
            This includes all currently selected metrics and applied filters.
            """)
        with col2:
            st.download_button(
                label="⬇️ Download CSV",
                data=convert_df_to_csv(df),
                file_name=f"solar_data_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch"
            )
    
    # Enhanced Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <h3 style='color: #667eea; margin-bottom: 1rem;'>☀️ Solar Challenge Dashboard</h3>
        <p style='color: #666; font-size: 1rem; margin: 0.5rem 0;'>
            <strong>10 Academy KAIM Week 0</strong> | Built with ❤️ using Streamlit
        </p>
        <p style='color: #888; font-size: 0.9rem; margin: 0.5rem 0;'>
            📊 Data sources: Benin, Sierra Leone, and Togo Solar Radiation Measurements
        </p>
        <p style='color: #aaa; font-size: 0.85rem; margin-top: 1rem;'>
            Version 1.0.0 | Last Updated: November 2024
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
