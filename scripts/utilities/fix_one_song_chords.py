import sqlite3

def fix_chord_progression_for_one_song():
    """Extract and update chord progression for one song"""
    
    conn = sqlite3.connect('music_database.db')
    cursor = conn.cursor()
    
    # Get one song
    cursor.execute("""
        SELECT id, artist, song_title, filepath
        FROM mcgill_chord_data 
        WHERE filepath LIKE '%.hum'
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        print("No .hum file found")
        return
    
    song_id, artist, title, filepath = result
    print(f"Fixing chord progression for: {artist} - {title}")
    
    try:
        # Read the file and extract chords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        all_chords = []
        
        # Extract chords from column 8
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 8:
                    chord = parts[7].strip()
                    if chord and not chord.startswith('*') and not chord.startswith('=') and chord != '**harte':
                        all_chords.append(chord)
        
        # Create a clean chord progression (remove dots and N.C.)
        clean_chords = []
        current_chord = None
        
        for chord in all_chords:
            if chord == '.':
                # Continue previous chord
                continue
            elif chord == 'N.C.':
                # Skip "No Chord"
                continue
            else:
                if chord != current_chord:  # Only add if different from previous
                    clean_chords.append(chord)
                    current_chord = chord
        
        # Create the progression string
        progression = ' - '.join(clean_chords[:20])  # First 20 unique chords
        
        print(f"Original chords found: {len(all_chords)}")
        print(f"Clean progression: {progression}")
        
        # Update the database
        cursor.execute("""
            UPDATE mcgill_chord_data 
            SET chord_progression = ?
            WHERE id = ?
        """, (progression, song_id))
        
        conn.commit()
        print(f"\n✅ Updated database for {artist} - {title}")
        
        # Verify the update
        cursor.execute("SELECT chord_progression FROM mcgill_chord_data WHERE id = ?", (song_id,))
        updated = cursor.fetchone()[0]
        print(f"Database now shows: {updated}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    fix_chord_progression_for_one_song()