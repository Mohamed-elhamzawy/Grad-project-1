import sqlite3

# Connect to the database
conn = sqlite3.connect("greenhouse.db")
cursor = conn.cursor()

# Function to print column details for a given table
def show_table_structure(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"\n Structure of '{table_name}' table:")
    for col in columns:
        print(f"Column: {col[1]} | Type: {col[2]}")

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print structure for each table
for table in tables:
    show_table_structure(table[0])

conn.close()
