#!/usr/bin/env python3
"""
Interactive Family Property Research Portal
Browse regions → Explore towns → Find houses → Build dad's wishlist
"""
import json
import os
from datetime import datetime

class FamilyPropertyPortal:
    def __init__(self):
        self.budget_min = 150000
        self.budget_max = 400000
        
        # Load saved wishlist if exists
        self.wishlist_file = "family_wishlist.json"
        self.load_wishlist()
        
        # Regional breakdown with detailed town info
        self.regions = {
            'Puglia': {
                'description': 'Heel of Italy - Authentic, affordable, great food',
                'climate': 'Mediterranean, mild winters, hot summers',
                'airport_hub': 'Bari Airport (BAI)',
                'coastal_towns': {
                    'Monopoli': {
                        'type': 'Historic port town',
                        'population': '49,000',
                        'beach_walk': '5 minutes to old port and beaches',
                        'town_center': 'Medieval old town, daily market, restaurants',
                        'airport_time': '45 minutes to Bari',
                        'price_range': '€120k-350k typical',
                        'pros': 'Authentic, walkable, great restaurants, airport access',
                        'cons': 'Can be crowded in summer',
                        'search_terms': ['monopoli', 'puglia', 'bari']
                    },
                    'Polignano a Mare': {
                        'type': 'Cliff-top coastal gem',
                        'population': '17,000',
                        'beach_walk': '10 minutes down to beach via stairs/paths',
                        'town_center': 'Compact center, famous for cliff views',
                        'airport_time': '45 minutes to Bari',
                        'price_range': '€150k-400k (premium for views)',
                        'pros': 'Stunning views, Instagram famous, walkable',
                        'cons': 'Tourist crowds, higher prices, limited beach access',
                        'search_terms': ['polignano a mare', 'puglia']
                    },
                    'Otranto': {
                        'type': 'Historic walled coastal city',
                        'population': '5,800',
                        'beach_walk': '2 minutes to town beach, many others nearby',
                        'town_center': 'UNESCO cathedral, shops, restaurants in walls',
                        'airport_time': '1.5 hours to Brindisi, 2 hours to Bari',
                        'price_range': '€80k-250k great value',
                        'pros': 'Historic, affordable, authentic, pristine beaches',
                        'cons': 'Further from airport, smaller town',
                        'search_terms': ['otranto', 'puglia', 'salento']
                    }
                },
                'inland_towns': {
                    'Andria': {
                        'type': 'Inland city near coast',
                        'population': '100,000',
                        'beach_walk': '30 minutes drive to coast',
                        'town_center': 'Large city with all amenities, cathedral',
                        'airport_time': '30 minutes to Bari',
                        'price_range': '€60k-200k very affordable',
                        'pros': 'Affordable, authentic, all services, airport access',
                        'cons': 'Not coastal, need car for beach',
                        'search_terms': ['andria', 'puglia']
                    }
                }
            },
            'Calabria': {
                'description': 'Toe of Italy - Stunning coast, mountains, very affordable',
                'climate': 'Mediterranean, mild winters, perfect summers',
                'airport_hub': 'Lamezia Terme Airport (SUF)',
                'coastal_towns': {
                    'Tropea': {
                        'type': 'Famous cliff-top beach resort',
                        'population': '6,000',
                        'beach_walk': '5 minutes down cliff path to famous beach',
                        'town_center': 'Tourist-focused but charming historic center',
                        'airport_time': '1 hour to Lamezia Terme',
                        'price_range': '€100k-300k (premium for views)',
                        'pros': 'World-famous beach, stunning views, good restaurants',
                        'cons': 'Very touristy, seasonal closures, crowded summer',
                        'search_terms': ['tropea', 'calabria']
                    },
                    'Pizzo': {
                        'type': 'Working fishing town',
                        'population': '9,000',
                        'beach_walk': '5 minutes to town beach',
                        'town_center': 'Authentic center, famous for tartufo gelato',
                        'airport_time': '30 minutes to Lamezia Terme',
                        'price_range': '€70k-180k excellent value',
                        'pros': 'Authentic, affordable, great food, airport close',
                        'cons': 'Less English spoken, working town feel',
                        'search_terms': ['pizzo', 'calabria']
                    },
                    'Scilla': {
                        'type': 'Mythical fishing village',
                        'population': '5,000',
                        'beach_walk': '2 minutes to beach, view of Sicily',
                        'town_center': 'Small but authentic, fishing quarter',
                        'airport_time': '30 minutes to Reggio Calabria',
                        'price_range': '€50k-150k incredible value',
                        'pros': 'Stunning location, very affordable, authentic',
                        'cons': 'Very small, limited services, seasonal',
                        'search_terms': ['scilla', 'calabria']
                    },
                    'Crotone': {
                        'type': 'Ancient coastal city',
                        'population': '65,000',
                        'beach_walk': '10 minutes to various beaches',
                        'town_center': 'Historic center, archaeological museum',
                        'airport_time': '1.5 hours to Lamezia Terme',
                        'price_range': '€40k-120k very affordable',
                        'pros': 'Affordable, authentic, historic, full services',
                        'cons': 'Less touristy (pro/con), further from airport',
                        'search_terms': ['crotone', 'calabria']
                    }
                }
            },
            'Sicily': {
                'description': 'Mediterranean island - Diverse, cultural, great airports',
                'climate': 'Mediterranean, warm winters, hot summers',
                'airport_hub': 'Catania Airport (CTA) or Palermo Airport (PMO)',
                'coastal_towns': {
                    'Cefalù': {
                        'type': 'Norman cathedral coastal town',
                        'population': '14,000',
                        'beach_walk': '2 minutes to golden beach from center',
                        'town_center': 'Medieval streets, shops, restaurants, cathedral',
                        'airport_time': '1 hour to Palermo',
                        'price_range': '€120k-350k (tourist premium)',
                        'pros': 'Stunning beach in town, walkable, good restaurants',
                        'cons': 'Tourist crowds, higher prices, parking issues',
                        'search_terms': ['cefalu', 'sicilia', 'palermo']
                    },
                    'Taormina': {
                        'type': 'Hilltop resort town',
                        'population': '11,000',
                        'beach_walk': '10 min cable car to Isola Bella beach',
                        'town_center': 'Luxury shopping, restaurants, Greek theater',
                        'airport_time': '1 hour to Catania',
                        'price_range': '€200k-500k+ (luxury market)',
                        'pros': 'World-class amenities, stunning views, cultural sites',
                        'cons': 'Very expensive, very touristy, not authentic',
                        'search_terms': ['taormina', 'sicilia']
                    },
                    'Catania': {
                        'type': 'Major city with coast access',
                        'population': '315,000',
                        'beach_walk': '15 minutes to city beaches',
                        'town_center': 'Major city, all amenities, baroque architecture',
                        'airport_time': '15 minutes to Catania airport',
                        'price_range': '€80k-250k city prices',
                        'pros': 'All services, airport next door, cultural life',
                        'cons': 'Big city, traffic, not quaint coastal feel',
                        'search_terms': ['catania', 'sicilia']
                    }
                }
            },
            'Liguria': {
                'description': 'Italian Riviera - Stunning but expensive',
                'climate': 'Mild year-round, protected by mountains',
                'airport_hub': 'Genoa Airport (GOA)',
                'coastal_towns': {
                    'Monterosso al Mare': {
                        'type': 'Cinque Terre village',
                        'population': '1,400',
                        'beach_walk': '1 minute - only Cinque Terre town with beach',
                        'town_center': 'Car-free village, train access only',
                        'airport_time': '2 hours to Genoa (by train)',
                        'price_range': '€300k-800k+ (premium)',
                        'pros': 'World heritage site, spectacular, beach access',
                        'cons': 'Very expensive, very touristy, car restrictions',
                        'search_terms': ['monterosso', 'liguria', 'cinque terre']
                    },
                    'Camogli': {
                        'type': 'Fishing village near Portofino',
                        'population': '5,500',
                        'beach_walk': '3 minutes to small beach',
                        'town_center': 'Colorful houses, harbor restaurants',
                        'airport_time': '45 minutes to Genoa',
                        'price_range': '€200k-500k (Riviera prices)',
                        'pros': 'Authentic, beautiful, good transport',
                        'cons': 'Expensive, small beach, limited parking',
                        'search_terms': ['camogli', 'liguria']
                    }
                }
            }
        }
    
    def load_wishlist(self):
        """Load existing family wishlist"""
        try:
            with open(self.wishlist_file, 'r') as f:
                self.wishlist = json.load(f)
        except FileNotFoundError:
            self.wishlist = []
    
    def save_wishlist(self):
        """Save wishlist to file"""
        with open(self.wishlist_file, 'w') as f:
            json.dump(self.wishlist, f, indent=2)
    
    def generate_search_urls(self, search_terms, town_name):
        """Generate property search URLs for a specific town"""
        urls = {}
        
        # Immobiliare.it
        main_term = search_terms[0].replace(' ', '-')
        immobiliare_url = f"https://www.immobiliare.it/vendita-case/{main_term}/?prezzoMinimo={self.budget_min}&prezzoMassimo={self.budget_max}&localiMinimo=2&criterio=rilevanza"
        urls['immobiliare'] = immobiliare_url
        
        # Casa.it
        casa_url = f"https://www.casa.it/vendita/residenziale/?localita={town_name.replace(' ', '+')}&prezzo_min={self.budget_min}&prezzo_max={self.budget_max}&locali_min=2"
        urls['casa'] = casa_url
        
        # Idealista.it
        idealista_url = f"https://www.idealista.it/vendita-case/{main_term}/?prezzo-min={self.budget_min}&prezzo-max={self.budget_max}&ordine=relevance"
        urls['idealista'] = idealista_url
        
        # Subito.it (local listings)
        subito_url = f"https://www.subito.it/annunci-italia/vendita/case/?q={town_name}&prezzo_min={self.budget_min}&prezzo_max={self.budget_max}"
        urls['subito'] = subito_url
        
        return urls
    
    def create_interactive_portal(self):
        """Create the main interactive portal HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🏡 Family Italian Property Portal</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #ff6b6b, #ffa726); 
            color: white; 
            padding: 30px; 
            text-align: center; 
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .tabs {{ 
            display: flex; 
            justify-content: center; 
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            padding: 5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .tab {{ 
            padding: 15px 25px; 
            margin: 0 5px; 
            background: transparent; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .tab.active {{ 
            background: #667eea; 
            color: white; 
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .tab-content {{ 
            display: none; 
            background: white; 
            border-radius: 15px; 
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        .tab-content.active {{ display: block; }}
        .regions-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 25px; 
            margin: 25px 0;
        }}
        .region-card {{ 
            border: 2px solid #e0e0e0; 
            border-radius: 15px; 
            padding: 25px; 
            transition: all 0.3s ease;
            cursor: pointer;
            background: white;
            position: relative;
            overflow: hidden;
        }}
        .region-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        }}
        .region-card:hover {{ 
            border-color: #667eea; 
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        }}
        .region-header {{ 
            font-size: 24px; 
            font-weight: bold; 
            color: #667eea; 
            margin-bottom: 15px;
        }}
        .towns-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 20px; 
            margin: 20px 0;
        }}
        .town-card {{ 
            border: 1px solid #e0e0e0; 
            border-radius: 12px; 
            padding: 20px; 
            background: #fafafa;
            transition: all 0.3s ease;
        }}
        .town-card:hover {{ 
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        .town-header {{ 
            font-size: 20px; 
            font-weight: bold; 
            color: #ff6b6b; 
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .town-type {{ 
            font-size: 12px; 
            background: #e3f2fd; 
            padding: 4px 8px; 
            border-radius: 4px;
            color: #1976d2;
        }}
        .town-details {{ margin: 15px 0; }}
        .detail-row {{ 
            margin: 8px 0; 
            display: flex;
            align-items: center;
        }}
        .detail-icon {{ 
            margin-right: 10px; 
            font-size: 16px; 
            min-width: 20px;
        }}
        .search-properties {{ 
            margin: 20px 0; 
        }}
        .search-buttons {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px; 
            margin: 15px 0;
        }}
        .search-btn {{ 
            background: #4caf50; 
            color: white; 
            padding: 10px 15px; 
            border: none; 
            border-radius: 8px; 
            text-decoration: none; 
            font-size: 14px; 
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .search-btn:hover {{ 
            background: #45a049; 
            transform: scale(1.05);
        }}
        .wishlist-btn {{ 
            background: #ff9800; 
            margin-top: 15px;
            width: 100%;
            padding: 12px;
            font-size: 16px;
        }}
        .wishlist-btn:hover {{ background: #f57c00; }}
        .pros-cons {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 15px; 
            margin: 15px 0;
        }}
        .pros {{ 
            background: #e8f5e8; 
            padding: 15px; 
            border-radius: 8px; 
            border-left: 4px solid #4caf50;
        }}
        .cons {{ 
            background: #ffebee; 
            padding: 15px; 
            border-radius: 8px; 
            border-left: 4px solid #f44336;
        }}
        .wishlist-section {{ 
            background: #f0f8ff; 
            border-radius: 15px; 
            padding: 25px;
        }}
        .wishlist-item {{ 
            background: white; 
            border-radius: 10px; 
            padding: 20px; 
            margin: 15px 0;
            border-left: 5px solid #ff9800;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .remove-btn {{ 
            background: #f44336; 
            color: white; 
            border: none; 
            padding: 8px 12px; 
            border-radius: 5px; 
            cursor: pointer;
        }}
        .instructions {{ 
            background: #e3f2fd; 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0;
            border-left: 5px solid #2196f3;
        }}
        @media (max-width: 768px) {{
            .towns-grid {{ grid-template-columns: 1fr; }}
            .pros-cons {{ grid-template-columns: 1fr; }}
            .tabs {{ flex-direction: column; }}
            .search-buttons {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏡 Family Italian Property Portal</h1>
            <p>Explore Regions → Discover Towns → Find Houses → Build Dad's Wishlist</p>
            <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                <strong>🎯 Budget: €{self.budget_min:,} - €{self.budget_max:,} | ✈️ Focus: Coastal + Airport Access | 👨 For: Dad's Review</strong>
            </div>
        </div>

        <div class="instructions">
            <h2>📋 How This Works</h2>
            <ol>
                <li><strong>Browse Regions</strong> - Click through Italy's coastal regions to learn about each area</li>
                <li><strong>Explore Towns</strong> - See detailed info about walkability, beaches, and airport access</li>
                <li><strong>Search Properties</strong> - Click property search buttons for each town you're interested in</li>
                <li><strong>Add to Wishlist</strong> - Found a great property? Add town/property combos to Dad's review list</li>
                <li><strong>Review Together</strong> - Dad can review the wishlist and we can plan visits to top choices</li>
            </ol>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('explore')">🗺️ Explore Regions</button>
            <button class="tab" onclick="showTab('wishlist')">❤️ Dad's Wishlist</button>
            <button class="tab" onclick="showTab('search-tips')">💡 Search Tips</button>
        </div>

        <div id="explore" class="tab-content active">
            <div class="regions-grid">
"""
        
        # Generate region cards
        for region_name, region_data in self.regions.items():
            html += f"""
                <div class="region-card" onclick="toggleRegion('{region_name}')">
                    <div class="region-header">📍 {region_name}</div>
                    <p><strong>{region_data['description']}</strong></p>
                    <div class="detail-row">
                        <span class="detail-icon">🌤️</span>
                        <span>{region_data['climate']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-icon">✈️</span>
                        <span>{region_data['airport_hub']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-icon">🏖️</span>
                        <span>{len(region_data.get('coastal_towns', {}))} coastal towns</span>
                    </div>
                    <div id="{region_name}-towns" style="display: none; margin-top: 20px;">
                        <h3>Coastal Towns in {region_name}:</h3>
                        <div class="towns-grid">
"""
            
            # Add coastal towns
            for town_name, town_data in region_data.get('coastal_towns', {}).items():
                search_urls = self.generate_search_urls(town_data['search_terms'], town_name)
                
                html += f"""
                            <div class="town-card">
                                <div class="town-header">
                                    🏘️ {town_name}
                                    <span class="town-type">{town_data['type']}</span>
                                </div>
                                <div class="town-details">
                                    <div class="detail-row">
                                        <span class="detail-icon">👥</span>
                                        <span>{town_data['population']} people</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">🏖️</span>
                                        <span>{town_data['beach_walk']}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">🛍️</span>
                                        <span>{town_data['town_center']}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">✈️</span>
                                        <span>{town_data['airport_time']}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">💰</span>
                                        <span>{town_data['price_range']}</span>
                                    </div>
                                </div>
                                
                                <div class="pros-cons">
                                    <div class="pros">
                                        <strong>✅ Pros:</strong><br>
                                        {town_data['pros']}
                                    </div>
                                    <div class="cons">
                                        <strong>⚠️ Cons:</strong><br>
                                        {town_data['cons']}
                                    </div>
                                </div>
                                
                                <div class="search-properties">
                                    <strong>🔍 Search Properties:</strong>
                                    <div class="search-buttons">
                                        <a href="{search_urls['immobiliare']}" target="_blank" class="search-btn">🏠 Immobiliare.it</a>
                                        <a href="{search_urls['casa']}" target="_blank" class="search-btn">🏡 Casa.it</a>
                                        <a href="{search_urls['idealista']}" target="_blank" class="search-btn">🏘️ Idealista.it</a>
                                        <a href="{search_urls['subito']}" target="_blank" class="search-btn">📋 Subito.it</a>
                                    </div>
                                    <button class="search-btn wishlist-btn" onclick="addToWishlist('{region_name}', '{town_name}', 'Interested in this town')">
                                        ❤️ Add Town to Dad's Wishlist
                                    </button>
                                </div>
                            </div>
"""
            
            # Add inland towns if they exist
            if 'inland_towns' in region_data:
                html += """
                        </div>
                        <h3>Inland Towns (Near Coast):</h3>
                        <div class="towns-grid">
"""
                for town_name, town_data in region_data['inland_towns'].items():
                    search_urls = self.generate_search_urls(town_data['search_terms'], town_name)
                    
                    html += f"""
                            <div class="town-card">
                                <div class="town-header">
                                    🏙️ {town_name}
                                    <span class="town-type">{town_data['type']}</span>
                                </div>
                                <div class="town-details">
                                    <div class="detail-row">
                                        <span class="detail-icon">👥</span>
                                        <span>{town_data['population']} people</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">🏖️</span>
                                        <span>{town_data['beach_walk']}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">🛍️</span>
                                        <span>{town_data['town_center']}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">✈️</span>
                                        <span>{town_data['airport_time']}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-icon">💰</span>
                                        <span>{town_data['price_range']}</span>
                                    </div>
                                </div>
                                
                                <div class="pros-cons">
                                    <div class="pros">
                                        <strong>✅ Pros:</strong><br>
                                        {town_data['pros']}
                                    </div>
                                    <div class="cons">
                                        <strong>⚠️ Cons:</strong><br>
                                        {town_data['cons']}
                                    </div>
                                </div>
                                
                                <div class="search-properties">
                                    <strong>🔍 Search Properties:</strong>
                                    <div class="search-buttons">
                                        <a href="{search_urls['immobiliare']}" target="_blank" class="search-btn">🏠 Immobiliare.it</a>
                                        <a href="{search_urls['casa']}" target="_blank" class="search-btn">🏡 Casa.it</a>
                                        <a href="{search_urls['idealista']}" target="_blank" class="search-btn">🏘️ Idealista.it</a>
                                        <a href="{search_urls['subito']}" target="_blank" class="search-btn">📋 Subito.it</a>
                                    </div>
                                    <button class="search-btn wishlist-btn" onclick="addToWishlist('{region_name}', '{town_name}', 'Interested in this town')">
                                        ❤️ Add Town to Dad's Wishlist
                                    </button>
                                </div>
                            </div>
"""
            
            html += """
                        </div>
                    </div>
                </div>
"""
        
        # Wishlist tab
        html += f"""
            </div>
        </div>

        <div id="wishlist" class="tab-content">
            <div class="wishlist-section">
                <h2>❤️ Dad's Property Wishlist</h2>
                <p>Properties and towns the family has added for Dad to review. Perfect for planning our Italy trip!</p>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>📝 Add Custom Property to Wishlist</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 2fr auto; gap: 10px; align-items: end;">
                        <input type="text" id="custom-region" placeholder="Region (e.g. Puglia)" style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <input type="text" id="custom-town" placeholder="Town Name" style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <input type="text" id="custom-notes" placeholder="Property details, price, URL, notes..." style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <button onclick="addCustomToWishlist()" class="search-btn">Add to Wishlist</button>
                    </div>
                </div>
                
                <div id="wishlist-items">
                    <!-- Wishlist items will be populated by JavaScript -->
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #e8f5e8; border-radius: 10px;">
                    <h3>📊 Next Steps</h3>
                    <ul>
                        <li>Share this wishlist with Dad for review</li>
                        <li>Plan virtual tours of top properties</li>
                        <li>Research flights to nearest airports</li>
                        <li>Contact real estate agents for favorites</li>
                        <li>Schedule Italy trip to visit finalists</li>
                    </ul>
                </div>
            </div>
        </div>

        <div id="search-tips" class="tab-content">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px;">
                <div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
                    <h3>🔍 Property Search Tips</h3>
                    <ul>
                        <li><strong>"vista mare"</strong> = sea view</li>
                        <li><strong>"fronte mare"</strong> = seafront</li>
                        <li><strong>"centro storico"</strong> = historic center</li>
                        <li><strong>"a piedi dal mare"</strong> = walk to sea</li>
                        <li><strong>"ristrutturato"</strong> = renovated</li>
                        <li><strong>"abitabile"</strong> = livable condition</li>
                    </ul>
                </div>
                
                <div style="background: #fff3e0; padding: 20px; border-radius: 10px;">
                    <h3>💰 Price Analysis</h3>
                    <ul>
                        <li><strong>Puglia:</strong> Best value, €50k-300k typical</li>
                        <li><strong>Calabria:</strong> Very affordable, €40k-200k</li>
                        <li><strong>Sicily:</strong> Variable, €80k-400k+</li>
                        <li><strong>Liguria:</strong> Premium, €200k-800k+</li>
                        <li><strong>Coastal premium:</strong> +30-50% vs inland</li>
                        <li><strong>Airport proximity:</strong> +20-30% premium</li>
                    </ul>
                </div>
                
                <div style="background: #f3e5f5; padding: 20px; border-radius: 10px;">
                    <h3>✅ Evaluation Checklist</h3>
                    <ul>
                        <li>Walk time to beach (under 10 min?)</li>
                        <li>Walk time to shops/restaurants</li>
                        <li>Drive time to airport</li>
                        <li>Property condition and age</li>
                        <li>Parking availability</li>
                        <li>Internet connectivity</li>
                        <li>English-speaking services</li>
                    </ul>
                </div>
                
                <div style="background: #e8f5e8; padding: 20px; border-radius: 10px;">
                    <h3>🎯 Dad's Priorities</h3>
                    <ul>
                        <li><strong>Beach access:</strong> Walking distance essential</li>
                        <li><strong>Town center:</strong> Must be walkable</li>
                        <li><strong>Airport:</strong> Under 2 hours drive</li>
                        <li><strong>Services:</strong> Shops, restaurants, pharmacy</li>
                        <li><strong>Authentic feel:</strong> Not too touristy</li>
                        <li><strong>Year-round life:</strong> Not seasonal only</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let wishlist = {json.dumps(self.wishlist)};
        
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'wishlist') {{
                displayWishlist();
            }}
        }}
        
        function toggleRegion(regionName) {{
            const townDiv = document.getElementById(regionName + '-towns');
            if (townDiv.style.display === 'none') {{
                townDiv.style.display = 'block';
            }} else {{
                townDiv.style.display = 'none';
            }}
        }}
        
        function addToWishlist(region, town, notes) {{
            const item = {{
                region: region,
                town: town,
                notes: notes,
                added_by: 'Family Member',
                date_added: new Date().toLocaleDateString()
            }};
            
            wishlist.push(item);
            saveWishlist();
            alert('✅ Added to Dad\\'s wishlist: ' + town + ', ' + region);
            
            if (document.getElementById('wishlist').classList.contains('active')) {{
                displayWishlist();
            }}
        }}
        
        function addCustomToWishlist() {{
            const region = document.getElementById('custom-region').value;
            const town = document.getElementById('custom-town').value;
            const notes = document.getElementById('custom-notes').value;
            
            if (!region || !town || !notes) {{
                alert('Please fill in all fields');
                return;
            }}
            
            addToWishlist(region, town, notes);
            
            // Clear form
            document.getElementById('custom-region').value = '';
            document.getElementById('custom-town').value = '';
            document.getElementById('custom-notes').value = '';
        }}
        
        function removeFromWishlist(index) {{
            wishlist.splice(index, 1);
            saveWishlist();
            displayWishlist();
        }}
        
        function displayWishlist() {{
            const container = document.getElementById('wishlist-items');
            
            if (wishlist.length === 0) {{
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><h3>No items in wishlist yet</h3><p>Browse regions and towns, then click "Add to Wishlist" buttons!</p></div>';
                return;
            }}
            
            let html = '<h3>📋 ' + wishlist.length + ' Items for Dad to Review:</h3>';
            
            wishlist.forEach((item, index) => {{
                html += `
                    <div class="wishlist-item">
                        <div>
                            <h4 style="margin: 0 0 10px 0; color: #ff6b6b;">${{item.town}}, ${{item.region}}</h4>
                            <p style="margin: 5px 0;"><strong>Notes:</strong> ${{item.notes}}</p>
                            <p style="margin: 5px 0; font-size: 12px; color: #666;">Added by ${{item.added_by}} on ${{item.date_added}}</p>
                        </div>
                        <button class="remove-btn" onclick="removeFromWishlist(${{index}})">Remove</button>
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }}
        
        function saveWishlist() {{
            // In a real app, this would save to a server
            // For now, it just updates the local variable
            console.log('Wishlist saved:', wishlist);
        }}
        
        // Initialize
        displayWishlist();
        
        // Add click tracking
        document.querySelectorAll('.search-btn').forEach(btn => {{
            if (!btn.onclick) {{ // Don't override wishlist buttons
                btn.addEventListener('click', function() {{
                    this.style.background = '#2e7d32';
                    const originalText = this.innerHTML;
                    this.innerHTML = '✅ Opening...';
                    setTimeout(() => {{
                        this.innerHTML = originalText;
                        this.style.background = '#4caf50';
                    }}, 2000);
                }});
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def run(self):
        """Generate the interactive family portal"""
        print("🏡 Generating Interactive Family Property Portal...")
        
        html_content = self.create_interactive_portal()
        filename = f"family_property_portal_{datetime.now().strftime('%Y%m%d')}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Also save current wishlist
        self.save_wishlist()
        
        print(f"✅ Interactive portal created: {filename}")
        print("🎯 Features included:")
        print("   - Browse all coastal regions and towns")
        print("   - Direct property search links for each town")
        print("   - Interactive wishlist for Dad's review")
        print("   - Detailed town comparisons")
        print("   - Mobile-friendly design")
        print("   - Family collaboration tools")
        
        return filename

if __name__ == "__main__":
    portal = FamilyPropertyPortal()
    portal.run()