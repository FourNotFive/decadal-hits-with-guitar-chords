#!/usr/bin/env python3
"""
Debug script to check chord_progression data retrieval
"""

import sqlite3

def debug_chord_query():
    """Debug the chord query to see what's happening"""
    
    db_path = "../data/databases/billboard_data.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Test the same query used in the website
    song_query = """
        SELECT id, title, artist, chord_progression FROM bimmuda_songs WHERE id = 1
    """
    
    song = conn.execute(song_query).fetchone()
    
    if song:
        print("Raw database result:")
        print(f"  ID: {song['id']}")
        print(f"  Title: {song['title']}")
        print(f"  Artist: {song['artist']}")
        print(f"  Chord Progression: '{song['chord_progression']}'")
        print(f"  Type: {type(song['chord_progression'])}")
        print(f"  Length: {len(str(song['chord_progression'])) if song['chord_progression'] else 0}")
        
        # Convert to dict like the website does
        song_dict = dict(song)
        print(f"\nAs dictionary:")
        print(f"  chord_progression: '{song_dict['chord_progression']}'")
        print(f"  bool(chord_progression): {bool(song_dict['chord_progression'])}")
        
        # Test the template condition
        if song_dict['chord_progression']:
            print("  ✓ Template condition would be TRUE")
        else:
            print("  ✗ Template condition would be FALSE")
    else:
        print("No song found with ID 1")
    
    # Check a few more songs
    print("\nChecking first 5 songs with chord progressions:")
    songs_query = """
        SELECT id, title, artist, chord_progression 
        FROM bimmuda_songs 
        WHERE chord_progression IS NOT NULL 
        AND chord_progression != ''
        LIMIT 5
    """
    
    songs = conn.execute(songs_query).fetchall()
    for song in songs:
        print(f"  ID {song['id']}: {song['title']} - '{song['chord_progression']}'")
    
    conn.close()

if __name__ == "__main__":
    debug_chord_query()