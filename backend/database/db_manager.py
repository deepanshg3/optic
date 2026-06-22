import sqlite3
import json
import os
from datetime import datetime
from backend.core.logger import setup_logger

logger = setup_logger("Database") # 🎯 CREATE THE LOGGER

# Define the absolute path to store the database file in your data/ folder
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/optic.db'))

def get_connection():
    """Helper to establish a connection and ensure the directory exists."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # This row_factory allows us to access columns by their name like a dictionary
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Initializes the SQLite database and builds the incidents table."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 🚨 ARCHITECTURE UPGRADE: Added incident_type to the schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_name TEXT NOT NULL,
            incident_type TEXT NOT NULL, -- NEW: 'BUILD_LINTER' or 'RUNTIME_SENTRY'
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            crash_logs TEXT NOT NULL,
            ai_diagnosis TEXT NOT NULL,
            proposed_patch TEXT NOT NULL, -- Stored as a JSON string
            status TEXT DEFAULT 'PENDING' -- PENDING, APPROVED, REJECTED, RESOLVED
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("🗄️ Database initialized successfully.")

def create_incident(container_name, incident_type, crash_logs, ai_diagnosis, proposed_patch):
    """The Detective (AI) uses this to drop a new report for human review."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure the patch is safely converted to a JSON string for storage
    if isinstance(proposed_patch, (dict, list)):
        proposed_patch = json.dumps(proposed_patch)
        
    cursor.execute('''
        INSERT INTO incidents (container_name, incident_type, crash_logs, ai_diagnosis, proposed_patch, status)
        VALUES (?, ?, ?, ?, ?, 'PENDING')
    ''', (container_name, incident_type, crash_logs, ai_diagnosis, proposed_patch))
    
    incident_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"📝 Incident #{incident_id} [{incident_type}] logged. Status: PENDING.")
    return incident_id

def get_pending_incidents():
    """The Dashboard uses this to fetch reports that need your approval."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # We only want to see things that haven't been resolved yet
    cursor.execute('''
        SELECT * FROM incidents WHERE status = 'PENDING' ORDER BY timestamp DESC
    ''')
    
    # Convert the SQLite objects into standard Python dictionaries for Streamlit
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def update_incident_status(incident_id, status):
    """The Dashboard uses this when you click 'Approve' or 'Reject'."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE incidents SET status = ? WHERE id = ?
    ''', (status, incident_id))
    
    conn.commit()
    conn.close()
    logger.info(f"🔄 Incident #{incident_id} status updated to: {status}")