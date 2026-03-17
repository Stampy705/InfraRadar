from radar_eyes import run_scraper
from radar_brain import analyze_pending_contracts as process_data
from infraradar_dashboard import InfraRadarApp
from database import InfraRadarDB # <--- Make sure this is imported

def main():
    print("-" * 50)
    print("🚀 INFRA-RADAR: STARTING DAILY INTELLIGENCE CYCLE")
    print("-" * 50)

    # NEW: Run the cleanup BEFORE anything else
    db = InfraRadarDB()
    db.cleanup_expired_leads()

    # Step 1: Scrape
    run_scraper()

    # Step 2: AI Analysis
    process_data()

    # Step 3: Launch UI
    print("\n[3/3] 🖥️ LAUNCHING DASHBOARD...")
    app = InfraRadarApp()
    app.mainloop()

if __name__ == "__main__":
    main()