"""
Data loading and preprocessing utilities for Solar Data Discovery Dashboard
Provides functions to load, standardize, validate, and document solar datasets from any source.
"""

import pandas as pd
import numpy as np
import os
import io
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List


# Comprehensive Glossary of Metric Abbreviations, Full Names, Units, and Descriptions
METRIC_GLOSSARY: Dict[str, Dict[str, str]] = {
    'GHI': {
        'full_name': 'Global Horizontal Irradiance',
        'unit': 'W/m²',
        'category': 'Solar Radiation',
        'description': 'Total amount of terrestrial solar radiation received from above by a horizontal surface. It is the sum of direct normal irradiance projected onto the horizontal plane and diffuse horizontal irradiance: GHI = DNI · cos(θz) + DHI.'
    },
    'DNI': {
        'full_name': 'Direct Normal Irradiance',
        'unit': 'W/m²',
        'category': 'Solar Radiation',
        'description': 'Solar radiation received per unit area by a surface held perpendicular (normal) to the direct sun rays. Crucial for Concentrated Solar Power (CSP) and solar tracking photovoltaic systems.'
    },
    'DHI': {
        'full_name': 'Diffuse Horizontal Irradiance',
        'unit': 'W/m²',
        'category': 'Solar Radiation',
        'description': 'Solar radiation scattered by atmospheric molecules, aerosols, water vapor, and clouds that reaches a horizontal surface from all directions in the sky hemisphere.'
    },
    'Tamb': {
        'full_name': 'Ambient Temperature',
        'unit': '°C',
        'category': 'Temperature & Humidity',
        'description': 'Dry-bulb temperature of the ambient surrounding air measured in the shade inside a radiation-shielded, ventilated sensor housing.'
    },
    'TModA': {
        'full_name': 'Module Temperature A',
        'unit': '°C',
        'category': 'Temperature & Humidity',
        'description': 'Temperature measured directly on the back surface of reference PV sensor module A. Crucial because silicon solar panel efficiency degrades by ~0.4% per °C rise above 25°C.'
    },
    'TModB': {
        'full_name': 'Module Temperature B',
        'unit': '°C',
        'category': 'Temperature & Humidity',
        'description': 'Temperature measured on the back surface of reference PV sensor module B for redundancy and thermal gradient analysis.'
    },
    'RH': {
        'full_name': 'Relative Humidity',
        'unit': '%',
        'category': 'Temperature & Humidity',
        'description': 'Ratio of the partial pressure of water vapor to the equilibrium vapor pressure at the current ambient temperature, indicating air moisture content.'
    },
    'WS': {
        'full_name': 'Wind Speed',
        'unit': 'm/s',
        'category': 'Wind & Atmosphere',
        'description': 'Average horizontal velocity of air movement at the anemometer height. Wind provides passive convective cooling that improves solar module performance.'
    },
    'WSgust': {
        'full_name': 'Wind Gust Speed',
        'unit': 'm/s',
        'category': 'Wind & Atmosphere',
        'description': 'Maximum peak momentary wind speed recorded during the measurement interval. Essential for structural mounting safety and mechanical stress analysis.'
    },
    'WSstdev': {
        'full_name': 'Wind Speed Standard Deviation',
        'unit': 'm/s',
        'category': 'Wind & Atmosphere',
        'description': 'Statistical standard deviation of wind speed over the measurement sampling window, serving as a proxy for atmospheric turbulence.'
    },
    'WD': {
        'full_name': 'Wind Direction',
        'unit': '° North',
        'category': 'Wind & Atmosphere',
        'description': 'Compass direction from which the wind originates, measured in degrees clockwise from True North (0° = North, 90° = East, 180° = South, 270° = West).'
    },
    'WDstdev': {
        'full_name': 'Wind Direction Standard Deviation',
        'unit': '°',
        'category': 'Wind & Atmosphere',
        'description': 'Angular standard deviation of wind direction, characterizing wind shiftiness and turbulence variability.'
    },
    'BP': {
        'full_name': 'Barometric Pressure',
        'unit': 'hPa',
        'category': 'Wind & Atmosphere',
        'description': 'Local atmospheric barometric air pressure measured at station altitude (1 hPa = 1 mbar = 100 Pa).'
    },
    'Precipitation': {
        'full_name': 'Precipitation / Rainfall Rate',
        'unit': 'mm',
        'category': 'Environmental',
        'description': 'Depth of liquid water accumulated over the measurement duration. Rain naturally washes dust and soiling off solar panels, temporarily restoring generation efficiency.'
    },
    'ModA': {
        'full_name': 'Sensor Module A Irradiance',
        'unit': 'W/m²',
        'category': 'Sensor Hardware',
        'description': 'Solar irradiance output reading from calibrated reference photovoltaic sensor module A.'
    },
    'ModB': {
        'full_name': 'Sensor Module B Irradiance',
        'unit': 'W/m²',
        'category': 'Sensor Hardware',
        'description': 'Solar irradiance output reading from calibrated reference photovoltaic sensor module B.'
    },
    'Cleaning': {
        'full_name': 'Panel Cleaning Event',
        'unit': 'Flag (0/1)',
        'category': 'Station Operations',
        'description': 'Binary indicator (1 = cleaning performed, 0 = uncleaned state) used to analyze dust/soiling accumulation rates and cleaning recovery benefits.'
    },
    'Comments': {
        'full_name': 'Quality Control Comments',
        'unit': 'Text',
        'category': 'Station Operations',
        'description': 'Station observer annotations, maintenance records, sensor calibration logs, or data quality flags.'
    }
}

# Broader Solar & Meteorological Terminology Glossary
GENERAL_SOLAR_TERMS: Dict[str, Dict[str, str]] = {
    'POA': {
        'full_name': 'Plane of Array Irradiance',
        'unit': 'W/m²',
        'category': 'General Solar Terms',
        'description': 'Total solar irradiance received on the surface of a tilted solar array matching the tilt and azimuth of the installation.'
    },
    'GNI': {
        'full_name': 'Global Normal Irradiance',
        'unit': 'W/m²',
        'category': 'General Solar Terms',
        'description': 'Total irradiance falling on a surface that is continuously oriented perpendicular to the sun direct rays.'
    },
    'PV': {
        'full_name': 'Photovoltaic',
        'unit': 'Technology',
        'category': 'General Solar Terms',
        'description': 'Technology that converts light (photons) directly into electricity (voltage) using semiconductor materials.'
    },
    'CSP': {
        'full_name': 'Concentrated Solar Power',
        'unit': 'Technology',
        'category': 'General Solar Terms',
        'description': 'Solar thermal power generation using mirrors or lenses to concentrate sunlight onto a small area.'
    },
    'PR': {
        'full_name': 'Performance Ratio',
        'unit': '%',
        'category': 'General Solar Terms',
        'description': 'Quality factor of a PV plant: ratio of actual AC energy generated to theoretical DC energy under ideal conditions.'
    },
    'STC': {
        'full_name': 'Standard Test Conditions',
        'unit': 'Standard',
        'category': 'General Solar Terms',
        'description': 'Laboratory testing standard for rating solar PV panels: 1000 W/m² irradiance, 25°C cell temperature, and AM 1.5 spectrum.'
    },
    'NOCT': {
        'full_name': 'Nominal Operating Cell Temperature',
        'unit': '°C',
        'category': 'General Solar Terms',
        'description': 'Estimated cell temperature reached by open-rack PV modules under 800 W/m² irradiance, 20°C ambient, and 1 m/s wind.'
    },
    'UTC': {
        'full_name': 'Coordinated Universal Time',
        'unit': 'Time Standard',
        'category': 'General Solar Terms',
        'description': 'Global primary time standard used to ensure consistent solar position calculations regardless of local daylight saving rules.'
    },
    'QC': {
        'full_name': 'Quality Control',
        'unit': 'Process',
        'category': 'General Solar Terms',
        'description': 'Data validation procedures checking physical limits, sensor ranges, tracker alignment, and anomalous readings.'
    }
}

# Mapping of common column aliases from diverse sources (e.g., NASA POWER, NSRDB, PVGIS, local loggers)
METRIC_ALIASES: Dict[str, str] = {
    'ghi': 'GHI',
    'global_horizontal': 'GHI',
    'global_horizontal_irradiance': 'GHI',
    'global_irradiance': 'GHI',
    'ghi_w_m2': 'GHI',
    'ghi_(w/m2)': 'GHI',
    'ghi_clean': 'GHI',
    
    'dni': 'DNI',
    'direct_normal': 'DNI',
    'direct_normal_irradiance': 'DNI',
    'direct_irradiance': 'DNI',
    'dni_w_m2': 'DNI',
    'dni_(w/m2)': 'DNI',
    'dni_clean': 'DNI',
    
    'dhi': 'DHI',
    'diffuse_horizontal': 'DHI',
    'diffuse_horizontal_irradiance': 'DHI',
    'diffuse_irradiance': 'DHI',
    'dhi_w_m2': 'DHI',
    'dhi_(w/m2)': 'DHI',
    'dhi_clean': 'DHI',
    
    'tamb': 'Tamb',
    'ambient_temp': 'Tamb',
    'ambient_temperature': 'Tamb',
    'air_temp': 'Tamb',
    'air_temperature': 'Tamb',
    'temp': 'Tamb',
    'temperature': 'Tamb',
    't_amb': 'Tamb',
    
    'rh': 'RH',
    'relative_humidity': 'RH',
    'humidity': 'RH',
    'rel_humidity': 'RH',
    
    'ws': 'WS',
    'wind_speed': 'WS',
    'windspeed': 'WS',
    'wind_speed_10m': 'WS',
    'wind_speed_2m': 'WS',
    
    'wsgust': 'WSgust',
    'wind_gust': 'WSgust',
    'gust_speed': 'WSgust',
    'gust': 'WSgust',
    
    'wsstdev': 'WSstdev',
    'wind_speed_stdev': 'WSstdev',
    
    'wd': 'WD',
    'wind_direction': 'WD',
    'wind_dir': 'WD',
    'winddir': 'WD',
    
    'wdstdev': 'WDstdev',
    'wind_direction_stdev': 'WDstdev',
    
    'bp': 'BP',
    'barometric_pressure': 'BP',
    'pressure': 'BP',
    'surface_pressure': 'BP',
    'air_pressure': 'BP',
    
    'precip': 'Precipitation',
    'precipitation': 'Precipitation',
    'rainfall': 'Precipitation',
    'rain': 'Precipitation',
    
    'tmoda': 'TModA',
    't_mod_a': 'TModA',
    'mod_temp_a': 'TModA',
    'module_temperature_a': 'TModA',
    
    'tmodb': 'TModB',
    't_mod_b': 'TModB',
    'mod_temp_b': 'TModB',
    'module_temperature_b': 'TModB',
    
    'moda': 'ModA',
    'mod_a': 'ModA',
    'module_a': 'ModA',
    
    'modb': 'ModB',
    'mod_b': 'ModB',
    'module_b': 'ModB',
    
    'cleaning': 'Cleaning',
    'cleaned': 'Cleaning',

    # NASA POWER and satellite reanalysis aliases
    'allsky_sfc_sw_dwn': 'GHI',
    'all_sky_surface_shortwave_downward_irradiance': 'GHI',
    'allsky_sfc_sw_dni': 'DNI',
    'all_sky_surface_shortwave_direct_normal_irradiance': 'DNI',
    'allsky_sfc_sw_diff': 'DHI',
    'all_sky_surface_diffuse_horizontal_irradiance': 'DHI',
    'clrsky_sfc_sw_dwn': 'GHI_ClearSky',
    'allsky_kt': 'Clearness_Index',
    't2m': 'Tamb',
    't2m_min': 'Tamb_Min',
    't2m_max': 'Tamb_Max',
    't2mdew': 'Dew_Point',
    'rh2m': 'RH',
    'ws10m': 'WS',
    'ws2m': 'WS',
    'wd10m': 'WD',
    'wd2m': 'WD',
    'ps': 'BP',
    'prectotcorr': 'Precipitation',
}


def get_metric_full_name(metric: str) -> str:
    """Return the full descriptive name for a metric abbreviation."""
    if metric in METRIC_GLOSSARY:
        return METRIC_GLOSSARY[metric]['full_name']
    if metric in GENERAL_SOLAR_TERMS:
        return GENERAL_SOLAR_TERMS[metric]['full_name']
    return metric


def get_metric_unit(metric: str) -> str:
    """Return measurement unit string for a metric."""
    if metric in METRIC_GLOSSARY:
        return METRIC_GLOSSARY[metric]['unit']
    if metric in GENERAL_SOLAR_TERMS:
        return GENERAL_SOLAR_TERMS[metric]['unit']
    return ""


def get_metric_category(metric: str) -> str:
    """Return the thematic category for a metric."""
    if metric in METRIC_GLOSSARY:
        return METRIC_GLOSSARY[metric]['category']
    if metric in GENERAL_SOLAR_TERMS:
        return GENERAL_SOLAR_TERMS[metric]['category']
    return "Other / Custom Measurement"


def get_metric_description(metric: str) -> str:
    """Return detailed description for a metric."""
    if metric in METRIC_GLOSSARY:
        return METRIC_GLOSSARY[metric]['description']
    if metric in GENERAL_SOLAR_TERMS:
        return GENERAL_SOLAR_TERMS[metric]['description']
    return f"Measurement column: {metric}"


def get_metric_label(metric: str) -> str:
    """
    Format a metric identifier with its full descriptive text and unit for UI display.
    Example: 'GHI' -> 'GHI — Global Horizontal Irradiance (W/m²)'
    """
    if metric in METRIC_GLOSSARY:
        full_name = METRIC_GLOSSARY[metric]['full_name']
        unit = METRIC_GLOSSARY[metric]['unit']
        return f"{metric} — {full_name} ({unit})"
    if metric in GENERAL_SOLAR_TERMS:
        full_name = GENERAL_SOLAR_TERMS[metric]['full_name']
        unit = GENERAL_SOLAR_TERMS[metric]['unit']
        return f"{metric} — {full_name} ({unit})"
    return metric


def get_glossary_dataframe(include_general_terms: bool = True) -> pd.DataFrame:
    """
    Generate a clean pandas DataFrame containing all metric abbreviations,
    full names, units, categories, and descriptions.
    """
    records = []
    for abbr, data in METRIC_GLOSSARY.items():
        records.append({
            'Abbreviation': abbr,
            'Full Name': data['full_name'],
            'Unit': data['unit'],
            'Category': data['category'],
            'Description': data['description']
        })
    
    if include_general_terms:
        for abbr, data in GENERAL_SOLAR_TERMS.items():
            records.append({
                'Abbreviation': abbr,
                'Full Name': data['full_name'],
                'Unit': data['unit'],
                'Category': data['category'],
                'Description': data['description']
            })
            
    return pd.DataFrame(records)


def discover_local_csv_files(directory: str = "data") -> List[str]:
    """
    Recursively discover all CSV files present in the specified directory.
    Enables automatic loading of any newly added country or solar dataset.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    csv_paths = []
    for file_path in sorted(dir_path.rglob("*.csv")):
        csv_paths.append(str(file_path))
    return csv_paths


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate if the file exists and is a CSV or text dataset file
    
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
    
    if path.suffix.lower() not in ['.csv', '.txt', '.tsv', '.dat']:
        return False, f"File must be a CSV/text dataset file, got: {path.suffix}"
    
    return True, ""


def read_csv_flexible(file_or_path: Any) -> pd.DataFrame:
    """
    Read CSV file with automatic delimiter, encoding, and metadata header detection.
    Supports standard comma-separated files, semicolon-separated (European),
    tab-separated datasets, and NASA POWER datasets with '-BEGIN HEADER-' / '-END HEADER-' blocks.
    Automatically handles missing value sentinels (-999, -999.0, na, NA).
    """
    na_vals = ['-999', '-999.0', -999, -999.0, '-9999', '-9999.0', 'na', 'NA', 'null', 'None', '-']

    # 1. Extract raw text from file_or_path (handles path strings, Path, BytesIO, StringIO, UploadedFile)
    text = None
    if isinstance(file_or_path, (str, Path)):
        p = Path(file_or_path)
        if p.exists() and p.is_file():
            try:
                text = p.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                text = p.read_text(encoding='latin1', errors='replace')
    elif hasattr(file_or_path, 'read'):
        if hasattr(file_or_path, 'seek'):
            file_or_path.seek(0)
        raw = file_or_path.read()
        if hasattr(file_or_path, 'seek'):
            file_or_path.seek(0)
        if isinstance(raw, bytes):
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                text = raw.decode('latin1', errors='replace')
        else:
            text = str(raw)
    elif isinstance(file_or_path, bytes):
        try:
            text = file_or_path.decode('utf-8')
        except UnicodeDecodeError:
            text = file_or_path.decode('latin1', errors='replace')

    # If text was extracted, clean preambles and parse
    if text is not None:
        # Check for NASA POWER header block ending with '-END HEADER-'
        if '-END HEADER-' in text.upper():
            lines = text.splitlines(keepends=True)
            end_idx = -1
            for i, line in enumerate(lines):
                if '-END HEADER-' in line.upper():
                    end_idx = i
                    break
            if end_idx != -1 and end_idx + 1 < len(lines):
                text = ''.join(lines[end_idx + 1:]).lstrip('\r\n ')

        # Try standard comma-separated read first
        try:
            df = pd.read_csv(io.StringIO(text), na_values=na_vals)
            if len(df.columns) == 1 and ';' in str(df.columns[0]):
                df = pd.read_csv(io.StringIO(text), sep=';', na_values=na_vals)
            elif len(df.columns) == 1 and '\t' in str(df.columns[0]):
                df = pd.read_csv(io.StringIO(text), sep='\t', na_values=na_vals)
            return df
        except Exception:
            try:
                return pd.read_csv(io.StringIO(text), sep=None, engine='python', na_values=na_vals)
            except Exception:
                return pd.read_csv(io.StringIO(text), encoding='latin1', sep=None, engine='python', na_values=na_vals)

    # Fallback to direct pd.read_csv if file_or_path wasn't extracted as text
    try:
        df = pd.read_csv(file_or_path, na_values=na_vals)
        if len(df.columns) == 1 and ';' in str(df.columns[0]):
            if hasattr(file_or_path, 'seek'):
                file_or_path.seek(0)
            df = pd.read_csv(file_or_path, sep=';', na_values=na_vals)
        return df
    except Exception:
        if hasattr(file_or_path, 'seek'):
            file_or_path.seek(0)
        try:
            return pd.read_csv(file_or_path, sep=None, engine='python', na_values=na_vals)
        except Exception:
            if hasattr(file_or_path, 'seek'):
                file_or_path.seek(0)
            return pd.read_csv(file_or_path, encoding='latin1', sep=None, engine='python', na_values=na_vals)


def standardize_solar_dataframe(df: pd.DataFrame, parse_dates: bool = True) -> pd.DataFrame:
    """
    Standardize timestamp and metric column names to support ANY solar dataset worldwide.
    Handles flexible date column names, separate Year/Month/Day columns, and case-insensitive aliases.
    
    Args:
        df: Input DataFrame
        parse_dates: Whether to parse the timestamp column as datetime
        
    Returns:
        Standardized DataFrame
    """
    df = df.copy()
    
    # 1. Normalize Timestamp column if 'Timestamp' is not directly present
    if 'Timestamp' not in df.columns:
        # Check normalized column names (lowercase, stripped, underscores)
        col_normalized = {
            col.lower().strip().replace(' ', '_').replace('/', '_').replace('-', '_').replace('(', '').replace(')', ''): col
            for col in df.columns
        }
        
        timestamp_candidates = [
            'timestamp', 'datetime', 'date_time', 'time', 'date', 'dt',
            'timestamp_utc', 'time_utc', 'utc_time', 'datetime_utc',
            'recorded_at', 'observation_time', 'period', 'epoch', 'date_time_utc'
        ]
        
        matched_col = None
        for cand in timestamp_candidates:
            if cand in col_normalized:
                matched_col = col_normalized[cand]
                break
        
        if matched_col:
            df = df.rename(columns={matched_col: 'Timestamp'})
        else:
            # Check if separate Year, Month, Day columns exist (supports year/yr, month/mo, day/dy, hour/hr)
            cols_lower = {c.lower().strip(): c for c in df.columns}
            col_year = cols_lower.get('year') or cols_lower.get('yr')
            col_month = cols_lower.get('month') or cols_lower.get('mo')
            col_day = cols_lower.get('day') or cols_lower.get('dy')
            col_hour = cols_lower.get('hour') or cols_lower.get('hr')
            col_minute = cols_lower.get('minute') or cols_lower.get('min')
            col_second = cols_lower.get('second') or cols_lower.get('sec')

            if col_year and col_month and col_day:
                dt_dict = {
                    'year': df[col_year],
                    'month': df[col_month],
                    'day': df[col_day]
                }
                if col_hour:
                    dt_dict['hour'] = df[col_hour]
                    if col_minute:
                        dt_dict['minute'] = df[col_minute]
                        if col_second:
                            dt_dict['second'] = df[col_second]
                try:
                    df['Timestamp'] = pd.to_datetime(dt_dict, errors='coerce')
                except Exception:
                    pass

    # 2. Parse timestamp if it exists and parse_dates is True
    if parse_dates and 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    
    # 3. Standardize common metric aliases to canonical abbreviations
    # Only map if the target standard name is not already present
    rename_mapping = {}
    for col in df.columns:
        if col == 'Timestamp':
            continue
        clean_key = col.lower().strip().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        if clean_key in METRIC_ALIASES:
            canonical_name = METRIC_ALIASES[clean_key]
            if canonical_name not in df.columns and canonical_name != col:
                rename_mapping[col] = canonical_name
    
    if rename_mapping:
        df = df.rename(columns=rename_mapping)
    
    return df


def load_solar_data(file_path: str, parse_dates: bool = True) -> Optional[pd.DataFrame]:
    """
    Load solar dataset from CSV file with proper validation and flexible parsing
    
    Args:
        file_path: Path to the CSV file
        parse_dates: Whether to parse the Timestamp column as datetime
        
    Returns:
        DataFrame with standardized solar data
    """
    is_valid, error_msg = validate_file_path(file_path)
    
    if not is_valid:
        raise FileNotFoundError(error_msg)
    
    try:
        raw_df = read_csv_flexible(file_path)
        return standardize_solar_dataframe(raw_df, parse_dates=parse_dates)
    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")


def get_available_metrics(df: pd.DataFrame) -> List[str]:
    """
    Get list of available numeric metrics from the dataframe.
    Prioritizes standard solar metrics first, and automatically includes
    any other numeric measurement columns so ANY CSV can be analyzed.
    
    Args:
        df: Solar dataset DataFrame
        
    Returns:
        List of plottable metric column names
    """
    # Standard solar & meteorological metrics in priority order
    priority_metrics = [
        'GHI', 'DNI', 'DHI', 'Tamb', 'TModA', 'TModB', 'RH', 'WS', 
        'WSgust', 'WSstdev', 'WD', 'WDstdev', 'BP', 'Precipitation', 
        'ModA', 'ModB', 'Cleaning'
    ]
    
    # Identify priority columns that are numeric and contain at least one valid value
    available = []
    for col in priority_metrics:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            if df[col].notna().sum() > 0:
                available.append(col)
    
    # Automatically discover any other numeric measurement columns (e.g., from other weather stations or sensors)
    ignored_col_names = {
        'id', 'index', 'unnamed: 0', 'year', 'month', 'day', 'hour', 
        'minute', 'second', 'comments', 'comment', 'notes',
        'yr', 'mo', 'dy', 'hr', 'min', 'sec',
        'lat', 'lon', 'latitude', 'longitude', 'elevation'
    }
    
    other_numeric = []
    for col in df.select_dtypes(include=['number']).columns:
        if col not in available and col.lower().strip() not in ignored_col_names:
            if df[col].notna().sum() > 0:
                other_numeric.append(col)
    
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
        valid_dates = df['Timestamp'].dropna()
        if valid_dates.empty:
            return None, None
        return valid_dates.min(), valid_dates.max()
    except Exception:
        return None, None


def filter_by_date_range(df: pd.DataFrame, start_date: Any, end_date: Any) -> pd.DataFrame:
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
    
    try:
        # Include the entire end date up to end of day
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        
        mask = (df['Timestamp'] >= start_ts) & (df['Timestamp'] <= end_ts)
        return df[mask]
    except Exception:
        return df


def get_summary_statistics(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
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
        if metric in df.columns and pd.api.types.is_numeric_dtype(df[metric]):
            metric_data = df[metric].dropna()
            if not metric_data.empty:
                stats_dict[metric] = {
                    'Mean': metric_data.mean(),
                    'Median': metric_data.median(),
                    'Std Dev': metric_data.std(),
                    'Min': metric_data.min(),
                    'Max': metric_data.max(),
                    'Count': int(metric_data.count())
                }
    
    if not stats_dict:
        return pd.DataFrame()
        
    return pd.DataFrame(stats_dict).T


def get_top_hours(df: pd.DataFrame, metric: str, top_n: int = 10) -> pd.DataFrame:
    """
    Get top N records with highest values for a given metric
    
    Args:
        df: Solar dataset DataFrame
        metric: Metric column to analyze
        top_n: Number of top records to return
        
    Returns:
        DataFrame with top N records
    """
    if metric not in df.columns or 'Timestamp' not in df.columns:
        return pd.DataFrame()
    
    valid_data = df.dropna(subset=[metric, 'Timestamp'])
    if valid_data.empty:
        return pd.DataFrame()
        
    top_df = valid_data.nlargest(top_n, metric)[['Timestamp', metric]].copy()
    top_df = top_df.reset_index(drop=True)
    return top_df
