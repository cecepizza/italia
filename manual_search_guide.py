#!/usr/bin/env python3
"""
Manual Search Guide Generator for Italian Properties
Creates search URLs and guides for family members to use manually
"""
from datetime import datetime
import webbrowser
import sys

class ManualSearchGuide:
    def __init__(self):
        self.budget_min = 150000
        self.budget_max = 400000
        self.towns = {
            'Crotone': {'region': 'Calabria', 'province': 'Crotone'},
            'Catania': {'region': 'Sicilia', 'province': 'Catania'}, 
            'Andria': {'region': 'Puglia', 'province': 'Barletta-Andria-Trani'},
            'Rodi Garganico': {'region': 'Puglia', 'province': 'Foggia'}
        }
    
    def generate_search_urls(self):
        """Generate direct search URLs for each site and town"""
        urls = {}
        
        for town, info in self.towns.items():
            urls[town] = {}
            
            # Immobiliare.it URLs
            town_slug = town.lower().replace(' ', '-').replace('ò', 'o')
            region_slug = info['region'].lower()
            
            immobiliare_url = f"https://www.immobiliare.it/vendita-case/{region_slug}/?prezzoMassimo={self.budget_max}&prezzoMinimo={self.budget_min}&localiMinimo=2&criterio=rilevanza"
            urls[town]['immobiliare'] = immobiliare_url
            
            # Casa.it URLs
            region_casa = info['region'].lower().replace('sicilia', 'sicilia')
            casa_url = f"https://www.casa.it/vendita/residenziale/{region_casa}/?localita={town}&prezzo_max={self.budget_max}&prezzo_min={self.budget_min}&locali_min=2"
            urls[town]['casa'] = casa_url
            
            # Idealista.it URLs (when accessible)
            idealista_url = f"https://www.idealista.it/vendita-case/{town_slug}/?prezzo-min={self.budget_min}&prezzo-max={self.budget_max}&ordine=relevance"
            urls[town]['idealista'] = idealista_url
            
            # Subito.it (local classifieds)
            subito_url = f"https://www.subito.it/annunci-italia/vendita/case/?q={town}&prezzo_min={self.budget_min}&prezzo_max={self.budget_max}"
            urls[town]['subito'] = subito_url
        
        return urls
    
    def create_html_guide(self, urls):
        """Create HTML guide with all search URLs and instructions"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🇮🇹 Italian Property Manual Search Guide</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #1976d2, #42a5f5); color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .town-section {{ margin: 30px 0; border: 2px solid #e3f2fd; border-radius: 10px; padding: 20px; }}
        .town-name {{ background: #1976d2; color: white; padding: 10px 20px; border-radius: 5px; margin: -10px -10px 20px -10px; }}
        .site-links {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }}
        .site-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: #f8f9fa; }}
        .site-name {{ font-weight: bold; color: #1976d2; font-size: 16px; margin-bottom: 10px; }}
        .search-link {{ background: #4caf50; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; display: inline-block; margin: 5px 0; }}
        .search-link:hover {{ background: #45a049; }}
        .manual-link {{ background: #ff9800; color: white; padding: 8px 12px; border-radius: 5px; text-decoration: none; display: inline-block; margin: 5px 0; font-size: 14px; }}
        .manual-link:hover {{ background: #f57c00; }}
        .instructions {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .tips {{ background: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        .checklist {{ background: #f3e5f5; padding: 15px; border-radius: 8px; }}
        ul {{ margin: 10px 0; }}
        .emoji {{ font-size: 20px; }}
        .budget {{ background: #c8e6c9; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="emoji">🏡 Italian Property Manual Search Guide</h1>
        <p>Your Complete Family Research Toolkit</p>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <div class="budget">🎯 Budget: €{self.budget_min:,} - €{self.budget_max:,}</div>
    </div>

    <div class="instructions">
        <h2>🚀 How to Use This Guide</h2>
        <ol>
            <li><strong>Click "Search Now"</strong> buttons to open pre-configured searches</li>
            <li><strong>Browse results</strong> and save interesting properties to a shared document</li>
            <li><strong>Use "Manual Search"</strong> if the direct links don't work</li>
            <li><strong>Share findings</strong> in your family group chat with property URLs</li>
        </ol>
    </div>
"""
        
        for town, town_urls in urls.items():
            region = self.towns[town]['region']
            html += f"""
    <div class="town-section">
        <div class="town-name">📍 {town}, {region}</div>
        
        <div class="site-links">
            <div class="site-card">
                <div class="site-name">🏠 Immobiliare.it</div>
                <p>Italy's largest property site</p>
                <a href="{town_urls['immobiliare']}" target="_blank" class="search-link">🔍 Search Now</a><br>
                <a href="https://www.immobiliare.it" target="_blank" class="manual-link">Manual Search</a>
            </div>
            
            <div class="site-card">
                <div class="site-name">🏡 Casa.it</div>
                <p>Regional property listings</p>
                <a href="{town_urls['casa']}" target="_blank" class="search-link">🔍 Search Now</a><br>
                <a href="https://www.casa.it" target="_blank" class="manual-link">Manual Search</a>
            </div>
            
            <div class="site-card">
                <div class="site-name">🏘️ Idealista.it</div>
                <p>Modern property platform</p>
                <a href="{town_urls['idealista']}" target="_blank" class="search-link">🔍 Search Now</a><br>
                <a href="https://www.idealista.it" target="_blank" class="manual-link">Manual Search</a>
            </div>
            
            <div class="site-card">
                <div class="site-name">📋 Subito.it</div>
                <p>Local classifieds & direct sales</p>
                <a href="{town_urls['subito']}" target="_blank" class="search-link">🔍 Search Now</a><br>
                <a href="https://www.subito.it" target="_blank" class="manual-link">Manual Search</a>
            </div>
        </div>
    </div>
"""
        
        html += f"""
    <div class="tips">
        <h2>💡 Search Tips</h2>
        <ul>
            <li><strong>Use Chrome Translate</strong> - Right-click and "Translate to English"</li>
            <li><strong>Price formats:</strong> €150.000 = €150,000 (periods vs commas)</li>
            <li><strong>Key words:</strong> "vendita" = for sale, "locali" = rooms, "mq" = square meters</li>
            <li><strong>Property types:</strong> "casa" = house, "appartamento" = apartment, "villa" = villa</li>
            <li><strong>Conditions:</strong> "abitabile" = livable, "da ristrutturare" = needs renovation</li>
        </ul>
    </div>

    <div class="checklist">
        <h2>✅ Family Research Checklist</h2>
        <p><strong>For each interesting property, collect:</strong></p>
        <ul>
            <li>📍 Exact address and neighborhood</li>
            <li>💰 Price and price per square meter</li>
            <li>🏠 Size, bedrooms, bathrooms</li>
            <li>🔧 Condition (move-in ready vs renovation needed)</li>
            <li>📅 How long on market</li>
            <li>📞 Agent contact information</li>
            <li>📸 Screenshot or save photos</li>
            <li>🔗 Save the property URL</li>
        </ul>
    </div>

    <div class="instructions">
        <h2>📊 Family Coordination</h2>
        <ul>
            <li><strong>Create a shared spreadsheet</strong> with everyone's findings</li>
            <li><strong>Weekly family calls</strong> to review discoveries</li>
            <li><strong>Assign towns</strong> to different family members</li>
            <li><strong>Set up Google Alerts</strong> for "{town} property for sale"</li>
        </ul>
    </div>

    <script>
        // Add some interactivity
        document.querySelectorAll('.search-link').forEach(link => {{
            link.addEventListener('click', function() {{
                this.style.background = '#2e7d32';
                this.innerHTML = '✅ Opening...';
                setTimeout(() => {{
                    this.innerHTML = '🔍 Search Now';
                    this.style.background = '#4caf50';
                }}, 2000);
            }});
        }});
    </script>
</body>
</html>
"""
        return html
    
    def create_family_worksheet(self):
        """Create a template worksheet for tracking findings"""
        worksheet = """# Italian Property Research Worksheet

## Family Member: _______________
## Research Date: _______________
## Town Focus: __________________

### Properties Found:

#### Property 1:
- **URL:** 
- **Price:** €_______
- **Size:** _____ m²
- **Bedrooms:** _____
- **Condition:** 
- **Notes:** 


#### Property 2:
- **URL:** 
- **Price:** €_______
- **Size:** _____ m²
- **Bedrooms:** _____
- **Condition:** 
- **Notes:** 


#### Property 3:
- **URL:** 
- **Price:** €_______
- **Size:** _____ m²
- **Bedrooms:** _____
- **Condition:** 
- **Notes:** 

### Research Notes:
- **Average prices in this town:** €_______
- **Best neighborhoods:** 
- **Properties to visit on trip:** 
- **Questions for real estate agents:** 

### Next Steps:
- [ ] Share findings with family
- [ ] Schedule virtual tour if available
- [ ] Contact agent for more info
- [ ] Research neighborhood amenities
"""
        return worksheet
    
    def run(self, open_browser=True):
        """Generate the complete manual search guide"""
        print("🏡 Generating Italian Property Manual Search Guide...")
        
        # Generate URLs
        urls = self.generate_search_urls()
        
        # Create HTML guide
        html_content = self.create_html_guide(urls)
        html_filename = f"italian_property_guide_{datetime.now().strftime('%Y%m%d')}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create worksheet template
        worksheet_content = self.create_family_worksheet()
        worksheet_filename = f"property_research_worksheet_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(worksheet_filename, 'w', encoding='utf-8') as f:
            f.write(worksheet_content)
        
        print(f"✅ Guide created: {html_filename}")
        print(f"📋 Worksheet created: {worksheet_filename}")
        
        if open_browser:
            try:
                webbrowser.open(f'file://{html_filename}')
                print("🌐 Opening guide in browser...")
            except:
                print("❌ Could not open browser automatically")
        
        return html_filename, worksheet_filename

if __name__ == "__main__":
    guide = ManualSearchGuide()
    html_file, worksheet_file = guide.run()
    
    print("\n🎉 Manual search guide ready!")
    print(f"📧 Share the HTML file with your family: {html_file}")
    print(f"📝 Use the worksheet template: {worksheet_file}")