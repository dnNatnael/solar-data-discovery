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
- **Data Source Selection**: Upload CSV file or use local path
- **Country Selection**: Choose from Benin, Sierra Leone, Togo, or custom path
- **Metric Selection**: Multi-select from GHI, DNI, DHI, Tamb, RH, WS, WSgust, etc.
- **Date Range Filter**: Filter data by specific date ranges
- **Dataset Information**: View record counts and date ranges

#### 📈 **Visualization Tabs**

1. **Overview Tab**
   - Summary statistics (Mean, Median, Std Dev, Min, Max)
   - Quick metrics display
   - Interactive boxplot for metric comparison

2. **Time Series Tab**
   - Dynamic time series plots
   - Peak hours analysis (Top 10 highest values)
   - Temporal trend visualization

3. **Detailed Analysis Tab**
   - Distribution plots with histograms
   - Scatter plots with customizable axes
   - Bubble charts for multi-dimensional analysis
   - Wind speed distribution analysis

4. **Patterns Tab**
   - Hourly pattern analysis (average by hour of day)
   - Monthly pattern analysis (average by month)
   - Seasonal trend identification

5. **Correlations Tab**
   - Interactive correlation heatmap
   - Identify relationships between metrics

6. **Data Table Tab**
   - View raw data with customizable row counts
   - Download filtered data as CSV

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

## 📝 Data Format

Expected CSV format for solar datasets:

| Column | Description | Unit |
|--------|-------------|------|
| Timestamp | Date and time of measurement | datetime |
| GHI | Global Horizontal Irradiance | W/m² |
| DNI | Direct Normal Irradiance | W/m² |
| DHI | Diffuse Horizontal Irradiance | W/m² |
| Tamb | Ambient Temperature | °C |
| RH | Relative Humidity | % |
| WS | Wind Speed | m/s |
| WSgust | Wind Gust Speed | m/s |
| BP | Barometric Pressure | hPa |
| Precipitation | Precipitation | mm |

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
