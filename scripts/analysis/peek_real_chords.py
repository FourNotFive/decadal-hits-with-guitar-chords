import sqlite3

def peek_real_chords():
    """Look at what's actually in the database files"""
    conn = sqlite3.connect('music_database.db')
    cursor = conn.cursor()
    
    print("=== LOOKING AT ACTUAL FILE CONTENT ===\n")
    
    # Get one song's actual file content
    cursor.execute("""
        SELECT artist, song_title, filepath, 
               SUBSTR(chord_progression, 1, 500) as stored_chords
        FROM mcgill_chord_data 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if result:
        artist, title, filepath, stored_chords = result
        print(f"Song: {artist} - {title}")
        print(f"File: {filepath}")
        print(f"What's stored as 'chord_progression': {stored_chords}")
        print()
        
        # Now let's try to read the actual file to see what it contains
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # First 1000 characters
            
            print("What's actually in the file:")
            lines = content.split('\n')
            for i, line in enumerate(lines[:15]):  # First 15 lines
                if line.strip():
                    print(f"{i+1:2d}: {line}")
                    
        except Exception as e:
            print(f"Can't read file: {e}")
    
    conn.close()

if __name__ == "__main__":
    peek_real_chords()