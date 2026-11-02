# ☀️ Solar Data Discovery

A comprehensive data analysis and interactive visualization platform for solar radiation and meteorological data. This project includes exploratory data analysis, statistical insights, and an **interactive Streamlit dashboard** compatible with solar measurement datasets worldwide (with initial focus on Benin, Sierra Leone, and Togo).

## 🎯 Project Overview

This project analyzes solar radiation measurement data to identify key patterns, trends, and insights that inform solar energy investments and system design. The analysis includes:

- **Data Cleaning & Quality Assessment**
- **Statistical Analysis & Distribution Modeling**
- **Time Series & Diurnal Pattern Analysis**
- **Environmental Correlation Studies**
- **Interactive Web Dashboard** for real-time visualization & CSV export

## 📁 Project Structure

```
solar-data-discovery/
├── .github/
│   └── workflows/
│       └── unittests.yml          # CI/CD workflows
├── .vscode/
│   └── settings.json              # VS Code configurations
├── app/
│   ├── __init__.py
│   ├── main.py                    # Streamlit dashboard application
│   └── utils.py                   # Dashboard utilities
├── data/                          # Data folder (gitignored)
│   ├── benin-malanville.csv
│   ├── sierraleone-bumbuna.csv
│   └── togo-dapaong_qc.csv
├── notebooks/
│   ├── __init__.py
│   ├── eda.ipynb                  # Exploratory Data Analysis
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Data loading utilities
│   └── plot_utils.py              # Reusable plotting functions
├── scripts/
│   ├── __init__.py
│   └── README.md
├── tests/
│   ├── __init__.py
│   └── test_*.py                  # Unit tests
├── .gitignore
├── requirements.txt               # Project dependencies
└── README.md
```

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/solar-challenge-week0.git
cd solar-challenge-week0
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Your Data

Place your cleaned CSV files in the `data/` folder:
- `data/benin-malanville.csv`
- `data/sierraleone-bumbuna.csv`
- `data/togo-dapaong_qc.csv`

**Note:** The `data/` folder is gitignored to keep the repository lightweight.

## 📊 Interactive Dashboard

### Running the Dashboard Locally

To launch the interactive Streamlit dashboard:

```bash
streamlit run app/main.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`.

### Dashboard Features

The dashboard provides the following interactive features:

#### 🎛️ **Sidebar Controls**
- **Upload CSV Dataset**: On launch, data from CSV files is **not** displayed automatically. All data, graphs, charts, and visualizations are rendered only after the user uploads a CSV file.
  - 📤 **Upload Any CSV File**: Drag & drop any solar or meteorological CSV dataset from any region, station, or country (Benin, Sierra Leone, Togo, NASA POWER, NREL NSRDB, PVGIS, Solargis, etc.) via sidebar or the landing dropzone.
  - 📥 **Sample Datasets Available**: Convenient one-click download buttons for sample datasets (Benin, Sierra Leone, Togo) to test uploading immediately.
- **Metric Selection**: Multi-select to choose one or more metrics (GHI, DNI, DHI, Tamb, WS, etc.) for analysis (appears once data is uploaded)
- **Date Range Filter**: Filter records interactively by date
- **Dataset Information**: Summary record counts, column counts, and timestamp spans
- **Sidebar Abbreviations Glossary**: Quick expandable lookup for abbreviations while navigating any tab

#### 📈 **Visualization & Analytics Tabs**

1. **📊 Overview Tab**
   - Statistical summary table (Mean, Median, Std Dev, Min, Max, Count)
   - Quick metrics displaying current values with peak percentages and full names
   - Metric definitions and abbreviations reference expander
   - Interactive boxplot comparison with full names in hover tooltips

2. **📈 Time Series Tab**
   - Dynamic time series plots with full metric titles and units
   - Peak readings table (Top 10 highest measurement intervals)
   - Summary figures (Peak maximum, average, standard deviation)

3. **🔍 Detailed Analysis Tab**
   - Probability density distribution histograms
   - Bivariate scatter plots with color coding
   - 3D multi-dimensional bubble charts
   - Wind speed and gust velocity distributions

4. **🌡️ Patterns Tab**
   - Diurnal hourly profile (24-hour average cycle)
   - Seasonal monthly profile (12-month calendar cycle)

5. **🔗 Correlations Tab**
   - Interactive Pearson correlation heatmap
   - Strongest positive and negative linear correlations ranking

6. **📋 Data Table Tab**
   - Interactive data preview with customizable row count
   - One-click filtered CSV dataset export

7. **📖 Abbreviations & Glossary Tab**
   - Comprehensive interactive dictionary of all solar metric abbreviations and full descriptive text
   - Real-time search filter and category selector
   - Fundamental solar geometry formula breakdown: $\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}$
   - Compatibility guide for external datasets (NASA POWER, NREL NSRDB, PVGIS, Solargis)

### Dashboard Usage Example

```python
# Example workflow:
# 1. Start the dashboard
streamlit run app/main.py

# 2. In the sidebar:
#    - Select "Use Local Path"
#    - Choose "Benin" from dropdown
#    - Click "Load Data"

# 3. Select metrics:
#    - Choose GHI, DNI, DHI, Tamb

# 4. Explore visualizations:
#    - View summary statistics in Overview tab
#    - Analyze time series patterns
#    - Check correlations between metrics
```

## 🌐 Deploying to Streamlit Community Cloud

### Prerequisites
1. A GitHub account
2. Your repository pushed to GitHub
3. A Streamlit Community Cloud account (free at [streamlit.io/cloud](https://streamlit.io/cloud))

### Deployment Steps

1. **Push Your Code to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit dashboard"
   git push origin main
   ```

2. **Sign in to Streamlit Community Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Deploy New App**
   - Click "New app"
   - Select your repository: `<your-username>/solar-challenge-week0`
   - Set branch: `main`
   - Set main file path: `app/main.py`
   - Click "Deploy"

4. **Configure App Settings** (Optional)
   - Set custom URL subdomain
   - Configure secrets if needed
   - Set Python version (3.8+)

5. **Upload Your Data**
   Since CSV files are not in the repo, use the dashboard's file upload feature to load your data directly in the deployed app.

### Important Notes for Deployment

- ✅ **No CSV files are included in the repository** (they're gitignored)
- ✅ **All code uses relative imports** for compatibility
- ✅ **Dependencies are specified in requirements.txt**
- ✅ **The app supports file upload** for data loading
- ✅ **Dashboard is fully self-contained** and doesn't require external files

### Troubleshooting Deployment

If you encounter issues:

1. **Import Errors**: Ensure all imports use relative paths
2. **Module Not Found**: Verify `requirements.txt` includes all dependencies
3. **File Not Found**: Use the file upload feature instead of local paths
4. **Memory Issues**: Consider sampling large datasets before upload

## 🔧 Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Format your code using:

```bash
black .
flake8 .
```

## 📦 Dependencies

Main dependencies include:
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Static visualizations
- **seaborn**: Statistical visualizations
- **streamlit**: Interactive dashboard framework
- **plotly**: Interactive plotting library
- **scipy**: Scientific computing

See `requirements.txt` for complete list.

## 📝 Solar Metric Abbreviations & Full Descriptive Names

The platform standardizes and recognizes solar and meteorological variables from any country or station:

| Abbreviation | Full Name | Unit | Category | Description |
|:---|:---|:---|:---|:---|
| **Timestamp** | Date and Time | YYYY-MM-DD HH:MM:SS | Time | Timestamp of observation (auto-detected from various formats) |
| **GHI** | Global Horizontal Irradiance | W/m² | Solar Radiation | Total solar radiation received on a horizontal surface ($\text{GHI} = \text{DNI} \cos\theta_z + \text{DHI}$) |
| **DNI** | Direct Normal Irradiance | W/m² | Solar Radiation | Direct beam solar radiation received perpendicular to the sun's rays |
| **DHI** | Diffuse Horizontal Irradiance | W/m² | Solar Radiation | Solar radiation scattered by the atmosphere and clouds onto a horizontal plane |
| **Tamb** | Ambient Temperature | °C | Temperature & Humidity | Dry-bulb ambient air temperature in the shade |
| **TModA** | Module Temperature A | °C | Temperature & Humidity | Rear surface temperature of reference PV sensor module A |
| **TModB** | Module Temperature B | °C | Temperature & Humidity | Rear surface temperature of reference PV sensor module B |
| **RH** | Relative Humidity | % | Temperature & Humidity | Percentage of water vapor saturation in ambient air |
| **WS** | Wind Speed | m/s | Wind & Atmosphere | Average horizontal air velocity (cools PV modules) |
| **WSgust** | Wind Gust Speed | m/s | Wind & Atmosphere | Peak momentary wind speed during the observation window |
| **WSstdev** | Wind Speed Standard Deviation | m/s | Wind & Atmosphere | Standard deviation of wind speed (proxy for turbulence) |
| **WD** | Wind Direction | ° North | Wind & Atmosphere | Direction from which wind blows (0° to 360° clockwise from True North) |
| **WDstdev** | Wind Direction Std Dev | ° | Wind & Atmosphere | Angular standard deviation of wind direction |
| **BP** | Barometric Pressure | hPa | Wind & Atmosphere | Atmospheric station barometric pressure (1 hPa = 1 mbar) |
| **Precipitation** | Precipitation / Rainfall | mm | Environmental | Liquid water accumulation depth (washes dust off panels) |
| **ModA** | Sensor Module A Irradiance | W/m² | Sensor Hardware | Irradiance output reading from reference PV cell A |
| **ModB** | Sensor Module B Irradiance | W/m² | Sensor Hardware | Irradiance output reading from reference PV cell B |
| **Cleaning** | Panel Cleaning Event | Flag (0/1) | Operations | Binary flag indicating when solar modules were cleaned |
| **Comments** | Quality Control Comments | Text | Operations | Operational notes, anomalies, or calibration logs |
| **POA** | Plane of Array Irradiance | W/m² | General Solar | Solar radiation received on the tilted surface of PV panels |
| **PR** | Performance Ratio | % | General Solar | Ratio of actual solar plant generation to nominal expected output |

## 🎓 Learning Objectives

This project demonstrates:
- ✅ Data cleaning and preprocessing
- ✅ Exploratory data analysis (EDA)
- ✅ Statistical analysis and hypothesis testing
- ✅ Time series analysis
- ✅ Interactive dashboard development
- ✅ Cloud deployment
- ✅ Production-ready code architecture

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is part of the 10 Academy KAIM program.

## 👥 Authors

- [Natnael Yilma](https://github.com/dnNatnael)

## 🙏 Acknowledgments

- 10 Academy KAIM Program
- Solar radiation data providers
- Streamlit community

---

**Note**: Remember to update file paths in the dashboard to match your local directory structure before running locally. For deployment, use the file upload feature.
