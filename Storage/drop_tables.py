import sqlite3

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('events.db')

def drop_table(conn):
    c = conn.cursor()
    c.execute('''
              DROP TABLE IF EXISTS point
              ''')
    conn.commit()

if __name__ == "__main__":
    conn = connect_db()
    try:
        drop_table(conn)
        print("Table 'point' dropped successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
