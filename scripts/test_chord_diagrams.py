#!/usr/bin/env python3
"""
Test script to verify chord diagrams are working correctly
"""

import sqlite3
import json

def test_sample_songs():
    """Test chord progressions for a few sample songs"""
    
    # Connect to database
    db_path = "../data/databases/billboard_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a few songs with chord progressions
    cursor.execute("""
        SELECT title, artist, chord_progression 
        FROM bimmuda_songs 
        WHERE chord_progression IS NOT NULL 
        AND chord_progression != ''
        LIMIT 10
    """)
    
    songs = cursor.fetchall()
    
    print("Testing chord diagrams for sample songs:")
    print("=" * 50)
    
    # Load chord library to verify coverage
    try:
        with open('chord_library.json', 'r') as f:
            chord_library = json.load(f)
        print(f"Chord library loaded: {len(chord_library)} chords available")
        print()
    except:
        print("Warning: chord_library.json not found")
        chord_library = {}
    
    for title, artist, chord_progression in songs:
        print(f"Song: {title} by {artist}")
        print(f"Chords: {chord_progression}")
        
        # Parse chords and check if they're in the library
        if chord_progression:
            chords = [c.strip() for c in chord_progression.split(' - ') if c.strip()]
            missing_chords = []
            
            for chord in chords:
                if chord not in chord_library:
                    missing_chords.append(chord)
            
            if missing_chords:
                print(f"Missing chords: {missing_chords}")
            else:
                print("All chords available in library!")
        
        print()
    
    conn.close()
    return songs

if __name__ == "__main__":
    test_sample_songs()