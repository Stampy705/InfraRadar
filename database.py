import sqlite3
import datetime

class InfraRadarDB:
    def __init__(self, db_name='infraradar_contracts.db'):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT,
                title TEXT UNIQUE,
                budget TEXT,
                deadline TEXT,
                authority TEXT,
                location TEXT,
                emd TEXT,
                ai_brief TEXT,
                url TEXT
            )
        ''')
        self.conn.commit()

    def add_contract(self, data):
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO contracts 
                (status, title, budget, deadline, authority, location, emd, ai_brief, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['status'], data['title'], data['budget'], data['deadline'], 
                  data['authority'], data['location'], data['emd'], data['ai_brief'], data['url']))
            self.conn.commit()
        except Exception as e:
            print(f"❌ Database Error: {e}")

    def get_all_contracts(self):
        self.cursor.execute("SELECT * FROM contracts ORDER BY id DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_contract(self, contract_id):
        self.cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
        self.conn.commit()

    def cleanup_expired_leads(self):
        """Checks dates and marks past deadlines as 'Taken'."""
        print("🧹 Running Database Cleanup...")
        today = datetime.date.today()
    
        self.cursor.execute(
            "SELECT id, deadline FROM contracts WHERE status IN ('Upcoming', 'Available')"
        )
        rows = self.cursor.fetchall()
        
        updated_count = 0
        for row in rows:
            deadline_str = row['deadline']
            
            if deadline_str in ('TBD', 'Pending', 'TBA') or not deadline_str:
                continue
            
            try:
    
                deadline_date = datetime.datetime.strptime(deadline_str, '%d-%m-%Y').date()
            
                if deadline_date < today:
                    self.cursor.execute(
                        "UPDATE contracts SET status = ? WHERE id = ?",
                        ('Taken', row['id'])
                    )
                    updated_count += 1
            except ValueError:
                continue
        
        self.conn.commit()
        if updated_count > 0:
            print(f"✅ Cleanup complete: {updated_count} expired lead(s) marked as 'Taken'.")
        else:
            print("✅ Cleanup complete: No expired leads found.")

    def close(self):
        self.conn.close()
