import sqlite3
from pathlib import Path

# Quick database check
db = sqlite3.connect('data/databases/music_database_backup.db')
cursor = db.cursor()

# Show tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"📋 Tables: {', '.join(tables)}")

# Check mcgill_chord_data
if 'mcgill_chord_data' in tables:
    cursor.execute('PRAGMA table_info(mcgill_chord_data)')
    columns = [col[1] for col in cursor.fetchall()]
    print(f"🎼 Columns: {', '.join(columns)}")
    
    cursor.execute('SELECT COUNT(*) FROM mcgill_chord_data')
    count = cursor.fetchone()[0]
    print(f"📊 Records: {count:,}")
    
    cursor.execute('SELECT * FROM mcgill_chord_data LIMIT 2')
    for i, record in enumerate(cursor.fetchall(), 1):
        print(f"Sample {i}: {record}")

db.close()