# 🏗️ Property Scraping Architecture & Implementation Plan

## 📊 Technical Analysis

### **1. Geocoding Complexity: SIMPLE ✅**

**Answer: Not hard at all!** We'll use **Nominatim (OpenStreetMap)** - it's:
- ✅ **Free** (no API key needed)
- ✅ **Simple** (just HTTP requests)
- ✅ **Reliable** (used by millions)
- ✅ **No rate limits** (if used respectfully)

**How it works:**
1. During scraping, get property address from listing
2. Send address to Nominatim → get coordinates (lat/lng)
3. Calculate distance to nearest coast point (we'll pre-define coastal coordinates for each region)
4. Calculate distance to nearest airport (we already have airport locations)
5. Store distances in JSON

**Effort:** ~2-3 hours to implement, adds ~0.5-1 second per property (acceptable for 12-hour runs)

---

## 🏛️ Architecture Decision

### **Recommended Approach: Hybrid (Python + JavaScript)**

**Why this is best:**

1. **Python for Scraping** ✅
   - Already have scraping infrastructure
   - Better for complex parsing, geocoding, data processing
   - Can run on schedule (local machine or cloud)

2. **JSON Files for Storage** ✅
   - Simple, version-controlled
   - No database needed
   - Works perfectly with GitHub Pages
   - Easy to debug and inspect

3. **JavaScript for Display** ✅
   - Fast, client-side rendering
   - No server needed
   - Works with static hosting (GitHub Pages)
   - Handles favoriting seamlessly

4. **Static HTML Pages** ✅
   - One page per town (e.g., `towns/polignano.html`)
   - Each page reads its JSON file
   - Fast loading, SEO-friendly
   - Easy to maintain

---

## 📁 File Structure

```
italia/
├── data/                          # Scraped property data (JSON)
│   ├── puglia_polignano.json
│   ├── puglia_monopoli.json
│   ├── calabria_crotone.json
│   └── ...
├── towns/                         # Individual town pages
│   ├── polignano.html
│   ├── monopoli.html
│   ├── crotone.html
│   └── ...
├── property_research.py           # Enhanced scraper
├── scrape_scheduler.py            # Runs every 12 hours
└── index.html                     # Main page (links to towns)
```

---

## 🔄 Workflow

### **Scraping Process (Every 12 Hours):**

1. **Python scraper runs:**
   - Scrapes all 4 sites (Immobiliare, Casa, Idealista, Subito)
   - Filters by criteria:
     - Price: €150k-€400k
     - Bathrooms: ≥2 (or 1 if "perfect" keywords found)
     - Rooms: ≥2 (prefer 3+)
     - Property type: house, apartment, duplex
   - Geocodes each property address
   - Calculates distance to coast & airport
   - Saves to JSON: `data/{region}_{town}.json`

2. **JSON Structure:**
```json
{
  "town": "Polignano a Mare",
  "region": "Puglia",
  "last_updated": "2025-01-15T10:30:00",
  "properties": [
    {
      "id": "immobiliare_12345",
      "title": "Casa con vista mare",
      "price": 280000,
      "bedrooms": 3,
      "bathrooms": 2,
      "size_sqm": 120,
      "property_type": "house",
      "url": "https://...",
      "image_url": "https://...",
      "description": "...",
      "location": {
        "address": "Via Roma 10, Polignano a Mare",
        "lat": 40.996,
        "lng": 17.218,
        "distance_to_coast_km": 0.2,
        "distance_to_airport_km": 45.5
      },
      "source": "immobiliare",
      "scraped_at": "2025-01-15T10:30:00"
    }
  ]
}
```

3. **Git commit & push** (if running locally, or auto-commit if on server)

### **Display Process (User Browsing):**

1. **Main page (`index.html`):**
   - Shows all regions/towns
   - Each town links to its dedicated page: `towns/polignano.html`

2. **Town page (`towns/polignano.html`):**
   - **Top Section:** Town bio, images, references, lifestyle info
   - **Bottom Section:** Scraped properties (loaded from `data/puglia_polignano.json`)
   - Each property card shows:
     - Image, price, bedrooms, bathrooms, size
     - Distance to coast & airport
     - "Favorite" button
   - JavaScript loads JSON and renders properties

3. **Favoriting:**
   - User clicks "❤️ Favorite" on property
   - JavaScript adds to Papa's wishlist (same localStorage system)
   - Property appears in `collaborative_wishlist.html`

---

## 🎯 Implementation Steps

### **Phase 1: Enhanced Scraper** (2-3 hours)
- [ ] Add geocoding with Nominatim
- [ ] Add distance calculations (coast & airport)
- [ ] Enhance filtering (bathrooms, rooms, property type)
- [ ] Output JSON files per town
- [ ] Test with one town

### **Phase 2: Town Pages** (3-4 hours)
- [ ] Create template HTML for town pages
- [ ] Add town bios, images, references
- [ ] JavaScript to load and display properties from JSON
- [ ] Property card styling
- [ ] Favorite button integration

### **Phase 3: Main Page Integration** (1 hour)
- [ ] Update main page to link to town pages
- [ ] Add "View Scraped Properties" buttons

### **Phase 4: Scheduling** (1-2 hours)
- [ ] Create scheduler script
- [ ] Set up to run every 12 hours
- [ ] Auto-commit JSON files (if on server)

### **Phase 5: Testing & Refinement** (2-3 hours)
- [ ] Test all 4 sites
- [ ] Verify geocoding accuracy
- [ ] Test favoriting workflow
- [ ] Polish UI/UX

**Total Estimated Time: 9-13 hours**

---

## 🔧 Technical Details

### **Geocoding Implementation:**

```python
import requests
from geopy.distance import geodesic

def geocode_address(address, town, region):
    """Get coordinates for an address"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': f"{address}, {town}, {region}, Italy",
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'ItalianPropertyScraper/1.0'}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

def distance_to_coast(lat, lng, region):
    """Calculate distance to nearest coastal point"""
    # Pre-defined coastal coordinates for each region
    coast_points = {
        'Puglia': [(40.996, 17.218), ...],  # Polignano, etc.
        'Calabria': [(39.081, 17.127), ...],  # Crotone, etc.
        # ...
    }
    # Find nearest coast point
    min_dist = float('inf')
    for coast_lat, coast_lng in coast_points.get(region, []):
        dist = geodesic((lat, lng), (coast_lat, coast_lng)).km
        min_dist = min(min_dist, dist)
    return min_dist
```

### **Property Filtering:**

```python
def matches_criteria(property_data):
    """Check if property meets our requirements"""
    # Price range
    if not (150000 <= property_data['price'] <= 400000):
        return False
    
    # Bathrooms: at least 2, or 1 if "perfect" keywords
    bathrooms = property_data.get('bathrooms', 0)
    if bathrooms < 2:
        # Check for "perfect" keywords in description
        desc = property_data.get('description', '').lower()
        perfect_keywords = ['vista mare', 'spiaggia privata', 'terrazza', 'giardino']
        if bathrooms == 1 and any(kw in desc for kw in perfect_keywords):
            pass  # Allow 1 bathroom if perfect
        else:
            return False
    
    # Rooms: at least 2, prefer 3+
    bedrooms = property_data.get('bedrooms', 0)
    if bedrooms < 2:
        return False
    
    # Property type
    prop_type = property_data.get('property_type', '').lower()
    allowed_types = ['house', 'casa', 'appartamento', 'apartment', 'duplex', 'villa']
    if not any(t in prop_type for t in allowed_types):
        return False
    
    return True
```

---

## ✅ Advantages of This Approach

1. **Simple:** No complex infrastructure, just files
2. **Fast:** Static pages load instantly
3. **Maintainable:** Easy to debug, inspect JSON files
4. **Scalable:** Can add more towns easily
5. **Reliable:** Works with GitHub Pages (no server needed)
6. **Flexible:** Can run scraper locally or on cloud

---

## 🚀 Next Steps

1. **Start with Phase 1:** Enhance the scraper
2. **Test with one town:** Polignano a Mare (good test case)
3. **Iterate:** Refine based on results
4. **Expand:** Add more towns once working

---

**Ready to start implementation?** Let's begin with Phase 1! 🎯

