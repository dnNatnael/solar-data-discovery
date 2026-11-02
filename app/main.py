"""
Solar Data Discovery Interactive Dashboard
10 Academy KAIM Week 0 - Bonus Task & Portfolio Project

A production-ready Streamlit dashboard for analyzing and visualizing solar radiation
and meteorological datasets from Benin, Sierra Leone, Togo, and ANY country or station worldwide.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import (
    load_solar_data, 
    read_csv_flexible,
    standardize_solar_dataframe,
    get_available_metrics, 
    get_date_range,
    filter_by_date_range,
    get_summary_statistics,
    get_top_hours,
    discover_local_csv_files,
    get_metric_full_name,
    get_metric_unit,
    get_metric_category,
    get_metric_description,
    get_glossary_dataframe,
    METRIC_GLOSSARY,
    GENERAL_SOLAR_TERMS
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
    page_title="Solar Data Discovery",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, responsive styling
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
        margin-bottom: 0.25rem;
        padding: 0.5rem;
    }
    
    /* Sub Header */
    .sub-header {
        font-size: clamp(0.9rem, 2vw, 1.15rem);
        color: #555;
        text-align: center;
        margin-bottom: 1.25rem;
        font-weight: 400;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #667eea20;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
    }

    /* Glossy Table Styling */
    .glossary-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    .glossary-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 14px;
        text-align: left;
    }
    
    .glossary-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .glossary-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 12px;
        margin-top: 2rem;
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


def render_glossary_overview():
    """Render a comprehensive abbreviations & full text table in markdown"""
    df_glossary = get_glossary_dataframe(include_general_terms=True)
    st.dataframe(
        df_glossary,
        width="stretch",
        height=400,
        column_config={
            "Abbreviation": st.column_config.TextColumn("Abbreviation", width="small"),
            "Full Name": st.column_config.TextColumn("Full Descriptive Text", width="medium"),
            "Unit": st.column_config.TextColumn("Measurement Unit", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Description": st.column_config.TextColumn("Description & Physical Meaning", width="large")
        }
    )


def main():
    """Main application function"""
    
    # Header
    st.markdown('''
        <div class="main-header">☀️ Solar Data Discovery</div>
        <div class="sub-header">Interactive Analytics Platform for Solar Radiation & Meteorological Datasets Worldwide</div>
    ''', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Dataset Configuration")
    st.sidebar.markdown("---")
    
    # Dataset Upload in Sidebar
    st.sidebar.subheader("📤 Upload CSV Dataset")
    st.sidebar.markdown(
        "Upload any solar or meteorological CSV dataset to begin analysis and visualization."
    )
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File:",
        type=['csv', 'txt', 'tsv'],
        help="Upload solar irradiance, weather station, PV system, or meteorological CSV file (Benin, Sierra Leone, Togo, or any station worldwide)",
        key="sidebar_csv_uploader"
    )
    
    df = None
    dataset_name = "Solar Dataset"
    
    # 1. Check if a file was uploaded via sidebar uploader
    if uploaded_file is not None:
        # Clear main page session upload if sidebar file is chosen
        st.session_state.pop('main_uploaded_df', None)
        st.session_state.pop('main_uploaded_name', None)
        dataset_name = uploaded_file.name
        try:
            with st.spinner(f"Loading and processing `{uploaded_file.name}`..."):
                raw_df = read_csv_flexible(uploaded_file)
                df = standardize_solar_dataframe(raw_df)
                st.sidebar.success(f"✅ Loaded `{uploaded_file.name}` ({len(df):,} records)")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading uploaded CSV: {str(e)}")
            df = None

    # 2. Check if a file was uploaded via main landing page uploader
    elif 'main_uploaded_df' in st.session_state and st.session_state.get('main_uploaded_df') is not None:
        df = st.session_state['main_uploaded_df']
        dataset_name = st.session_state.get('main_uploaded_name', 'Uploaded Solar Dataset')
        st.sidebar.success(f"✅ Loaded `{dataset_name}` ({len(df):,} records)")
        if st.sidebar.button("🗑️ Remove File / Upload Another"):
            st.session_state.pop('main_uploaded_df', None)
            st.session_state.pop('main_uploaded_name', None)
            st.rerun()

    # Persistent Metric Abbreviations Glossary in Sidebar
    st.sidebar.markdown("---")
    with st.sidebar.expander("📖 Metric Abbreviations Glossary", expanded=False):
        st.markdown("""
        **Quick Abbreviation Lookup:**
        - **GHI**: Global Horizontal Irradiance ($W/m^2$)
        - **DNI**: Direct Normal Irradiance ($W/m^2$)
        - **DHI**: Diffuse Horizontal Irradiance ($W/m^2$)
        - **Tamb**: Ambient Temperature ($^\\circ C$)
        - **TModA / TModB**: Module Temperature A / B ($^\\circ C$)
        - **RH**: Relative Humidity ($\\%$)
        - **WS**: Wind Speed ($m/s$)
        - **WSgust**: Wind Gust Speed ($m/s$)
        - **WD**: Wind Direction ($^\\circ$ North)
        - **BP**: Barometric Pressure ($hPa$)
        - **ModA / ModB**: Module Sensors ($W/m^2$)
        - **Precipitation**: Rainfall ($mm$)
        - **Cleaning**: Cleaning Flag ($1/0$)
        """)
        st.caption("👉 See the dedicated **'📖 Abbreviations & Glossary'** tab for full definitions, units, and formulas.")

    # Landing page view when no data is loaded
    if df is None:
        st.info("👈 **Please upload a CSV file to get started! All data, graphs, charts, and other visualizations will only be displayed after upload.**")
        
        # Prominent upload drop zone on landing page
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                    border: 2px dashed #667eea; border-radius: 12px; padding: 1.75rem; 
                    text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #667eea; margin-top: 0; font-size: 1.4rem;">📤 Upload Your Solar CSV Dataset</h3>
            <p style="color: #444; font-size: 1rem; margin-bottom: 0.5rem;">
                Select or drag & drop any solar or meteorological CSV file below (or use the sidebar on the left):
            </p>
            <p style="color: #777; font-size: 0.85rem; margin-bottom: 0;">
                Compatible with Benin, Sierra Leone, Togo, NASA POWER, NREL NSRDB, PVGIS, Solargis, and custom weather station CSVs worldwide.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        landing_file = st.file_uploader(
            "Upload any CSV dataset file",
            type=['csv', 'txt', 'tsv'],
            help="Upload solar irradiance, weather station, PV system, or meteorological CSV file",
            key="landing_csv_uploader"
        )
        
        if landing_file is not None:
            try:
                with st.spinner(f"Loading and processing `{landing_file.name}`..."):
                    raw_df = read_csv_flexible(landing_file)
                    loaded_df = standardize_solar_dataframe(raw_df)
                    st.session_state['main_uploaded_df'] = loaded_df
                    st.session_state['main_uploaded_name'] = landing_file.name
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading uploaded CSV: {str(e)}")
        
        # Sample datasets download section
        with st.expander("📥 Need sample datasets to test upload?", expanded=False):
            st.markdown("Download a sample solar CSV dataset to test uploading into the dashboard:")
            col_s1, col_s2, col_s3 = st.columns(3)
            
            sample_files = [
                ("Benin (Malanville)", "data/benin-malanville.csv", "sample_benin_malanville.csv"),
                ("Sierra Leone (Bumbuna)", "data/sierraleone-bumbuna.csv", "sample_sierraleone_bumbuna.csv"),
                ("Togo (Dapaong)", "data/togo-dapaong_qc.csv", "sample_togo_dapaong.csv")
            ]
            
            for (label, path_str, export_name), col in zip(sample_files, [col_s1, col_s2, col_s3]):
                with col:
                    p = Path(path_str)
                    if p.exists():
                        try:
                            sample_df = pd.read_csv(p, nrows=3000)
                            sample_csv = sample_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label=f"📥 {label}",
                                data=sample_csv,
                                file_name=export_name,
                                mime="text/csv",
                                width="stretch"
                            )
                        except Exception:
                            st.caption(f"{label} dataset")
                    else:
                        st.caption(f"{label} dataset")

        # Prominent callout answering Question 1: Does it receive any other CSV files?
        st.markdown("""
        ### 🌍 Universal CSV File Compatibility
        
        > [!NOTE]
        > **Yes! This platform receives and processes ANY CSV file** — not just the 3 sample countries (Benin, Sierra Leone, Togo).
        > 
        > Whether your data comes from **NASA POWER**, **NREL NSRDB**, **PVGIS**, **Solargis**, an on-site solar pyranometer logger, or any regional meteorological station worldwide:
        > 1. **Flexible Uploading**: Upload any CSV, TSV, or TXT file using the sidebar or center upload box.
        > 2. **Automatic Schema Standardization**: The engine auto-detects date/time columns (`timestamp`, `datetime`, `date_time`, `date`, `time`, `dt`, or separate Year/Month/Day columns) and case-insensitive metric aliases (`ghi`, `dni`, `dhi`, `temp`, `humidity`, `wind_speed`, etc.).
        > 3. **Dynamic Metric Discovery**: Any numeric sensor or measurement column present in your CSV file is automatically identified, selectable, and plottable across all tabs.
        """)
        
        # Prominent section answering Question 2: List abbreviations with full text on the Streamlit browser
        st.markdown("### 📖 Solar Metric Abbreviations & Full Descriptive Names")
        st.markdown("Comprehensive reference of standard measurement abbreviations, full descriptive names, SI units, and physical meanings:")
        
        render_glossary_overview()
        
        with st.expander("ℹ️ How to Use This Dashboard", expanded=False):
            st.markdown(r"""
            1. **Upload Data**: Upload any solar or meteorological CSV dataset using the sidebar or center upload box.
            2. **Choose Metrics**: Select one or more metrics from the sidebar. Each metric is listed with its **abbreviation AND full name**.
            3. **Filter Date Range**: Optionally focus on a specific season, month, or multi-week event.
            4. **Explore Interactive Tabs**:
               - **📊 Overview**: Summary statistics, distributions, and quick metrics.
               - **📈 Time Series**: Temporal dynamics, diurnal fluctuations, and peak solar hours.
               - **🔍 Detailed Analysis**: Distribution densities, bivariate scatter plots, 3D bubble charts, and wind profiles.
               - **🌡️ Patterns**: 24-hour diurnal curves and 12-month seasonal profiles.
               - **🔗 Correlations**: Pearson correlation heatmap and strongest variable couplings.
               - **📋 Data Table**: Raw record inspection and filtered CSV export.
               - **📖 Abbreviations & Glossary**: Complete metric dictionary and solar engineering terminology.
            """)
        return

    # Data loaded successfully - show metric selection with full text
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Select Metrics")
    
    available_metrics = get_available_metrics(df)
    
    if not available_metrics:
        st.error("❌ No valid numeric metrics found in the dataset!")
        return
    
    # Default selection prioritizing core solar irradiance metrics if present
    default_selection = [m for m in ['GHI', 'DNI', 'DHI', 'Tamb', 'WS'] if m in available_metrics]
    if not default_selection:
        default_selection = available_metrics[:min(3, len(available_metrics))]
    
    # Multi-select for metrics
    selected_metrics = st.sidebar.multiselect(
        "Choose metrics to analyze:",
        options=available_metrics,
        default=default_selection,
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
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
            
            if len(date_range) == 2:
                df = filter_by_date_range(df, date_range[0], date_range[1])
                st.sidebar.info(f"📊 Filtered to {len(df):,} records")
    else:
        st.sidebar.caption("ℹ️ No datetime column detected; displaying all records.")

    # Dataset Summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Dataset Information")
    st.sidebar.write(f"**Dataset**: `{dataset_name}`")
    st.sidebar.write(f"**Records**: {len(df):,}")
    st.sidebar.write(f"**Columns**: {len(df.columns)}")
    if min_date and max_date:
        st.sidebar.write(f"**Time Span**: {min_date.date()} to {max_date.date()}")
    
    # Main Dashboard Tabs (Includes dedicated Tab 7 for Abbreviations & Glossary)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", 
        "📈 Time Series", 
        "🔍 Detailed Analysis",
        "🌡️ Patterns",
        "🔗 Correlations",
        "📋 Data Table",
        "📖 Abbreviations & Glossary"
    ])
    
    # TAB 1: OVERVIEW
    with tab1:
        st.header(f"📊 Overview & Summary Statistics — {dataset_name}")
        
        # Metric Definitions & Units Expander on Overview Tab
        with st.expander("📖 Metric Abbreviations & Full Names Reference", expanded=False):
            st.markdown("Quick reference table of abbreviations and full descriptive text:")
            render_glossary_overview()
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar to display statistics.")
        else:
            col1, col2 = st.columns([2, 1], gap="large")
            
            with col1:
                st.markdown("### 📈 Statistical Summary")
                summary_df = get_summary_statistics(df, selected_metrics)
                if not summary_df.empty:
                    st.dataframe(
                        summary_df.style.format({
                            'Mean': '{:.2f}',
                            'Median': '{:.2f}',
                            'Std Dev': '{:.2f}',
                            'Min': '{:.2f}',
                            'Max': '{:.2f}',
                            'Count': '{:,}'
                        }).background_gradient(cmap='Blues', subset=['Mean']),
                        width="stretch",
                        height=380
                    )
                else:
                    st.info("No statistics available for the selected columns.")
            
            with col2:
                st.markdown("### ⚡ Quick Metrics")
                metrics_to_show = selected_metrics[:4]
                for metric in metrics_to_show:
                    if metric in df.columns:
                        metric_data = df[metric].dropna()
                        if not metric_data.empty:
                            mean_val = metric_data.mean()
                            max_val = metric_data.max()
                            delta_pct = ((mean_val / max_val) * 100) if max_val != 0 else 0
                            full_name = get_metric_full_name(metric)
                            unit = get_metric_unit(metric)
                            unit_suffix = f" {unit}" if unit else ""
                            st.metric(
                                label=f"**{metric}** — {full_name}",
                                value=f"{mean_val:.2f}{unit_suffix}",
                                delta=f"{delta_pct:.1f}% of peak ({max_val:.1f}{unit_suffix})",
                                delta_color="normal"
                            )
            
            # Boxplot comparison
            st.markdown("---")
            st.markdown("### 📊 Distribution Comparison (Boxplots)")
            st.markdown("*Compare medians, quartiles, and standard deviations across selected metrics.*")
            fig_box = create_boxplot(df, selected_metrics, f"Metric Distributions: {', '.join(selected_metrics)}")
            st.plotly_chart(fig_box, width="stretch", config={'displayModeBar': True, 'displaylogo': False})

    # TAB 2: TIME SERIES
    with tab2:
        st.header("📈 Time Series Analysis")
        
        if 'Timestamp' not in df.columns:
            st.warning("⚠️ A valid Timestamp column is required for time series analysis. Please ensure your dataset includes a recognized date/time column.")
        elif not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        else:
            metric_for_ts = st.selectbox(
                "Select metric for time series:",
                selected_metrics,
                help="Choose which metric to display over time"
            )
            
            if metric_for_ts:
                fn = get_metric_full_name(metric_for_ts)
                unit = get_metric_unit(metric_for_ts)
                unit_str = f" ({unit})" if unit else ""
                
                st.markdown(f"### 📈 {metric_for_ts} — {fn} Over Time")
                fig_ts = create_time_series(df, metric_for_ts)
                st.plotly_chart(fig_ts, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
                # Top peak records
                st.markdown("---")
                col_left, col_right = st.columns([1, 1], gap="large")
                
                with col_left:
                    st.markdown(f"### 🏆 Top 10 Peak Readings for {metric_for_ts}")
                    top_df = get_top_hours(df, metric_for_ts, top_n=10)
                    if not top_df.empty:
                        st.dataframe(
                            top_df.style.format({metric_for_ts: "{:.2f}"}).highlight_max(axis=0, color='lightgreen'),
                            width="stretch",
                            height=380
                        )
                    else:
                        st.info("No peak timestamp data available.")
                
                with col_right:
                    st.markdown(f"### 📊 Summary Figures for {metric_for_ts}")
                    metric_data = df[metric_for_ts].dropna()
                    if not metric_data.empty:
                        st.metric("Peak Maximum", f"{metric_data.max():.2f}{unit_str}")
                        st.metric("Overall Average", f"{metric_data.mean():.2f}{unit_str}")
                        st.metric("Standard Deviation", f"{metric_data.std():.2f}{unit_str}")
                        st.metric("Minimum", f"{metric_data.min():.2f}{unit_str}")

    # TAB 3: DETAILED ANALYSIS
    with tab3:
        st.header("🔍 Detailed Analysis & Exploratory Plots")
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        else:
            analysis_type = st.selectbox(
                "Select analysis view:",
                ["Distribution", "Scatter Plot", "Bubble Chart", "Wind Analysis"]
            )
            
            if analysis_type == "Distribution":
                metric = st.selectbox("Select metric for histogram:", selected_metrics, key="dist_metric")
                fn = get_metric_full_name(metric)
                st.markdown(f"### 📊 Probability Density Distribution: {metric} ({fn})")
                fig = create_distribution_plot(df, metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            elif analysis_type == "Scatter Plot":
                col1, col2, col3 = st.columns(3)
                with col1:
                    x_metric = st.selectbox("X-axis metric:", selected_metrics, key="scatter_x")
                with col2:
                    y_idx = min(1, len(selected_metrics)-1)
                    y_metric = st.selectbox("Y-axis metric:", selected_metrics, index=y_idx, key="scatter_y")
                with col3:
                    color_options = ["None"] + selected_metrics
                    color_opt = st.selectbox(
                        "Color by metric:", 
                        color_options, 
                        key="scatter_color"
                    )
                
                color_metric = None if color_opt == "None" else color_opt
                st.markdown(f"### 🔵 Bivariate Scatter: {y_metric} vs {x_metric}")
                fig = create_scatter_plot(df, x_metric, y_metric, color_metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            elif analysis_type == "Bubble Chart":
                if len(selected_metrics) < 3:
                    st.warning("⚠️ Please select at least 3 metrics from the sidebar for bubble chart analysis.")
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        x_metric = st.selectbox("X-axis:", selected_metrics, key="bubble_x")
                    with col2:
                        y_metric = st.selectbox("Y-axis:", selected_metrics, index=min(1, len(selected_metrics)-1), key="bubble_y")
                    with col3:
                        size_metric = st.selectbox("Bubble Size:", selected_metrics, index=min(2, len(selected_metrics)-1), key="bubble_size")
                    
                    color_options = ["None"] + selected_metrics
                    color_opt = st.selectbox(
                        "Color dimension:", 
                        color_options, 
                        key="bubble_color"
                    )
                    color_metric = None if color_opt == "None" else color_opt
                    
                    st.markdown(f"### 🫧 Multi-Dimensional Bubble Chart")
                    fig = create_bubble_chart(df, x_metric, y_metric, size_metric, color_metric)
                    st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            elif analysis_type == "Wind Analysis":
                if 'WS' in df.columns:
                    st.markdown("### 🌬️ Wind Speed & Gust Velocity Analysis")
                    fig = create_wind_distribution(df)
                    st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Wind Speed (WS)", f"{df['WS'].mean():.2f} m/s")
                    with col2:
                        st.metric("Peak Wind Speed (WS)", f"{df['WS'].max():.2f} m/s")
                    with col3:
                        if 'WSgust' in df.columns:
                            st.metric("Peak Wind Gust (WSgust)", f"{df['WSgust'].max():.2f} m/s")
                else:
                    st.warning("⚠️ Wind Speed (WS) data column not present in the current dataset.")

    # TAB 4: TEMPORAL PATTERNS
    with tab4:
        st.header("🌡️ Temporal & Diurnal Patterns")
        
        if 'Timestamp' not in df.columns:
            st.warning("⚠️ Timestamp column not found in this dataset. Temporal profiles require timestamp observations.")
        elif not selected_metrics:
            st.warning("⚠️ Please select at least one metric from the sidebar.")
        else:
            metric = st.selectbox("Select metric for pattern profile:", selected_metrics, key="pattern_metric")
            pattern_type = st.radio("Profile Type:", ["Hourly Diurnal Profile (24 Hours)", "Monthly Seasonal Profile (12 Months)"], horizontal=True)
            
            if "Hourly" in pattern_type:
                fig = create_hourly_pattern(df, metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            else:
                fig = create_monthly_pattern(df, metric)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})

    # TAB 5: CORRELATIONS
    with tab5:
        st.header("🔗 Environmental Correlation Analysis")
        
        if len(selected_metrics) < 2:
            st.warning("⚠️ Please select at least 2 metrics from the sidebar for correlation analysis.")
        else:
            st.markdown("### 🔗 Pearson Correlation Matrix")
            st.info("💡 Values close to **+1.0** indicate strong positive correlation (e.g. GHI and Module Temperature), while values near **-1.0** indicate inverse correlation (e.g. Temperature and Relative Humidity).")
            fig_corr = create_correlation_heatmap(df, selected_metrics)
            st.plotly_chart(fig_corr, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
            # Key correlations ranking
            st.markdown("---")
            st.markdown("### 🎯 Strongest Linear Relationships")
            corr_matrix = df[selected_metrics].corr()
            
            pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    c1 = corr_matrix.columns[i]
                    c2 = corr_matrix.columns[j]
                    pairs.append({
                        'Metric 1': f"{c1} ({get_metric_full_name(c1)})",
                        'Metric 2': f"{c2} ({get_metric_full_name(c2)})",
                        'Pearson r': corr_matrix.iloc[i, j]
                    })
            
            if pairs:
                corr_df = pd.DataFrame(pairs)
                corr_df['abs_r'] = corr_df['Pearson r'].abs()
                corr_df = corr_df.sort_values('abs_r', ascending=False).drop(columns=['abs_r'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🔺 Strongest Positive Correlations")
                    pos_df = corr_df[corr_df['Pearson r'] > 0].head(5)
                    if not pos_df.empty:
                        st.dataframe(pos_df.style.format({'Pearson r': '{:.3f}'}).background_gradient(cmap='Greens'), width="stretch")
                with col2:
                    st.markdown("#### 🔻 Strongest Negative Correlations")
                    neg_df = corr_df[corr_df['Pearson r'] < 0].sort_values('Pearson r').head(5)
                    if not neg_df.empty:
                        st.dataframe(neg_df.style.format({'Pearson r': '{:.3f}'}).background_gradient(cmap='Reds'), width="stretch")

    # TAB 6: DATA TABLE
    with tab6:
        st.header("📋 Raw Data Records & Export")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            num_rows = st.slider("Display row count:", 5, 100, 25)
        with col2:
            show_all_cols = st.checkbox("Show all columns in dataset", value=False)
        with col3:
            st.metric("Total Records", f"{len(df):,}")
        
        if show_all_cols:
            st.dataframe(df.head(num_rows), width="stretch")
        else:
            display_cols = (['Timestamp'] if 'Timestamp' in df.columns else []) + selected_metrics
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[display_cols].head(num_rows), width="stretch")
        
        st.markdown("---")
        st.markdown("### 📥 Export Filtered Dataset")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Download the currently loaded and filtered dataset in standard CSV format for external modeling, Python scripts, or reporting.")
        with col2:
            st.download_button(
                label="⬇️ Download CSV",
                data=convert_df_to_csv(df),
                file_name=f"solar_data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch"
            )

    # TAB 7: ABBREVIATIONS & GLOSSARY (NEW DEDICATED TAB)
    with tab7:
        st.header("📖 Solar Metric Abbreviations & Full Technical Reference")
        st.markdown("""
        This interactive reference lists all measurement abbreviations, full descriptive titles,
        SI units, physical formulas, and engineering significance used across the dashboard and solar energy meteorology.
        """)
        
        # Interactive Search & Filter
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search abbreviations or full descriptive names:", placeholder="e.g., GHI, Irradiance, Temperature, Wind, ModA")
        with col_s2:
            all_categories = ["All Categories"] + sorted(list(set(
                [data['category'] for data in METRIC_GLOSSARY.values()] + 
                [data['category'] for data in GENERAL_SOLAR_TERMS.values()]
            )))
            selected_cat = st.selectbox("Filter by Category:", all_categories)
        
        # Filter glossary data
        full_glossary = get_glossary_dataframe(include_general_terms=True)
        filtered_glossary = full_glossary.copy()
        
        if selected_cat != "All Categories":
            filtered_glossary = filtered_glossary[filtered_glossary['Category'] == selected_cat]
        
        if search_query:
            q = search_query.lower()
            filtered_glossary = filtered_glossary[
                filtered_glossary['Abbreviation'].str.lower().str.contains(q) |
                filtered_glossary['Full Name'].str.lower().str.contains(q) |
                filtered_glossary['Description'].str.lower().str.contains(q)
            ]
        
        st.markdown(f"**Showing {len(filtered_glossary)} definitions:**")
        st.dataframe(
            filtered_glossary,
            width="stretch",
            height=450,
            column_config={
                "Abbreviation": st.column_config.TextColumn("Abbreviation", width="small"),
                "Full Name": st.column_config.TextColumn("Full Descriptive Text", width="medium"),
                "Unit": st.column_config.TextColumn("Unit", width="small"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "Description": st.column_config.TextColumn("Definition & Operational Role", width="large")
            }
        )
        
        # Solar Irradiance Geometry & Physics Formula Section
        st.markdown("---")
        st.markdown("### ☀️ Fundamental Solar Irradiance Relationship")
        st.markdown(r"""
        The three fundamental solar radiation components (Global, Direct, and Diffuse) are linked by the astronomical cosine law:
        
        $$\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}$$
        
        Where:
        - **$\text{GHI}$ (Global Horizontal Irradiance)**: Total radiant solar flux received on a horizontal plane ($W/m^2$).
        - **$\text{DNI}$ (Direct Normal Irradiance)**: Radiant solar flux coming in a direct beam from the sun disk ($W/m^2$).
        - **$\theta_z$ (Solar Zenith Angle)**: The angle between the sun's position and the local vertical (zenith).
        - **$\text{DHI}$ (Diffuse Horizontal Irradiance)**: Solar radiant flux scattered downward by the atmosphere and clouds ($W/m^2$).
        """)
        
        st.markdown("---")
        st.markdown("### 🌍 Universal CSV Dataset Compatibility Guide")
        st.markdown("""
        | Data Provider / Source | Typical Timestamp Column | Typical Irradiance Columns | Compatibility Status |
        | :--- | :--- | :--- | :--- |
        | **10 Academy (Benin, Sierra Leone, Togo)** | `Timestamp` | `GHI`, `DNI`, `DHI`, `ModA`, `ModB` | ✅ Fully Supported |
        | **NASA POWER API / CSV** | `YEAR`, `MO`, `DY`, `HR` | `ALLSKY_SFC_SW_DWN` (mapped to GHI), `T2M` | ✅ Auto-standardized |
        | **NREL NSRDB** | `Year`, `Month`, `Day`, `Hour`, `Minute` | `GHI`, `DNI`, `DHI`, `Temperature` | ✅ Auto-standardized |
        | **PVGIS (European Commission)** | `time` / `Date` | `G(h)` (GHI), `Gb(n)` (DNI), `Gd(h)` (DHI) | ✅ Auto-standardized |
        | **Solargis / Meteonorm** | `DateTime` / `Date/Time` | `GHI`, `DNI`, `TEMP`, `WS` | ✅ Auto-standardized |
        | **Custom Weather Stations / Inverters** | Any date or datetime format | Any numeric measurement columns | ✅ Dynamically Discovered |
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <h3 style='color: #667eea; margin-bottom: 0.5rem;'>☀️ Solar Data Discovery</h3>
        <p style='color: #555; font-size: 1rem; margin: 0.25rem 0;'>
            Production Analytics Platform for Solar Radiation & Meteorological Datasets
        </p>
        <p style='color: #777; font-size: 0.85rem; margin: 0.25rem 0;'>
            Compatible with Benin, Sierra Leone, Togo, and solar CSV datasets worldwide.
        </p>
        <p style='color: #999; font-size: 0.8rem; margin-top: 0.75rem;'>
            Version 2.1.0 • Built with Streamlit, Plotly, and Pandas
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
