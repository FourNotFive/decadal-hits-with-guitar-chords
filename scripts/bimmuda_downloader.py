import os
import requests
import zipfile
import pandas as pd
from pathlib import Path
import sqlite3

def download_bimmuda_data():
    """Download and extract BiMMuDa dataset from GitHub"""
    
    # Create bimmuda directory in your project
    bimmuda_dir = Path("../data/bimmuda")
    bimmuda_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎵 Downloading BiMMuDa dataset...")
    
    # GitHub repository URL for downloading as zip
    repo_url = "https://github.com/madelinehamilton/BiMMuDa/archive/refs/heads/main.zip"
    
    # Download the repository
    response = requests.get(repo_url)
    if response.status_code == 200:
        zip_path = bimmuda_dir / "bimmuda.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(bimmuda_dir)
        
        # Remove the zip file
        os.remove(zip_path)
        
        print("✅ BiMMuDa dataset downloaded successfully!")
        return True
    else:
        print(f"❌ Failed to download BiMMuDa dataset. Status code: {response.status_code}")
        return False

def explore_bimmuda_metadata():
    """Load and examine BiMMuDa metadata files"""
    
    # Look for metadata files
    metadata_path = Path("../data/bimmuda/BiMMuDa-main/metadata")
    
    if not metadata_path.exists():
        print("❌ Metadata directory not found. Make sure download completed successfully.")
        return None, None
    
    # Load metadata files
    song_metadata_file = metadata_path / "bimmuda_per_song_metadata.csv"
    melody_metadata_file = metadata_path / "bimmuda_per_melody_metadata.csv"
    
    song_metadata = None
    melody_metadata = None
    
    if song_metadata_file.exists():
        song_metadata = pd.read_csv(song_metadata_file)
        print(f"📊 Song metadata loaded: {len(song_metadata)} songs")
        print("Columns:", list(song_metadata.columns))
        print("\nFirst few songs:")
        print(song_metadata.head())
    
    if melody_metadata_file.exists():
        melody_metadata = pd.read_csv(melody_metadata_file)
        print(f"\n📊 Melody metadata loaded: {len(melody_metadata)} melodies")
        print("Columns:", list(melody_metadata.columns))
    
    return song_metadata, melody_metadata

def find_matches_with_billboard_data():
    """Find matches between BiMMuDa and your Billboard data"""
    
    # Connect to your database
    db_path = "../data/databases/music_database.db"
    conn = sqlite3.connect(db_path)
    
    # Get your Billboard songs
    billboard_query = """
    SELECT song_id, song_title, artist, first_chart_date, peak_position 
    FROM unique_songs 
    ORDER BY peak_position, song_title
    """
    
    billboard_df = pd.read_sql_query(billboard_query, conn)
    print(f"📊 Your Billboard database has {len(billboard_df)} unique songs")
    
    # Load BiMMuDa metadata
    song_metadata, _ = explore_bimmuda_metadata()
    
    if song_metadata is not None:
        # Try to find matches (we'll implement this after seeing the metadata structure)
        print(f"\n🔍 BiMMuDa has {len(song_metadata)} songs to match against")
        print("We'll implement matching logic after examining the data structure...")
    
    conn.close()
    return billboard_df, song_metadata

if __name__ == "__main__":
    print("🎸 BiMMuDa Integration for Guitar Chord Website")
    print("=" * 50)
    
    # Step 1: Download BiMMuDa data
    if download_bimmuda_data():
        print("\n" + "=" * 50)
        
        # Step 2: Explore metadata
        song_metadata, melody_metadata = explore_bimmuda_metadata()
        
        print("\n" + "=" * 50)
        
        # Step 3: Find matches with your Billboard data
        billboard_data, bimmuda_data = find_matches_with_billboard_data()
        
        print("\n🎯 Next steps:")
        print("1. Examine BiMMuDa metadata structure")
        print("2. Create song matching algorithm")
        print("3. Extract chords from MIDI files")
        print("4. Populate your song_chord_data table")
    else:
        print("❌ Download failed. Please check your internet connection and try again.")
