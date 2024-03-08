

import mysql.connector

# Configuration details from docker-compose.yml
config = {
    'user': 'user',
    'password': 'Password',  # Ensure you use the correct password as defined in your docker-compose file
    'host': 'microservices-3855.eastus.cloudapp.azure.com',  # Use the DNS Name of your VM
    'database': 'events',  # The database name from your docker-compose file
    'raise_on_warnings': True,
}

# Establishing a connection to the database
db_conn = mysql.connector.connect(**config)
db_cursor = db_conn.cursor()

# SQL for creating workout_events table
create_workout_events_table_sql = '''
    CREATE TABLE IF NOT EXISTS workout_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_device_id VARCHAR(250) NOT NULL,
        exercise_type VARCHAR(250) NOT NULL,
        duration INT NOT NULL,
        intensity VARCHAR(250) NOT NULL,
        date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        trace_id VARCHAR(250) NOT NULL
    );
'''

# SQL for creating health_metrics table
create_health_metrics_table_sql = '''
    CREATE TABLE IF NOT EXISTS health_metrics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_device_id VARCHAR(250) NOT NULL,
        heart_rate INT NOT NULL,
        calories_burned INT NOT NULL,
        date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        trace_id VARCHAR(250) NOT NULL
    );
'''

# Executing SQL statements
db_cursor.execute(create_workout_events_table_sql)
db_cursor.execute(create_health_metrics_table_sql)

# Commit the changes and close the connection
db_conn.commit()
db_conn.close()
