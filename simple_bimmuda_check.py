#!/usr/bin/env python3
"""
Simple BiMMuDa Status Check
============================

Quick check of your BiMMuDa integration progress.
"""

import sqlite3
from pathlib import Path

def main():
    print("🎵 BIMMUDA STATUS CHECK")
    print("=" * 30)
    
    # Check databases
    db_folder = Path("data/databases")
    
    print("📊 Available databases:")
    for db_file in db_folder.glob("*.db"):
        size_mb = db_file.stat().st_size / (1024 * 1024)
        print(f"   • {db_file.name} ({size_mb:.1f} MB)")
        
        # Quick table check
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            
            # Check for BiMMuDa related tables
            bimmuda_tables = [t for t in tables if 'bimmuda' in t.lower()]
            if bimmuda_tables:
                for table in bimmuda_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"      📋 {table}: {count:,} records")
            
            conn.close()
            
        except Exception as e:
            print(f"      ❌ Error reading: {e}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. If you see BiMMuDa data above, we can continue linking")
    print("2. If not, we need to integrate the data first")
    print("3. Goal: Link BiMMuDa melodies to Billboard chart positions")

if __name__ == "__main__":
    main()
