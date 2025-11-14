#!/usr/bin/env python3
"""
Simple Property URL Collector for Italian Real Estate
Saves property URLs for manual review by the family
"""
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

class PropertyURLCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        }
        
        self.towns = {
            'Crotone': 'calabria/crotone',
            'Catania': 'sicilia/catania', 
            'Andria': 'puglia/andria',
            'Rodi Garganico': 'puglia/foggia/rodi-garganico'
        }
        
        self.budget_min = 150000
        self.budget_max = 400000
        
    def collect_casa_it_urls(self, town, region_path):
        """Collect URLs from Casa.it"""
        print(f"Searching Casa.it for {town}...")
        
        base_url = f"https://www.casa.it/vendita/residenziale/{region_path}/"
        
        try:
            response = requests.get(base_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Casa.it returned {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for property links
            links = soup.find_all('a', href=True)
            property_urls = []
            
            for link in links:
                href = link['href']
                if '/vendita/' in href and ('/casa-' in href or '/appartamento-' in href or '/villa-' in href):
                    full_url = urljoin(base_url, href)
                    
                    # Extract basic info from the link context
                    property_info = {
                        'url': full_url,
                        'site': 'Casa.it',
                        'town': town,
                        'title': link.get_text(strip=True) or 'Property',
                        'found_date': datetime.now().isoformat(),
                        'estimated_price': 'Unknown'
                    }
                    
                    # Try to find price near the link
                    parent = link.find_parent()
                    if parent:
                        price_text = parent.get_text()
                        if '€' in price_text:
                            import re
                            price_match = re.search(r'€\s*([\d.,]+)', price_text.replace('.', ''))
                            if price_match:
                                property_info['estimated_price'] = price_match.group(0)
                    
                    property_urls.append(property_info)
                    
            print(f"  ✅ Found {len(property_urls)} potential properties")
            return property_urls[:20]  # Limit to first 20
            
        except Exception as e:
            print(f"  ❌ Error collecting from Casa.it: {e}")
            return []
    
    def collect_immobiliare_it_urls(self, town):
        """Collect URLs from Immobiliare.it search pages"""
        print(f"Searching Immobiliare.it for {town}...")
        
        # Try direct search URL
        search_url = f"https://www.immobiliare.it/vendita-case/{town.lower().replace(' ', '-')}/"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Immobiliare.it returned {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for property links
            links = soup.find_all('a', href=True)
            property_urls = []
            
            for link in links:
                href = link['href']
                if '/annunci/' in href and href.startswith('/annunci/'):
                    full_url = f"https://www.immobiliare.it{href}"
                    
                    property_info = {
                        'url': full_url,
                        'site': 'Immobiliare.it',
                        'town': town,
                        'title': link.get_text(strip=True) or 'Property',
                        'found_date': datetime.now().isoformat(),
                        'estimated_price': 'Unknown'
                    }
                    
                    property_urls.append(property_info)
                    
            print(f"  ✅ Found {len(property_urls)} properties")
            return property_urls[:20]  # Limit to first 20
            
        except Exception as e:
            print(f"  ❌ Error collecting from Immobiliare.it: {e}")
            return []
    
    def save_results(self, all_properties):
        """Save results to CSV and JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Save as CSV for easy viewing
        csv_filename = f"property_urls_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['town', 'site', 'title', 'estimated_price', 'url', 'found_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for prop in all_properties:
                writer.writerow(prop)
        
        # Save as JSON for programmatic use
        json_filename = f"property_urls_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_properties, jsonfile, indent=2, ensure_ascii=False)
        
        # Create simple HTML report
        html_filename = f"property_urls_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(self.create_html_report(all_properties))
        
        print(f"\n📁 Results saved:")
        print(f"  📋 CSV: {csv_filename}")
        print(f"  📄 JSON: {json_filename}")
        print(f"  🌐 HTML: {html_filename}")
        
        return csv_filename, json_filename, html_filename
    
    def create_html_report(self, properties):
        """Create HTML report of collected URLs"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Italian Property URLs - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #1976d2; color: white; padding: 20px; text-align: center; }}
        .property {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
        .price {{ font-weight: bold; color: #d32f2f; font-size: 18px; }}
        .site {{ background: #e3f2fd; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
        .town {{ background: #f1f8e9; padding: 5px 10px; border-radius: 3px; font-size: 12px; margin-left: 10px; }}
        a {{ text-decoration: none; color: #1976d2; }}
        a:hover {{ text-decoration: underline; }}
        .summary {{ background: #f5f5f5; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🇮🇹 Italian Property URLs Collection</h1>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>✅ <strong>{len(properties)} property URLs collected</strong></p>
        <p>🎯 Budget Range: €150,000 - €400,000</p>
        <p>📍 Target Towns: {', '.join(self.towns.keys())}</p>
    </div>
"""
        
        # Group by town
        by_town = {}
        for prop in properties:
            town = prop['town']
            if town not in by_town:
                by_town[town] = []
            by_town[town].append(prop)
        
        for town, town_properties in by_town.items():
            html += f"<h2>🏘️ {town} ({len(town_properties)} properties)</h2>"
            
            for prop in town_properties:
                html += f"""
                <div class="property">
                    <div style="margin-bottom: 10px;">
                        <span class="site">{prop['site']}</span>
                        <span class="town">{prop['town']}</span>
                    </div>
                    <h3><a href="{prop['url']}" target="_blank">{prop['title']}</a></h3>
                    <div class="price">💰 {prop['estimated_price']}</div>
                    <p style="font-size: 12px; color: #666;">Found: {prop['found_date'][:10]}</p>
                </div>
                """
        
        html += """
</body>
</html>
"""
        return html
    
    def run_collection(self):
        """Run the complete URL collection process"""
        print("🏡 Starting Italian Property URL Collection")
        print("=" * 50)
        
        all_properties = []
        
        for town, region_path in self.towns.items():
            print(f"\n🔍 Searching {town}...")
            
            # Collect from Casa.it
            casa_properties = self.collect_casa_it_urls(town, region_path)
            all_properties.extend(casa_properties)
            
            time.sleep(2)  # Be respectful
            
            # Collect from Immobiliare.it
            immobiliare_properties = self.collect_immobiliare_it_urls(town)
            all_properties.extend(immobiliare_properties)
            
            time.sleep(2)  # Be respectful
        
        print(f"\n🎉 Collection Complete!")
        print(f"📊 Total URLs collected: {len(all_properties)}")
        
        if all_properties:
            self.save_results(all_properties)
        else:
            print("❌ No property URLs found")
        
        return all_properties

if __name__ == "__main__":
    collector = PropertyURLCollector()
    results = collector.run_collection()