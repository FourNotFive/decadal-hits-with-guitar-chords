#!/usr/bin/env python3
"""
BiMMuDa Guitar Chord Website
A decade-based website showcasing 381 unique songs with rich metadata
"""

from flask import Flask, render_template_string, request, jsonify
import sqlite3
import os
from collections import Counter, defaultdict

app = Flask(__name__)

# Database path
import os
BIMMUDA_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'databases', 'billboard_data.db')

class TablatureGenerator:
    """Simplified tablature generator for website integration"""
    
    def __init__(self):
        # Basic chord-to-tablature patterns
        self.chord_tab_patterns = {
            'C': {'frets': ['x', '3', '2', '0', '1', '0'], 'difficulty': 'Beginner'},
            'D': {'frets': ['x', 'x', '0', '2', '3', '2'], 'difficulty': 'Beginner'},
            'E': {'frets': ['0', '2', '2', '1', '0', '0'], 'difficulty': 'Beginner'},
            'F': {'frets': ['1', '3', '3', '2', '1', '1'], 'difficulty': 'Intermediate', 'barre': True},
            'G': {'frets': ['3', '2', '0', '0', '3', '3'], 'difficulty': 'Beginner'},
            'A': {'frets': ['x', '0', '2', '2', '2', '0'], 'difficulty': 'Beginner'},
            'B': {'frets': ['x', '2', '4', '4', '4', '2'], 'difficulty': 'Intermediate', 'barre': True},
            'Am': {'frets': ['x', '0', '2', '2', '1', '0'], 'difficulty': 'Beginner'},
            'Bm': {'frets': ['x', '2', '4', '4', '3', '2'], 'difficulty': 'Intermediate', 'barre': True},
            'Cm': {'frets': ['x', '3', '5', '5', '4', '3'], 'difficulty': 'Intermediate', 'barre': True},
            'Dm': {'frets': ['x', 'x', '0', '2', '3', '1'], 'difficulty': 'Beginner'},
            'Em': {'frets': ['0', '2', '2', '0', '0', '0'], 'difficulty': 'Beginner'},
            'Fm': {'frets': ['1', '3', '3', '1', '1', '1'], 'difficulty': 'Intermediate', 'barre': True},
            'Gm': {'frets': ['3', '5', '5', '3', '3', '3'], 'difficulty': 'Intermediate', 'barre': True}
        }
        
        self.strumming_patterns = {
            'basic': 'D-D-U-U-D-U',
            'folk': 'D-D-U-D-U',
            'rock': 'D-X-U-X-D-U'
        }
    
    def generate_chord_progression_tab(self, chord_progression, style='basic'):
        """Generate a basic tablature for a chord progression"""
        if not chord_progression:
            return None
        
        chords = [chord.strip() for chord in chord_progression.split(' - ')]
        available_chords = [chord for chord in chords if chord in self.chord_tab_patterns]
        
        if not available_chords:
            return {
                'error': 'No tablature available for these chords',
                'missing_chords': chords
            }
        
        difficulty = self._assess_difficulty(available_chords)
        tab_notation = self._create_tab_notation(available_chords, style)
        
        return {
            'chords': available_chords,
            'strumming_pattern': self.strumming_patterns.get(style, 'D-D-U-U-D-U'),
            'difficulty': difficulty,
            'tab_notation': tab_notation,
            'missing_chords': [chord for chord in chords if chord not in available_chords]
        }
    
    def _create_tab_notation(self, chords, style):
        """Create professional Songsterr-style guitar tablature"""
        if not chords:
            return []
        
        display_chords = chords[:6]  # Show up to 6 chords for cleaner display
        tab_lines = []
        
        # Professional header with musical notation style
        tab_lines.extend([
            "═══════════════════════════════════════════════════════════════",
            f"♫  CHORD PROGRESSION: {' → '.join(display_chords)}",
            f"♪  STRUM PATTERN: {self.strumming_patterns.get(style, 'D-D-U-U-D-U')}",
            "═══════════════════════════════════════════════════════════════",
            ""
        ])
        
        # Create chord names with better spacing and musical symbols
        chord_line = "     "
        for i, chord in enumerate(display_chords):
            if i > 0:
                chord_line += "    "
            chord_line += f" {chord} "
        tab_lines.append(chord_line)
        
        # Add measure separators
        measure_line = "     "
        for i, chord in enumerate(display_chords):
            if i > 0:
                measure_line += "    "
            measure_line += "│─ │"
        tab_lines.append(measure_line)
        tab_lines.append("")
        
        # Create professional tablature lines with better typography
        string_names = ['E', 'B', 'G', 'D', 'A', 'E']  # High to low (standard notation)
        string_labels = ['e', 'B', 'G', 'D', 'A', 'E']  # Display labels
        
        for string_idx, (string_name, label) in enumerate(zip(string_names, string_labels)):
            line = f"{label}│─"
            
            for i, chord in enumerate(display_chords):
                if i > 0:
                    line += "───│─"
                
                if chord in self.chord_tab_patterns:
                    # Get fret for this string (correct index for high-to-low order)
                    fret = self.chord_tab_patterns[chord]['frets'][string_idx]
                    
                    if fret == 'x':
                        line += "─X─"
                    elif fret == '0':
                        line += "─0─"
                    else:
                        line += f"─{fret}─"
                else:
                    line += "───"
            
            line += "─│"
            tab_lines.append(line)
        
        # Add closing measure line
        tab_lines.append("")
        closing_line = "     "
        for i, chord in enumerate(display_chords):
            if i > 0:
                closing_line += "    "
            closing_line += "└─ ┘"
        tab_lines.append(closing_line)
        
        # Add rhythm notation guide
        tab_lines.extend([
            "",
            "RHYTHM GUIDE:",
            "D = Down strum  ↓    U = Up strum  ↑    X = Muted strum  ✕",
            "═══════════════════════════════════════════════════════════════"
        ])
        
        return tab_lines
    
    def _assess_difficulty(self, chords):
        """Assess difficulty level"""
        difficulty_scores = []
        for chord in chords:
            if chord in self.chord_tab_patterns:
                if self.chord_tab_patterns[chord]['difficulty'] == 'Beginner':
                    difficulty_scores.append(1)
                else:
                    difficulty_scores.append(2)
        
        if not difficulty_scores:
            return "Unknown"
        
        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
        return "Beginner" if avg_difficulty <= 1.2 else "Intermediate"

# Create tablature generator instance
tab_generator = TablatureGenerator()

def get_db_connection():
    """Get database connection to BiMMuDa data"""
    conn = sqlite3.connect(BIMMUDA_DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_lyrics_data(folder_path):
    """Load lyrics from BiMMuDa dataset"""
    if not folder_path:
        return None
    
    try:
        # Construct path to lyrics file
        # folder_path format: 'BiMMuDa-main/bimmuda_dataset/1950/1'
        folder_parts = folder_path.split('/')
        year = folder_parts[-2]
        song_number = folder_parts[-1]
        
        lyrics_filename = f"{year}_{song_number.zfill(2)}_lyrics.txt"
        
        # Full path to BiMMuDa lyrics file
        bimmuda_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bimmuda')
        lyrics_path = os.path.join(bimmuda_base, folder_path, lyrics_filename)
        
        if os.path.exists(lyrics_path):
            with open(lyrics_path, 'r', encoding='utf-8') as f:
                lyrics_content = f.read().strip()
                return lyrics_content
        
    except Exception as e:
        print(f"Error loading lyrics: {e}")
    
    return None

@app.route('/')
def home():
    """Main page with decade selection"""
    conn = get_db_connection()
    
    # Get decade summary
    decades_query = """
        SELECT 
            (year/10)*10 as decade,
            COUNT(*) as song_count,
            MIN(year) as start_year,
            MAX(year) as end_year
        FROM bimmuda_songs 
        GROUP BY decade 
        ORDER BY decade
    """
    
    decades = conn.execute(decades_query).fetchall()
    conn.close()
    
    return render_template_string(HOME_TEMPLATE, decades=decades)

@app.route('/decade/<int:decade>')
def decade_view(decade):
    """Show songs for a specific decade"""
    conn = get_db_connection()
    
    # Get songs for this decade with rich metadata and chord progressions
    songs_query = """
        SELECT 
            id, title, artist, year, 
            genre_broad_1 as genre,
            bpm_1 as tempo,
            tonic_1 as key_signature,
            mode_1 as mode,
            time_signature_1 as time_sig,
            audio_link,
            has_midi_files,
            has_lyrics,
            chord_progression
        FROM bimmuda_songs 
        WHERE year >= ? AND year < ?
        ORDER BY year, title
    """
    
    songs = conn.execute(songs_query, (decade, decade + 10)).fetchall()
    
    # Count songs with chords
    songs_with_chords = []
    chord_count = 0
    for song in songs:
        song_dict = dict(song)
        if song_dict['chord_progression']:
            chord_count += 1
        songs_with_chords.append(song_dict)
    
    # Get decade stats
    stats_query = """
        SELECT 
            COUNT(*) as total_songs,
            COUNT(CASE WHEN has_midi_files = 1 THEN 1 END) as midi_count,
            COUNT(CASE WHEN has_lyrics = 1 THEN 1 END) as lyrics_count,
            COUNT(CASE WHEN audio_link != 'N/A' THEN 1 END) as audio_count
        FROM bimmuda_songs 
        WHERE year >= ? AND year < ?
    """
    
    stats = conn.execute(stats_query, (decade, decade + 10)).fetchone()
    stats_dict = dict(stats)
    stats_dict['chord_count'] = chord_count
    conn.close()
    
    return render_template_string(
        DECADE_TEMPLATE, 
        decade=decade, 
        songs=songs_with_chords, 
        stats=stats_dict
    )

@app.route('/song/<int:song_id>')
def song_detail(song_id):
    """Detailed view of a single song"""
    conn = get_db_connection()
    
    song_query = """
        SELECT * FROM bimmuda_songs WHERE id = ?
    """
    
    song = conn.execute(song_query, (song_id,)).fetchone()
    conn.close()
    
    if not song:
        return "Song not found", 404
    
    # Convert to dict and generate tablature if chords available
    song_dict = dict(song)
    
    # Generate tablature data
    tablature_data = None
    if song_dict.get('chord_progression'):
        tablature_data = tab_generator.generate_chord_progression_tab(song_dict['chord_progression'])
    
    # Load lyrics data if available
    lyrics_data = None
    if song_dict.get('has_lyrics') and song_dict.get('folder_path'):
        lyrics_data = get_lyrics_data(song_dict['folder_path'])
    
    return render_template_string(SONG_TEMPLATE, song=song_dict, tablature=tablature_data, lyrics=lyrics_data)

@app.route('/search')
def search():
    """Search songs by various criteria"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    
    if not query:
        return render_template_string(SEARCH_TEMPLATE, query='', results=[], search_type='all')
    
    conn = get_db_connection()
    
    # Build search query based on type
    if search_type == 'title':
        search_query = """
            SELECT * FROM bimmuda_songs 
            WHERE title LIKE ? 
            ORDER BY year, title
        """
        results = conn.execute(search_query, (f'%{query}%',)).fetchall()
    
    elif search_type == 'artist':
        search_query = """
            SELECT * FROM bimmuda_songs 
            WHERE artist LIKE ? 
            ORDER BY year, title
        """
        results = conn.execute(search_query, (f'%{query}%',)).fetchall()
    
    elif search_type == 'key':
        search_query = """
            SELECT * FROM bimmuda_songs 
            WHERE tonic_1 LIKE ? OR mode_1 LIKE ?
            ORDER BY year, title
        """
        results = conn.execute(search_query, (f'%{query}%', f'%{query}%')).fetchall()
    
    elif search_type == 'year':
        results = []
        query_lower = query.lower().strip()
        
        # Handle various decade formats - normalize ALL types of apostrophes
        # Different devices/keyboards produce different apostrophe characters
        apostrophes = [''', ''', '`', '′', '´', '῾', '῿', "'"]  # All possible apostrophes
        for apostrophe in apostrophes:
            query_lower = query_lower.replace(apostrophe, "'")
        
        decade_found = False
        
        # Check for written decades first: "sixties", "seventies", etc.
        if query_lower in ['fifties', 'sixties', 'seventies', 'eighties', 'nineties']:
            decade_map = {
                'fifties': 1950, 'sixties': 1960, 'seventies': 1970, 
                'eighties': 1980, 'nineties': 1990
            }
            decade = decade_map[query_lower]
            search_query = """
                SELECT * FROM bimmuda_songs 
                WHERE year >= ? AND year < ?
                ORDER BY year, title
            """
            results = conn.execute(search_query, (decade, decade + 10)).fetchall()
            decade_found = True
        
        # Check for decades with apostrophe: "1970's", "70's"  
        elif query_lower.endswith("'s"):
            base_year = query_lower[:-2]  # Remove 's from end
            if base_year.isdigit():
                if len(base_year) == 2:  # "70's" -> 1970s
                    base_num = int(base_year)
                    # Handle century logic: 50-99 = 1900s, 00-49 = 2000s
                    if base_num >= 50:
                        decade = 1900 + base_num
                    else:
                        decade = 2000 + base_num
                elif len(base_year) == 4:  # "1970's"
                    decade = int(base_year)
                else:
                    decade = None
                
                if decade and decade >= 1950 and decade <= 2020:  # Reasonable range check
                    search_query = """
                        SELECT * FROM bimmuda_songs 
                        WHERE year >= ? AND year < ?
                        ORDER BY year, title
                    """
                    results = conn.execute(search_query, (decade, decade + 10)).fetchall()
                    decade_found = True
        
        # Check for decades ending in 's': "1970s", "70s"  
        elif query_lower.endswith('s'):
            base_year = query_lower[:-1]  # Remove 's from end
            if base_year.isdigit():
                if len(base_year) == 2:  # "70s" -> 1970s
                    base_num = int(base_year)
                    # Handle century logic: 50-99 = 1900s, 00-49 = 2000s
                    if base_num >= 50:
                        decade = 1900 + base_num
                    else:
                        decade = 2000 + base_num
                elif len(base_year) == 4:  # "1970s"
                    decade = int(base_year)
                else:
                    decade = None
                
                if decade and decade >= 1950 and decade <= 2020:  # Reasonable range check
                    search_query = """
                        SELECT * FROM bimmuda_songs 
                        WHERE year >= ? AND year < ?
                        ORDER BY year, title
                    """
                    results = conn.execute(search_query, (decade, decade + 10)).fetchall()
                    decade_found = True
        
        
        # If no decade found, try exact year match
        if not decade_found:
            try:
                year_int = int(query)
                search_query = """
                    SELECT * FROM bimmuda_songs 
                    WHERE year = ? 
                    ORDER BY title
                """
                results = conn.execute(search_query, (year_int,)).fetchall()
            except ValueError:
                results = []
    
    else:  # search_type == 'all'
        search_query = """
            SELECT * FROM bimmuda_songs 
            WHERE title LIKE ? OR artist LIKE ? OR genre_broad_1 LIKE ? 
            ORDER BY year, title
        """
        results = conn.execute(search_query, (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    # Convert to list of dicts for template
    search_results = [dict(row) for row in results]
    
    return render_template_string(SEARCH_TEMPLATE, query=query, results=search_results, search_type=search_type)

@app.route('/api/suggestions')
def get_suggestions():
    """Get autocomplete suggestions based on search type and query"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    
    if len(query) < 2:  # Only suggest after 2+ characters
        return {'suggestions': []}
    
    conn = get_db_connection()
    suggestions = []
    
    try:
        if search_type == 'title':
            # Get song titles that match
            results = conn.execute("""
                SELECT DISTINCT title FROM bimmuda_songs 
                WHERE title LIKE ? 
                ORDER BY title LIMIT 10
            """, (f'%{query}%',)).fetchall()
            suggestions = [row['title'] for row in results]
        
        elif search_type == 'artist':
            # Get artists that match
            results = conn.execute("""
                SELECT DISTINCT artist FROM bimmuda_songs 
                WHERE artist LIKE ? 
                ORDER BY artist LIMIT 10
            """, (f'%{query}%',)).fetchall()
            suggestions = [row['artist'] for row in results]
        
        elif search_type == 'key':
            # Get musical keys that match
            results = conn.execute("""
                SELECT DISTINCT tonic_1, mode_1 FROM bimmuda_songs 
                WHERE (tonic_1 LIKE ? OR mode_1 LIKE ?) 
                AND tonic_1 != 'N/A' AND mode_1 != 'N/A'
                ORDER BY tonic_1, mode_1 LIMIT 10
            """, (f'%{query}%', f'%{query}%')).fetchall()
            suggestions = []
            for row in results:
                if row['tonic_1'] and row['mode_1']:
                    key_name = f"{row['tonic_1']} {row['mode_1']}"
                    if key_name not in suggestions:
                        suggestions.append(key_name)
                elif row['tonic_1']:
                    if row['tonic_1'] not in suggestions:
                        suggestions.append(row['tonic_1'])
        
        elif search_type == 'year':
            query_lower = query.lower().strip()
            
            # Handle different year/decade input patterns
            if query.isdigit():
                # For numeric input, suggest years and decades
                results = conn.execute("""
                    SELECT DISTINCT year FROM bimmuda_songs 
                    WHERE CAST(year AS TEXT) LIKE ? 
                    ORDER BY year LIMIT 8
                """, (f'%{query}%',)).fetchall()
                suggestions = [str(row['year']) for row in results]
                
                # Suggest decade variations
                if len(query) == 4:  # Full year like 1965
                    decade = (int(query) // 10) * 10
                    decade_short = str(decade)[2:4]  # "70" for 1970
                    suggestions.extend([f"{decade}s", f"{decade}'s", f"{decade_short}s"])
                elif len(query) == 3:  # Like "196"
                    decade = int(query + "0")
                    decade_short = str(decade)[2:4]
                    suggestions.extend([f"{decade}s", f"{decade}'s", f"{decade_short}s"])
                elif len(query) == 2 and int(query) >= 50:  # Like "70"
                    decade = 1900 + int(query)
                    suggestions.extend([f"{decade}s", f"{decade}'s", f"{query}s", f"{query}'s"])
                elif len(query) == 2 and int(query) < 50:  # Like "10" for 2010s
                    decade = 2000 + int(query)
                    suggestions.extend([f"{decade}s", f"{decade}'s", f"{query}s", f"{query}'s"])
            
            elif query_lower.startswith(('fif', 'six', 'sev', 'eig', 'nin')):
                # Handle written decades
                decade_words = ['fifties', 'sixties', 'seventies', 'eighties', 'nineties']
                suggestions = [word for word in decade_words if word.startswith(query_lower)]
                
            else:
                # Handle partial decade formats
                base_query = query_lower.replace("'s", "").replace("'s", "").replace("s", "")
                if base_query.isdigit():
                    if len(base_query) == 2:
                        decade = 1900 + int(base_query) if int(base_query) >= 50 else 2000 + int(base_query)
                        suggestions = [f"{decade}s", f"{decade}'s", f"{base_query}s", f"{base_query}'s"]
                    elif len(base_query) == 4:
                        decade = int(base_query)
                        decade_short = str(decade)[2:4]
                        suggestions = [f"{decade}s", f"{decade}'s", f"{decade_short}s", f"{decade_short}'s"]
        
        else:  # search_type == 'all'
            # Mix of titles and artists
            title_results = conn.execute("""
                SELECT DISTINCT title FROM bimmuda_songs 
                WHERE title LIKE ? 
                ORDER BY title LIMIT 5
            """, (f'%{query}%',)).fetchall()
            
            artist_results = conn.execute("""
                SELECT DISTINCT artist FROM bimmuda_songs 
                WHERE artist LIKE ? 
                ORDER BY artist LIMIT 5
            """, (f'%{query}%',)).fetchall()
            
            suggestions = [row['title'] for row in title_results] + [row['artist'] for row in artist_results]
    
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        suggestions = []
    
    finally:
        conn.close()
    
    return jsonify({'suggestions': suggestions[:10]})  # Limit to 10 suggestions


# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BiMMuDa Guitar Chords - Decades of Music</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 40px; }
        .header h1 { font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; margin: 10px 0; opacity: 0.9; }
        .decades-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .decade-card { 
            background: white; border-radius: 15px; padding: 25px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease; text-decoration: none; color: inherit;
        }
        .decade-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.2); }
        .decade-title { font-size: 2em; font-weight: bold; margin: 0 0 10px 0; color: #4a5568; }
        .decade-info { color: #718096; margin: 5px 0; }
        .song-count { font-size: 1.5em; font-weight: bold; color: #2d3748; }
        .stats { text-align: center; margin: 40px 0; color: white; }
        .stat-item { display: inline-block; margin: 0 20px; }
        .stat-number { font-size: 2em; font-weight: bold; display: block; }
        .autocomplete-container { position: relative; }
        .autocomplete-suggestions { 
            position: absolute; top: 100%; left: 0; right: 0; background: white; 
            border-radius: 10px; box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
            max-height: 200px; overflow-y: auto; z-index: 1000; display: none;
        }
        .autocomplete-item { 
            padding: 12px 16px; cursor: pointer; border-bottom: 1px solid #e2e8f0; 
            color: #2d3748; font-size: 14px;
        }
        .autocomplete-item:hover, .autocomplete-item.selected { background: #f7fafc; }
        .autocomplete-item:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎸 BiMMuDa Guitar Chords</h1>
            <p>Explore decades of music with rich metadata and guitar chords</p>
            
            <!-- Search Box -->
            <div style="margin: 30px 0; max-width: 600px; margin-left: auto; margin-right: auto;">
                <form action="/search" method="GET" style="display: flex; gap: 10px; align-items: flex-start; flex-wrap: wrap; justify-content: center;">
                    <div class="autocomplete-container" style="flex: 1; min-width: 300px;">
                        <input type="text" name="q" id="home-search-input" placeholder="Search songs, artists, keys, or years..." 
                               style="width: 100%; padding: 15px 20px; border: none; border-radius: 25px; font-size: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); box-sizing: border-box;">
                        <div id="home-autocomplete-suggestions" class="autocomplete-suggestions"></div>
                    </div>
                    <select name="type" id="home-search-type" style="padding: 15px; border: none; border-radius: 20px; background: white; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <option value="all">All Fields</option>
                        <option value="title">Song Title</option>
                        <option value="artist">Artist</option>
                        <option value="key">Musical Key</option>
                        <option value="year">Year/Decade</option>
                    </select>
                    <button type="submit" style="padding: 15px 25px; background: #667eea; color: white; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        🔍 Search
                    </button>
                </form>
                <div style="margin-top: 15px; text-align: center; color: rgba(255,255,255,0.8); font-size: 0.9em;">
                    <p style="margin: 5px 0;">Try: "Goodnight Irene", "Beatles", "C major", "1965"</p>
                    <p style="margin: 5px 0; font-size: 0.85em;">Decades: "1960s", "60s", "1960's", "sixties"</p>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <span class="stat-number">381</span>
                <span>Unique Songs</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">70+</span>
                <span>Years of Music</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">1,545</span>
                <span>MIDI Files</span>
            </div>
        </div>
        
        <div class="decades-grid">
            {% for decade in decades %}
            <a href="/decade/{{ decade.decade }}" class="decade-card">
                <div class="decade-title">{{ decade.decade }}s</div>
                <div class="decade-info">{{ decade.start_year }} - {{ decade.end_year }}</div>
                <div class="song-count">{{ decade.song_count }} songs</div>
                <div class="decade-info">
                    Rich metadata • MIDI files • Audio links
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
    
    <script>
        // Autocomplete functionality for home page
        const searchInput = document.getElementById('home-search-input');
        const searchType = document.getElementById('home-search-type');
        const suggestionsContainer = document.getElementById('home-autocomplete-suggestions');
        let currentSuggestions = [];
        let selectedIndex = -1;
        
        function showSuggestions(suggestions) {
            suggestionsContainer.innerHTML = '';
            if (suggestions.length === 0) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            suggestions.forEach((suggestion, index) => {
                const item = document.createElement('div');
                item.className = 'autocomplete-item';
                item.textContent = suggestion;
                item.onclick = () => selectSuggestion(suggestion);
                suggestionsContainer.appendChild(item);
            });
            
            suggestionsContainer.style.display = 'block';
            currentSuggestions = suggestions;
            selectedIndex = -1;
        }
        
        function selectSuggestion(suggestion) {
            searchInput.value = suggestion;
            suggestionsContainer.style.display = 'none';
            searchInput.focus();
        }
        
        function updateSelection() {
            const items = suggestionsContainer.querySelectorAll('.autocomplete-item');
            items.forEach((item, index) => {
                item.classList.toggle('selected', index === selectedIndex);
            });
        }
        
        // Debounce function to limit API calls
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        // Fetch suggestions from API
        async function fetchSuggestions(query, type) {
            if (query.length < 2) {
                showSuggestions([]);
                return;
            }
            
            try {
                const response = await fetch(`/api/suggestions?q=${encodeURIComponent(query)}&type=${type}`);
                const data = await response.json();
                showSuggestions(data.suggestions || []);
            } catch (error) {
                console.error('Error fetching suggestions:', error);
                showSuggestions([]);
            }
        }
        
        const debouncedFetchSuggestions = debounce(fetchSuggestions, 300);
        
        // Event listeners
        searchInput.addEventListener('input', (e) => {
            debouncedFetchSuggestions(e.target.value, searchType.value);
        });
        
        searchType.addEventListener('change', () => {
            if (searchInput.value.length >= 2) {
                fetchSuggestions(searchInput.value, searchType.value);
            }
        });
        
        searchInput.addEventListener('keydown', (e) => {
            if (currentSuggestions.length === 0) return;
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, currentSuggestions.length - 1);
                updateSelection();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection();
            } else if (e.key === 'Enter' && selectedIndex >= 0) {
                e.preventDefault();
                selectSuggestion(currentSuggestions[selectedIndex]);
            } else if (e.key === 'Escape') {
                suggestionsContainer.style.display = 'none';
                selectedIndex = -1;
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

DECADE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ decade }}s - BiMMuDa Guitar Chords</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .back-link { color: white; text-decoration: none; font-size: 1.1em; margin-bottom: 20px; display: inline-block; }
        .back-link:hover { text-decoration: underline; }
        .stats-bar { 
            background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 20px 0; 
            display: flex; justify-content: space-around; color: white; backdrop-filter: blur(10px);
        }
        .stat { text-align: center; }
        .stat-number { font-size: 1.5em; font-weight: bold; display: block; }
        .songs-list { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .song-item { 
            padding: 20px; border-bottom: 1px solid #e2e8f0; transition: background-color 0.2s; 
            cursor: pointer; display: flex; justify-content: space-between; align-items: center;
        }
        .song-item:hover { background-color: #f7fafc; }
        .song-item:last-child { border-bottom: none; }
        .song-main { flex-grow: 1; }
        .song-title { font-size: 1.2em; font-weight: bold; color: #2d3748; margin: 0 0 5px 0; }
        .song-artist { color: #4a5568; font-size: 1.1em; margin: 0 0 8px 0; }
        .song-meta { color: #718096; font-size: 0.9em; }
        .song-badges { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
        .badge { 
            padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 500;
            background: #e2e8f0; color: #4a5568;
        }
        .badge.midi { background: #c6f6d5; color: #22543d; }
        .badge.audio { background: #bee3f8; color: #2a4365; }
        .badge.chords { background: #c6f6d5; color: #22543d; }
        .year-badge { background: #667eea; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Decades</a>
        
        <div class="header">
            <h1>🎵 {{ decade }}s Music</h1>
            <p>{{ stats.total_songs }} unique songs from the {{ decade }}s</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat">
                <span class="stat-number">{{ stats.total_songs }}</span>
                <span>Total Songs</span>
            </div>
            <div class="stat">
                <span class="stat-number">{{ stats.chord_count }}</span>
                <span>With Chords</span>
            </div>
            <div class="stat">
                <span class="stat-number">{{ stats.midi_count }}</span>
                <span>MIDI Files</span>
            </div>
            <div class="stat">
                <span class="stat-number">{{ stats.lyrics_count }}</span>
                <span>With Lyrics</span>
            </div>
        </div>
        
        <div class="songs-list">
            {% for song in songs %}
            <div class="song-item" onclick="location.href='/song/{{ song.id }}'">
                <div class="song-main">
                    <div class="song-title">{{ song.title }}</div>
                    <div class="song-artist">{{ song.artist }}</div>
                    <div class="song-meta">
                        {% if song.key_signature and song.key_signature != 'N/A' %}
                            Key: {{ song.key_signature }}{% if song.mode and song.mode != 'N/A' %} {{ song.mode }}{% endif %} |
                        {% endif %}
                        {% if song.tempo and song.tempo != 'N/A' %}
                            {{ song.tempo }} BPM |
                        {% endif %}
                        {% if song.genre and song.genre != 'N/A' %}
                            {{ song.genre }}
                        {% endif %}
                    </div>
                </div>
                <div class="song-badges">
                    <span class="badge year-badge">{{ song.year }}</span>
                    {% if song.chord_progression %}
                        <span class="badge chords">🎸 Chords</span>
                    {% endif %}
                    {% if song.has_midi_files %}
                        <span class="badge midi">MIDI</span>
                    {% endif %}
                    {% if song.has_lyrics %}
                        <span class="badge lyrics">🎤 Lyrics</span>
                    {% endif %}
                    {% if song.audio_link and song.audio_link != 'N/A' %}
                        <span class="badge audio">Audio</span>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

SONG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ song.title }} - {{ song.artist }}</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .back-link { color: white; text-decoration: none; font-size: 1.1em; margin-bottom: 20px; display: inline-block; }
        .back-link:hover { text-decoration: underline; }
        .song-card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .song-header { text-align: center; margin-bottom: 30px; }
        .song-title { font-size: 2.5em; font-weight: bold; color: #2d3748; margin: 0 0 10px 0; }
        .song-artist { font-size: 1.5em; color: #4a5568; margin: 0 0 20px 0; }
        .year-badge { 
            display: inline-block; background: #667eea; color: white; padding: 8px 16px; 
            border-radius: 20px; font-weight: bold; font-size: 1.1em;
        }
        .metadata-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .metadata-item { text-align: center; padding: 15px; background: #f7fafc; border-radius: 10px; }
        .metadata-label { font-size: 0.9em; color: #718096; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
        .metadata-value { font-size: 1.2em; color: #2d3748; font-weight: 500; }
        .features { display: flex; justify-content: center; gap: 15px; margin: 30px 0; flex-wrap: wrap; }
        .feature { 
            padding: 10px 20px; border-radius: 25px; font-weight: bold; 
            background: #e2e8f0; color: #4a5568;
        }
        .feature.available { background: #c6f6d5; color: #22543d; }
        .audio-link { 
            display: block; text-align: center; background: #1db954; color: white; 
            padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; 
            margin: 20px 0; transition: background 0.3s;
        }
        .audio-link:hover { background: #1aa54a; }
        .chord-section { margin: 30px 0; padding: 20px; background: #f0f4f8; border-radius: 10px; text-align: center; }
        .chord-buttons button:hover { background: #5a67d8; }
        .chord-diagram-display { border: 2px solid #e2e8f0; border-radius: 10px; padding: 20px; margin: 10px 0; }
    </style>
    
    <!-- JavaScript Libraries for Chord Diagrams -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/svguitar@1.8.3/dist/svguitar.umd.js"></script>
    <script src="https://tardate.github.io/jtab/javascripts/jtab.js"></script>
    <script src="https://github.com/tardate/jTab/raw/master/lib/raphael-min.js"></script>
</head>
<body>
    <div class="container">
        <a href="/decade/{{ (song.year//10)*10 }}" class="back-link">← Back to {{ (song.year//10)*10 }}s</a>
        
        <div class="song-card">
            <div class="song-header">
                <h1 class="song-title">{{ song.title }}</h1>
                <h2 class="song-artist">{{ song.artist }}</h2>
                <span class="year-badge">{{ song.year }}</span>
            </div>
            
            <div class="metadata-grid">
                {% if song.genre_broad_1 and song.genre_broad_1 != 'N/A' %}
                <div class="metadata-item">
                    <div class="metadata-label">Genre</div>
                    <div class="metadata-value">{{ song.genre_broad_1 }}</div>
                </div>
                {% endif %}
                
                {% if song.bpm_1 and song.bpm_1 != 'N/A' %}
                <div class="metadata-item">
                    <div class="metadata-label">Tempo</div>
                    <div class="metadata-value">{{ song.bpm_1 }} BPM</div>
                </div>
                {% endif %}
                
                {% if song.tonic_1 and song.tonic_1 != 'N/A' %}
                <div class="metadata-item">
                    <div class="metadata-label">Key</div>
                    <div class="metadata-value">
                        {{ song.tonic_1 }}{% if song.mode_1 and song.mode_1 != 'N/A' %} {{ song.mode_1 }}{% endif %}
                    </div>
                </div>
                {% endif %}
                
                {% if song.time_signature_1 and song.time_signature_1 != 'N/A' %}
                <div class="metadata-item">
                    <div class="metadata-label">Time Signature</div>
                    <div class="metadata-value">{{ song.time_signature_1 }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="features">
                <span class="feature {% if song.has_midi_files %}available{% endif %}">
                    🎹 MIDI Files {% if song.has_midi_files %}Available{% else %}N/A{% endif %}
                </span>
                <span class="feature {% if song.has_lyrics %}available{% endif %}">
                    🎤 Lyrics {% if song.has_lyrics %}Available{% else %}N/A{% endif %}
                </span>
            </div>
            
            {% if song.audio_link and song.audio_link != 'N/A' %}
            <a href="{{ song.audio_link }}" target="_blank" class="audio-link">
                🎧 Listen on Spotify
            </a>
            {% endif %}
            
            
            <div class="chord-section">
                <h3>🎸 Guitar Chords</h3>
                {% if song.chord_progression %}
                    <div style="background: #c6f6d5; padding: 15px; border-radius: 10px; margin: 15px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #22543d;">Chord Progression:</h4>
                        <div style="font-size: 1.3em; font-weight: bold; color: #22543d; font-family: monospace;">
                            {{ song.chord_progression }}
                        </div>
                    </div>
                    
                    <!-- Interactive Chord Diagrams -->
                    <div class="chord-diagrams" style="margin: 20px 0;">
                        <h4 style="margin: 10px 0; color: #2d3748;">Interactive Chord Diagrams:</h4>
                        <div id="chord-display" style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">
                            <div class="chord-buttons" style="margin-bottom: 20px; text-align: center;">
                                {% for chord in song.chord_progression.split(' - ') %}
                                <button onclick="showChord('{{ chord.strip() }}')" 
                                        style="margin: 5px; padding: 10px 15px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
                                    {{ chord.strip() }}
                                </button>
                                {% endfor %}
                            </div>
                            <div id="chord-diagram-container" style="text-align: center; min-height: 200px;">
                                <p style="color: #718096;">Click a chord button above to see its diagram</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- jTab Display (Alternative) -->
                    <div style="margin: 20px 0;">
                        <h4 style="margin: 10px 0; color: #2d3748;">Chord Chart (jTab):</h4>
                        <div class="jtab" style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">
                            {{ song.chord_progression.replace(' - ', ' ') }}
                        </div>
                    </div>
                    
                    <!-- Tablature Section -->
                    {% if tablature and not tablature.error %}
                    <div style="margin: 20px 0;">
                        <h4 style="margin: 10px 0; color: #2d3748;">🎼 Guitar Tablature:</h4>
                        <div style="background: #f7fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">
                            <div style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div>
                                    <strong>Difficulty:</strong> 
                                    <span style="color: {% if tablature.difficulty == 'Beginner' %}#22543d{% else %}#d69e2e{% endif %}; font-weight: bold;">{{ tablature.difficulty }}</span>
                                </div>
                                <div>
                                    <strong>Strumming:</strong> <span style="font-family: monospace; color: #4a5568;">{{ tablature.strumming_pattern }}</span>
                                </div>
                            </div>
                            
                            <div style="background: white; padding: 25px; border-radius: 10px; overflow-x: auto; border: 1px solid #d2d6dc; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <pre style="font-family: 'Courier New', 'Monaco', 'Consolas', 'Liberation Mono', monospace; font-size: 15px; line-height: 1.6; margin: 0; color: #1a202c; letter-spacing: 0.3px; background-color: #f7fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #4299e1; overflow-x: auto;">{% for line in tablature.tab_notation %}{{ line }}
{% endfor %}</pre>
                            </div>
                            
                            {% if tablature.missing_chords %}
                            <div style="margin-top: 15px; padding: 10px; background: #fed7d7; border-radius: 5px; color: #742a2a; font-size: 0.9em;">
                                <strong>Note:</strong> Tablature not available for: {{ tablature.missing_chords|join(', ') }}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% elif tablature and tablature.error %}
                    <div style="margin: 20px 0;">
                        <h4 style="margin: 10px 0; color: #2d3748;">🎼 Guitar Tablature:</h4>
                        <div style="background: #fed7d7; padding: 15px; border-radius: 10px; color: #742a2a;">
                            <strong>{{ tablature.error }}</strong><br>
                            <em>Available for basic open chords like: C, Am, F, G, D, Em, A, E</em>
                        </div>
                    </div>
                    {% endif %}
                    
                    <p><em>✅ Chord progression extracted from BiMMuDa MIDI data</em></p>
                {% else %}
                    <div style="background: #fed7d7; padding: 15px; border-radius: 10px; margin: 15px 0;">
                        <p style="margin: 0; color: #742a2a;">⚠️ No chord progression available for this song</p>
                    </div>
                    {% if song.has_midi_files %}
                        <p><em>MIDI data is available but chord extraction failed.</em></p>
                    {% else %}
                        <p><em>No MIDI files available for chord analysis.</em></p>
                    {% endif %}
                {% endif %}
            </div>
            
            <!-- Lyrics Section -->
            {% if lyrics %}
            <div class="lyrics-section" style="margin: 30px 0; padding: 25px; background: #f8fafc; border-radius: 15px; border-left: 5px solid #667eea;">
                <h3 style="margin: 0 0 20px 0; color: #2d3748; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">🎤</span>
                    Song Lyrics
                </h3>
                <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); line-height: 1.8;">
                    <pre style="font-family: 'Georgia', 'Times New Roman', serif; font-size: 16px; color: #2d3748; white-space: pre-wrap; margin: 0;">{{ lyrics }}</pre>
                </div>
                <div style="margin-top: 15px; text-align: center; font-size: 0.9em; color: #718096;">
                    <p style="margin: 0;">📁 Source: BiMMuDa Dataset • Educational/Research Use</p>
                </div>
            </div>
            {% elif song.has_lyrics %}
            <div class="lyrics-section" style="margin: 30px 0; padding: 25px; background: #fff5f5; border-radius: 15px; border-left: 5px solid #f56565;">
                <h3 style="margin: 0 0 15px 0; color: #2d3748; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">🎤</span>
                    Song Lyrics
                </h3>
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; color: #742a2a;">
                    <p style="margin: 0;">⚠️ Lyrics file not found in BiMMuDa dataset</p>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em;">Expected at: <code>{{ song.folder_path }}/{{ song.folder_path.split('/')[-2] }}_{{ song.folder_path.split('/')[-1].zfill(2) }}_lyrics.txt</code></p>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <!-- Chord Diagram JavaScript -->
    <script>
        // Chord Library (from our Python generator)
        const chordLibrary = {
            'C': {frets: ['x', '3', '2', '0', '1', '0'], fingers: ['', '3', '2', '', '1', ''], name: 'C Major'},
            'D': {frets: ['x', 'x', '0', '2', '3', '2'], fingers: ['', '', '', '1', '3', '2'], name: 'D Major'},
            'E': {frets: ['0', '2', '2', '1', '0', '0'], fingers: ['', '2', '3', '1', '', ''], name: 'E Major'},
            'F': {frets: ['1', '3', '3', '2', '1', '1'], fingers: ['1', '3', '4', '2', '1', '1'], name: 'F Major', barre: 1},
            'G': {frets: ['3', '2', '0', '0', '3', '3'], fingers: ['3', '2', '', '', '4', '4'], name: 'G Major'},
            'A': {frets: ['x', '0', '2', '2', '2', '0'], fingers: ['', '', '2', '3', '4', ''], name: 'A Major'},
            'B': {frets: ['x', '2', '4', '4', '4', '2'], fingers: ['', '1', '2', '3', '4', '1'], name: 'B Major', barre: 2},
            'Am': {frets: ['x', '0', '2', '2', '1', '0'], fingers: ['', '', '2', '3', '1', ''], name: 'A Minor'},
            'Bm': {frets: ['x', '2', '4', '4', '3', '2'], fingers: ['', '1', '3', '4', '2', '1'], name: 'B Minor', barre: 2},
            'Cm': {frets: ['x', '3', '5', '5', '4', '3'], fingers: ['', '1', '3', '4', '2', '1'], name: 'C Minor', barre: 3},
            'Dm': {frets: ['x', 'x', '0', '2', '3', '1'], fingers: ['', '', '', '2', '3', '1'], name: 'D Minor'},
            'Em': {frets: ['0', '2', '2', '0', '0', '0'], fingers: ['', '2', '3', '', '', ''], name: 'E Minor'},
            'Fm': {frets: ['1', '3', '3', '1', '1', '1'], fingers: ['1', '3', '4', '1', '1', '1'], name: 'F Minor', barre: 1},
            'Gm': {frets: ['3', '5', '5', '3', '3', '3'], fingers: ['1', '3', '4', '1', '1', '1'], name: 'G Minor', barre: 3},
            'C7': {frets: ['x', '3', '2', '3', '1', '0'], fingers: ['', '3', '2', '4', '1', ''], name: 'C Dominant 7'},
            'D7': {frets: ['x', 'x', '0', '2', '1', '2'], fingers: ['', '', '', '3', '1', '2'], name: 'D Dominant 7'},
            'E7': {frets: ['0', '2', '0', '1', '0', '0'], fingers: ['', '2', '', '1', '', ''], name: 'E Dominant 7'},
            'G7': {frets: ['3', '2', '0', '0', '0', '1'], fingers: ['3', '2', '', '', '', '1'], name: 'G Dominant 7'},
            'A7': {frets: ['x', '0', '2', '0', '2', '0'], fingers: ['', '', '2', '', '3', ''], name: 'A Dominant 7'},
            'B7': {frets: ['x', '2', '1', '2', '0', '2'], fingers: ['', '2', '1', '3', '', '4'], name: 'B Dominant 7'},
            // Sharp/Flat chords
            'A#': {frets: ['x', '1', '3', '3', '3', '1'], fingers: ['', '1', '2', '3', '4', '1'], name: 'A# Major', barre: 1},
            'Bb': {frets: ['x', '1', '3', '3', '3', '1'], fingers: ['', '1', '2', '3', '4', '1'], name: 'Bb Major', barre: 1},
            'C#': {frets: ['x', '4', '6', '6', '6', '4'], fingers: ['', '1', '2', '3', '4', '1'], name: 'C# Major', barre: 4},
            'F#': {frets: ['2', '4', '4', '3', '2', '2'], fingers: ['1', '3', '4', '2', '1', '1'], name: 'F# Major', barre: 2},
            'F#m': {frets: ['2', '4', '4', '2', '2', '2'], fingers: ['1', '3', '4', '1', '1', '1'], name: 'F# Minor', barre: 2},
            'G#': {frets: ['4', '6', '6', '5', '4', '4'], fingers: ['1', '3', '4', '2', '1', '1'], name: 'G# Major', barre: 4},
            'D#m': {frets: ['x', 'x', '1', '3', '4', '2'], fingers: ['', '', '1', '3', '4', '2'], name: 'D# Minor'},
            'Cmaj7': {frets: ['x', '3', '2', '0', '0', '0'], fingers: ['', '3', '2', '', '', ''], name: 'C Major 7'},
            'Dmaj7': {frets: ['x', 'x', '0', '2', '2', '2'], fingers: ['', '', '', '1', '1', '1'], name: 'D Major 7'},
            'Emaj7': {frets: ['0', '2', '1', '1', '0', '0'], fingers: ['', '2', '1', '1', '', ''], name: 'E Major 7'},
            'Gmaj7': {frets: ['3', 'x', '0', '0', '0', '2'], fingers: ['3', '', '', '', '', '2'], name: 'G Major 7'},
            'Amaj7': {frets: ['x', '0', '2', '1', '2', '0'], fingers: ['', '', '2', '1', '3', ''], name: 'A Major 7'},
            'Bmaj7': {frets: ['x', '2', '4', '3', '4', '2'], fingers: ['', '1', '3', '2', '4', '1'], name: 'B Major 7'}
        };

        function showChord(chordName) {
            const chord = chordLibrary[chordName];
            const container = document.getElementById('chord-diagram-container');
            
            if (!chord) {
                container.innerHTML = '<p style="color: #e53e3e;">Chord diagram not available for ' + chordName + '</p>';
                return;
            }
            
            // Clear previous content
            container.innerHTML = '';
            
            // Create traditional fretboard diagram using SVG
            const fretboardSvg = createFretboardDiagram(chord);
            
            const diagramHtml = `
                <div style="margin: 20px auto; max-width: 400px;">
                    <h5 style="margin: 10px 0; color: #2d3748; text-align: center;">${chord.name}</h5>
                    <div class="chord-fretboard" style="text-align: center; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e2e8f0;">
                        ${fretboardSvg}
                        <div style="margin-top: 15px; font-size: 0.9em; color: #4a5568; line-height: 1.4;">
                            <strong>Fingering:</strong> ${chord.fingers.map(f => f || '–').join(' - ')}<br>
                            ${chord.barre ? `<em style="color: #667eea;">Barre chord at fret ${chord.barre}</em><br>` : ''}
                            <small style="color: #718096;">○ = open string, ✗ = muted string</small>
                        </div>
                    </div>
                </div>
            `;
            
            container.innerHTML = diagramHtml;
        }
        
        function createFretboardDiagram(chord) {
            const strings = ['E', 'A', 'D', 'G', 'B', 'e'];
            const frets = chord.frets;
            const fingers = chord.fingers;
            
            // Determine fret range to show
            const numericFrets = frets.filter(f => f !== 'x' && f !== '0').map(Number);
            const minFret = Math.max(1, Math.min(...numericFrets) - 1);
            const maxFret = Math.min(5, Math.max(...numericFrets, minFret + 4));
            const showFrets = maxFret - minFret + 1;
            
            const width = 280;
            const height = 200;
            const stringSpacing = width / 7; // 6 strings + margins
            const fretSpacing = (height - 60) / (showFrets + 1);
            const startX = stringSpacing;
            const startY = 40;
            
            let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">`;
            
            // Draw strings (vertical lines)
            for (let i = 0; i < 6; i++) {
                const x = startX + i * stringSpacing;
                svg += `<line x1="${x}" y1="${startY}" x2="${x}" y2="${startY + showFrets * fretSpacing}" stroke="#666" stroke-width="2"/>`;
                
                // String labels at top
                svg += `<text x="${x}" y="${startY - 10}" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#4a5568">${strings[i]}</text>`;
                
                // Open/muted indicators above strings
                if (frets[i] === '0') {
                    svg += `<circle cx="${x}" cy="${startY - 25}" r="6" fill="none" stroke="#38a169" stroke-width="2"/>`;
                } else if (frets[i] === 'x') {
                    svg += `<text x="${x}" y="${startY - 20}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#e53e3e">✗</text>`;
                }
            }
            
            // Draw frets (horizontal lines)
            for (let f = 0; f <= showFrets; f++) {
                const y = startY + f * fretSpacing;
                const strokeWidth = (f === 0 && minFret === 1) ? 4 : 1; // Nut is thicker
                svg += `<line x1="${startX}" y1="${y}" x2="${startX + 5 * stringSpacing}" y2="${y}" stroke="#333" stroke-width="${strokeWidth}"/>`;
                
                // Fret numbers on the side
                if (f > 0) {
                    const fretNum = minFret + f - 1;
                    svg += `<text x="${startX - 15}" y="${y - fretSpacing/2 + 5}" text-anchor="middle" font-family="Arial" font-size="11" fill="#666">${fretNum}</text>`;
                }
            }
            
            // Draw finger positions
            for (let i = 0; i < 6; i++) {
                const fret = frets[i];
                if (fret !== 'x' && fret !== '0') {
                    const fretNum = parseInt(fret);
                    if (fretNum >= minFret && fretNum <= maxFret) {
                        const x = startX + i * stringSpacing;
                        const y = startY + (fretNum - minFret + 0.5) * fretSpacing;
                        const finger = fingers[i];
                        
                        // Draw finger dot
                        svg += `<circle cx="${x}" cy="${y}" r="8" fill="#2d3748"/>`;
                        
                        // Draw finger number if available
                        if (finger && finger !== '') {
                            svg += `<text x="${x}" y="${y + 4}" text-anchor="middle" font-family="Arial" font-size="11" font-weight="bold" fill="white">${finger}</text>`;
                        }
                    }
                }
            }
            
            // Draw barre if present
            if (chord.barre && chord.barre >= minFret && chord.barre <= maxFret) {
                const barreY = startY + (chord.barre - minFret + 0.5) * fretSpacing;
                const barreStrings = [];
                
                // Find strings involved in barre
                for (let i = 0; i < 6; i++) {
                    if (frets[i] == chord.barre.toString()) {
                        barreStrings.push(i);
                    }
                }
                
                if (barreStrings.length > 1) {
                    const startStringX = startX + Math.min(...barreStrings) * stringSpacing;
                    const endStringX = startX + Math.max(...barreStrings) * stringSpacing;
                    svg += `<rect x="${startStringX - 6}" y="${barreY - 3}" width="${endStringX - startStringX + 12}" height="6" rx="3" fill="#2d3748"/>`;
                }
            }
            
            svg += '</svg>';
            return svg;
        }
        
        
        
        
        
        
        
        // Initialize jTab if available
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof jtab !== 'undefined') {
                jtab.renderImplicit();
            }
        });
    </script>
</body>
</html>
"""

SEARCH_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if query %}Search: {{ query }}{% else %}Search{% endif %} - BiMMuDa Guitar Chords</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .back-link { color: white; text-decoration: none; font-size: 1.1em; margin-bottom: 20px; display: inline-block; }
        .back-link:hover { text-decoration: underline; }
        .search-header { text-align: center; color: white; margin-bottom: 30px; }
        .search-form { 
            background: rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; margin: 20px 0; 
            backdrop-filter: blur(10px); display: flex; gap: 15px; align-items: center; flex-wrap: wrap;
        }
        .search-form input[type="text"] { 
            flex: 1; min-width: 300px; padding: 12px 18px; border: none; border-radius: 20px; 
            font-size: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .search-form select { 
            padding: 12px 15px; border: none; border-radius: 15px; background: white; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .search-form button { 
            padding: 12px 20px; background: #38a169; color: white; border: none; 
            border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .search-form button:hover { background: #2f855a; }
        .results-summary { 
            text-align: center; color: white; margin: 20px 0; font-size: 1.1em;
        }
        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin: 30px 0; }
        .result-card { 
            background: white; border-radius: 15px; padding: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease; cursor: pointer;
        }
        .result-card:hover { transform: translateY(-3px); box-shadow: 0 12px 35px rgba(0,0,0,0.15); }
        .result-title { font-size: 1.3em; font-weight: bold; color: #2d3748; margin: 0 0 5px 0; }
        .result-artist { font-size: 1.1em; color: #4a5568; margin: 0 0 10px 0; }
        .result-meta { color: #718096; font-size: 0.9em; margin: 5px 0; }
        .result-badges { display: flex; gap: 8px; margin: 10px 0; flex-wrap: wrap; }
        .badge { 
            padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 500;
            background: #e2e8f0; color: #4a5568;
        }
        .badge.year { background: #667eea; color: white; font-weight: bold; }
        .badge.chords { background: #c6f6d5; color: #22543d; }
        .badge.midi { background: #bee3f8; color: #2a4365; }
        .badge.lyrics { background: #f0e68c; color: #744210; }
        .no-results { 
            text-align: center; background: white; padding: 40px; border-radius: 15px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 30px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Home</a>
        
        <div class="search-header">
            <h1>🔍 Search BiMMuDa Songs</h1>
            {% if query %}
                <p>Search results for: <strong>"{{ query }}"</strong></p>
            {% endif %}
        </div>
        
        <!-- Search Form -->
        <div class="search-form">
            <div class="autocomplete-container" style="flex: 1; min-width: 300px;">
                <input type="text" name="q" value="{{ query }}" placeholder="Search songs, artists, keys, or years..." id="search-input" style="width: 100%; box-sizing: border-box;">
                <div id="search-autocomplete-suggestions" class="autocomplete-suggestions"></div>
            </div>
            <select name="type" id="search-type">
                <option value="all" {% if search_type == 'all' %}selected{% endif %}>All Fields</option>
                <option value="title" {% if search_type == 'title' %}selected{% endif %}>Song Title</option>
                <option value="artist" {% if search_type == 'artist' %}selected{% endif %}>Artist</option>
                <option value="key" {% if search_type == 'key' %}selected{% endif %}>Musical Key</option>
                <option value="year" {% if search_type == 'year' %}selected{% endif %}>Year/Decade</option>
            </select>
            <button onclick="performSearch()">🔍 Search</button>
        </div>
        
        {% if query %}
        <div class="results-summary">
            <p>Found <strong>{{ results|length }}</strong> song{{ 's' if results|length != 1 else '' }}</p>
        </div>
        {% endif %}
        
        {% if results %}
        <div class="results-grid">
            {% for song in results %}
            <div class="result-card" onclick="location.href='/song/{{ song.id }}'">
                <div class="result-title">{{ song.title }}</div>
                <div class="result-artist">{{ song.artist }}</div>
                <div class="result-meta">
                    {% if song.tonic_1 and song.tonic_1 != 'N/A' %}
                        Key: {{ song.tonic_1 }}{% if song.mode_1 and song.mode_1 != 'N/A' %} {{ song.mode_1 }}{% endif %} |
                    {% endif %}
                    {% if song.bpm_1 and song.bpm_1 != 'N/A' %}
                        {{ song.bpm_1 }} BPM |
                    {% endif %}
                    {% if song.genre_broad_1 and song.genre_broad_1 != 'N/A' %}
                        {{ song.genre_broad_1 }}
                    {% endif %}
                </div>
                <div class="result-badges">
                    <span class="badge year">{{ song.year }}</span>
                    {% if song.chord_progression %}
                        <span class="badge chords">🎸 Chords</span>
                    {% endif %}
                    {% if song.has_midi_files %}
                        <span class="badge midi">🎹 MIDI</span>
                    {% endif %}
                    {% if song.has_lyrics %}
                        <span class="badge lyrics">🎤 Lyrics</span>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="no-results">
            <h3 style="color: #4a5568; margin: 0 0 15px 0;">No Results Found</h3>
            <p style="color: #718096; margin: 0;">Try searching for:</p>
            <ul style="color: #718096; text-align: left; display: inline-block; margin: 10px 0;">
                <li>Song titles: "Goodnight Irene", "Hey Jude"</li>
                <li>Artists: "Beatles", "Lead Belly", "Joni Mitchell"</li>
                <li>Musical keys: "C", "Am", "F major"</li>
                <li>Years: "1965", "1970"</li>
                <li>Decades: "1960s", "60s", "1960's", "sixties"</li>
            </ul>
        </div>
        {% endif %}
    </div>
    
    <script>
        function performSearch() {
            const query = document.getElementById('search-input').value;
            const type = document.getElementById('search-type').value;
            if (query.trim()) {
                window.location.href = `/search?q=${encodeURIComponent(query)}&type=${type}`;
            }
        }
        
        // Autocomplete functionality for search page
        const searchInput = document.getElementById('search-input');
        const searchType = document.getElementById('search-type');
        const suggestionsContainer = document.getElementById('search-autocomplete-suggestions');
        let currentSuggestions = [];
        let selectedIndex = -1;
        
        function showSuggestions(suggestions) {
            suggestionsContainer.innerHTML = '';
            if (suggestions.length === 0) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            suggestions.forEach((suggestion, index) => {
                const item = document.createElement('div');
                item.className = 'autocomplete-item';
                item.textContent = suggestion;
                item.onclick = () => selectSuggestion(suggestion);
                suggestionsContainer.appendChild(item);
            });
            
            suggestionsContainer.style.display = 'block';
            currentSuggestions = suggestions;
            selectedIndex = -1;
        }
        
        function selectSuggestion(suggestion) {
            searchInput.value = suggestion;
            suggestionsContainer.style.display = 'none';
            searchInput.focus();
        }
        
        function updateSelection() {
            const items = suggestionsContainer.querySelectorAll('.autocomplete-item');
            items.forEach((item, index) => {
                item.classList.toggle('selected', index === selectedIndex);
            });
        }
        
        // Debounce function to limit API calls
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        // Fetch suggestions from API
        async function fetchSuggestions(query, type) {
            if (query.length < 2) {
                showSuggestions([]);
                return;
            }
            
            try {
                const response = await fetch(`/api/suggestions?q=${encodeURIComponent(query)}&type=${type}`);
                const data = await response.json();
                showSuggestions(data.suggestions || []);
            } catch (error) {
                console.error('Error fetching suggestions:', error);
                showSuggestions([]);
            }
        }
        
        const debouncedFetchSuggestions = debounce(fetchSuggestions, 300);
        
        // Event listeners
        searchInput.addEventListener('input', (e) => {
            debouncedFetchSuggestions(e.target.value, searchType.value);
        });
        
        searchType.addEventListener('change', () => {
            if (searchInput.value.length >= 2) {
                fetchSuggestions(searchInput.value, searchType.value);
            }
        });
        
        searchInput.addEventListener('keydown', (e) => {
            if (currentSuggestions.length === 0) return;
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, currentSuggestions.length - 1);
                updateSelection();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection();
            } else if (e.key === 'Enter' && selectedIndex >= 0) {
                e.preventDefault();
                selectSuggestion(currentSuggestions[selectedIndex]);
                return false; // Prevent form submission
            } else if (e.key === 'Escape') {
                suggestionsContainer.style.display = 'none';
                selectedIndex = -1;
            }
        });
        
        // Allow Enter key to submit search (only when not selecting suggestion)
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && selectedIndex === -1) {
                performSearch();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("Starting BiMMuDa Guitar Chord Website")
    print(f"Database: {BIMMUDA_DB}")
    print("Website: http://localhost:5000")
    print("Featuring 381 unique songs with rich metadata!")
    
    app.run(debug=True, port=5000)
