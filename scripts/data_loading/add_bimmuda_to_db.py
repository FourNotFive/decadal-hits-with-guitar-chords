#!/usr/bin/env python3
"""
Baby Step 3: Add BiMMuDa data to your SQLite database
Simple and gentle - just adding the song info so you can explore in DB Browser!
"""

import os
import csv
import sqlite3

def find_bimmuda_folder():
    """Find the BiMMuDa folder"""
    if os.path.exists("BiMMuDa"):
        return "BiMMuDa"
    elif os.path.exists("BiMMuDa-main"):
        return "BiMMuDa-main"
    else:
        return None

def find_database():
    """Find your existing database file"""
    possible_names = [
        "billboard_data.db",
        "mcgill_billboard.db", 
        "music_data.db",
        "chord_data.db"
    ]
    
    for db_name in possible_names:
        if os.path.exists(db_name):
            print(f"✅ Found database: {db_name}")
            return db_name
    
    # If no existing database, create a new one
    print("📁 No existing database found, creating: billboard_data.db")
    return "billboard_data.db"

def create_bimmuda_table(db_path):
    """Create a simple table for BiMMuDa songs"""
    print("🗃️ Creating BiMMuDa table...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a simple table for BiMMuDa songs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bimmuda_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            year INTEGER,
            position INTEGER,
            genre_broad_1 TEXT,
            genre_broad_2 TEXT,
            genre_specific_1 TEXT,
            time_signature_1 TEXT,
            tonic_1 TEXT,
            mode_1 TEXT,
            bpm_1 TEXT,
            audio_link TEXT,
            has_midi_files BOOLEAN DEFAULT TRUE,
            has_lyrics BOOLEAN DEFAULT FALSE,
            folder_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ BiMMuDa table created!")

def load_bimmuda_metadata(db_path):
    """Load BiMMuDa metadata into the database"""
    print("📊 Loading BiMMuDa songs into database...")
    
    bimmuda_folder = find_bimmuda_folder()
    if not bimmuda_folder:
        print("❌ BiMMuDa folder not found")
        return
    
    metadata_file = os.path.join(bimmuda_folder, "metadata", "bimmuda_per_song_metadata.csv")
    if not os.path.exists(metadata_file):
        print("❌ Metadata file not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read the CSV file
    songs_added = 0
    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Extract the main info
            title = row.get('Title', '')
            artist = row.get('Artist', '')
            year = int(row.get('Year', 0)) if row.get('Year') else None
            
            # Handle position - some might be like "2a" or non-numeric
            position_raw = row.get('Position', '')
            position = None
            if position_raw:
                try:
                    position = int(position_raw)
                except ValueError:
                    # For things like "2a", just take the first number
                    import re
                    numbers = re.findall(r'\d+', position_raw)
                    if numbers:
                        position = int(numbers[0])
                    else:
                        position = None
            
            # Extract genre info
            genre_broad_1 = row.get('Genre (Broad 1)', '')
            genre_broad_2 = row.get('Genre (Broad 2)', '')
            genre_specific_1 = row.get('Genre (Specific 1)', '')
            
            # Extract music theory info
            time_signature_1 = row.get('Time Signature 1', '')
            tonic_1 = row.get('Tonic 1', '')
            mode_1 = row.get('Mode 1', '')
            bpm_1 = row.get('BPM 1', '')
            
            # Other info
            audio_link = row.get('Link to Audio', '')
            
            # Figure out folder path based on year and position
            folder_path = f"{bimmuda_folder}/bimmuda_dataset/{year}/{position}"
            
            # Check if this song has lyrics (not instrumental)
            has_lyrics = True
            instrumental_songs = [
                "Third Man Theme", "Blue Tango", "The Song from Moulin Rouge",
                "Cherry Pink and Apple Blossom White", "Autumn Leaves", 
                "Lisbon Antigua", "Patricia", "The Theme from 'A Summer Place'",
                "Stranger on the Shore", "The Stripper", "Love is Blue",
                "Love's Theme", "Harlem Shake"
            ]
            if title in instrumental_songs:
                has_lyrics = False
            
            # Insert into database
            cursor.execute('''
                INSERT INTO bimmuda_songs 
                (title, artist, year, position, genre_broad_1, genre_broad_2, 
                 genre_specific_1, time_signature_1, tonic_1, mode_1, bpm_1, 
                 audio_link, has_lyrics, folder_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, artist, year, position, genre_broad_1, genre_broad_2,
                  genre_specific_1, time_signature_1, tonic_1, mode_1, bpm_1,
                  audio_link, has_lyrics, folder_path))
            
            songs_added += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {songs_added} BiMMuDa songs to database!")
    return songs_added

def check_existing_mcgill_data(db_path):
    """Check if McGill data exists in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if McGill table exists
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%mcgill%'
    ''')
    tables = cursor.fetchall()
    
    if tables:
        table_name = tables[0][0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} McGill songs in table '{table_name}'")
    else:
        print("ℹ️  No McGill data found in database yet")
    
    conn.close()
    return len(tables) > 0

def show_database_summary(db_path):
    """Show what's now in your database"""
    print("\n" + "="*50)
    print("📊 YOUR DATABASE NOW CONTAINS")
    print("="*50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Show all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("📋 Tables in your database:")
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f"   📁 {table_name}: {count:,} rows")
    
    # Show some BiMMuDa samples
    print("\n🎵 Sample BiMMuDa songs:")
    cursor.execute('''
        SELECT title, artist, year, genre_broad_1 
        FROM bimmuda_songs 
        ORDER BY year, position 
        LIMIT 5
    ''')
    
    for title, artist, year, genre in cursor.fetchall():
        print(f"   • {title} - {artist} ({year}) [{genre}]")
    
    # Show decade breakdown
    print("\n📅 BiMMuDa songs by decade:")
    cursor.execute('''
        SELECT (year/10)*10 as decade, COUNT(*) as count
        FROM bimmuda_songs 
        GROUP BY decade 
        ORDER BY decade
    ''')
    
    for decade, count in cursor.fetchall():
        if decade:
            print(f"   📊 {int(decade)}s: {count} songs")
    
    conn.close()

def show_next_steps(db_path):
    """Show what the user can do next"""
    print("\n" + "="*50)
    print("🚀 WHAT TO DO NEXT")
    print("="*50)
    
    print(f"🗃️ Your database file: {db_path}")
    print("\n📱 Open it in DB Browser for SQLite to:")
    print("   • Browse the 'bimmuda_songs' table")
    print("   • Filter songs by year, genre, artist")
    print("   • Search for specific songs")
    print("   • Compare with your McGill data (if you have it)")
    print("\n💡 Try these SQL queries in DB Browser:")
    print("   • SELECT * FROM bimmuda_songs WHERE year = 1960")
    print("   • SELECT * FROM bimmuda_songs WHERE genre_broad_1 = 'Rock'") 
    print("   • SELECT artist, COUNT(*) FROM bimmuda_songs GROUP BY artist")
    print("\n🍼 Next baby steps:")
    print("   A) Explore the data in DB Browser")
    print("   B) Add your McGill chord data to the same database")
    print("   C) Find songs that exist in both datasets")
    print("   D) Play some MIDI files to hear the melodies")

def main():
    print("🍼 BABY STEP #3: Adding BiMMuDa to Your SQLite Database")
    print("This will put the BiMMuDa song data into SQLite so you can explore it!")
    print()
    
    # Step 1: Find everything we need
    bimmuda_folder = find_bimmuda_folder()
    if not bimmuda_folder:
        print("❌ BiMMuDa folder not found. Did Step 1 work?")
        return
    
    db_path = find_database()
    
    # Step 2: Create table and load data
    create_bimmuda_table(db_path)
    
    # Step 3: Check if we already have the data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bimmuda_songs")
    existing_count = cursor.fetchone()[0]
    conn.close()
    
    if existing_count > 0:
        print(f"ℹ️  Database already has {existing_count} BiMMuDa songs")
        print("Skipping data load to avoid duplicates")
    else:
        songs_added = load_bimmuda_metadata(db_path)
        if not songs_added:
            return
    
    # Step 4: Check for McGill data
    check_existing_mcgill_data(db_path)
    
    # Step 5: Show summary
    show_database_summary(db_path)
    
    # Step 6: Show next steps
    show_next_steps(db_path)
    
    print(f"\n🎉 SUCCESS! BiMMuDa data is now in your database!")
    print(f"Open '{db_path}' in DB Browser for SQLite to explore!")

if __name__ == "__main__":
    main()
