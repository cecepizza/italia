#!/usr/bin/env python3
"""
Italian Property Research Assistant

Automates property research for Italian real estate across multiple towns.
Scrapes listings, translates descriptions, filters by criteria, and generates reports.
"""

import requests
import time
import json
import sqlite3
import smtplib
import schedule
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import html

import pandas as pd
from bs4 import BeautifulSoup
from googletrans import Translator
import requests_cache


# Configuration
@dataclass
class Config:
    """Configuration settings for the property research tool"""
    
    # Target locations
    target_towns = [
        "Crotone, Calabria",
        "Catania, Sicily", 
        "Andria, Puglia",
        "Rodi Garganico, Puglia"
    ]
    
    # Search criteria
    min_price = 150000  # EUR
    max_price = 400000  # EUR
    min_bedrooms = 2
    acceptable_conditions = ["excellent", "good", "habitable", "minor renovation"]
    
    # Email settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "your-email@gmail.com"
    sender_password = ""  # Set your Gmail app password here
    recipient_emails = ["your-email@gmail.com"]
    
    # Database settings
    db_path = "properties.db"
    
    # Scheduling
    run_schedule = "weekly"  # weekly, daily
    run_time = "09:00"
    
    # Logging
    log_level = logging.INFO
    log_file = "property_research.log"


@dataclass
class Property:
    """Data structure for a property listing"""
    id: str
    title: str
    description: str
    description_en: str
    price: int
    size_sqm: Optional[int]
    bedrooms: Optional[int]
    condition: str
    location: str
    url: str
    image_urls: List[str]
    price_per_sqm: Optional[float]
    first_seen: datetime
    last_seen: datetime
    price_history: List[Tuple[datetime, int]]


class PropertyResearcher:
    """Main class for property research functionality"""
    
    def __init__(self, config: Config):
        self.config = config
        self.translator = Translator()
        self.session = requests_cache.CachedSession('property_cache', expire_after=3600)
        
        # More realistic headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.setup_logging()
        self.setup_database()
        
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Initialize SQLite database for tracking properties"""
        self.conn = sqlite3.connect(self.config.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                description_en TEXT,
                price INTEGER,
                size_sqm INTEGER,
                bedrooms INTEGER,
                condition TEXT,
                location TEXT,
                url TEXT,
                image_urls TEXT,
                price_per_sqm REAL,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                price_history TEXT
            )
        ''')
        
        self.conn.commit()
        
    def scrape_immobiliare_it(self, location: str) -> List[Property]:
        """Scrape properties from Immobiliare.it"""
        properties = []
        
        try:
            # Map location to region for better URL structure
            region_map = {
                'Crotone, Calabria': 'calabria',
                'Catania, Sicily': 'sicilia', 
                'Andria, Puglia': 'puglia',
                'Rodi Garganico, Puglia': 'puglia'
            }
            
            region = region_map.get(location, 'italia')
            
            # Try direct regional URL first
            base_url = f"https://www.immobiliare.it/vendita-case/{region}/"
            search_params = {
                'prezzoMinimo': self.config.min_price,
                'prezzoMassimo': self.config.max_price,
                'localiMinimo': self.config.min_bedrooms,
                'criterio': 'rilevanza'
            }
            
            response = self.session.get(base_url, params=search_params, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch from Immobiliare.it for {location}: {response.status_code}")
                return properties
                
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('div', class_='nd-list__item')
            
            for listing in listings[:20]:  # Limit to first 20 results
                try:
                    property_data = self._parse_immobiliare_listing(listing, location)
                    if property_data:
                        properties.append(property_data)
                        time.sleep(1)  # Be respectful to the server
                except Exception as e:
                    self.logger.error(f"Error parsing listing: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Immobiliare.it for {location}: {e}")
            
        return properties
        
    def _parse_immobiliare_listing(self, listing, location: str) -> Optional[Property]:
        """Parse individual listing from Immobiliare.it"""
        try:
            # Extract basic information
            title_elem = listing.find('a', class_='nd-list__title')
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            url = "https://www.immobiliare.it" + title_elem['href']
            
            # Extract price
            price_elem = listing.find('div', class_='nd-list__price')
            if not price_elem:
                return None
                
            price_text = price_elem.get_text(strip=True)
            price = self._extract_price(price_text)
            if not price or price < self.config.min_price or price > self.config.max_price:
                return None
                
            # Extract details
            details = listing.find('div', class_='nd-list__details')
            bedrooms, size_sqm = self._extract_details(details.get_text() if details else "")
            
            if bedrooms and bedrooms < self.config.min_bedrooms:
                return None
                
            # Extract images
            img_elem = listing.find('img')
            image_urls = [img_elem['src']] if img_elem else []
            
            # Get detailed description from property page
            description = self._get_property_description(url)
            description_en = self._translate_text(description)
            
            # Calculate price per sqm
            price_per_sqm = price / size_sqm if size_sqm else None
            
            # Generate unique ID
            property_id = f"immobiliare_{hash(url)}"
            
            now = datetime.now()
            
            return Property(
                id=property_id,
                title=title,
                description=description,
                description_en=description_en,
                price=price,
                size_sqm=size_sqm,
                bedrooms=bedrooms,
                condition="unknown",  # Will be determined from description
                location=location,
                url=url,
                image_urls=image_urls,
                price_per_sqm=price_per_sqm,
                first_seen=now,
                last_seen=now,
                price_history=[(now, price)]
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing individual listing: {e}")
            return None
            
    def _extract_price(self, price_text: str) -> Optional[int]:
        """Extract numeric price from text"""
        price_match = re.search(r'€\s*([\d.,]+)', price_text.replace('.', '').replace(',', ''))
        if price_match:
            try:
                return int(price_match.group(1).replace('.', '').replace(',', ''))
            except ValueError:
                return None
        return None
        
    def _extract_details(self, details_text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract bedrooms and size from details text"""
        bedrooms = None
        size_sqm = None
        
        # Look for bedrooms (locali, camere)
        bedroom_match = re.search(r'(\d+)\s*(?:locali|camere|cam)', details_text.lower())
        if bedroom_match:
            bedrooms = int(bedroom_match.group(1))
            
        # Look for size in square meters
        size_match = re.search(r'(\d+)\s*m[²2]', details_text)
        if size_match:
            size_sqm = int(size_match.group(1))
            
        return bedrooms, size_sqm
        
    def _get_property_description(self, url: str) -> str:
        """Fetch detailed description from property page"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                desc_elem = soup.find('div', class_='im-description__text')
                if desc_elem:
                    return desc_elem.get_text(strip=True)
        except Exception as e:
            self.logger.warning(f"Could not fetch description for {url}: {e}")
            
        return ""
        
    def _translate_text(self, text: str) -> str:
        """Translate Italian text to English"""
        if not text:
            return ""
            
        try:
            result = self.translator.translate(text, src='it', dest='en')
            return result.text
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
            return text
            
    def _determine_condition(self, description: str) -> str:
        """Determine property condition from description"""
        description_lower = description.lower()
        
        condition_keywords = {
            "excellent": ["ottimo", "eccellente", "perfetto", "ristrutturato"],
            "good": ["buono", "buone condizioni", "abitabile"],
            "habitable": ["abitabile", "vivibile"],
            "minor renovation": ["piccoli lavori", "da ristrutturare parzialmente"],
            "major renovation": ["da ristrutturare", "da rifare", "da sistemare"]
        }
        
        for condition, keywords in condition_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return condition
                
        return "unknown"
        
    def filter_properties(self, properties: List[Property]) -> List[Property]:
        """Filter properties based on criteria"""
        filtered = []
        
        for prop in properties:
            # Check price
            if prop.price < self.config.min_price or prop.price > self.config.max_price:
                continue
                
            # Check bedrooms
            if prop.bedrooms and prop.bedrooms < self.config.min_bedrooms:
                continue
                
            # Determine condition from description
            prop.condition = self._determine_condition(prop.description + " " + prop.description_en)
            
            # Check condition
            if prop.condition not in self.config.acceptable_conditions and prop.condition != "unknown":
                continue
                
            filtered.append(prop)
            
        return filtered
    
    def scrape_casa_it(self, location: str) -> List[Property]:
        """Scrape properties from Casa.it"""
        properties = []
        
        try:
            # Map location to Casa.it region paths
            region_map = {
                'Crotone, Calabria': 'calabria',
                'Catania, Sicily': 'sicilia', 
                'Andria, Puglia': 'puglia',
                'Rodi Garganico, Puglia': 'puglia'
            }
            
            region = region_map.get(location, 'italia')
            base_url = f"https://www.casa.it/vendita/residenziale/{region}/"
            
            search_params = {
                'prezzo_min': self.config.min_price,
                'prezzo_max': self.config.max_price,
                'locali_min': self.config.min_bedrooms
            }
            
            response = self.session.get(base_url, params=search_params, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch from Casa.it for {location}: {response.status_code}")
                return properties
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for property cards/listings (Casa.it structure)
            listings = soup.find_all(['div', 'article'], class_=lambda x: x and any(term in x.lower() for term in ['property', 'listing', 'annuncio', 'casa']))
            
            for listing in listings[:15]:  # Limit to first 15 results
                try:
                    property_data = self._parse_casa_listing(listing, location)
                    if property_data:
                        properties.append(property_data)
                        time.sleep(0.5)  # Be respectful to the server
                except Exception as e:
                    self.logger.error(f"Error parsing Casa.it listing: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Casa.it for {location}: {e}")
            
        return properties
    
    def _parse_casa_listing(self, listing, location: str) -> Optional[Property]:
        """Parse individual listing from Casa.it"""
        try:
            # Find title/link
            title_elem = listing.find('a', href=True)
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            href = title_elem['href']
            url = href if href.startswith('http') else f"https://www.casa.it{href}"
            
            # Extract price
            price_elem = listing.find(text=lambda text: text and '€' in text)
            if not price_elem:
                return None
                
            price = self._extract_price(str(price_elem))
            if not price or price < self.config.min_price or price > self.config.max_price:
                return None
            
            # Extract basic details from listing text
            listing_text = listing.get_text()
            bedrooms, size_sqm = self._extract_details(listing_text)
            
            if bedrooms and bedrooms < self.config.min_bedrooms:
                return None
            
            # Generate unique ID
            property_id = f"casa_{hash(url)}"
            
            # Try to get image
            img_elem = listing.find('img')
            image_urls = [img_elem['src']] if img_elem and img_elem.get('src') else []
            
            now = datetime.now()
            price_per_sqm = price / size_sqm if size_sqm else None
            
            return Property(
                id=property_id,
                title=title,
                description=listing_text[:200],  # Basic description from listing
                description_en=self._translate_text(listing_text[:200]),
                price=price,
                size_sqm=size_sqm,
                bedrooms=bedrooms,
                condition="unknown",
                location=location,
                url=url,
                image_urls=image_urls,
                price_per_sqm=price_per_sqm,
                first_seen=now,
                last_seen=now,
                price_history=[(now, price)]
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing Casa.it listing: {e}")
            return None
        
    def save_properties(self, properties: List[Property]):
        """Save properties to database and track changes"""
        cursor = self.conn.cursor()
        
        for prop in properties:
            # Check if property exists
            cursor.execute("SELECT price, price_history FROM properties WHERE id = ?", (prop.id,))
            result = cursor.fetchone()
            
            if result:
                # Property exists, check for price changes
                old_price, price_history_json = result
                price_history = json.loads(price_history_json) if price_history_json else []
                
                if old_price != prop.price:
                    # Price changed
                    self.logger.info(f"Price change detected for {prop.title}: €{old_price} -> €{prop.price}")
                    price_history.append([datetime.now().isoformat(), prop.price])
                    prop.price_history = [(datetime.fromisoformat(h[0]), h[1]) for h in price_history]
                    
                # Update existing property
                cursor.execute('''
                    UPDATE properties SET
                    price = ?, last_seen = ?, price_history = ?
                    WHERE id = ?
                ''', (prop.price, prop.last_seen, json.dumps([[h[0].isoformat(), h[1]] for h in prop.price_history]), prop.id))
            else:
                # New property
                cursor.execute('''
                    INSERT INTO properties VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prop.id, prop.title, prop.description, prop.description_en,
                    prop.price, prop.size_sqm, prop.bedrooms, prop.condition,
                    prop.location, prop.url, json.dumps(prop.image_urls),
                    prop.price_per_sqm, prop.first_seen, prop.last_seen,
                    json.dumps([[h[0].isoformat(), h[1]] for h in prop.price_history])
                ))
                
        self.conn.commit()
        
    def generate_html_report(self, properties: List[Property]) -> str:
        """Generate HTML report of properties"""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Italian Property Research Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .property {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }}
                .property img {{ max-width: 300px; height: auto; }}
                .price {{ font-size: 24px; color: #d32f2f; font-weight: bold; }}
                .details {{ margin: 10px 0; }}
                .description {{ margin: 15px 0; padding: 10px; background: #f5f5f5; }}
                .header {{ background: #1976d2; color: white; padding: 20px; text-align: center; }}
                .summary {{ background: #e3f2fd; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Italian Property Research Report</h1>
                <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>{len(properties)}</strong> properties found matching your criteria:</p>
                <ul>
                    <li>Price range: €{self.config.min_price:,} - €{self.config.max_price:,}</li>
                    <li>Minimum bedrooms: {self.config.min_bedrooms}</li>
                    <li>Locations: {', '.join(self.config.target_towns)}</li>
                </ul>
            </div>
        '''
        
        for prop in properties:
            price_per_sqm_text = f"€{prop.price_per_sqm:,.0f}/m²" if prop.price_per_sqm else "N/A"
            bedrooms_text = f"{prop.bedrooms} bedrooms" if prop.bedrooms else "N/A"
            size_text = f"{prop.size_sqm}m²" if prop.size_sqm else "N/A"
            
            html_content += f'''
            <div class="property">
                <h3>{html.escape(prop.title)}</h3>
                <div class="price">€{prop.price:,}</div>
                <div class="details">
                    <strong>Location:</strong> {html.escape(prop.location)}<br>
                    <strong>Size:</strong> {size_text}<br>
                    <strong>Bedrooms:</strong> {bedrooms_text}<br>
                    <strong>Price/m²:</strong> {price_per_sqm_text}<br>
                    <strong>Condition:</strong> {prop.condition.title()}<br>
                    <strong>Link:</strong> <a href="{prop.url}" target="_blank">View Property</a>
                </div>
                
                {f'<img src="{prop.image_urls[0]}" alt="Property photo">' if prop.image_urls else ''}
                
                <div class="description">
                    <h4>Description (English)</h4>
                    <p>{html.escape(prop.description_en[:500])}{'...' if len(prop.description_en) > 500 else ''}</p>
                </div>
            </div>
            '''
            
        html_content += '''
        </body>
        </html>
        '''
        
        return html_content
        
    def send_email_report(self, html_content: str):
        """Send HTML report via email"""
        if not self.config.sender_email or not self.config.recipient_emails:
            self.logger.warning("Email not configured - skipping email send")
            return
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Italian Property Research Report - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.config.sender_email
            msg['To'] = ', '.join(self.config.recipient_emails)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.sender_email, self.config.sender_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email report sent to {len(self.config.recipient_emails)} recipients")
            
        except Exception as e:
            self.logger.error(f"Failed to send email report: {e}")
            
    def run_search(self):
        """Run the complete property search process"""
        self.logger.info("Starting property search...")
        
        all_properties = []
        
        # Search each target location
        for location in self.config.target_towns:
            self.logger.info(f"Searching properties in {location}")
            
            try:
                # Scrape from Immobiliare.it
                immobiliare_properties = self.scrape_immobiliare_it(location)
                self.logger.info(f"Found {len(immobiliare_properties)} properties from Immobiliare.it in {location}")
                
                # Scrape from Casa.it
                casa_properties = self.scrape_casa_it(location)
                self.logger.info(f"Found {len(casa_properties)} properties from Casa.it in {location}")
                
                # Combine all properties
                all_location_properties = immobiliare_properties + casa_properties
                self.logger.info(f"Total properties found in {location}: {len(all_location_properties)}")
                
                # Filter properties
                filtered_properties = self.filter_properties(all_location_properties)
                self.logger.info(f"Filtered to {len(filtered_properties)} matching properties")
                
                all_properties.extend(filtered_properties)
                
                # Be respectful to servers
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error searching {location}: {e}")
                continue
                
        # Save properties to database
        self.save_properties(all_properties)
        
        # Generate and send report
        if all_properties:
            html_report = self.generate_html_report(all_properties)
            
            # Save report to file
            report_path = f"property_report_{datetime.now().strftime('%Y%m%d')}.html"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            self.logger.info(f"Report saved to {report_path}")
            
            # Send email report
            self.send_email_report(html_report)
        else:
            self.logger.info("No properties found matching criteria")
            
        self.logger.info("Property search completed")


def main():
    """Main function to run the property researcher"""
    config = Config()
    researcher = PropertyResearcher(config)
    
    if config.run_schedule == "daily":
        schedule.every().day.at(config.run_time).do(researcher.run_search)
    elif config.run_schedule == "weekly":
        schedule.every().week.do(researcher.run_search)
    
    # Run once immediately for testing
    print("Starting Italian property search...")
    print(f"Budget: €{config.min_price:,} - €{config.max_price:,}")
    print(f"Target towns: {', '.join(config.target_towns)}")
    print("=" * 50)
    
    researcher.run_search()
    
    print("\nTest completed! Check for generated HTML report.")
    
    # Uncomment to keep running on schedule
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)


if __name__ == "__main__":
    main()