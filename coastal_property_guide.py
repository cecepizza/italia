#!/usr/bin/env python3
"""
Coastal Italian Property Guide Generator
Focuses on coastal towns with walkable centers, shops, and nearby airports
"""
from datetime import datetime

class CoastalPropertyGuide:
    def __init__(self):
        self.budget_min = 150000
        self.budget_max = 400000
        
        # Coastal towns with walkable centers, shops, and airport access
        self.coastal_towns = {
            'Puglia Coast': {
                'towns': {
                    'Monopoli': {
                        'airport': 'Bari (45 min)',
                        'coast_type': 'Adriatic - beautiful old port town',
                        'walkable_center': 'Medieval old town with shops, restaurants',
                        'beach_access': 'Walking distance to beaches and marina',
                        'vibe': 'Historic fishing port, very walkable, great restaurants',
                        'search_terms': ['monopoli', 'puglia']
                    },
                    'Polignano a Mare': {
                        'airport': 'Bari (45 min)',
                        'coast_type': 'Adriatic - dramatic cliff-top town',
                        'walkable_center': 'Compact historic center, famous for views',
                        'beach_access': 'Beach below town, accessible by stairs',
                        'vibe': 'Tourist favorite, stunning views, pricier but walkable',
                        'search_terms': ['polignano a mare', 'puglia']
                    },
                    'Otranto': {
                        'airport': 'Brindisi (1 hr), Bari (2 hr)',
                        'coast_type': 'Adriatic - historic port, easternmost Italy',
                        'walkable_center': 'Walled medieval town with cathedral',
                        'beach_access': 'Town beach + nearby pristine beaches',
                        'vibe': 'Historic, less touristy, authentic coastal life',
                        'search_terms': ['otranto', 'puglia']
                    },
                    'Castro': {
                        'airport': 'Brindisi (1.5 hr)',
                        'coast_type': 'Adriatic - cliff-top fishing village',
                        'walkable_center': 'Small but charming center with essentials',
                        'beach_access': 'Marina Castro below with restaurants',
                        'vibe': 'Quiet, authentic, stunning coastal views',
                        'search_terms': ['castro', 'puglia', 'salento']
                    }
                }
            },
            'Calabria Coast': {
                'towns': {
                    'Tropea': {
                        'airport': 'Lamezia Terme (1 hr)',
                        'coast_type': 'Tyrrhenian - famous beach town',
                        'walkable_center': 'Historic center with shops, restaurants',
                        'beach_access': 'Stunning beach below town cliffs',
                        'vibe': 'Tourist destination, expensive but beautiful',
                        'search_terms': ['tropea', 'calabria']
                    },
                    'Pizzo': {
                        'airport': 'Lamezia Terme (30 min)',
                        'coast_type': 'Tyrrhenian - working fishing town',
                        'walkable_center': 'Authentic town center, great gelato',
                        'beach_access': 'Town beach and nearby sandy beaches',
                        'vibe': 'Authentic, affordable, famous for tartufo ice cream',
                        'search_terms': ['pizzo', 'calabria']
                    },
                    'Scilla': {
                        'airport': 'Reggio Calabria (30 min)',
                        'coast_type': 'Tyrrhenian - mythical fishing village',
                        'walkable_center': 'Small center, traditional fishing quarter',
                        'beach_access': 'Beach in town, views of Sicily',
                        'vibe': 'Authentic, affordable, stunning location',
                        'search_terms': ['scilla', 'calabria']
                    }
                }
            },
            'Sicily Coast': {
                'towns': {
                    'Cefalù': {
                        'airport': 'Palermo (1 hr)',
                        'coast_type': 'Tyrrhenian - Norman cathedral town',
                        'walkable_center': 'Medieval streets, shops, restaurants',
                        'beach_access': 'Golden beach right in town',
                        'vibe': 'Tourist favorite, pricey but stunning',
                        'search_terms': ['cefalu', 'sicilia']
                    },
                    'Taormina': {
                        'airport': 'Catania (1 hr)',
                        'coast_type': 'Ionian - hilltop town with coastal access',
                        'walkable_center': 'Luxury shopping, restaurants, Greek theater',
                        'beach_access': 'Cable car to Isola Bella beach',
                        'vibe': 'Upscale resort town, expensive but world-class',
                        'search_terms': ['taormina', 'sicilia']
                    },
                    'Castellammare del Golfo': {
                        'airport': 'Palermo (1 hr)',
                        'coast_type': 'Tyrrhenian - working port town',
                        'walkable_center': 'Traditional center with harbor',
                        'beach_access': 'Town beach and nearby Scopello',
                        'vibe': 'Authentic, affordable, great seafood',
                        'search_terms': ['castellammare del golfo', 'sicilia']
                    }
                }
            },
            'Liguria Coast': {
                'towns': {
                    'Monterosso al Mare': {
                        'airport': 'Genoa (2 hr by train), Pisa (2 hr)',
                        'coast_type': 'Ligurian Sea - Cinque Terre village',
                        'walkable_center': 'Car-free village, train accessible',
                        'beach_access': 'Only Cinque Terre town with real beach',
                        'vibe': 'Tourist destination, pricey, spectacular',
                        'search_terms': ['monterosso', 'liguria', 'cinque terre']
                    },
                    'Camogli': {
                        'airport': 'Genoa (45 min)',
                        'coast_type': 'Ligurian Sea - fishing village',
                        'walkable_center': 'Colorful houses, harbor restaurants',
                        'beach_access': 'Small beach, boat excursions',
                        'vibe': 'Authentic, upscale but not touristy',
                        'search_terms': ['camogli', 'liguria']
                    }
                }
            }
        }
    
    def generate_targeted_searches(self):
        """Generate specific search URLs for coastal properties"""
        searches = {}
        
        for region, region_data in self.coastal_towns.items():
            searches[region] = []
            
            for town, details in region_data['towns'].items():
                town_searches = {}
                
                # Immobiliare.it specific searches
                for search_term in details['search_terms']:
                    immobiliare_url = f"https://www.immobiliare.it/vendita-case/{search_term.replace(' ', '-')}/?prezzoMinimo={self.budget_min}&prezzoMassimo={self.budget_max}&localiMinimo=2&criterio=rilevanza"
                    town_searches['immobiliare'] = immobiliare_url
                
                # Casa.it searches
                casa_url = f"https://www.casa.it/vendita/residenziale/?localita={town.replace(' ', '+')}&prezzo_min={self.budget_min}&prezzo_max={self.budget_max}&locali_min=2"
                town_searches['casa'] = casa_url
                
                # Idealista searches  
                idealista_url = f"https://www.idealista.it/vendita-case/{town.lower().replace(' ', '-')}/?prezzo-min={self.budget_min}&prezzo-max={self.budget_max}&ordine=relevance"
                town_searches['idealista'] = idealista_url
                
                searches[region].append({
                    'town': town,
                    'details': details,
                    'urls': town_searches
                })
        
        return searches
    
    def create_coastal_html_guide(self, searches):
        """Create HTML guide focused on coastal properties"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🏖️ Italian Coastal Property Guide - Walk to Beach & Town!</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            line-height: 1.6; 
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #1976d2, #42a5f5); 
            color: white; 
            padding: 40px; 
            text-align: center; 
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .criteria {{ 
            background: #e8f5e8; 
            padding: 25px; 
            border-radius: 10px; 
            margin: 25px 0;
            border-left: 5px solid #4caf50;
        }}
        .region {{ 
            margin: 40px 0; 
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .region-header {{ 
            background: linear-gradient(45deg, #ff6b6b, #ffa726); 
            color: white; 
            padding: 20px 30px; 
            font-size: 24px; 
            font-weight: bold;
        }}
        .towns-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); 
            gap: 0;
        }}
        .town-card {{ 
            padding: 30px; 
            border-right: 1px solid #eee;
            position: relative;
        }}
        .town-card:nth-child(even) {{ background: #fafafa; }}
        .town-name {{ 
            font-size: 22px; 
            font-weight: bold; 
            color: #1976d2; 
            margin-bottom: 15px;
            border-bottom: 2px solid #e3f2fd;
            padding-bottom: 10px;
        }}
        .town-details {{ margin: 15px 0; }}
        .detail-item {{ 
            margin: 10px 0; 
            display: flex; 
            align-items: flex-start;
        }}
        .detail-icon {{ 
            margin-right: 10px; 
            font-size: 18px; 
            min-width: 25px;
        }}
        .search-buttons {{ 
            margin: 20px 0; 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px;
        }}
        .search-btn {{ 
            background: #4caf50; 
            color: white; 
            padding: 12px 18px; 
            border-radius: 8px; 
            text-decoration: none; 
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .search-btn:hover {{ 
            background: #45a049; 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .vibe {{ 
            background: #fff3e0; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0;
            border-left: 4px solid #ff9800;
            font-style: italic;
        }}
        .tips {{ 
            background: #f3e5f5; 
            padding: 25px; 
            border-radius: 10px; 
            margin: 30px 0;
        }}
        .budget-highlight {{ 
            background: #c8e6c9; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center; 
            font-weight: bold; 
            font-size: 18px;
            margin: 20px 0;
        }}
        .emoji {{ font-size: 20px; }}
        @media (max-width: 768px) {{
            .towns-grid {{ grid-template-columns: 1fr; }}
            .town-card {{ border-right: none; border-bottom: 1px solid #eee; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏖️ Italian Coastal Property Guide</h1>
            <h2>Walk to Beach + Town Center + Easy Airport Access</h2>
            <p>Perfect for your dad's dream of coastal living!</p>
            <div class="budget-highlight">🎯 Budget: €{self.budget_min:,} - €{self.budget_max:,}</div>
        </div>

        <div class="criteria">
            <h2>✅ Dad's Perfect Coastal Town Criteria</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <strong>🏖️ Coastal Location</strong><br>
                    Walking distance to beach and water
                </div>
                <div>
                    <strong>🛍️ Walkable Town Center</strong><br>
                    Shops, restaurants, daily necessities on foot
                </div>
                <div>
                    <strong>✈️ Airport Access</strong><br>
                    Major airport within 1-2 hours for easy travel
                </div>
                <div>
                    <strong>🏠 Right-Sized Property</strong><br>
                    2+ bedrooms, move-in ready or minor renovation
                </div>
            </div>
        </div>
"""

        # Generate content for each region
        for region, towns_data in searches.items():
            html += f"""
        <div class="region">
            <div class="region-header">
                📍 {region}
            </div>
            <div class="towns-grid">
"""
            
            for town_data in towns_data:
                town = town_data['town']
                details = town_data['details']
                urls = town_data['urls']
                
                html += f"""
                <div class="town-card">
                    <div class="town-name">🏘️ {town}</div>
                    <div class="town-details">
                        <div class="detail-item">
                            <span class="detail-icon">✈️</span>
                            <span><strong>Airport:</strong> {details['airport']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">🌊</span>
                            <span><strong>Coast:</strong> {details['coast_type']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">🚶</span>
                            <span><strong>Town Center:</strong> {details['walkable_center']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">🏖️</span>
                            <span><strong>Beach Access:</strong> {details['beach_access']}</span>
                        </div>
                    </div>
                    <div class="vibe">
                        <strong>🎭 Vibe:</strong> {details['vibe']}
                    </div>
                    <div class="search-buttons">
                        <a href="{urls['immobiliare']}" target="_blank" class="search-btn">
                            🏠 Immobiliare.it
                        </a>
                        <a href="{urls['casa']}" target="_blank" class="search-btn">
                            🏡 Casa.it
                        </a>
                        <a href="{urls['idealista']}" target="_blank" class="search-btn">
                            🏘️ Idealista.it
                        </a>
                    </div>
                </div>
"""
            
            html += """
            </div>
        </div>
"""

        html += f"""
        <div class="tips">
            <h2>💡 Coastal Property Search Tips</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h3>🔍 Search Keywords</h3>
                    <ul>
                        <li><strong>"vista mare"</strong> = sea view</li>
                        <li><strong>"fronte mare"</strong> = seafront</li>
                        <li><strong>"centro storico"</strong> = historic center</li>
                        <li><strong>"a piedi dal mare"</strong> = walking to sea</li>
                    </ul>
                </div>
                <div>
                    <h3>⚠️ Things to Check</h3>
                    <ul>
                        <li>Summer vs winter population</li>
                        <li>Seasonal restaurant closures</li>
                        <li>Parking situation in town</li>
                        <li>Public transportation options</li>
                    </ul>
                </div>
                <div>
                    <h3>📍 Distance Priorities</h3>
                    <ul>
                        <li>Beach: 5-10 min walk max</li>
                        <li>Shops/restaurants: 5 min walk</li>
                        <li>Airport: Under 2 hours drive</li>
                        <li>Hospital: Under 30 min drive</li>
                    </ul>
                </div>
                <div>
                    <h3>💰 Price Expectations</h3>
                    <ul>
                        <li>Puglia: Most affordable</li>
                        <li>Calabria: Great value</li>
                        <li>Sicily: Variable by location</li>
                        <li>Liguria: Most expensive</li>
                    </ul>
                </div>
            </div>
        </div>

        <div style="background: #e3f2fd; padding: 25px; border-radius: 10px; margin: 30px 0; text-align: center;">
            <h2>🎯 Next Steps for Dad</h2>
            <p style="font-size: 18px; margin: 20px 0;">
                1. Pick 2-3 regions that appeal to you<br>
                2. Search properties in those specific coastal towns<br>
                3. Save screenshots of interesting properties<br>
                4. Check Google Street View for walkability<br>
                5. Research flight connections from your area
            </p>
        </div>

        <div style="text-align: center; margin: 40px 0; color: #666;">
            <p>🤖 Generated specifically for coastal living preferences</p>
            <p>Last updated: {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
    </div>

    <script>
        // Add click tracking
        document.querySelectorAll('.search-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                this.style.background = '#2e7d32';
                this.innerHTML = this.innerHTML.replace('🏠', '✅').replace('🏡', '✅').replace('🏘️', '✅');
                setTimeout(() => {{
                    this.style.background = '#4caf50';
                    this.innerHTML = this.innerHTML.replace('✅', this.innerHTML.includes('Immobiliare') ? '🏠' : this.innerHTML.includes('Casa') ? '🏡' : '🏘️');
                }}, 2000);
            }});
        }});
    </script>
</body>
</html>
"""
        return html
    
    def run(self):
        """Generate the coastal property guide"""
        print("🏖️ Generating Coastal Italian Property Guide...")
        
        searches = self.generate_targeted_searches()
        html_content = self.create_coastal_html_guide(searches)
        
        filename = f"coastal_property_guide_{datetime.now().strftime('%Y%m%d')}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Coastal guide created: {filename}")
        print("🎯 Perfect for your dad's requirements:")
        print("   - Beach walking distance")
        print("   - Walkable town centers") 
        print("   - Easy airport access")
        print("   - Shops and restaurants on foot")
        
        return filename

if __name__ == "__main__":
    guide = CoastalPropertyGuide()
    guide.run()