# Italian Property Research Setup Guide

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit the `Config` class in `property_research.py`:

```python
# Email settings (required for email reports)
sender_email = "your-email@gmail.com"  
sender_password = "your-app-password"  # Use Gmail app password
recipient_emails = ["family1@email.com", "family2@email.com"]

# Search criteria (adjust as needed)
max_price = 150000  # EUR
min_bedrooms = 2
acceptable_conditions = ["excellent", "good", "habitable", "minor renovation"]

# Target locations (modify as needed)
target_towns = [
    "Crotone, Calabria",
    "Catania, Sicily", 
    "Andria, Puglia",
    "Rodi Garganico, Puglia"
]
```

## Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings > Security > App passwords
3. Generate an app password for "Mail"
4. Use this password in the `sender_password` field

## Running

### One-time search:
```bash
python property_research.py
```

### Background service:
```bash
nohup python property_research.py &
```

## Features

- **Web Scraping**: Searches Immobiliare.it for properties
- **Translation**: Converts Italian descriptions to English
- **Filtering**: Finds properties matching your criteria
- **Price Tracking**: Monitors price changes over time
- **HTML Reports**: Generates visual reports with photos
- **Email Digest**: Sends weekly reports to family
- **Database**: SQLite storage for historical data

## Output Files

- `properties.db` - SQLite database with all property data
- `property_report_YYYYMMDD.html` - Weekly HTML reports
- `property_research.log` - Application logs
- `property_cache.sqlite` - Web request cache

## Scheduling

The script runs weekly by default. Modify the schedule in the `main()` function:

```python
# Daily at 9 AM
schedule.every().day.at("09:00").do(researcher.run_search)

# Weekly (default)
schedule.every().week.do(researcher.run_search)
```

## Legal Note

This tool is for personal research only. Please respect website terms of service and use reasonable request delays.