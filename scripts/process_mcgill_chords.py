#!/usr/bin/env python3
"""
McGill Chord Processor
======================
Processes McGill chord annotation files and loads them into the database
for your decade-based guitar chord website.
"""

import sqlite3
import os
import glob
from pathlib import Path

def parse_chord_file(filepath):
    """
    Parse a McGill .lab chord file and extract chord progressions.
    
    Returns list of tuples: (start_time, end_time, chord)
    """
    chords = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 3:
                    start_time = float(parts[0])
                    end_time = float(parts[1])
                    chord = parts[2].strip()
                    
                    # Skip 'N' (no chord) entries for now
                    if chord != 'N':
                        chords.append((start_time, end_time, chord))
    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return chords

def get_simplified_chord_progression(chords):
    """
    Convert detailed chord progression to simplified chord sequence.
    For your guitar website, we want the main chord progression.
    """
    if not chords:
        return ""
    
    # Get unique chords in order
    chord_sequence = []
    last_chord = None
    
    for start_time, end_time, chord in chords:
        if chord != last_chord:
            chord_sequence.append(chord)
            last_chord = chord
    
    return " | ".join(chord_sequence)

def process_mcgill_songs():
    """
    Process all McGill chord files and prepare data for database insertion.
    """
    # Path to McGill annotations
    annotations_path = "../data/mcgill/annotations/annotations"
    
    if not os.path.exists(annotations_path):
        print(f"❌ McGill annotations not found at: {annotations_path}")
        return []
    
    processed_songs = []
    song_folders = glob.glob(os.path.join(annotations_path, "*"))
    
    print(f"🎵 Processing {len(song_folders)} McGill songs...")
    
    for i, folder in enumerate(song_folders[:], 1):  # Process all songs
        if not os.path.isdir(folder):
            continue
            
        song_id = os.path.basename(folder)
        
        # Look for majmin.lab file (simplest chord representation)
        chord_file = os.path.join(folder, "majmin.lab")
        
        if os.path.exists(chord_file):
            print(f"  {i:3d}. Processing song {song_id}...")
            
            # Parse chord progression
            chords = parse_chord_file(chord_file)
            
            if chords:
                chord_progression = get_simplified_chord_progression(chords)
                
                processed_songs.append({
                    'mcgill_id': song_id,
                    'chord_file': chord_file,
                    'chord_count': len(chords),
                    'chord_progression': chord_progression,
                    'duration': chords[-1][1] if chords else 0  # Last end time
                })
                
                print(f"       → {len(chords)} chords, {chord_progression[:50]}...")
            else:
                print(f"       → No chords found")
        else:
            print(f"  {i:3d}. Song {song_id} - no majmin.lab file")
    
    return processed_songs

def create_chord_table():
    """
    Create a table to store McGill chord data.
    """
    conn = sqlite3.connect('../data/databases/music_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mcgill_chord_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mcgill_id TEXT UNIQUE,
            chord_progression TEXT,
            chord_count INTEGER,
            duration REAL,
            processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ McGill chord data table created/verified")

def insert_chord_data(processed_songs):
    """
    Insert processed chord data into database.
    """
    if not processed_songs:
        print("❌ No songs to insert")
        return
    
    conn = sqlite3.connect('../data/databases/music_database.db')
    cursor = conn.cursor()
    
    inserted_count = 0
    
    for song in processed_songs:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO mcgill_chord_data 
                (mcgill_id, chord_progression, chord_count, duration)
                VALUES (?, ?, ?, ?)
            ''', (
                song['mcgill_id'],
                song['chord_progression'], 
                song['chord_count'],
                song['duration']
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting song {song['mcgill_id']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {inserted_count} songs into mcgill_chord_data table")

def main():
    print("🎸 McGILL CHORD PROCESSOR")
    print("=" * 40)
    print("Processing chord data for your decade guitar website...")
    print()
    
    # Step 1: Create table
    create_chord_table()
    
    # Step 2: Process McGill songs
    processed_songs = process_mcgill_songs()
    
    if processed_songs:
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"   Songs processed: {len(processed_songs)}")
        print(f"   Average chords per song: {sum(s['chord_count'] for s in processed_songs) / len(processed_songs):.1f}")
        print()
        
        # Step 3: Insert into database
        insert_chord_data(processed_songs)
        
        print("\n🎯 NEXT STEPS:")
        print("1. Run this script to see the first 10 songs processed")
        print("2. If it looks good, we'll process all 750+ songs")
        print("3. Then we'll start building your website interface!")
    else:
        print("❌ No songs were processed. Check your file paths.")

if __name__ == "__main__":
    main()