import sqlite3
import json
import time
from groq import Groq 


# Grab your new API key from console.groq.com
GROQ_API_KEY=your_actual_key_here
client = Groq(api_key=API_KEY) 

def analyze_pending_contracts():
    print("🧠 InfraRadar Brain: Booting up Groq AI analysis module...")
    
    conn = sqlite3.connect('infraradar_contracts.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, url FROM contracts WHERE budget = 'Pending AI'")
    pending_targets = cursor.fetchall()
    
    if not pending_targets:
        print("✅ No pending targets found. All intelligence is up to date.")
        return

    print(f"🎯 Found {len(pending_targets)} targets requiring AI analysis.\n")

    for row in pending_targets:
        contract_id = row['id']
        title = row['title']
        print(f"Analyzing: {title[:60]}...")
        
        prompt = f"""
        You are an expert Indian Infrastructure Contractor analyst.
        Analyze this news headline for a construction project: "{title}"
        
        Extract the information and return ONLY a valid JSON object.
        
        Required Keys:
        "budget" : The financial value (e.g., "₹ 11,000 Crore" or "₹ 50 Lakh"). If none is mentioned, output "Undisclosed".
        "location": The specific city or state mentioned (e.g., "Maharashtra").
        "ai_brief": A professional 2-sentence summary of what this project means for a heavy civil contractor.
        """
        
        try:
            # <-- UPDATE THE MODEL NAME HERE -->
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}, 
                temperature=0.2 
            )
            
            # Extract the text from Groq's response structure
            clean_text = response.choices[0].message.content
            result = json.loads(clean_text)
            
            budget = result.get('budget', 'Unknown')
            location = result.get('location', 'Maharashtra')
            ai_brief = result.get('ai_brief', 'Analysis failed.')
            
            cursor.execute("""
                UPDATE contracts 
                SET budget = ?, location = ?, ai_brief = ? 
                WHERE id = ?
            """, (budget, location, ai_brief, contract_id))
            
            conn.commit()
            print(f"  -> ✔️ Extracted Budget: {budget}")
            
            # Groq is fast, but keep the throttle to avoid rate limits on their free tier
            time.sleep(4)
            
        except Exception as e:
            # Added the actual error 'e' to the print statement so you can debug if it fails
            print(f"  -> ⚠️ Error or API Limit Hit: {e}")
            print(f"  -> Target remains 'Pending AI' in queue. Cooling down for 30s...")
            time.sleep(30)

    conn.close()
    print("\n✅ AI processing complete. Database updated.")

if __name__ == "__main__":
    analyze_pending_contracts()
