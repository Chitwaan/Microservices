import sqlite3
import os

def initialize_database(app_config):
    db_path = app_config['datastore']['filename']
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the Unified Stats table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS unified_stats (
        id INTEGER PRIMARY KEY ASC,
        num_health_metrics INTEGER NOT NULL,
        max_heart_rate INTEGER,
        total_calories_burned INTEGER,
        num_workout_events INTEGER NOT NULL,
        total_duration INTEGER,  -- For workout events
        last_updated DATETIME NOT NULL
    )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()
