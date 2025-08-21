import sqlite3
import pandas as pd
from pathlib import Path
import difflib
from datetime import datetime

def load_bimmuda_data():
    """Load BiMMuDa metadata"""
    # Try different possible paths
    possible_paths = [
        Path("../data/bimmuda/BiMMuDa-main/metadata/bimmuda_per_song_metadata.csv"),
        Path("../data/bimmuda/metadata/bimmuda_per_song_metadata.csv"),
        Path("data/bimmuda/BiMMuDa-main/metadata/bimmuda_per_song_metadata.csv"),
        Path("data/bimmuda/metadata/bimmuda_per_song_metadata.csv")
    ]
    
    metadata_path = None
    for path in possible_paths:
        if path.exists():
            metadata_path = path
            break
    
    if metadata_path is None:
        print("❌ BiMMuDa metadata not found. Let's check what was actually downloaded:")
        # List the contents to debug
        bimmuda_base = Path("../data/bimmuda")
        if bimmuda_base.exists():
            print(f"Contents of {bimmuda_base}:")
            for item in bimmuda_base.rglob("*"):
                print(f"  {item}")
        return None
    
    bimmuda_df = pd.read_csv(metadata_path)
    print(f"📊 Loaded {len(bimmuda_df)} BiMMuDa songs")
    return bimmuda_df

def clean_song_title(title):
    """Clean song titles for better matching"""
    if pd.isna(title):
        return ""
    
    # Remove common variations
    title = str(title).strip()
    title = title.replace("'", "'")  # Smart quotes
    title = title.replace('"', '"')  # Smart quotes
    title = title.replace('&', 'and')
    
    # Remove parenthetical info for matching
    if '(' in title:
        title = title.split('(')[0].strip()
    
    return title.lower()

def clean_artist_name(artist):
    """Clean artist names for better matching"""
    if pd.isna(artist):
        return ""
    
    artist = str(artist).strip()
    artist = artist.replace('&', 'and')
    
    # Handle common variations
    variations = {
        'feat.': 'featuring',
        'ft.': 'featuring', 
        ' w/ ': ' with ',
        ' vs ': ' versus ',
    }
    
    for old, new in variations.items():
        artist = artist.replace(old, new)
    
    return artist.lower()

def find_exact_matches(bimmuda_df, billboard_df):
    """Find exact matches between BiMMuDa and Billboard data"""
    
    matches = []
    
    for _, bimmuda_song in bimmuda_df.iterrows():
        bimmuda_title = clean_song_title(bimmuda_song['Title'])
        bimmuda_artist = clean_artist_name(bimmuda_song['Artist'])
        
        # Try exact matching first
        for _, billboard_song in billboard_df.iterrows():
            billboard_title = clean_song_title(billboard_song['song_title'])
            billboard_artist = clean_artist_name(billboard_song['artist'])
            
            if (bimmuda_title == billboard_title and 
                bimmuda_artist == billboard_artist):
                
                matches.append({
                    'bimmuda_title': bimmuda_song['Title'],
                    'bimmuda_artist': bimmuda_song['Artist'],
                    'bimmuda_year': bimmuda_song['Year'],
                    'bimmuda_position': bimmuda_song['Position'],
                    'billboard_song_id': billboard_song['song_id'],
                    'billboard_title': billboard_song['song_title'],
                    'billboard_artist': billboard_song['artist'],
                    'billboard_peak': billboard_song['peak_position'],
                    'match_type': 'exact',
                    'confidence': 1.0
                })
                break
    
    return matches

def find_fuzzy_matches(bimmuda_df, billboard_df, existing_matches):
    """Find fuzzy matches for unmatched BiMMuDa songs"""
    
    matched_billboard_ids = {match['billboard_song_id'] for match in existing_matches}
    matched_bimmuda_titles = {match['bimmuda_title'] for match in existing_matches}
    
    fuzzy_matches = []
    
    for _, bimmuda_song in bimmuda_df.iterrows():
        if bimmuda_song['Title'] in matched_bimmuda_titles:
            continue  # Skip already matched songs
            
        bimmuda_title = clean_song_title(bimmuda_song['Title'])
        bimmuda_artist = clean_artist_name(bimmuda_song['Artist'])
        
        best_match = None
        best_score = 0.0
        
        for _, billboard_song in billboard_df.iterrows():
            if billboard_song['song_id'] in matched_billboard_ids:
                continue  # Skip already matched songs
                
            billboard_title = clean_song_title(billboard_song['song_title'])
            billboard_artist = clean_artist_name(billboard_song['artist'])
            
            # Calculate similarity scores
            title_score = difflib.SequenceMatcher(None, bimmuda_title, billboard_title).ratio()
            artist_score = difflib.SequenceMatcher(None, bimmuda_artist, billboard_artist).ratio()
            
            # Combined score (title is more important)
            combined_score = (title_score * 0.7) + (artist_score * 0.3)
            
            if combined_score > best_score and combined_score > 0.8:  # High threshold
                best_score = combined_score
                best_match = {
                    'bimmuda_title': bimmuda_song['Title'],
                    'bimmuda_artist': bimmuda_song['Artist'],
                    'bimmuda_year': bimmuda_song['Year'],
                    'bimmuda_position': bimmuda_song['Position'],
                    'billboard_song_id': billboard_song['song_id'],
                    'billboard_title': billboard_song['song_title'],
                    'billboard_artist': billboard_song['artist'],
                    'billboard_peak': billboard_song['peak_position'],
                    'match_type': 'fuzzy',
                    'confidence': round(combined_score, 3)
                }
        
        if best_match and best_score > 0.8:
            fuzzy_matches.append(best_match)
            matched_billboard_ids.add(best_match['billboard_song_id'])
    
    return fuzzy_matches

def main():
    """Main matching process"""
    print("🎸 BiMMuDa to Billboard Song Matcher")
    print("=" * 50)
    
    # Load data
    bimmuda_df = load_bimmuda_data()
    if bimmuda_df is None:
        return
    
    # Connect to database - try different paths
    possible_db_paths = [
        "../data/databases/music_database.db",
        "data/databases/music_database.db",
        "../music_database.db",
        "music_database.db"
    ]
    
    conn = None
    for db_path in possible_db_paths:
        try:
            if Path(db_path).exists():
                conn = sqlite3.connect(db_path)
                print(f"✅ Connected to database: {db_path}")
                break
        except:
            continue
    
    if conn is None:
        print("❌ Could not find music_database.db. Let's check what we have:")
        for search_path in [".", "..", "../data", "data"]:
            search_dir = Path(search_path)
            if search_dir.exists():
                print(f"\nContents of {search_dir.absolute()}:")
                for item in search_dir.glob("*.db"):
                    print(f"  {item}")
        return
    
    billboard_df = pd.read_sql_query("""
        SELECT song_id, song_title, artist, first_chart_date, peak_position, weeks_on_chart
        FROM unique_songs 
        WHERE peak_position <= 50
        ORDER BY peak_position
    """, conn)
    
    print(f"📊 Loaded {len(billboard_df)} Billboard songs (top 50 hits only)")
    
    # Find exact matches
    print("\n🔍 Finding exact matches...")
    exact_matches = find_exact_matches(bimmuda_df, billboard_df)
    print(f"✅ Found {len(exact_matches)} exact matches")
    
    # Find fuzzy matches
    print("\n🔍 Finding fuzzy matches...")
    fuzzy_matches = find_fuzzy_matches(bimmuda_df, billboard_df, exact_matches)
    print(f"✅ Found {len(fuzzy_matches)} fuzzy matches")
    
    # Combine all matches
    all_matches = exact_matches + fuzzy_matches
    
    print(f"\n🎯 Total matches found: {len(all_matches)}")
    print(f"📊 Match rate: {len(all_matches)}/{len(bimmuda_df)} = {len(all_matches)/len(bimmuda_df)*100:.1f}%")
    
    # Show sample matches
    print("\n📋 Sample matches:")
    for i, match in enumerate(all_matches[:10]):
        print(f"{i+1:2d}. {match['bimmuda_title']} by {match['bimmuda_artist']} ({match['bimmuda_year']})")
        print(f"    → {match['billboard_title']} by {match['billboard_artist']} (Peak: #{match['billboard_peak']})")
        print(f"    → Confidence: {match['confidence']} ({match['match_type']})")
        print()
    
    # Save matches to database
    if all_matches:
        save_matches_to_db(conn, all_matches)
    
    conn.close()
    
    return all_matches

def save_matches_to_db(conn, matches):
    """Save matches to the song_chord_data table"""
    print(f"\n💾 Saving {len(matches)} matches to database...")
    
    # Clear existing BiMMuDa matches
    conn.execute("DELETE FROM song_chord_data WHERE data_source = 'BiMMuDa'")
    
    # Insert new matches (without chord data for now - we'll add that next)
    for match in matches:
        conn.execute("""
            INSERT INTO song_chord_data 
            (song_id, chord_progression, basic_chords, genre, main_genre, decade, 
             release_date, match_confidence, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match['billboard_song_id'],
            None,  # We'll extract chords from MIDI next
            None,
            None,  # Will add from BiMMuDa metadata
            None,
            str(match['bimmuda_year'])[:3] + '0',  # Convert year to decade
            f"{match['bimmuda_year']}-01-01",
            str(match['confidence']),
            'BiMMuDa'
        ))
    
    conn.commit()
    print("✅ Matches saved to database!")

if __name__ == "__main__":
    matches = main()
