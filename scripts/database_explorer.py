import sqlite3
import pandas as pd

def explore_database(db_path='../data/databases/music_database.db'):
    """
    Explore the database structure to understand what data we have.
    """
    print("🔍 DATABASE EXPLORATION")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get all table names
        print("\n1. Available Tables:")
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = pd.read_sql_query(tables_query, conn)
        
        for table in tables['name']:
            print(f"   📋 {table}")
        
        print("\n" + "="*50)
        
        # Examine each table structure
        for table_name in tables['name']:
            print(f"\n2. Table: {table_name}")
            print("-" * (len(table_name) + 10))
            
            # Get column info
            pragma_query = f"PRAGMA table_info({table_name})"
            columns = pd.read_sql_query(pragma_query, conn)
            
            print("   Columns:")
            for _, col in columns.iterrows():
                print(f"   - {col['name']} ({col['type']})")
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count = pd.read_sql_query(count_query, conn)
            print(f"   📊 Row count: {count['count'].iloc[0]:,}")
            
            # Show sample data
            sample_query = f"SELECT * FROM {table_name} LIMIT 3"
            try:
                sample = pd.read_sql_query(sample_query, conn)
                print("   Sample data:")
                print(sample.to_string(index=False, max_colwidth=30))
            except Exception as e:
                print(f"   ⚠️  Could not read sample data: {e}")
            
            print("\n" + "-" * 50)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're running this from the 'scripts' folder")
        print("2. Check if the database file exists at: ../data/databases/music_database.db")
        print("3. Try running: ls ../data/databases/")

if __name__ == "__main__":
    explore_database()
