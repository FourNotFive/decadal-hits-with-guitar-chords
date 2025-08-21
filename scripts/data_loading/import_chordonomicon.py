from datasets import load_dataset
import sqlite3
import pandas as pd
import re

print("Loading CHORDONOMICON dataset...")
dataset = load_dataset("ailsntua/Chordonomicon")
df = pd.DataFrame(dataset['train'])

print(f"Processing {len(df)} songs...")

# Function to extract song and artist from chord progression
def extract_basic_chord_progression(chord_string):
    # Remove structural markers like <intro_1>, <verse_1>, etc.
    clean_chords = re.sub(r'<[^>]+>', '', chord_string)
    # Remove extra spaces and return first few chords
    chords = clean_chords.strip().split()[:8]  # Take first 8 chords
    return ' '.join(chords) if chords else None

# Process a sample of the data first (first 1000 songs to test)
sample_df = df.head(1000).copy()

# Extract basic chord progressions
sample_df['basic_chords'] = sample_df['chords'].apply(extract_basic_chord_progression)

# Connect to your database
conn = sqlite3.connect('music_database.db')

# Create a new table for the bulk chord data
conn.execute('''
CREATE TABLE IF NOT EXISTS chordonomicon_data (
    id INTEGER PRIMARY KEY,
    chords TEXT,
    basic_chords TEXT,
    release_date TEXT,
    genres TEXT,
    decade TEXT,
    main_genre TEXT
)
''')

# Insert the sample data
sample_df[['id', 'chords', 'basic_chords', 'release_date', 'genres', 'decade', 'main_genre']].to_sql(
    'chordonomicon_data', conn, if_exists='replace', index=False
)

conn.commit()
conn.close()

print(f"Successfully imported {len(sample_df)} songs from CHORDONOMICON!")
print("Sample chord progressions:")
for i, row in sample_df.head(5).iterrows():
    print(f"- {row['basic_chords']} ({row['main_genre']}, {row['decade']})")