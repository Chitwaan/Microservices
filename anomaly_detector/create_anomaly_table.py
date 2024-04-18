import sqlite3

def create_database():

    conn = sqlite3.connect('anomaly_detector.db')
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS anomaly (
        id INTEGER PRIMARY KEY ASC, 
        event_id VARCHAR(250) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        event_type VARCHAR(100) NOT NULL,
        anomaly_type VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL,
        date_created VARCHAR(100) NOT NULL
    )
    """
    
    cursor.execute(create_table_sql)
    
    # Commit the changes to the database
    conn.commit()
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    create_database()
