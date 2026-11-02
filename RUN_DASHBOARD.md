# 🚀 Running the Solar Challenge Dashboard

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app/main.py
```

### 3. Access the Dashboard
The dashboard will automatically open in your browser at:
- **Local**: http://localhost:8501
- **Network**: http://YOUR_IP:8501

## 📱 Testing Responsive Design

### Desktop Browser
1. Open the dashboard in your browser
2. Press `F12` to open Developer Tools
3. Click the device toolbar icon (or press `Ctrl+Shift+M`)
4. Test different screen sizes:
   - Mobile: 375x667 (iPhone)
   - Tablet: 768x1024 (iPad)
   - Desktop: 1920x1080

### Real Devices
```bash
# Allow network access
streamlit run app/main.py --server.address 0.0.0.0
```
Then access from your mobile/tablet using your computer's IP address.

## 📊 Using the Dashboard

### Loading Data (Upload Required)

When you run `streamlit run app/main.py`, data from CSV files is **not** displayed automatically. All data, graphs, charts, and other visualizations are only displayed after uploading a CSV file.

#### How to Upload:
1. Open the dashboard at `http://localhost:8501`.
2. In the sidebar under **📤 Upload CSV Dataset** (or in the center upload dropzone), click **Browse files** or drag & drop any solar/meteorological CSV file.
3. *Don't have a dataset handy?* Expand **"Need sample datasets to test upload?"** on the landing screen, download a sample CSV (Benin, Sierra Leone, or Togo), and upload it.
4. Once uploaded, all 7 analysis tabs, graphs, charts, and visualizations are instantly rendered.

### Exploring Visualizations

#### 📊 Overview Tab
- View statistical summaries
- Compare metric distributions with boxplots
- See quick metrics and key statistics

#### 📈 Time Series Tab
- Select a metric to analyze over time
- View top 10 peak hours
- Explore key statistics

#### 🔍 Detailed Analysis Tab
- **Distribution**: Histogram of metric values
- **Scatter Plot**: Relationship between two metrics
- **Bubble Chart**: Multi-dimensional analysis
- **Wind Analysis**: Wind speed and gust patterns

#### 🌡️ Patterns Tab
- **Hourly Pattern**: Average by hour of day
- **Monthly Pattern**: Seasonal trends

#### 🔗 Correlations Tab
- View correlation heatmap
- Identify strongest positive/negative correlations
- Understand metric relationships

#### 📋 Data Table Tab
- Preview raw data
- Filter and customize view
- Export filtered data as CSV

## 🎨 Customization

### Change Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#667eea"  # Your brand color
```

### Modify Metrics
Edit `src/data_loader.py`:
```python
potential_metrics = ['GHI', 'DNI', 'DHI', 'YourMetric']
```

## 💡 Tips

### Performance
- Use cleaned data for faster loading
- Enable date filtering for large datasets
- Close unused browser tabs

### Mobile Usage
- Use landscape mode for better chart visibility
- Pinch to zoom on charts
- Swipe between tabs

### Data Export
- Filter data using sidebar controls
- Apply date range if needed
- Download from Data Table tab

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check if Streamlit is installed
streamlit --version

# Reinstall if needed
pip install streamlit --upgrade
```

### Data won't load
- Check file path is correct
- Ensure CSV has required columns (Timestamp, GHI, etc.)
- Verify file permissions

### Charts not displaying
- Check browser console (F12)
- Clear browser cache
- Try different browser

### Slow performance
- Reduce date range
- Select fewer metrics
- Use data sampling (built-in for large datasets)

## 📚 Data Format

Your CSV should include:
```csv
Timestamp,GHI,DNI,DHI,Tamb,RH,WS,WSgust
2024-01-01 00:00:00,0.0,0.0,0.0,25.5,65.2,2.3,3.1
```

Required columns:
- `Timestamp`: Date and time
- At least one metric (GHI, DNI, DHI, etc.)

## 🌐 Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Go to streamlit.io/cloud
3. Deploy from repository
4. Add secrets if needed

### Local Network
```bash
streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501
```

## 📞 Support

For issues or questions:
- Check `RESPONSIVE_UI_GUIDE.md` for UI details
- See `DASHBOARD.md` for technical documentation
- Review `ARCHITECTURE.md` for system design

---

**Version**: 1.0.0  
**Last Updated**: November 2024  
**Built with**: Streamlit 🎈
