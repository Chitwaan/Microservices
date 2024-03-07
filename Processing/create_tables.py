import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('stats.sqlite')
cursor = conn.cursor()

# Create a Unified Stats table
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
