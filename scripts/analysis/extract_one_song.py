import sqlite3

def extract_chords_from_one_song():
    """Extract actual chords from one .hum file to see if it works"""
    
    conn = sqlite3.connect('music_database.db')
    cursor = conn.cursor()
    
    # Get one song's file path
    cursor.execute("""
        SELECT artist, song_title, filepath
        FROM mcgill_chord_data 
        WHERE filepath LIKE '%.hum'
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        print("No .hum file found")
        return
    
    artist, title, filepath = result
    print(f"Extracting chords from: {artist} - {title}")
    print(f"File: {filepath}")
    print()
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        chords_found = []
        
        # Extract chords from column 8 (**harte column)
        print("Extracting all chords from the song...")
        
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                
                # Check if we have enough columns and get column 8 (index 7)
                if len(parts) >= 8:
                    chord = parts[7].strip()  # Column 8 = index 7
                    
                    # Skip header lines and empty chords
                    if chord and not chord.startswith('*') and not chord.startswith('=') and chord != '**harte':
                        chords_found.append(chord)
        
        print("Raw chords found:")
        for i, chord in enumerate(chords_found[:20]):  # First 20 chords
            print(f"{i+1:2d}: {chord}")
        
        if len(chords_found) > 20:
            print(f"... and {len(chords_found)-20} more chords")
        
        print(f"\nTotal chords found: {len(chords_found)}")
        
        # Create a simple chord progression
        unique_chords = []
        for chord in chords_found:
            if chord != 'N.C.' and chord not in unique_chords:
                unique_chords.append(chord)
        
        print(f"\nUnique chords: {' - '.join(unique_chords[:10])}")
        
    except Exception as e:
        print(f"Error reading file: {e}")
    
    conn.close()

if __name__ == "__main__":
    extract_chords_from_one_song()