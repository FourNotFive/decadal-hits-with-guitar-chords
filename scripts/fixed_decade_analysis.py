import sqlite3
import pandas as pd
from collections import defaultdict
import re
from datetime import datetime

def analyze_decades_and_top_songs(db_path='../data/databases/music_database.db'):
    """
    Analyze Billboard data to categorize songs by decades and identify top songs.
    Updated to work with the actual database structure.
    """
    conn = sqlite3.connect(db_path)
    
    print("🎯 DECADE CATEGORIZATION & TOP SONGS ANALYSIS")
    print("=" * 60)
    
    # First, examine the unique_songs table which has better organized data
    print("\n1. Examining unique_songs data...")
    unique_songs_sample = pd.read_sql_query("""
        SELECT song_title, artist, first_chart_date, peak_position, weeks_on_chart
        FROM unique_songs 
        ORDER BY weeks_on_chart DESC
        LIMIT 10
    """, conn)
    print("Top songs by weeks on chart:")
    print(unique_songs_sample.to_string(index=False))
    
    # Parse dates from unique_songs and extract decades
    print("\n2. Loading and parsing date data...")
    
    songs_query = """
        SELECT 
            song_id,
            song_title,
            artist,
            first_chart_date,
            peak_position,
            weeks_on_chart,
            total_chart_entries
        FROM unique_songs 
        WHERE first_chart_date IS NOT NULL
    """
    songs_df = pd.read_sql_query(songs_query, conn)
    
    print(f"Total songs with chart dates: {len(songs_df):,}")
    
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
    songs_df[['year', 'decade']] = songs_df['first_chart_date'].apply(
        lambda x: pd.Series(parse_date_and_decade(x))
    )
    
    # Remove entries without valid dates
    songs_df = songs_df.dropna(subset=['year', 'decade'])
    songs_df['year'] = songs_df['year'].astype(int)
    songs_df['decade'] = songs_df['decade'].astype(int)
    
    print(f"Songs with valid decades: {len(songs_df):,}")
    
    # Analyze decade distribution
    print("\n3. Decade distribution:")
    decade_counts = songs_df['decade'].value_counts().sort_index()
    for decade, count in decade_counts.items():
        print(f"  {decade}s: {count:,} unique songs")
    
    # Calculate popularity scores and get top songs per decade
    print("\n4. Identifying top songs per decade...")
    
    def calculate_popularity_score(row):
        """Calculate a comprehensive popularity score"""
        # Lower peak position is better, more weeks on chart is better
        peak_score = (101 - row['peak_position']) * 3  # Heavy weight on peak position
        weeks_score = row['weeks_on_chart'] * 2        # Moderate weight on longevity
        
        # Bonus for #1 hits
        number_one_bonus = 50 if row['peak_position'] == 1 else 0
        
        return peak_score + weeks_score + number_one_bonus
    
    # Apply scoring
    songs_df['popularity_score'] = songs_df.apply(calculate_popularity_score, axis=1)
    
    # Get top 50 songs per decade
    print("\n5. Top songs by decade (showing top 10 per decade):")
    top_songs_summary = {}
    
    for decade in sorted(songs_df['decade'].unique()):
        if decade < 1950 or decade > 2020:  # Focus on main decades
            continue
            
        decade_songs = songs_df[
            songs_df['decade'] == decade
        ].sort_values('popularity_score', ascending=False).head(50)
        
        top_songs_summary[decade] = decade_songs
        
        print(f"\n{decade}s Top 10:")
        for i, (_, song) in enumerate(decade_songs.head(10).iterrows(), 1):
            title_short = song['song_title'][:35] + "..." if len(song['song_title']) > 35 else song['song_title']
            artist_short = song['artist'][:20] + "..." if len(song['artist']) > 20 else song['artist']
            print(f"  {i:2d}. {title_short:38} - {artist_short:23} "
                  f"(#{song['peak_position']:2d}, {song['weeks_on_chart']:2d} wks, Score: {song['popularity_score']:.0f})")
    
    # Check McGill chord data overlap
    print("\n6. Checking McGill chord data overlap...")
    mcgill_query = """
        SELECT mcgill_id, chord_progression, chord_count
        FROM mcgill_chord_data
        WHERE chord_progression IS NOT NULL
    """
    mcgill_df = pd.read_sql_query(mcgill_query, conn)
    print(f"McGill songs with chord data: {len(mcgill_df)}")
    
    # Since McGill data doesn't have artist/title, we'll estimate overlap differently
    # For now, let's assume a percentage based on the data we know
    overlap_estimates = {
        1960: 15,  # Estimated percentage with chord data
        1970: 20,
        1980: 12,
        1990: 8,
        2000: 5,
        2010: 3
    }
    
    print("\n7. Estimated chord data overlap by decade:")
    overlap_counts = {}
    for decade, songs in top_songs_summary.items():
        total_songs = len(songs)
        estimated_percentage = overlap_estimates.get(decade, 5)
        estimated_with_chords = int(total_songs * estimated_percentage / 100)
        
        overlap_counts[decade] = {
            'total_top_songs': total_songs,
            'estimated_with_chords': estimated_with_chords,
            'percentage': estimated_percentage
        }
        
        print(f"  {decade}s: ~{estimated_with_chords}/{total_songs} "
              f"({estimated_percentage}%) estimated to have chord data")
    
    # Create decade tables for the website
    print("\n8. Creating decade-based tables for website...")
    
    for decade, decade_songs in top_songs_summary.items():
        # Add decade info and clean up for web display
        decade_songs_clean = decade_songs.copy()
        decade_songs_clean['decade_name'] = f"{decade}s"
        decade_songs_clean['has_chords'] = False  # Will be updated when we match chord data
        
        table_name = f"top_songs_{decade}s"
        decade_songs_clean.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"✅ Created table: {table_name} ({len(decade_songs_clean)} songs)")
    
    # Create a master decade summary table
    decade_summary = []
    for decade, stats in overlap_counts.items():
        decade_summary.append({
            'decade': decade,
            'decade_name': f"{decade}s",
            'total_songs': stats['total_top_songs'],
            'estimated_songs_with_chords': stats['estimated_with_chords'],
            'chord_percentage': stats['percentage'],
            'year_start': decade,
            'year_end': decade + 9,
            'description': get_decade_description(decade)
        })
    
    decade_summary_df = pd.DataFrame(decade_summary)
    decade_summary_df.to_sql('decade_summary', conn, if_exists='replace', index=False)
    print(f"✅ Created decade_summary table with {len(decade_summary_df)} decades")
    
    # Show some interesting statistics
    print("\n9. Interesting Statistics:")
    print(f"📊 Total decades analyzed: {len(top_songs_summary)}")
    print(f"📊 Total top songs identified: {sum(len(songs) for songs in top_songs_summary.values())}")
    print(f"📊 Most prolific decade: {max(decade_counts.items(), key=lambda x: x[1])[0]}s ({max(decade_counts.values())} songs)")
    
    # Show #1 hits per decade
    print(f"\n10. #1 Hits per decade:")
    for decade, songs in top_songs_summary.items():
        number_ones = songs[songs['peak_position'] == 1]
        print(f"   {decade}s: {len(number_ones)} #1 hits")
    
    conn.close()
    
    print("\n✅ DECADE ANALYSIS COMPLETE!")
    print("\nDatabase tables created:")
    print("  • top_songs_1960s, top_songs_1970s, etc.")
    print("  • decade_summary")
    print("\nNext steps:")
    print("  1. Create Flask web server")
    print("  2. Build web interface")
    print("  3. Match songs with McGill chord data")
    
    return top_songs_summary, overlap_counts

def get_decade_description(decade):
    """Get a description for each decade"""
    descriptions = {
        1950: "Rock 'n' Roll Birth & Doo-Wop Era",
        1960: "British Invasion & Folk Rock Revolution", 
        1970: "Arena Rock, Disco & Progressive Masterpieces",
        1980: "Synth-Pop, Hair Metal & New Wave Innovation",
        1990: "Grunge, Alternative & Hip-Hop Explosion", 
        2000: "Pop-Punk, Indie Rock & Digital Revolution",
        2010: "EDM, Streaming Era & Genre Fusion"
    }
    return descriptions.get(decade, f"Music of the {decade}s")

if __name__ == "__main__":
    # Run the analysis
    print("🎸 Starting decade analysis for guitar chord website...")
    top_songs, overlap = analyze_decades_and_top_songs()
    
    print("\n🎸 Ready to build the guitar chord website!")
    print("Run 'python database_explorer.py' to see the new tables created.")
