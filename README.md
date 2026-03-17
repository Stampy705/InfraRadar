# ◉ InfraRadar — Infrastructure Intelligence Pipeline
A professional-grade Python automation tool for real-time infrastructure lead tracking and market analysis in Maharashtra.

## 🚀 Overview
InfraRadar is a full-stack data pipeline designed to scrape, analyze, and visualize high-value infrastructure projects. It automates the transition from raw news headlines to actionable business intelligence using Large Language Models (LLMs).

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **AI Engine:** Llama 3.1 (via Groq Cloud API)
* **Database:** SQLite3
* **GUI:** CustomTkinter
* **Data Viz:** Matplotlib
* **Automation:** Datetime, Regex, Subprocess

## 🏗️ Core Architecture
1. **The Orchestrator (`main.py`)**: Manages the automated lifecycle from data ingestion to UI launch.
2. **The Scraper (`radar_eyes.py`)**: Utilizes RSS feeds to monitor 15+ news sources for infrastructure and municipal keywords.
3. **The Brain (`radar_brain.py`)**: Processes raw text via Groq's high-speed inference engine to extract budget, location, and executive briefs in structured JSON format.
4. **The Cleaner (`database.py`)**: Features a smart-cleanup method that uses real-time date logic to archive expired leads.
5. **The Dashboard (`infraradar_dashboard.py`)**: A dark-mode desktop interface featuring real-time market cap calculations and Matplotlib-driven regional analytics.

## 📊 Key Features
* **Duplicate Protection:** Uses unique URL hashing in SQLite to prevent redundant AI processing.
* **Intelligent Parsing:** Custom Regex patterns extract and standardize financial values from "Lakh Crore" and "Crore" units.
* **Regional Intelligence:** Automatic geocoding for 20+ major Maharashtra hubs (Pune, Mumbai, Nagpur, etc.).
* **Security:** API key management via environment variables for safe deployment.

## 📸 Dashboard Preview
*<img width="1090" height="662" alt="Screenshot 2026-03-17 212433" src="https://github.com/user-attachments/assets/8feec378-173a-4a22-a28a-6386d68d1da2" />*

## 🚦 Getting Started
1. Clone the repository: `git clone https://github.com/yourusername/InfraRadar.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API Key to a `.env` file.
4. Run the pipeline: `python main.py`
