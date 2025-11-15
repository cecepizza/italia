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

# Geocoding support
try:
    from geopy.distance import geodesic
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    print("⚠️  geopy not installed. Install with: pip install geopy")

# Try to import Selenium for JavaScript-rendered sites
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium webdriver-manager")


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
    bathrooms: Optional[int] = None  # New field
    property_type: Optional[str] = None  # New field: house, apartment, duplex, etc.
    condition: str = "unknown"
    location: str = ""
    address: Optional[str] = None  # New field: full address
    url: str = ""
    image_urls: List[str] = None
    price_per_sqm: Optional[float] = None
    # Geocoding data
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_coast_km: Optional[float] = None
    distance_to_airport_km: Optional[float] = None
    # Metadata
    source: str = ""  # immobiliare, casa, idealista, subito
    first_seen: datetime = None
    last_seen: datetime = None
    price_history: List[Tuple[datetime, int]] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.image_urls is None:
            self.image_urls = []
        if self.price_history is None:
            self.price_history = []
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()


class PropertyResearcher:
    """Main class for property research functionality"""
    
    def __init__(self, config: Config, use_selenium=True):
        self.config = config
        self.translator = Translator()
        self.session = requests_cache.CachedSession('property_cache', expire_after=3600)
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        
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
        
        # Initialize geocoder if available
        if GEOPY_AVAILABLE:
            self.geolocator = Nominatim(user_agent="ItalianPropertyScraper/1.0")
            # Add delay to respect rate limits
            time.sleep(1)
        else:
            self.geolocator = None
        
        # Define coastal coordinates for each region (approximate)
        self.coastal_points = {
            'Puglia': [
                (40.996, 17.218),  # Polignano a Mare
                (40.953, 17.297),  # Monopoli
                (40.148, 18.486),  # Otranto
            ],
            'Calabria': [
                (39.081, 17.127),  # Crotone
            ],
            'Sicily': [
                (37.502, 15.087),  # Catania
            ],
            'Liguria': [
                (44.147, 9.655),   # Monterosso al Mare
            ]
        }
        
        # Define airport coordinates
        self.airport_coordinates = {
            'Bari': (41.138, 16.761),  # Bari Airport
            'Brindisi': (40.657, 17.947),  # Brindisi Airport
            'Catania': (37.466, 15.066),  # Catania Airport
            'Lamezia': (38.906, 16.242),  # Lamezia Terme Airport
        }
        
        # Map locations to nearest airports
        self.location_to_airport = {
            'Crotone, Calabria': 'Lamezia',
            'Catania, Sicily': 'Catania',
            'Andria, Puglia': 'Bari',
            'Rodi Garganico, Puglia': 'Bari',
        }
        
        # Initialize Selenium if available
        if self.use_selenium:
            self._init_selenium()
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Selenium: {e}. Falling back to requests.")
            self.use_selenium = False
    
    def __del__(self):
        """Clean up Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
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
        """Scrape properties from Immobiliare.it using Selenium if available"""
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
            
            # Build search URL
            base_url = f"https://www.immobiliare.it/vendita-case/{region}/"
            search_url = f"{base_url}?prezzoMinimo={self.config.min_price}&prezzoMassimo={self.config.max_price}&localiMinimo={self.config.min_bedrooms}&criterio=rilevanza"
            
            if self.use_selenium and self.driver:
                # Use Selenium for JavaScript-rendered content
                self.logger.info(f"Using Selenium to scrape Immobiliare.it for {location}")
                try:
                    self.driver.get(search_url)
                    time.sleep(3)  # Wait for JavaScript to render
                    
                    # Wait for property listings to load
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='list'], article, [data-id]"))
                    )
                    
                    # Get page source after JavaScript execution
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                except Exception as e:
                    self.logger.warning(f"Selenium failed for Immobiliare.it: {e}. Trying requests...")
                    response = self.session.get(search_url, headers=self.headers, timeout=30)
                    if response.status_code != 200:
                        return properties
                    soup = BeautifulSoup(response.content, 'html.parser')
            else:
                # Fallback to requests
                response = self.session.get(search_url, headers=self.headers, timeout=30)
                if response.status_code != 200:
                    self.logger.warning(f"Failed to fetch from Immobiliare.it for {location}: {response.status_code}")
                    return properties
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for property listings
            listings = []
            selectors = [
                'div.nd-list__item',
                'div[class*="list-item"]',
                'article[class*="property"]',
                'div[data-id]',
                'div[class*="card"]',
                'div[class*="listing"]'
            ]
            
            for selector in selectors:
                listings = soup.select(selector)
                if listings:
                    self.logger.info(f"Found {len(listings)} listings using selector: {selector}")
                    break
            
            if not listings:
                # Last resort: look for any links that might be properties
                property_links = soup.find_all('a', href=lambda x: x and ('/annunci/' in x or '/immobile/' in x))
                self.logger.info(f"Found {len(property_links)} property links as fallback")
                listings = property_links[:20]
            
            for listing in listings[:20]:  # Limit to first 20 results
                try:
                    property_data = self._parse_immobiliare_listing(listing, location)
                    if property_data:
                        properties.append(property_data)
                        time.sleep(0.5)  # Be respectful to the server
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
            details_text = details.get_text() if details else ""
            bedrooms, bathrooms, size_sqm, property_type = self._extract_details(details_text)
            
            if bedrooms and bedrooms < self.config.min_bedrooms:
                return None
                
            # Extract images
            img_elem = listing.find('img')
            image_urls = [img_elem['src']] if img_elem else []
            
            # Get detailed description from property page
            description = self._get_property_description(url)
            description_en = self._translate_text(description)
            
            # Try to extract address from description or title
            address = None
            # Look for address patterns in description
            address_match = re.search(r'(via|viale|piazza|strada|via)\s+[\w\s]+,\s*\d+', description, re.IGNORECASE)
            if address_match:
                address = address_match.group(0)
            
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
                bathrooms=bathrooms,
                property_type=property_type,
                condition="unknown",  # Will be determined from description
                location=location,
                address=address,
                url=url,
                image_urls=image_urls,
                price_per_sqm=price_per_sqm,
                source="immobiliare",
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
        
    def _extract_details(self, details_text: str) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[str]]:
        """Extract bedrooms, bathrooms, size, and property type from details text"""
        bedrooms = None
        bathrooms = None
        size_sqm = None
        property_type = None
        
        text_lower = details_text.lower()
        
        # Look for bedrooms (locali, camere)
        bedroom_match = re.search(r'(\d+)\s*(?:locali|camere|cam)', text_lower)
        if bedroom_match:
            bedrooms = int(bedroom_match.group(1))
            
        # Look for bathrooms (bagni, servizi)
        bathroom_match = re.search(r'(\d+)\s*(?:bagni|servizi|wc)', text_lower)
        if bathroom_match:
            bathrooms = int(bathroom_match.group(1))
            
        # Look for size in square meters
        size_match = re.search(r'(\d+)\s*m[²2]', details_text)
        if size_match:
            size_sqm = int(size_match.group(1))
        
        # Determine property type
        if any(word in text_lower for word in ['villa', 'villetta']):
            property_type = 'villa'
        elif any(word in text_lower for word in ['casa', 'house']):
            property_type = 'house'
        elif any(word in text_lower for word in ['appartamento', 'apartment', 'appart']):
            property_type = 'apartment'
        elif any(word in text_lower for word in ['duplex', 'bifamiliare']):
            property_type = 'duplex'
        else:
            property_type = 'unknown'
            
        return bedrooms, bathrooms, size_sqm, property_type
        
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
            
        # Skip translation for now - googletrans API has changed
        # Translation is not critical for core functionality
        # Can be added back later with a different translation service if needed
        return text
        
        # Old translation code (commented out due to API changes):
        # try:
        #     result = self.translator.translate(text, src='it', dest='en')
        #     return result.text
        # except Exception as e:
        #     self.logger.warning(f"Translation failed: {e}")
        #     return text
            
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
        
    def geocode_property(self, prop: Property, location: str) -> Property:
        """Geocode a property address and calculate distances"""
        if not GEOPY_AVAILABLE or not self.geolocator:
            return prop
        
        try:
            # Extract region from location string
            region = location.split(', ')[-1] if ', ' in location else location
            
            # Try to geocode if we have an address
            if prop.address:
                try:
                    location_data = self.geolocator.geocode(f"{prop.address}, {location}, Italy", timeout=10)
                    if location_data:
                        prop.latitude = location_data.latitude
                        prop.longitude = location_data.longitude
                        
                        # Calculate distance to coast
                        if region in self.coastal_points:
                            min_coast_dist = float('inf')
                            for coast_lat, coast_lng in self.coastal_points[region]:
                                dist = geodesic((prop.latitude, prop.longitude), (coast_lat, coast_lng)).km
                                min_coast_dist = min(min_coast_dist, dist)
                            prop.distance_to_coast_km = round(min_coast_dist, 2)
                        
                        # Calculate distance to airport
                        airport_name = self.location_to_airport.get(location)
                        if airport_name and airport_name in self.airport_coordinates:
                            airport_lat, airport_lng = self.airport_coordinates[airport_name]
                            prop.distance_to_airport_km = round(
                                geodesic((prop.latitude, prop.longitude), (airport_lat, airport_lng)).km, 2
                            )
                    
                    # Be respectful to Nominatim rate limits
                    time.sleep(1)
                except Exception as e:
                    self.logger.warning(f"Geocoding failed for {prop.address}: {e}")
        except Exception as e:
            self.logger.warning(f"Error geocoding property {prop.id}: {e}")
        
        return prop
    
    def property_to_dict(self, prop: Property) -> dict:
        """Convert Property dataclass to JSON-serializable dictionary"""
        return {
            'id': prop.id,
            'title': prop.title,
            'description': prop.description,
            'description_en': prop.description_en,
            'price': prop.price,
            'size_sqm': prop.size_sqm,
            'bedrooms': prop.bedrooms,
            'bathrooms': prop.bathrooms,
            'property_type': prop.property_type,
            'condition': prop.condition,
            'location': prop.location,
            'address': prop.address,
            'url': prop.url,
            'image_urls': prop.image_urls,
            'price_per_sqm': prop.price_per_sqm,
            'latitude': prop.latitude,
            'longitude': prop.longitude,
            'distance_to_coast_km': prop.distance_to_coast_km,
            'distance_to_airport_km': prop.distance_to_airport_km,
            'source': prop.source,
            'first_seen': prop.first_seen.isoformat() if prop.first_seen else None,
            'last_seen': prop.last_seen.isoformat() if prop.last_seen else None,
            'price_history': [(dt.isoformat(), price) for dt, price in prop.price_history] if prop.price_history else []
        }
    
    def save_town_json(self, properties: List[Property], location: str):
        """Save properties to JSON file for a specific town"""
        if not properties:
            return
        
        # Create data directory if it doesn't exist
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Extract town and region from location string
        # Format: "Town, Region" or "Town, Region, Country"
        parts = location.split(', ')
        town = parts[0].replace(' ', '_').lower()
        region = parts[1].replace(' ', '_').lower() if len(parts) > 1 else 'unknown'
        
        # Create filename: region_town.json
        filename = data_dir / f"{region}_{town}.json"
        
        # Convert properties to dictionaries
        properties_dict = [self.property_to_dict(prop) for prop in properties]
        
        # Create JSON structure
        json_data = {
            'town': parts[0],  # Original town name
            'region': parts[1] if len(parts) > 1 else 'Unknown',
            'location': location,
            'last_updated': datetime.now().isoformat(),
            'property_count': len(properties),
            'properties': properties_dict
        }
        
        # Save to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(properties)} properties to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save JSON file {filename}: {e}")
    
    def filter_properties(self, properties: List[Property]) -> List[Property]:
        """Filter properties based on enhanced criteria"""
        filtered = []
        
        # Keywords that indicate a "perfect" property (allows 1 bathroom)
        perfect_keywords = ['vista mare', 'spiaggia privata', 'terrazza', 'giardino', 'piscina', 
                           'panoramico', 'vista panoramica', 'spiaggia', 'mare']
        
        for prop in properties:
            # Check price
            if prop.price < self.config.min_price or prop.price > self.config.max_price:
                continue
                
            # Check bedrooms (at least 2)
            if prop.bedrooms and prop.bedrooms < self.config.min_bedrooms:
                continue
            
            # Check bathrooms (at least 2, or 1 if "perfect")
            if prop.bathrooms is not None:
                if prop.bathrooms < 2:
                    # Check if it's a "perfect" property
                    desc_lower = (prop.description + " " + prop.description_en).lower()
                    is_perfect = any(kw in desc_lower for kw in perfect_keywords)
                    if not is_perfect:
                        continue  # Skip if not perfect and only 1 bathroom
            
            # Check property type (house, apartment, duplex, villa)
            if prop.property_type:
                allowed_types = ['house', 'apartment', 'duplex', 'villa', 'casa', 'appartamento']
                if prop.property_type.lower() not in [t.lower() for t in allowed_types]:
                    # Still allow if unknown (might be valid)
                    if prop.property_type.lower() != 'unknown':
                        continue
                
            # Determine condition from description
            prop.condition = self._determine_condition(prop.description + " " + prop.description_en)
            
            # Check condition (more lenient - allow unknown)
            if prop.condition not in self.config.acceptable_conditions and prop.condition != "unknown":
                continue
                
            filtered.append(prop)
            
        return filtered
    
    def scrape_casa_it(self, location: str) -> List[Property]:
        """Scrape properties from Casa.it using Selenium if available"""
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
            search_url = f"{base_url}?prezzo_min={self.config.min_price}&prezzo_max={self.config.max_price}&locali_min={self.config.min_bedrooms}"
            
            if self.use_selenium and self.driver:
                # Use Selenium for JavaScript-rendered content
                self.logger.info(f"Using Selenium to scrape Casa.it for {location}")
                try:
                    self.driver.get(search_url)
                    time.sleep(3)  # Wait for JavaScript to render
                    
                    # Wait for property listings to load
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div, article, [class*='card'], [class*='item']"))
                    )
                    
                    # Get page source after JavaScript execution
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                except Exception as e:
                    self.logger.warning(f"Selenium failed for Casa.it: {e}. Trying requests...")
                    response = self.session.get(search_url, headers=self.headers, timeout=30)
                    if response.status_code != 200:
                        return properties
                    soup = BeautifulSoup(response.content, 'html.parser')
            else:
                # Fallback to requests
                response = self.session.get(search_url, headers=self.headers, timeout=30)
                if response.status_code != 200:
                    self.logger.warning(f"Failed to fetch from Casa.it for {location}: {response.status_code}")
                    return properties
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for property listings
            listings = []
            selectors = [
                ['div', 'article'],  # Generic containers
                'div[class*="card"]',
                'div[class*="item"]',
                'div[class*="property"]',
                'div[class*="listing"]',
                'article[class*="property"]'
            ]
            
            for selector in selectors:
                if isinstance(selector, list):
                    listings = soup.find_all(selector, class_=lambda x: x and any(term in str(x).lower() for term in ['property', 'listing', 'annuncio', 'casa', 'card', 'item']))
                else:
                    listings = soup.select(selector)
                if listings:
                    self.logger.info(f"Found {len(listings)} listings using selector: {selector}")
                    break
            
            if not listings:
                # Last resort: look for property links
                property_links = soup.find_all('a', href=lambda x: x and ('/vendita/' in x or '/immobile/' in x))
                self.logger.info(f"Found {len(property_links)} property links as fallback")
                listings = property_links[:15]
            
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
            # Find title/link - try multiple strategies
            title_elem = listing.find('a', href=True)
            if not title_elem:
                # Try finding any link in the listing
                title_elem = listing.find('a')
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True) or "Property"
            href = title_elem.get('href', '')
            if not href:
                return None
            url = href if href.startswith('http') else f"https://www.casa.it{href}"
            
            # Extract price - try multiple methods
            price = None
            listing_text = listing.get_text()
            
            # Method 1: Look for price in text nodes (using string instead of text for deprecation)
            price_elem = listing.find(string=lambda s: s and '€' in str(s) and any(c.isdigit() for c in str(s)))
            if price_elem:
                price = self._extract_price(str(price_elem))
            
            # Method 2: Look for price in any text
            if not price:
                price_match = re.search(r'€\s*([\d.,]+)', listing_text)
                if price_match:
                    try:
                        price = int(price_match.group(1).replace('.', '').replace(',', ''))
                    except:
                        pass
            
            # If no price found, skip this listing (price is required)
            if not price:
                return None
                
            # Check price range
            if price < self.config.min_price or price > self.config.max_price:
                return None
            
            # Extract basic details from listing text
            bedrooms, bathrooms, size_sqm, property_type = self._extract_details(listing_text)
            
            if bedrooms and bedrooms < self.config.min_bedrooms:
                return None
            
            # Try to extract address from listing text
            address = None
            address_match = re.search(r'(via|viale|piazza|strada|via)\s+[\w\s]+,\s*\d+', listing_text, re.IGNORECASE)
            if address_match:
                address = address_match.group(0)
            
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
                bathrooms=bathrooms,
                property_type=property_type,
                condition="unknown",
                location=location,
                address=address,
                url=url,
                image_urls=image_urls,
                price_per_sqm=price_per_sqm,
                source="casa",
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
                
                # Geocode properties (if geopy is available)
                if GEOPY_AVAILABLE:
                    self.logger.info(f"Geocoding {len(filtered_properties)} properties for {location}...")
                    geocoded_properties = []
                    for prop in filtered_properties:
                        geocoded_prop = self.geocode_property(prop, location)
                        geocoded_properties.append(geocoded_prop)
                    filtered_properties = geocoded_properties
                
                # Save properties to JSON file for this town
                self.save_town_json(filtered_properties, location)
                
                all_properties.extend(filtered_properties)
                
                # Be respectful to servers
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error searching {location}: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
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
    
    # Try to use Selenium if available
    use_selenium = SELENIUM_AVAILABLE
    if not SELENIUM_AVAILABLE:
        print("⚠️  Selenium not available. Scraping will use requests (may not work for JS-rendered sites)")
        print("   Install with: pip install selenium webdriver-manager")
    
    researcher = PropertyResearcher(config, use_selenium=use_selenium)
    
    if config.run_schedule == "daily":
        schedule.every().day.at(config.run_time).do(researcher.run_search)
    elif config.run_schedule == "weekly":
        schedule.every().week.do(researcher.run_search)
    
    # Run once immediately for testing
    print("Starting Italian property search...")
    print(f"Budget: €{config.min_price:,} - €{config.max_price:,}")
    print(f"Target towns: {', '.join(config.target_towns)}")
    print(f"Using Selenium: {researcher.use_selenium}")
    print("=" * 50)
    
    try:
        researcher.run_search()
        print("\n✅ Search completed! Check for generated HTML report.")
    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up Selenium driver
        if researcher.driver:
            try:
                researcher.driver.quit()
            except:
                pass
    
    # Uncomment to keep running on schedule
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)


if __name__ == "__main__":
    main()