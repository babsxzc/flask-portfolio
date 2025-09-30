import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect('database.db')

# Create a cursor
cursor = conn.cursor()

# Create the messages table
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Save and close
conn.commit()
conn.close()

print("✅ Database and table created.")
