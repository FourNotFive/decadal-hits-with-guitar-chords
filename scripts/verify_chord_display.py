#!/usr/bin/env python3
"""
Verify that chord diagrams are properly integrated and displaying
"""

import requests
import sqlite3
import re
import json

def verify_chord_integration():
    """Verify chord integration on the website"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Get a song with chord progressions
    db_path = "../data/databases/billboard_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, artist, chord_progression 
        FROM bimmuda_songs 
        WHERE chord_progression IS NOT NULL 
        AND chord_progression != ''
        LIMIT 3
    """)
    
    songs = cursor.fetchall()
    conn.close()
    
    print("Verifying chord diagram integration...")
    print("=" * 50)
    
    for song_id, title, artist, chord_progression in songs:
        print(f"\nSong: {title} by {artist}")
        print(f"Chords: {chord_progression}")
        
        try:
            song_url = f"{base_url}/song/{song_id}"
            response = requests.get(song_url, timeout=5)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Check for chord-related elements using regex
                chord_buttons = re.findall(r'<button[^>]*onclick="showChord\(\'([^\']+)\'\)"[^>]*>', html_content)
                chord_container = 'id="chord-diagram-container"' in html_content
                jtab_script = 'jTab' in html_content
                chord_library = 'chordLibrary' in html_content
                
                print(f"  Status: Page loaded successfully")
                print(f"  Chord buttons found: {len(chord_buttons)}")
                print(f"  Chord container present: {chord_container}")
                print(f"  jTab library loaded: {jtab_script}")
                print(f"  Chord library present: {chord_library}")
                
                # Check if individual chords are present as buttons
                if chord_progression:
                    chord_list = [c.strip() for c in chord_progression.split(' - ')]
                    
                    print(f"  Expected chords: {chord_list}")
                    print(f"  Found chord buttons: {chord_buttons}")
                    
                    missing = [c for c in chord_list if c not in chord_buttons]
                    if missing:
                        print(f"  Missing chord buttons: {missing}")
                    else:
                        print(f"  All chords present as interactive buttons!")
                
            else:
                print(f"  Error: Status {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nChord diagram integration test completed!")

if __name__ == "__main__":
    verify_chord_integration()