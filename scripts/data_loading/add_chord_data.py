import sqlite3

conn = sqlite3.connect('music_database.db')
cursor = conn.cursor()

# Create table for chord data
cursor.execute('''
CREATE TABLE IF NOT EXISTS song_chords (
    id INTEGER PRIMARY KEY,
    song TEXT,
    performer TEXT,
    key_signature TEXT,
    chord_progression TEXT,
    nashville_notation TEXT
)
''')

# Add some sample data
sample_songs = [
    ("Let It Be", "The Beatles", "C", "C-Am-F-G", "I-vi-IV-V"),
    ("Hey Jude", "The Beatles", "F", "F-C-G-Am", "I-V-II-vi"),
    ("Hound Dog", "Elvis Presley", "C", "C-F-G", "I-IV-V"),
    ("Can't Help Myself", "Four Tops", "C", "C-Am-F-G", "I-vi-IV-V")
]

cursor.executemany('''
INSERT OR REPLACE INTO song_chords (song, performer, key_signature, chord_progression, nashville_notation)
VALUES (?, ?, ?, ?, ?)
''', sample_songs)

conn.commit()
conn.close()

print("Chord database created with sample data!")