#!/usr/bin/env python3
"""
Check website functionality and chord diagram integration
"""

import requests
import sqlite3
from urllib.parse import quote

def test_website_endpoints():
    """Test key website endpoints"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("Testing website endpoints...")
    print("=" * 40)
    
    # Test main page
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("[OK] Main page accessible")
            if "chord" in response.text.lower():
                print("[OK] Chord functionality present on main page")
        else:
            print(f"[ERROR] Main page returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to website - make sure it's running on port 5000")
        return False
    except Exception as e:
        print(f"[ERROR] Error accessing main page: {e}")
        return False
    
    # Test a specific song page
    try:
        # Get a song with chord progressions
        db_path = "../data/databases/billboard_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, artist, chord_progression 
            FROM bimmuda_songs 
            WHERE chord_progression IS NOT NULL 
            AND chord_progression != ''
            LIMIT 1
        """)
        
        song = cursor.fetchone()
        conn.close()
        
        if song:
            song_id, title, artist, chord_progression = song
            song_url = f"{base_url}/song/{song_id}"
            
            response = requests.get(song_url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] Song page accessible: {title} by {artist}")
                
                # Check for chord diagram elements
                if "chord-container" in response.text:
                    print("[OK] Chord diagram container found")
                if "jTab" in response.text:
                    print("[OK] jTab library included")
                if chord_progression.replace(' - ', '') in response.text.replace(' ', ''):
                    print("[OK] Chord progression data present")
                
                print(f"  Chords: {chord_progression}")
            else:
                print(f"[ERROR] Song page returned status {response.status_code}")
        
    except Exception as e:
        print(f"[ERROR] Error testing song page: {e}")
    
    return True

if __name__ == "__main__":
    test_website_endpoints()