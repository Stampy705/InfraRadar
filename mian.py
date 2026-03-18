from radar_eyes import run_scraper
from radar_brain import analyze_pending_contracts as process_data
from infraradar_dashboard import InfraRadarApp
from database import InfraRadarDB 

def main():
    print("-" * 50)
    print("🚀 INFRA-RADAR: STARTING DAILY INTELLIGENCE CYCLE")
    print("-" * 50)

  
    db = InfraRadarDB()
    db.cleanup_expired_leads()


    run_scraper()

    process_data()


    print("\n[3/3] 🖥️ LAUNCHING DASHBOARD...")
    app = InfraRadarApp()
    app.mainloop()

if __name__ == "__main__":
    main()
