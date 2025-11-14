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
                listings = soup.find_all(['div', 'article'], class_=lambda x: x and ('property' in x.lower() or 'listing' in x.lower()))
                print(f"Found {len(listings)} potential property elements")
                
                # Look for prices to verify we're getting property data
                prices = soup.find_all(text=lambda text: text and '€' in text)
                price_count = len([p for p in prices if any(char.isdigit() for char in p)])
                print(f"Found {price_count} price elements")
                
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