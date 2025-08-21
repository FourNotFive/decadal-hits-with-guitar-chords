import sqlite3

conn = sqlite3.connect('../data/databases/music_database.db')
cursor = conn.cursor()

# Check chord data count
cursor.execute('SELECT COUNT(*) FROM mcgill_chord_data')
print('McGill songs with chords:', cursor.fetchone()[0])

# Show sample progressions
cursor.execute('SELECT mcgill_id, chord_progression FROM mcgill_chord_data LIMIT 3')
print('\nSample chord progressions:')
for row in cursor.fetchall():
    print(f'Song {row[0]}: {row[1][:60]}...')

conn.close()