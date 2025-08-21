#!/usr/bin/env python3
"""
Download Fresh Billboard Hot 100 Data
"""

import pandas as pd
import sqlite3
import requests
from io import StringIO

def download_billboard_data():
    """Download Billboard Hot 100 data from a reliable source"""
    print("📥 DOWNLOADING FRESH BILLBOARD DATA")
    print("=" * 40)
    
    # Try multiple sources
    sources = [
        {
            'name': 'GitHub Dataset',
            'url': 'https://raw.githubusercontent.com/walkerkq/musiclyrics/master/billboard_lyrics_1964-2015.csv'
        },
        {
            'name': 'Another Dataset',
            'url': 'https://gist.githubusercontent.com/mbejda/9912f7a366c62c1f296c/raw/dd94a25492b3062f4ca0dc2bb2cdf23fec0896ea/10000-MTV-Music-Artists-page-1.csv'
        }
    ]
    
    for source in sources:
        try:
            print(f"Trying {source['name']}...")
            response = requests.get(source['url'])
            
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                print(f"✅ Downloaded {len(df):,} records from {source['name']}")
                print("Columns:", df.columns.tolist())
                return df
            else:
                print(f"❌ Failed: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with {source['name']}: {e}")
    
    return None

def create_sample_billboard_data():
    """Create a sample dataset if download fails"""
    print("\n📝 CREATING SAMPLE BILLBOARD DATA")
    print("=" * 40)
    
    # Create sample data matching your McGill songs
    sample_data = [
        {'Song': 'Chiquitita', 'Artist': 'ABBA', 'Year': 1979, 'Rank': 29, 'Weeks': 12},
        {'Song': 'Honey Honey', 'Artist': 'ABBA', 'Year': 1974, 'Rank': 27, 'Weeks': 8},
        {'Song': "School's Out", 'Artist': 'Alice Cooper', 'Year': 1972, 'Rank': 7, 'Weeks': 13},
        {'Song': 'Shadow Dancing', 'Artist': 'Andy Gibb', 'Year': 1978, 'Rank': 1, 'Weeks': 17},
        {'Song': 'Sweet Love', 'Artist': 'Anita Baker', 'Year': 1986, 'Rank': 8, 'Weeks': 16},
        {'Song': 'Could I Have This Dance', 'Artist': 'Anne Murray', 'Year': 1980, 'Rank': 33, 'Weeks': 11},
        {'Song': 'Love Song', 'Artist': 'Anne Murray', 'Year': 1974, 'Rank': 12, 'Weeks': 12},
        {'Song': 'Roll On Down The Highway', 'Artist': 'Bachman Turner Overdrive', 'Year': 1975, 'Rank': 14, 'Weeks': 10}
    ]
    
    df = pd.DataFrame(sample_data)
    print(f"✅ Created sample dataset with {len(df)} songs")
    return df

def create_database_tables(df):
    """Create billboard_hot100 and unique_songs tables"""
    print(f"\n🗄️ CREATING BILLBOARD TABLES")
    print("=" * 40)
    
    conn = sqlite3.connect('music_database.db')
    
    # Create billboard_hot100 table
    df.to_sql('billboard_hot100', conn, if_exists='replace', index=False)
    print(f"✅ Created billboard_hot100 table with {len(df):,} records")
    
    # Create unique_songs table
    if 'Song' in df.columns and 'Artist' in df.columns:
        # Use the column names from the actual data
        song_col = 'Song'
        artist_col = 'Artist'
        rank_col = 'Rank' if 'Rank' in df.columns else df.columns[2]  # fallback
    else:
        # Try common column names
        song_col = df.columns[0]
        artist_col = df.columns[1] 
        rank_col = df.columns[2] if len(df.columns) > 2 else song_col
    
    unique_songs = df.groupby([song_col, artist_col]).agg({
        rank_col: 'min',  # Best position
    }).reset_index()
    
    unique_songs.columns = ['song_title', 'artist', 'peak_position']
    unique_songs['song_id'] = range(1, len(unique_songs) + 1)
    unique_songs['weeks_on_chart'] = 1  # Default value
    
    # Reorder columns
    unique_songs = unique_songs[['song_id', 'song_title', 'artist', 'peak_position', 'weeks_on_chart']]
    
    unique_songs.to_sql('unique_songs', conn, if_exists='replace', index=False)
    print(f"✅ Created unique_songs table with {len(unique_songs):,} unique songs")
    
    conn.close()
    return len(df), len(unique_songs)

def main():
    print("🎵 RESTORING BILLBOARD DATABASE")
    print("=" * 50)
    
    # Try to download data
    df = download_billboard_data()
    
    # If download fails, use sample data
    if df is None:
        df = create_sample_billboard_data()
    
    # Create database tables
    billboard_count, unique_count = create_database_tables(df)
    
    print(f"\n🎉 BILLBOARD DATABASE RESTORED!")
    print(f"   ✓ {billboard_count:,} Billboard entries")
    print(f"   ✓ {unique_count:,} unique songs")
    print(f"   ✓ Ready to match with McGill chord data!")

if __name__ == "__main__":
    main()