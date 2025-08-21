import sqlite3
import pandas as pd

def inspect_database():
    """Inspect the database structure and show sample data"""
    conn = sqlite3.connect('music_database.db')
    cursor = conn.cursor()
    
    print("=== DATABASE TABLES ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n--- Table: {table_name} ---")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
        
        # Show sample data (first 3 rows)
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample = cursor.fetchall()
            print("Sample data:")
            for i, row in enumerate(sample, 1):
                print(f"  Row {i}: {row[:5]}...")  # Show first 5 columns
        
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    inspect_database()