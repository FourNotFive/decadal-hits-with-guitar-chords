from flask import Flask, render_template, jsonify, request
import sqlite3
import json

app = Flask(__name__)

# Database path
DB_PATH = '../data/databases/music_database.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Main page with decade selection"""
    conn = get_db_connection()
    
    # Get decade summary data
    try:
        decades = conn.execute("""
            SELECT decade_name, total_songs, estimated_songs_with_chords, 
                   chord_percentage, description 
            FROM decade_summary
            ORDER BY decade
        """).fetchall()
        
        decades_data = [dict(decade) for decade in decades]
    except:
        # Fallback data if decade_summary table doesn't exist
        decades_data = [
            {'decade_name': '1960s', 'total_songs': 50, 'estimated_songs_with_chords': 7, 'chord_percentage': 15, 'description': 'British Invasion & Folk Rock Revolution'},
            {'decade_name': '1970s', 'total_songs': 50, 'estimated_songs_with_chords': 10, 'chord_percentage': 20, 'description': 'Arena Rock, Disco & Progressive Masterpieces'},
            {'decade_name': '1980s', 'total_songs': 50, 'estimated_songs_with_chords': 6, 'chord_percentage': 12, 'description': 'Synth-Pop, Hair Metal & New Wave Innovation'},
            {'decade_name': '1990s', 'total_songs': 50, 'estimated_songs_with_chords': 4, 'chord_percentage': 8, 'description': 'Grunge, Alternative & Hip-Hop Explosion'},
            {'decade_name': '2000s', 'total_songs': 50, 'estimated_songs_with_chords': 2, 'chord_percentage': 5, 'description': 'Pop-Punk, Indie Rock & Digital Revolution'},
            {'decade_name': '2010s', 'total_songs': 50, 'estimated_songs_with_chords': 1, 'chord_percentage': 3, 'description': 'EDM, Streaming Era & Genre Fusion'},
        ]
    
    conn.close()
    
    # Create the HTML template inline
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChordDeck - Guitar Chords Through the Decades</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298, #1e3c72);
            min-height: 100vh;
            color: white;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            background: rgba(0, 0, 0, 0.3);
            padding: 40px 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }

        .logo {
            font-size: 3.5em;
            font-weight: bold;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .tagline {
            font-size: 1.3em;
            opacity: 0.9;
            margin-bottom: 20px;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 0.9em;
            opacity: 0.8;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 1.8em;
            font-weight: bold;
            color: #ffd700;
        }

        .decades-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .decade-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px 25px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }

        .decade-card:hover {
            transform: translateY(-8px);
            border-color: #ffd700;
            box-shadow: 0 15px 30px rgba(255, 215, 0, 0.3);
        }

        .decade-title {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #ffd700;
        }

        .decade-description {
            font-size: 1em;
            opacity: 0.9;
            margin-bottom: 20px;
            line-height: 1.4;
        }

        .decade-stats {
            display: flex;
            justify-content: space-around;
            font-size: 0.9em;
            opacity: 0.8;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            padding-top: 15px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
        }

        .footer {
            text-align: center;
            padding: 40px;
            opacity: 0.7;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div style="font-size: 2em; margin-bottom: 10px;">🎸</div>
            <div class="logo">ChordDeck</div>
            <div class="tagline">Your Billboard Songs Now Have Guitar Chords!</div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">32K+</div>
                    <div>Billboard Songs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">890</div>
                    <div>Chord Progressions</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">400</div>
                    <div>Top Hits Ready</div>
                </div>
            </div>
        </header>

        <div class="decades-grid" id="decadesGrid">
            <!-- JavaScript will populate this -->
        </div>

        <div id="loadingMessage" class="loading" style="display: none;">
            🎵 Loading songs... 🎵
        </div>
    </div>

    <footer class="footer">
        <p>🎸 Built with real Billboard Hot 100 data and McGill chord progressions</p>
        <p>Click any decade above to see the top hits!</p>
    </footer>

    <script>
        // Decades data from Python
        const decades = """ + json.dumps(decades_data) + """;

        function loadDecades() {
            const grid = document.getElementById('decadesGrid');
            
            decades.forEach(decade => {
                const card = document.createElement('div');
                card.className = 'decade-card';
                card.onclick = () => loadDecadeSongs(decade.decade_name);
                
                card.innerHTML = `
                    <div class="decade-title">${decade.decade_name}</div>
                    <div class="decade-description">${decade.description}</div>
                    <div class="decade-stats">
                        <span>🎵 ${decade.total_songs} Songs</span>
                        <span>🎸 ~${decade.estimated_songs_with_chords} w/ Chords</span>
                        <span>📊 ${decade.chord_percentage}%</span>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }

        function loadDecadeSongs(decadeName) {
            document.getElementById('loadingMessage').style.display = 'block';
            document.getElementById('decadesGrid').style.opacity = '0.5';
            
            // Make API call to get songs for this decade
            fetch(`/api/decade/${decadeName}`)
                .then(response => response.json())
                .then(data => {
                    showDecadeSongs(decadeName, data.songs);
                })
                .catch(error => {
                    console.error('Error loading songs:', error);
                    alert('Error loading songs. Please try again.');
                })
                .finally(() => {
                    document.getElementById('loadingMessage').style.display = 'none';
                    document.getElementById('decadesGrid').style.opacity = '1';
                });
        }

        function showDecadeSongs(decadeName, songs) {
            const grid = document.getElementById('decadesGrid');
            
            let songsHtml = `
                <div style="grid-column: 1 / -1; text-align: center; margin-bottom: 30px;">
                    <h2 style="font-size: 2.5em; color: #ffd700; margin-bottom: 10px;">
                        🎵 Top Songs of the ${decadeName}
                    </h2>
                    <button onclick="goBackToDecades()" style="padding: 10px 20px; background: #ffd700; color: #000; border: none; border-radius: 20px; cursor: pointer; font-weight: bold;">
                        ← Back to Decades
                    </button>
                </div>
            `;
            
            songs.forEach((song, index) => {
                songsHtml += `
                    <div class="decade-card" style="text-align: left;">
                        <div style="font-size: 1.1em; font-weight: bold; color: #ffd700; margin-bottom: 8px;">
                            ${index + 1}. ${song.song_title}
                        </div>
                        <div style="opacity: 0.9; margin-bottom: 10px;">
                            by ${song.artist}
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.7; margin-bottom: 15px;">
                            Peak: #${song.peak_position} • ${song.weeks_on_chart} weeks • Year: ${song.year}
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-size: 0.9em;">
                            ${song.has_chords ? '🎸 Chord data available!' : '🔄 Chord data coming soon...'}
                        </div>
                    </div>
                `;
            });
            
            grid.innerHTML = songsHtml;
        }

        function goBackToDecades() {
            // Clear the grid and reload decades
            const grid = document.getElementById('decadesGrid');
            grid.innerHTML = '';
            loadDecades();
        }

        // Load decades on page load
        loadDecades();
    </script>
</body>
</html>
    """
    
    return html_template

@app.route('/api/decade/<decade_name>')
def get_decade_songs(decade_name):
    """API endpoint to get songs for a specific decade"""
    conn = get_db_connection()
    
    table_name = f"top_songs_{decade_name.lower()}"
    
    try:
        songs = conn.execute(f"""
            SELECT song_title, artist, peak_position, weeks_on_chart, 
                   year, popularity_score, has_chords
            FROM {table_name}
            ORDER BY popularity_score DESC
            LIMIT 20
        """).fetchall()
        
        songs_data = [dict(song) for song in songs]
        
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        songs_data = []
    
    conn.close()
    
    return jsonify({
        'decade': decade_name,
        'songs': songs_data
    })

if __name__ == '__main__':
    print("🎸 Starting ChordDeck Web Server...")
    print("🌐 Open your browser to: http://localhost:5000")
    print("🎵 Press Ctrl+C to stop the server")
    app.run(debug=True, port=5000)
