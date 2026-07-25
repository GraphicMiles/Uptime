import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_file="uptime.db"):
        self.db_file = db_file
        self.init_schema()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_schema(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'idle',
            specs TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_heartbeat TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            docker_image TEXT NOT NULL,
            command TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(device_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            output TEXT,
            error TEXT,
            exit_code INTEGER,
            completed_at TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def register_device(self, device_id, name, price, status, specs):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO devices 
        (device_id, name, price, status, specs, last_heartbeat)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (device_id, name, price, status, json.dumps(specs), datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_devices(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices ORDER BY registered_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_device(self, device_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_job(self, job_id, device_id, docker_image, command):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO jobs (id, device_id, docker_image, command, status)
        VALUES (?, ?, ?, ?, 'pending')
        """, (job_id, device_id, docker_image, command))
        conn.commit()
        conn.close()
    
    def get_pending_job(self, device_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM jobs 
        WHERE device_id = ? AND status = 'pending'
        LIMIT 1
        """, (device_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_job(self, job_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT j.*, r.output, r.error, r.exit_code, r.completed_at as result_completed_at
        FROM jobs j
        LEFT JOIN results r ON j.id = r.job_id
        WHERE j.id = ?
        """, (job_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def mark_job_started(self, job_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE jobs SET status = 'running', started_at = ? 
        WHERE id = ?
        """, (datetime.now().isoformat(), job_id))
        conn.commit()
        conn.close()
    
    def save_result(self, job_id, output, error, exit_code, completed_at):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE jobs SET status = 'completed', completed_at = ? 
        WHERE id = ?
        """, (completed_at, job_id))
        
        cursor.execute("""
        INSERT INTO results (job_id, output, error, exit_code, completed_at)
        VALUES (?, ?, ?, ?, ?)
        """, (job_id, output, error, exit_code, completed_at))
        
        conn.commit()
        conn.close()