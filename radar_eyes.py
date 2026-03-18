import urllib.request
import xml.etree.ElementTree as ET
from database import InfraRadarDB

def run_scraper():
    print("📡 InfraRadar Eyes: Sweeping for Civic & Municipal Projects...")
    url = 'https://news.google.com/rss/search?q=Maharashtra+(municipal+OR+civic+OR+infrastructure+OR+tender+OR+project)+(lakh+OR+crore)&hl=en-IN&gl=IN&ceid=IN:en'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        response = urllib.request.urlopen(req)
        rss_data = response.read()
        
        root = ET.fromstring(rss_data)
        db = InfraRadarDB()
        
        count = 0
        for item in root.findall('./channel/item')[:15]:
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            contract_data = {
                "status": "Upcoming", "title": title, "budget": "Pending AI",
                "deadline": "TBD", "authority": "Civic Intel", "location": "Maharashtra",
                "emd": "TBD", "ai_brief": f"Source Date: {pub_date}\n\nRAW INTEL: Awaiting AI Brain extraction.",
                "url": link
            }
            db.add_contract(contract_data)
            count += 1
            print(f"✔️ Target Acquired: {title[:60]}...")
            
        print(f"\n✅ Sweep Complete. {count} new leads injected.")
    except Exception as e:
        print(f"❌ Radar malfunction: {e}")

if __name__ == "__main__":
    run_scraper()
