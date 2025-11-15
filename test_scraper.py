#!/usr/bin/env python3
"""
Simple test to verify our Italian property research setup
"""
import requests
from bs4 import BeautifulSoup
import time

def test_property_search():
    print("Testing Italian property search...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'DNT': '1',
    }
    
    # Test simple connection first
    test_urls = [
        "https://www.immobiliare.it",
        "https://www.casa.it", 
        "https://www.idealista.it"
    ]
    
    working_sites = []
    
    for url in test_urls:
        try:
            print(f"Testing {url}...")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                working_sites.append(url)
                print(f"  ✅ {url} is accessible")
            else:
                print(f"  ❌ {url} returned {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {url} failed: {e}")
        
        time.sleep(1)  # Be respectful
    
    print(f"\n✅ Working sites: {len(working_sites)}/{len(test_urls)}")
    
    # Test search on Casa.it (often more permissive)
    if "https://www.casa.it" in working_sites:
        print("\nTesting search on Casa.it...")
        try:
            search_url = "https://www.casa.it/vendita/residenziale/puglia/"
            response = requests.get(search_url, headers=headers, timeout=15)
            print(f"Search status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple strategies to find property listings
                print("\n  🔍 Analyzing page structure...")
                
                # Strategy 1: Look for common property listing classes
                listings1 = soup.find_all(['div', 'article'], class_=lambda x: x and ('property' in x.lower() or 'listing' in x.lower() or 'annuncio' in x.lower() or 'casa' in x.lower()))
                print(f"  Strategy 1 (class-based): Found {len(listings1)} elements")
                
                # Strategy 2: Look for links that might be property links
                property_links = soup.find_all('a', href=lambda x: x and ('/vendita/' in x or '/annuncio/' in x or '/immobile/' in x))
                print(f"  Strategy 2 (link-based): Found {len(property_links)} property links")
                
                # Strategy 3: Look for price patterns in the HTML
                prices = soup.find_all(string=lambda text: text and '€' in str(text) and any(char.isdigit() for char in str(text)))
                price_count = len([p for p in prices if len(str(p).strip()) < 50])  # Filter out long text
                print(f"  Strategy 3 (price-based): Found {price_count} price mentions")
                
                # Strategy 4: Look for common data attributes
                data_listings = soup.find_all(attrs={'data-id': True}) + soup.find_all(attrs={'data-property-id': True})
                print(f"  Strategy 4 (data-attributes): Found {len(data_listings)} elements with data IDs")
                
                # Strategy 5: Look for specific Casa.it structure
                casa_listings = soup.find_all(['div', 'article'], attrs={'class': lambda x: x and any(term in str(x).lower() for term in ['card', 'item', 'box', 'result'])})
                print(f"  Strategy 5 (generic cards): Found {len(casa_listings)} card/item elements")
                
                # Show sample of what we found
                if property_links:
                    print(f"\n  📋 Sample property links found:")
                    for link in property_links[:3]:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)[:50]
                        print(f"    - {text} -> {href[:80]}")
                
                # Check if page has JavaScript-rendered content indicators
                scripts = soup.find_all('script')
                react_vue_angular = any('react' in str(s).lower() or 'vue' in str(s).lower() or 'angular' in str(s).lower() for s in scripts)
                if react_vue_angular or len(scripts) > 10:
                    print(f"\n  ⚠️  Page appears to be JavaScript-rendered ({len(scripts)} scripts found)")
                    print(f"     May need Selenium/Playwright for full content")
                
        except Exception as e:
            print(f"Casa.it search failed: {e}")
    
    return working_sites

if __name__ == "__main__":
    working_sites = test_property_search()
    
    if working_sites:
        print(f"\n🎉 Success! We can access {len(working_sites)} property sites")
        print("Next step: Implement targeted scraping for the working sites")
    else:
        print("\n❌ All sites are blocking us. We may need:")
        print("  - Different approach (APIs, proxies)")
        print("  - Manual data collection")
        print("  - Alternative property sites")