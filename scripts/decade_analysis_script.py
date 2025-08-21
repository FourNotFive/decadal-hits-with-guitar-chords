import sqlite3
import pandas as pd
from collections import defaultdict
import re
from datetime import datetime

def analyze_decades_and_top_songs(db_path='../data/databases/music_database.db'):
    """
    Analyze Billboard data to categorize songs by decades and identify top songs.
    """
    conn = sqlite3.connect(db_path)
    
    print("🎯 DECADE CATEGORIZATION & TOP SONGS ANALYSIS")
    print("=" * 60)
    
    # First, let's examine the date format in billboard_hot100
    print("\n1. Examining date format in Billboard data...")
    date_sample = pd.read_sql_query("""
        SELECT date, COUNT(*) as count
        FROM billboard_hot100 
        GROUP BY date 
        ORDER BY date 
        LIMIT 10
    """, conn)
    print("Sample dates:")
    print(date_sample)
    
    # Examine unique_songs structure
    print("\n2. Examining unique_songs structure...")
    unique_songs_sample = pd.read_sql_query("""
        SELECT * FROM unique_songs LIMIT 5
    """, conn)
    print("Unique songs sample:")
    print(unique_songs_sample.to_string())
    
    # Get all Billboard data with dates
    print("\n3. Loading Billboard chart data...")
    billboard_query = """
        SELECT b.*, u.song AS unique_song, u.performer AS unique_performer
        FROM billboard_hot100 b
        LEFT JOIN unique_songs u ON b.song = u.song AND b.performer = u.performer
        WHERE b.date IS NOT NULL
    """
    billboard_df = pd.read_sql_query(billboard_query, conn)
    
    print(f"Total Billboard entries with dates: {len(billboard_df):,}")
    
    # Parse dates and extract decades
    print("\n4. Parsing dates and extracting decades...")
    
    def parse_date_and_decade(date_str):
        """Parse date string and return year and decade"""
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y']:
                try:
                    date_obj = datetime.strptime(str(date_str), fmt)
                    year = date_obj.year
                    decade = (year // 10) * 10
                    return year, decade
                except ValueError:
                    continue
            
            # If no format works, try extracting year with regex
            year_match = re.search(r'(\d{4})', str(date_str))
            if year_match:
                year = int(year_match.group(1))
                decade = (year // 10) * 10
                return year, decade
            
            return None, None
        except:
            return None, None
    
    # Apply date parsing
    billboard_df[['year', 'decade']] = billboard_df['date'].apply(
        lambda x: pd.Series(parse_date_and_decade(x))
    )
    
    # Remove entries without valid dates
    billboard_df = billboard_df.dropna(subset=['year', 'decade'])
    billboard_df['year'] = billboard_df['year'].astype(int)
    billboard_df['decade'] = billboard_df['decade'].astype(int)
    
    print(f"Entries with valid dates: {len(billboard_df):,}")
    
    # Analyze decade distribution
    print("\n5. Decade distribution:")
    decade_counts = billboard_df['decade'].value_counts().sort_index()
    for decade, count in decade_counts.items():
        print(f"  {decade}s: {count:,} chart entries")
    
    # Identify top songs per decade using multiple criteria
    print("\n6. Identifying top songs per decade...")
    
    def calculate_song_score(group):
        """Calculate a comprehensive score for song popularity"""
        # Factors: peak position (lower is better), weeks on chart, average position
        peak_position = group['position'].min()
        weeks_on_chart = len(group)
        avg_position = group['position'].mean()
        
        # Score formula (lower is better for positions, higher for weeks)
        # Heavily weight peak position, moderately weight weeks on chart
        score = (101 - peak_position) * 2 + weeks_on_chart * 1 + (101 - avg_position)
        
        return pd.Series({
            'peak_position': peak_position,
            'weeks_on_chart': weeks_on_chart,
            'avg_position': avg_position,
            'popularity_score': score,
            'first_chart_date': group['date'].min(),
            'last_chart_date': group['date'].max()
        })
    
    # Group by decade, song, and performer
    top_songs_by_decade = billboard_df.groupby(['decade', 'song', 'performer']).apply(
        calculate_song_score
    ).reset_index()
    
    # Get top 50 songs per decade
    print("\n7. Top songs by decade (showing top 10 per decade):")
    top_songs_summary = {}
    
    for decade in sorted(top_songs_by_decade['decade'].unique()):
        decade_songs = top_songs_by_decade[
            top_songs_by_decade['decade'] == decade
        ].sort_values('popularity_score', ascending=False).head(50)
        
        top_songs_summary[decade] = decade_songs
        
        print(f"\n{decade}s Top 10:")
        for i, (_, song) in enumerate(decade_songs.head(10).iterrows(), 1):
            print(f"  {i:2d}. {song['song'][:40]:40} - {song['performer'][:25]:25} "
                  f"(Peak: #{song['peak_position']}, {song['weeks_on_chart']} weeks)")
    
    # Check McGill chord data overlap
    print("\n8. Checking McGill chord data overlap...")
    mcgill_query = """
        SELECT DISTINCT title, artist, COUNT(*) as chord_entries
        FROM mcgill_chord_data
        GROUP BY title, artist
    """
    mcgill_df = pd.read_sql_query(mcgill_query, conn)
    print(f"McGill songs with chord data: {len(mcgill_df)}")
    
    # Simple string matching to estimate overlap
    def normalize_string(s):
        """Normalize string for matching"""
        return re.sub(r'[^a-zA-Z0-9]', '', str(s).lower())
    
    mcgill_df['title_norm'] = mcgill_df['title'].apply(normalize_string)
    mcgill_df['artist_norm'] = mcgill_df['artist'].apply(normalize_string)
    
    # Check overlap for each decade
    overlap_counts = {}
    for decade, decade_songs in top_songs_summary.items():
        decade_songs['song_norm'] = decade_songs['song'].apply(normalize_string)
        decade_songs['performer_norm'] = decade_songs['performer'].apply(normalize_string)
        
        # Find potential matches
        matches = 0
        matched_songs = []
        
        for _, billboard_song in decade_songs.iterrows():
            for _, mcgill_song in mcgill_df.iterrows():
                # Check if titles and artists match (fuzzy)
                title_match = (
                    billboard_song['song_norm'] in mcgill_song['title_norm'] or
                    mcgill_song['title_norm'] in billboard_song['song_norm']
                )
                artist_match = (
                    billboard_song['performer_norm'] in mcgill_song['artist_norm'] or
                    mcgill_song['artist_norm'] in billboard_song['performer_norm']
                )
                
                if title_match and artist_match:
                    matches += 1
                    matched_songs.append(f"{billboard_song['song']} - {billboard_song['performer']}")
                    break
        
        overlap_counts[decade] = {
            'total_top_songs': len(decade_songs),
            'with_chord_data': matches,
            'percentage': (matches / len(decade_songs)) * 100,
            'matched_songs': matched_songs
        }
    
    print("\n9. Chord data overlap by decade:")
    for decade, stats in overlap_counts.items():
        print(f"  {decade}s: {stats['with_chord_data']}/{stats['total_top_songs']} "
              f"({stats['percentage']:.1f}%) have chord data")
    
    # Create decade tables for the website
    print("\n10. Creating decade-based tables...")
    
    for decade, decade_songs in top_songs_summary.items():
        table_name = f"top_songs_{decade}s"
        decade_songs.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Created table: {table_name} ({len(decade_songs)} songs)")
    
    # Create a summary table
    decade_summary = []
    for decade, stats in overlap_counts.items():
        decade_summary.append({
            'decade': decade,
            'total_songs': stats['total_top_songs'],
            'songs_with_chords': stats['with_chord_data'],
            'chord_percentage': round(stats['percentage'], 1),
            'year_start': decade,
            'year_end': decade + 9,
            'era_name': f"{decade}s"
        })
    
    decade_summary_df = pd.DataFrame(decade_summary)
    decade_summary_df.to_sql('decade_summary', conn, if_exists='replace', index=False)
    print(f"\nCreated decade_summary table with {len(decade_summary_df)} decades")
    
    conn.close()
    
    print("\n✅ DECADE ANALYSIS COMPLETE!")
    print("\nNext steps:")
    print("1. Run the basic web interface script")
    print("2. Implement song-chord matching algorithms") 
    print("3. Add chord diagrams and guitar tabs")
    
    return top_songs_summary, overlap_counts

if __name__ == "__main__":
    # Run the analysis
    top_songs, overlap = analyze_decades_and_top_songs()
    
    print("\n🎸 Ready to build the guitar chord website!")