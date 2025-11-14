# 🇮🇹 Italian Property Research Assistant - Project Overview

## What This Project Does

This Python application automates the search and analysis of Italian real estate properties in your target locations. It provides intelligent filtering, translation, price tracking, and automated reporting.

### Core Features ✅
- **Web Scraping**: Searches Immobiliare.it for properties in target towns
- **Smart Filtering**: Finds properties matching your budget and criteria
- **Translation**: Converts Italian descriptions to English using Google Translate
- **Price Tracking**: Monitors price changes over time with SQLite database
- **HTML Reports**: Generates visual reports with property photos and details
- **Email Automation**: Sends weekly digest reports to your email
- **Data Persistence**: Stores historical data for trend analysis
- **Scheduling**: Runs automatically on weekly schedule

### Target Locations 🎯
- Crotone, Calabria
- Catania, Sicily  
- Andria, Puglia
- Rodi Garganico, Puglia

### Current Search Criteria 🔍
- **Budget**: €150,000 - €400,000
- **Bedrooms**: Minimum 2
- **Condition**: Excellent, Good, Habitable, Minor Renovation
- **Reports**: Sent to `cepizzarell@gmail.com`

---

## Current Status & To-Do Checklist

### ✅ Completed
- [x] Python script structure and configuration
- [x] Web scraping framework (Immobiliare.it)
- [x] Translation system (Google Translate)
- [x] Data filtering and extraction
- [x] HTML report generation
- [x] Email system integration
- [x] SQLite database setup
- [x] Price change tracking
- [x] Virtual environment setup
- [x] Dependencies installation
- [x] Email configuration

### ⚠️ Known Issues (Needs Fixing)
- [ ] **Anti-bot Protection**: Website returns 403 errors (primary blocker)
- [ ] **Alternative Data Sources**: Need backup real estate sites
- [ ] **Request Headers**: Improve browser simulation
- [ ] **Rate Limiting**: Add delays and rotation strategies

### 🚀 Ready to Test
- [ ] **Email Functionality**: Test with sample data
- [ ] **Database Operations**: Verify SQLite storage
- [ ] **Report Generation**: Test HTML output
- [ ] **Schedule Testing**: Verify timing works

---

## How to Run the Application

### 1. Setup (One-time)
```bash
# Navigate to project directory
cd /Users/cort/coding/italia

# Activate virtual environment
source property_env/bin/activate

# Install dependencies (if not done)
pip install -r requirements.txt
```

### 2. Configuration
Email settings are already configured in `property_research.py`:
- **Sender**: `cepizzarell@gmail.com`
- **Password**: Set (Gmail app password)
- **Recipient**: `cepizzarell@gmail.com`

### 3. Running Options

#### Option A: Single Test Run
```bash
source property_env/bin/activate
python property_research.py
```

#### Option B: Background Service (Continuous)
```bash
source property_env/bin/activate
nohup python property_research.py &
```

#### Option C: Manual Schedule Control
Edit `property_research.py` line 548-550:
```python
# Uncomment these lines for continuous scheduling
while True:
    schedule.run_pending()
    time.sleep(60)
```

### 4. Output Files
- `property_report_YYYYMMDD.html` - Weekly HTML reports
- `properties.db` - SQLite database with all data
- `property_research.log` - Application logs
- `property_cache.sqlite` - Web request cache

---

## Improvement Options & Future Enhancements

### 🔧 Technical Improvements
- [ ] **Proxy Rotation**: Use rotating proxies to avoid blocking
- [ ] **Multiple Data Sources**: Add additional real estate platforms:
  - **Casa.it**: Secondary major Italian real estate portal with different property inventory
  - **Idealista.it**: Modern platform with detailed filters and international properties
  - **Subito.it**: Classified ads platform with private sellers and unique listings
  - **TecnoGare.it**: Government property auctions and foreclosures
- [ ] **CAPTCHA Solving**: Integrate 2captcha or similar service
- [ ] **Headless Browser**: Use Selenium/Playwright for JS-heavy sites
- [ ] **API Integration**: Direct API access where available

### 🎯 Feature Enhancements
- [ ] **Advanced Filtering**: 
  - Distance from sea/amenities
  - Property age and renovation history
  - Energy efficiency ratings
  - Garden/parking availability
- [ ] **Market Analysis**:
  - Price trend analysis
  - Neighborhood comparison
  - Investment ROI calculations
- [ ] **Alerts & Notifications**:
  - SMS alerts for urgent properties
  - Price drop notifications
  - New listing alerts
- [ ] **Interactive Dashboard**:
  - Web interface for browsing properties
  - Map visualization
  - Saved searches and favorites

### 📊 Data & Analytics
- [ ] **Property History**: Track listing duration
- [ ] **Market Insights**: Average prices per area
- [ ] **Prediction Models**: Price trend forecasting
- [ ] **Comparative Analysis**: Similar property comparisons

### 🔒 Security & Reliability
- [ ] **Environment Variables**: Move sensitive data to .env file
- [ ] **Error Handling**: Robust retry mechanisms
- [ ] **Monitoring**: Health checks and uptime monitoring
- [ ] **Backup System**: Automated database backups

---

## File Structure

```
italia/
├── property_research.py          # Main application
├── requirements.txt              # Python dependencies
├── setup_property_research.md    # Setup instructions
├── italian-property-research.md  # Original requirements
├── PROJECT_OVERVIEW.md          # This file
├── property_env/                # Virtual environment
├── properties.db               # SQLite database (created on run)
├── property_cache.sqlite       # Request cache (created on run)
├── property_research.log       # Application logs (created on run)
└── property_report_*.html      # Generated reports (created on run)
```

---

## Quick Start Commands

```bash
# 1. Activate environment
source property_env/bin/activate

# 2. Test run (exits after one search)
python property_research.py

# 3. Check logs
tail -f property_research.log

# 4. View latest report
open property_report_*.html

# 5. Check database
sqlite3 properties.db ".tables"
```

---

## Support & Troubleshooting

### Common Issues
1. **403 Errors**: Website blocking - normal, need anti-bot improvements
2. **Email Errors**: Check Gmail app password and 2FA settings
3. **Translation Errors**: Google Translate API limits - add delays
4. **Database Locked**: Close other SQLite connections

### Next Steps
1. Test email functionality with sample data
2. Research anti-bot solutions (proxies, headers, timing)
3. Add backup data sources
4. Implement monitoring and health checks

---

**Last Updated**: November 14, 2024  
**Status**: Core functionality complete, anti-bot protection needed for live operation