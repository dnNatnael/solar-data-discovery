"""
Automated Streamlit AppTests verifying that:
1. When running app/main.py, CSV data and visualizations are NOT displayed automatically.
2. All data, graphs, charts, and other visualizations are only displayed after the user uploads a CSV file.
3. Both sidebar upload and main landing upload work reliably and maintain state across reruns.
"""

import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

MAIN_APP_PATH = str(Path(__file__).parent.parent / "app" / "main.py")

SAMPLE_CSV_BYTES = b"""Timestamp,GHI,DNI,DHI,Tamb,WS,RH
2021-01-01 00:00:00,0.0,0.0,0.0,25.0,1.5,80.0
2021-01-01 01:00:00,15.2,5.1,10.1,24.5,2.0,82.0
2021-01-01 02:00:00,120.5,80.2,40.3,26.0,2.5,75.0
2021-01-01 03:00:00,450.0,350.0,100.0,29.0,3.1,65.0
2021-01-01 04:00:00,680.0,520.0,160.0,31.5,3.8,55.0
"""


def test_initial_launch_displays_no_data():
    """
    Verify that on initial startup (streamlit run app/main.py):
    - No CSV data is loaded or displayed automatically.
    - No visualization tabs, metric cards, or chart controls are rendered.
    - An informational banner instructs the user to upload a CSV file.
    """
    at = AppTest.from_file(MAIN_APP_PATH, default_timeout=30)
    at.run()

    # Must have no errors or exceptions
    assert not at.exception, f"Exceptions encountered: {at.exception}"

    # Visualizations and data tabs must NOT be displayed
    assert len(at.tabs) == 0, f"Expected 0 tabs before upload, but found {len(at.tabs)}"
    assert len(at.metric) == 0, f"Expected 0 metrics before upload, but found {len(at.metric)}"
    assert len(at.slider) == 0, f"Expected 0 sliders before upload, but found {len(at.slider)}"
    assert len(at.multiselect) == 0, f"Expected 0 multiselects before upload, but found {len(at.multiselect)}"

    # An upload instruction message must be shown
    info_texts = [info.value for info in at.info]
    assert any("upload a CSV file" in text for text in info_texts), "Upload instruction message not found"

    # File uploaders must be present for user action
    uploaders = at.get("file_uploader")
    assert len(uploaders) >= 1, "File uploader widget not found on initial launch"


def test_sidebar_upload_displays_all_visualizations():
    """
    Verify that after the user uploads a CSV file via sidebar:
    - All 7 visualization tabs are displayed.
    - Metrics, summaries, and charts are rendered.
    """
    at = AppTest.from_file(MAIN_APP_PATH, default_timeout=30)
    at.run()
    assert len(at.tabs) == 0

    # Locate the sidebar file uploader and upload test CSV
    sidebar_uploaders = at.sidebar.file_uploader
    assert len(sidebar_uploaders) > 0, "Sidebar file uploader missing"
    sidebar_uploaders[0].upload(filename="custom_solar_test.csv", content=SAMPLE_CSV_BYTES).run()

    assert not at.exception, f"Exceptions after sidebar upload: {at.exception}"
    assert len(at.tabs) == 7, f"Expected 7 visualization tabs, but found {len(at.tabs)}"

    expected_tab_prefixes = ["📊 Overview", "📈 Time Series", "🔍 Detailed Analysis", "🌡️ Patterns", "🔗 Correlations", "📋 Data Table", "📖 Abbreviations & Glossary"]
    tab_labels = [tab.label for tab in at.tabs]
    for expected in expected_tab_prefixes:
        assert any(expected in label for label in tab_labels), f"Missing tab: {expected}"

    # Metric multi-selector must be present in sidebar
    assert len(at.sidebar.multiselect) >= 1
    # Quick metrics should now be displayed
    assert len(at.metric) > 0


def test_landing_upload_and_reset():
    """
    Verify that uploading via the landing page dropzone displays all visualizations,
    and clicking the remove button returns the app to the initial empty state.
    """
    at = AppTest.from_file(MAIN_APP_PATH, default_timeout=30)
    at.run()
    assert len(at.tabs) == 0

    # Upload via the landing page uploader
    landing_uploader = at.get_by_key("landing_csv_uploader")
    assert landing_uploader is not None, "Landing page uploader missing"
    landing_uploader.upload(filename="landing_solar_test.csv", content=SAMPLE_CSV_BYTES).run()

    assert not at.exception, f"Exceptions after landing upload: {at.exception}"
    assert len(at.tabs) == 7, "All tabs should be displayed after landing upload"

    # Reset using the remove button
    remove_buttons = [b for b in at.sidebar.button if "Remove" in b.label]
    assert len(remove_buttons) == 1, "Remove / Clear button should be present"
    remove_buttons[0].click().run()

    # App must return to 0 tabs and no data displayed
    assert len(at.tabs) == 0, "Tabs should be removed after clicking reset button"


def test_nasa_power_csv_upload():
    """
    Verify that a NASA POWER CSV file with metadata header preamble
    and -999 missing values uploads and displays visualizations without errors.
    """
    nasa_content = (
        "-BEGIN HEADER-\n"
        "NASA/POWER Source Native Resolution Daily Data\n"
        "Dates (month/day/year): 09/01/2026 through 11/02/2026 in LST\n"
        "Location: Regional\n"
        "elevation from MERRA-2: Average for 0.5 x 0.625 degree lat/lon region = na meters\n"
        "The value for missing source data: -999\n"
        "parameter(s):\n"
        "ALLSKY_SFC_SW_DWN     CERES SYN1deg All Sky Irradiance\n"
        "-END HEADER-\n"
        "LAT,LON,YEAR,MO,DY,ALLSKY_SFC_SW_DWN\n"
        "31.5,-15.5,2026,9,1,6.6398\n"
        "31.5,-14.5,2026,9,1,-999.0\n"
        "31.5,-13.5,2026,9,2,5.4321\n"
    ).encode('utf-8')

    at = AppTest.from_file(MAIN_APP_PATH, default_timeout=30)
    at.run()
    assert len(at.tabs) == 0

    sidebar_uploaders = at.sidebar.file_uploader
    assert len(sidebar_uploaders) > 0
    sidebar_uploaders[0].upload(filename="POWER_Daily.csv", content=nasa_content).run()

    assert not at.exception, f"Exceptions after NASA POWER upload: {at.exception}"
    assert len(at.tabs) == 7, "All 7 tabs should render after NASA POWER upload"
    assert len(at.sidebar.success) > 0
    assert "POWER_Daily.csv" in at.sidebar.success[0].value

