import sqlite3

conn = sqlite3.connect('music_database.db')
cursor = conn.cursor()

print("Adding indexes to improve search performance...")

# Index for performer searches
cursor.execute("CREATE INDEX IF NOT EXISTS idx_performer ON billboard_hot100(performer)")

# Index for song searches  
cursor.execute("CREATE INDEX IF NOT EXISTS idx_song ON billboard_hot100(song)")

# Index for date searches
cursor.execute("CREATE INDEX IF NOT EXISTS idx_chart_date ON billboard_hot100(chart_date)")

# Composite index for finding peak dates efficiently
cursor.execute("CREATE INDEX IF NOT EXISTS idx_song_performer_position ON billboard_hot100(song, performer, chart_position)")

conn.commit()
conn.close()

print("Indexes added successfully!")