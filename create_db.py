import sqlite3

# Connect to a database (or create it if it doesn't exist)
conn = sqlite3.connect('household_services.db')

# Create a cursor object
cursor = conn.cursor()

# Optional: Create a table (example for your Professional model)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Professional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    service TEXT NOT NULL,
    rating REAL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
