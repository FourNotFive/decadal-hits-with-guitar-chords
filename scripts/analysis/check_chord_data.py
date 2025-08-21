import sqlite3
import pandas as pd

def check_chord_data():
    """Check what chord progression data we currently have"""
    conn = sqlite3.connect('music_database.db')
    
    print("=== YOUR CURRENT CHORD DATA ===\n")
    
    # Check mcgill_chord_data - this seems to be your main data
    query = """
    SELECT artist, song_title, year, 
           SUBSTR(chord_progression, 1, 100) as chord_preview
    FROM mcgill_chord_data 
    WHERE chord_progression IS NOT NULL 
    AND chord_progression != ''
    AND LENGTH(chord_progression) > 10
    LIMIT 5
    """
    
    df = pd.read_sql_query(query, conn)
    print("Sample songs from your McGill database:")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['artist']} - {row['song_title']} ({row['year']})")
        print(f"   Chords: {row['chord_preview']}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_chord_data()