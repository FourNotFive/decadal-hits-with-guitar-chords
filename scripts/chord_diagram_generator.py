#!/usr/bin/env python3
"""
Guitar Chord Diagram Generator
Creates chord diagrams for our extracted chord progressions
"""

import sqlite3
import json
from collections import defaultdict

class ChordDiagramGenerator:
    def __init__(self, db_path='../data/databases/billboard_data.db'):
        self.db_path = db_path
        
        # Common guitar chord fingerings (string positions: Low E, A, D, G, B, High E)
        # Format: [fret positions for each string, 'x' for muted, '0' for open]
        self.chord_library = {
            # Major chords
            'C': {'frets': ['x', '3', '2', '0', '1', '0'], 'fingers': ['', '3', '2', '', '1', ''], 'name': 'C Major'},
            'D': {'frets': ['x', 'x', '0', '2', '3', '2'], 'fingers': ['', '', '', '1', '3', '2'], 'name': 'D Major'},
            'E': {'frets': ['0', '2', '2', '1', '0', '0'], 'fingers': ['', '2', '3', '1', '', ''], 'name': 'E Major'},
            'F': {'frets': ['1', '3', '3', '2', '1', '1'], 'fingers': ['1', '3', '4', '2', '1', '1'], 'name': 'F Major', 'barre': 1},
            'G': {'frets': ['3', '2', '0', '0', '3', '3'], 'fingers': ['3', '2', '', '', '4', '4'], 'name': 'G Major'},
            'A': {'frets': ['x', '0', '2', '2', '2', '0'], 'fingers': ['', '', '2', '3', '4', ''], 'name': 'A Major'},
            'B': {'frets': ['x', '2', '4', '4', '4', '2'], 'fingers': ['', '1', '2', '3', '4', '1'], 'name': 'B Major', 'barre': 2},
            
            # Minor chords
            'Am': {'frets': ['x', '0', '2', '2', '1', '0'], 'fingers': ['', '', '2', '3', '1', ''], 'name': 'A Minor'},
            'Bm': {'frets': ['x', '2', '4', '4', '3', '2'], 'fingers': ['', '1', '3', '4', '2', '1'], 'name': 'B Minor', 'barre': 2},
            'Cm': {'frets': ['x', '3', '5', '5', '4', '3'], 'fingers': ['', '1', '3', '4', '2', '1'], 'name': 'C Minor', 'barre': 3},
            'Dm': {'frets': ['x', 'x', '0', '2', '3', '1'], 'fingers': ['', '', '', '2', '3', '1'], 'name': 'D Minor'},
            'Em': {'frets': ['0', '2', '2', '0', '0', '0'], 'fingers': ['', '2', '3', '', '', ''], 'name': 'E Minor'},
            'Fm': {'frets': ['1', '3', '3', '1', '1', '1'], 'fingers': ['1', '3', '4', '1', '1', '1'], 'name': 'F Minor', 'barre': 1},
            'Gm': {'frets': ['3', '5', '5', '3', '3', '3'], 'fingers': ['1', '3', '4', '1', '1', '1'], 'name': 'G Minor', 'barre': 3},
            
            # Seventh chords
            'C7': {'frets': ['x', '3', '2', '3', '1', '0'], 'fingers': ['', '3', '2', '4', '1', ''], 'name': 'C Dominant 7'},
            'D7': {'frets': ['x', 'x', '0', '2', '1', '2'], 'fingers': ['', '', '', '3', '1', '2'], 'name': 'D Dominant 7'},
            'E7': {'frets': ['0', '2', '0', '1', '0', '0'], 'fingers': ['', '2', '', '1', '', ''], 'name': 'E Dominant 7'},
            'G7': {'frets': ['3', '2', '0', '0', '0', '1'], 'fingers': ['3', '2', '', '', '', '1'], 'name': 'G Dominant 7'},
            'A7': {'frets': ['x', '0', '2', '0', '2', '0'], 'fingers': ['', '', '2', '', '3', ''], 'name': 'A Dominant 7'},
            'B7': {'frets': ['x', '2', '1', '2', '0', '2'], 'fingers': ['', '2', '1', '3', '', '4'], 'name': 'B Dominant 7'},
            
            # Major 7th chords
            'Cmaj7': {'frets': ['x', '3', '2', '0', '0', '0'], 'fingers': ['', '3', '2', '', '', ''], 'name': 'C Major 7'},
            'Dmaj7': {'frets': ['x', 'x', '0', '2', '2', '2'], 'fingers': ['', '', '', '1', '1', '1'], 'name': 'D Major 7'},
            'Emaj7': {'frets': ['0', '2', '1', '1', '0', '0'], 'fingers': ['', '2', '1', '1', '', ''], 'name': 'E Major 7'},
            'Fmaj7': {'frets': ['x', 'x', '3', '2', '1', '0'], 'fingers': ['', '', '3', '2', '1', ''], 'name': 'F Major 7'},
            'Gmaj7': {'frets': ['3', 'x', '0', '0', '0', '2'], 'fingers': ['3', '', '', '', '', '2'], 'name': 'G Major 7'},
            'Amaj7': {'frets': ['x', '0', '2', '1', '2', '0'], 'fingers': ['', '', '2', '1', '3', ''], 'name': 'A Major 7'},
            'Bmaj7': {'frets': ['x', '2', '4', '3', '4', '2'], 'fingers': ['', '1', '3', '2', '4', '1'], 'name': 'B Major 7'},
            
            # Minor 7th chords  
            'Am7': {'frets': ['x', '0', '2', '0', '1', '0'], 'fingers': ['', '', '2', '', '1', ''], 'name': 'A Minor 7'},
            'Bm7': {'frets': ['x', '2', '0', '2', '0', '2'], 'fingers': ['', '2', '', '3', '', '4'], 'name': 'B Minor 7'},
            'Cm7': {'frets': ['x', '3', '1', '3', '1', '1'], 'fingers': ['', '3', '1', '4', '1', '1'], 'name': 'C Minor 7'},
            'Dm7': {'frets': ['x', 'x', '0', '2', '1', '1'], 'fingers': ['', '', '', '2', '1', '1'], 'name': 'D Minor 7'},
            'Em7': {'frets': ['0', '2', '0', '0', '0', '0'], 'fingers': ['', '2', '', '', '', ''], 'name': 'E Minor 7'},
            'Fm7': {'frets': ['1', '3', '1', '1', '1', '1'], 'fingers': ['1', '3', '1', '1', '1', '1'], 'name': 'F Minor 7', 'barre': 1},
            'Gm7': {'frets': ['3', '5', '3', '3', '3', '3'], 'fingers': ['1', '3', '1', '1', '1', '1'], 'name': 'G Minor 7', 'barre': 3},
            
            # Sharp/Flat chords (using most common fingerings)
            'A#': {'frets': ['x', '1', '3', '3', '3', '1'], 'fingers': ['', '1', '2', '3', '4', '1'], 'name': 'A# Major', 'barre': 1},
            'Bb': {'frets': ['x', '1', '3', '3', '3', '1'], 'fingers': ['', '1', '2', '3', '4', '1'], 'name': 'Bb Major', 'barre': 1},
            'A#m': {'frets': ['x', '1', '3', '3', '2', '1'], 'fingers': ['', '1', '3', '4', '2', '1'], 'name': 'A# Minor', 'barre': 1},
            'Bbm': {'frets': ['x', '1', '3', '3', '2', '1'], 'fingers': ['', '1', '3', '4', '2', '1'], 'name': 'Bb Minor', 'barre': 1},
            'A#7': {'frets': ['x', '1', '3', '1', '3', '1'], 'fingers': ['', '1', '3', '1', '4', '1'], 'name': 'A# Dominant 7', 'barre': 1},
            'Bb7': {'frets': ['x', '1', '3', '1', '3', '1'], 'fingers': ['', '1', '3', '1', '4', '1'], 'name': 'Bb Dominant 7', 'barre': 1},
            'A#maj7': {'frets': ['x', '1', '3', '2', '3', '1'], 'fingers': ['', '1', '3', '2', '4', '1'], 'name': 'A# Major 7', 'barre': 1},
            'Bbmaj7': {'frets': ['x', '1', '3', '2', '3', '1'], 'fingers': ['', '1', '3', '2', '4', '1'], 'name': 'Bb Major 7', 'barre': 1},
            
            'C#': {'frets': ['x', '4', '6', '6', '6', '4'], 'fingers': ['', '1', '2', '3', '4', '1'], 'name': 'C# Major', 'barre': 4},
            'Db': {'frets': ['x', '4', '6', '6', '6', '4'], 'fingers': ['', '1', '2', '3', '4', '1'], 'name': 'Db Major', 'barre': 4},
            'C#m': {'frets': ['x', '4', '6', '6', '5', '4'], 'fingers': ['', '1', '3', '4', '2', '1'], 'name': 'C# Minor', 'barre': 4},
            'Dbm': {'frets': ['x', '4', '6', '6', '5', '4'], 'fingers': ['', '1', '3', '4', '2', '1'], 'name': 'Db Minor', 'barre': 4},
            'C#7': {'frets': ['x', '4', '6', '4', '6', '4'], 'fingers': ['', '1', '3', '1', '4', '1'], 'name': 'C# Dominant 7', 'barre': 4},
            'Db7': {'frets': ['x', '4', '6', '4', '6', '4'], 'fingers': ['', '1', '3', '1', '4', '1'], 'name': 'Db Dominant 7', 'barre': 4},
            'C#maj7': {'frets': ['x', '4', '6', '5', '6', '4'], 'fingers': ['', '1', '3', '2', '4', '1'], 'name': 'C# Major 7', 'barre': 4},
            'Dbmaj7': {'frets': ['x', '4', '6', '5', '6', '4'], 'fingers': ['', '1', '3', '2', '4', '1'], 'name': 'Db Major 7', 'barre': 4},
            
            'D#': {'frets': ['x', 'x', '1', '3', '4', '3'], 'fingers': ['', '', '1', '2', '4', '3'], 'name': 'D# Major'},
            'Eb': {'frets': ['x', 'x', '1', '3', '4', '3'], 'fingers': ['', '', '1', '2', '4', '3'], 'name': 'Eb Major'},
            'D#m': {'frets': ['x', 'x', '1', '3', '4', '2'], 'fingers': ['', '', '1', '3', '4', '2'], 'name': 'D# Minor'},
            'Ebm': {'frets': ['x', 'x', '1', '3', '4', '2'], 'fingers': ['', '', '1', '3', '4', '2'], 'name': 'Eb Minor'},
            'D#7': {'frets': ['x', 'x', '1', '3', '2', '3'], 'fingers': ['', '', '1', '4', '2', '3'], 'name': 'D# Dominant 7'},
            'Eb7': {'frets': ['x', 'x', '1', '3', '2', '3'], 'fingers': ['', '', '1', '4', '2', '3'], 'name': 'Eb Dominant 7'},
            'D#maj7': {'frets': ['x', 'x', '1', '3', '3', '3'], 'fingers': ['', '', '1', '2', '3', '4'], 'name': 'D# Major 7'},
            'Ebmaj7': {'frets': ['x', 'x', '1', '3', '3', '3'], 'fingers': ['', '', '1', '2', '3', '4'], 'name': 'Eb Major 7'},
            
            'F#': {'frets': ['2', '4', '4', '3', '2', '2'], 'fingers': ['1', '3', '4', '2', '1', '1'], 'name': 'F# Major', 'barre': 2},
            'Gb': {'frets': ['2', '4', '4', '3', '2', '2'], 'fingers': ['1', '3', '4', '2', '1', '1'], 'name': 'Gb Major', 'barre': 2},
            'F#m': {'frets': ['2', '4', '4', '2', '2', '2'], 'fingers': ['1', '3', '4', '1', '1', '1'], 'name': 'F# Minor', 'barre': 2},
            'Gbm': {'frets': ['2', '4', '4', '2', '2', '2'], 'fingers': ['1', '3', '4', '1', '1', '1'], 'name': 'Gb Minor', 'barre': 2},
            'F#7': {'frets': ['2', '4', '2', '3', '2', '2'], 'fingers': ['1', '4', '1', '3', '1', '1'], 'name': 'F# Dominant 7', 'barre': 2},
            'Gb7': {'frets': ['2', '4', '2', '3', '2', '2'], 'fingers': ['1', '4', '1', '3', '1', '1'], 'name': 'Gb Dominant 7', 'barre': 2},
            'F#maj7': {'frets': ['2', '4', '3', '3', '2', '2'], 'fingers': ['1', '4', '2', '3', '1', '1'], 'name': 'F# Major 7', 'barre': 2},
            'Gbmaj7': {'frets': ['2', '4', '3', '3', '2', '2'], 'fingers': ['1', '4', '2', '3', '1', '1'], 'name': 'Gb Major 7', 'barre': 2},
            
            'G#': {'frets': ['4', '6', '6', '5', '4', '4'], 'fingers': ['1', '3', '4', '2', '1', '1'], 'name': 'G# Major', 'barre': 4},
            'Ab': {'frets': ['4', '6', '6', '5', '4', '4'], 'fingers': ['1', '3', '4', '2', '1', '1'], 'name': 'Ab Major', 'barre': 4},
            'G#m': {'frets': ['4', '6', '6', '4', '4', '4'], 'fingers': ['1', '3', '4', '1', '1', '1'], 'name': 'G# Minor', 'barre': 4},
            'Abm': {'frets': ['4', '6', '6', '4', '4', '4'], 'fingers': ['1', '3', '4', '1', '1', '1'], 'name': 'Ab Minor', 'barre': 4},
            'G#7': {'frets': ['4', '6', '4', '5', '4', '4'], 'fingers': ['1', '4', '1', '3', '1', '1'], 'name': 'G# Dominant 7', 'barre': 4},
            'Ab7': {'frets': ['4', '6', '4', '5', '4', '4'], 'fingers': ['1', '4', '1', '3', '1', '1'], 'name': 'Ab Dominant 7', 'barre': 4},
            'G#maj7': {'frets': ['4', '6', '5', '5', '4', '4'], 'fingers': ['1', '4', '2', '3', '1', '1'], 'name': 'G# Major 7', 'barre': 4},
            'Abmaj7': {'frets': ['4', '6', '5', '5', '4', '4'], 'fingers': ['1', '4', '2', '3', '1', '1'], 'name': 'Ab Major 7', 'barre': 4},
        }
        
        # Alternative chord names and enharmonic equivalents
        self.chord_aliases = {
            'A#': 'Bb', 'A#m': 'Bbm', 'A#7': 'Bb7', 'A#maj7': 'Bbmaj7',
            'C#': 'Db', 'C#m': 'Dbm', 'C#7': 'Db7', 'C#maj7': 'Dbmaj7',
            'D#': 'Eb', 'D#m': 'Ebm', 'D#7': 'Eb7', 'D#maj7': 'Ebmaj7',
            'F#': 'Gb', 'F#m': 'Gbm', 'F#7': 'Gb7', 'F#maj7': 'Gbmaj7',
            'G#': 'Ab', 'G#m': 'Abm', 'G#7': 'Ab7', 'G#maj7': 'Abmaj7',
        }
        
    def normalize_chord_name(self, chord):
        """Normalize chord name to match our library"""
        # Remove whitespace and handle common variations
        chord = chord.strip()
        
        # Handle enharmonic equivalents
        if chord in self.chord_aliases:
            chord = self.chord_aliases[chord]
        
        # Try exact match first
        if chord in self.chord_library:
            return chord
        
        # Try with added 'maj' for major chords
        if chord + 'maj' in self.chord_library:
            return chord + 'maj'
        
        # Try removing 'maj' for major chords
        if chord.endswith('maj') and chord[:-3] in self.chord_library:
            return chord[:-3]
        
        return None
    
    def get_chord_data(self, chord_name):
        """Get chord diagram data for a chord name"""
        normalized = self.normalize_chord_name(chord_name)
        if normalized and normalized in self.chord_library:
            return self.chord_library[normalized]
        return None
    
    def analyze_chord_coverage(self):
        """Analyze how many of our extracted chords we can create diagrams for"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT chord_progression FROM bimmuda_songs 
            WHERE chord_progression IS NOT NULL
        """)
        
        all_chord_progressions = cursor.fetchall()
        conn.close()
        
        # Count all unique chords
        all_chords = set()
        found_chords = set()
        missing_chords = set()
        
        for progression in all_chord_progressions:
            chords_in_progression = progression[0].split(' - ')
            for chord in chords_in_progression:
                chord = chord.strip()
                all_chords.add(chord)
                
                if self.get_chord_data(chord):
                    found_chords.add(chord)
                else:
                    missing_chords.add(chord)
        
        coverage_percent = len(found_chords) / len(all_chords) * 100 if all_chords else 0
        
        return {
            'total_unique_chords': len(all_chords),
            'found_chords': len(found_chords),
            'missing_chords': len(missing_chords),
            'coverage_percent': coverage_percent,
            'found_chord_list': sorted(found_chords),
            'missing_chord_list': sorted(missing_chords)
        }
    
    def generate_chord_diagrams_for_song(self, chord_progression):
        """Generate chord diagram data for a song's chord progression"""
        if not chord_progression:
            return []
        
        chords_in_progression = chord_progression.split(' - ')
        chord_diagrams = []
        
        for chord in chords_in_progression:
            chord = chord.strip()
            chord_data = self.get_chord_data(chord)
            
            if chord_data:
                chord_diagrams.append({
                    'chord_name': chord,
                    'diagram_data': chord_data
                })
            else:
                # Create placeholder for missing chords
                chord_diagrams.append({
                    'chord_name': chord,
                    'diagram_data': None,
                    'missing': True
                })
        
        return chord_diagrams
    
    def export_chord_library_json(self, filename='chord_library.json'):
        """Export chord library as JSON for JavaScript use"""
        with open(filename, 'w') as f:
            json.dump(self.chord_library, f, indent=2)
        return filename
    
    def create_jstab_notation(self, chord_progression):
        """Create jTab notation for a chord progression"""
        if not chord_progression:
            return ""
        
        chords = chord_progression.split(' - ')
        jtab_chords = []
        
        for chord in chords:
            chord = chord.strip()
            # jTab can handle most standard chord notations directly
            # Convert our notation to jTab-compatible format
            jtab_chord = chord.replace('#', '#').replace('b', 'b')  # Ensure proper formatting
            jtab_chords.append(jtab_chord)
        
        # Return jTab notation (space-separated chords)
        return ' '.join(jtab_chords)
    
    def generate_sample_songs_with_diagrams(self, limit=10):
        """Generate sample songs with chord diagrams"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, year, chord_progression, genre_broad_1
            FROM bimmuda_songs 
            WHERE chord_progression IS NOT NULL 
            AND genre_broad_1 IN ('Rock', 'Pop', 'Country', 'Folk')
            ORDER BY year DESC
            LIMIT ?
        """, (limit,))
        
        songs = cursor.fetchall()
        conn.close()
        
        songs_with_diagrams = []
        for title, artist, year, chords, genre in songs:
            chord_diagrams = self.generate_chord_diagrams_for_song(chords)
            jtab_notation = self.create_jstab_notation(chords)
            
            songs_with_diagrams.append({
                'title': title,
                'artist': artist,
                'year': year,
                'genre': genre,
                'original_chords': chords,
                'chord_diagrams': chord_diagrams,
                'jtab_notation': jtab_notation,
                'diagram_coverage': sum(1 for cd in chord_diagrams if not cd.get('missing', False)) / len(chord_diagrams) * 100 if chord_diagrams else 0
            })
        
        return songs_with_diagrams

def main():
    print("Guitar Chord Diagram Generator")
    print("=" * 40)
    
    generator = ChordDiagramGenerator()
    
    # Analyze coverage
    print("1. ANALYZING CHORD COVERAGE")
    print("-" * 30)
    coverage = generator.analyze_chord_coverage()
    
    print(f"Total unique chords in database: {coverage['total_unique_chords']}")
    print(f"Chords we can create diagrams for: {coverage['found_chords']}")
    print(f"Missing chord diagrams: {coverage['missing_chords']}")
    print(f"Coverage: {coverage['coverage_percent']:.1f}%")
    
    print(f"\nChords we can diagram:")
    print(", ".join(coverage['found_chord_list'][:20]))  # Show first 20
    if len(coverage['found_chord_list']) > 20:
        print(f"... and {len(coverage['found_chord_list']) - 20} more")
    
    print(f"\nMissing chord diagrams:")
    print(", ".join(coverage['missing_chord_list'][:10]))  # Show first 10 missing
    if len(coverage['missing_chord_list']) > 10:
        print(f"... and {len(coverage['missing_chord_list']) - 10} more")
    
    # Generate sample songs
    print(f"\n\n2. SAMPLE SONGS WITH CHORD DIAGRAMS")
    print("-" * 40)
    samples = generator.generate_sample_songs_with_diagrams(limit=5)
    
    for song in samples:
        print(f"\n{song['title']} by {song['artist']} ({song['year']})")
        print(f"Genre: {song['genre']}")
        print(f"Original chords: {song['original_chords']}")
        print(f"jTab notation: {song['jtab_notation']}")
        print(f"Diagram coverage: {song['diagram_coverage']:.1f}%")
        
        print("Available diagrams:")
        for chord_diagram in song['chord_diagrams']:
            if not chord_diagram.get('missing', False):
                chord_name = chord_diagram['chord_name']
                print(f"  {chord_name}: {chord_diagram['diagram_data']['name']}")
            else:
                print(f"  {chord_diagram['chord_name']}: [MISSING DIAGRAM]")
    
    # Export chord library
    filename = generator.export_chord_library_json()
    print(f"\n\n3. CHORD LIBRARY EXPORTED")
    print("-" * 30)
    print(f"Chord library exported to: {filename}")
    print("This can be used with JavaScript chord diagram libraries")
    
    print(f"\n\n4. INTEGRATION RECOMMENDATIONS")
    print("-" * 35)
    print("Best integration approach:")
    print("1. Use jTab library for easy integration (handles chord names directly)")
    print("2. Use SVGuitar library for custom chord diagrams")
    print("3. Fallback to chord names for missing diagrams")
    print(f"4. {coverage['coverage_percent']:.1f}% of chords have diagrams available")

if __name__ == "__main__":
    main()