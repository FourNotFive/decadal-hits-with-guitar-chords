#!/usr/bin/env python3
"""
Guitar Tablature Generator
Explores possibilities for generating guitar tabs from chord progressions
"""

import sqlite3
from collections import defaultdict

class TablatureGenerator:
    def __init__(self, db_path='../data/databases/billboard_data.db'):
        self.db_path = db_path
        
        # Basic chord-to-tablature patterns (simplified strumming patterns)
        self.chord_tab_patterns = {
            # Open position chords (easier to read)
            'C': {
                'frets': ['x', '3', '2', '0', '1', '0'],
                'tab': [
                    "E|---0---0---0---0---|",
                    "B|---1---1---1---1---|",
                    "G|---0---0---0---0---|", 
                    "D|---2---2---2---2---|",
                    "A|---3---3---3---3---|",
                    "E|---x---x---x---x---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            },
            'Am': {
                'frets': ['x', '0', '2', '2', '1', '0'],
                'tab': [
                    "E|---0---0---0---0---|",
                    "B|---1---1---1---1---|",
                    "G|---2---2---2---2---|",
                    "D|---2---2---2---2---|",
                    "A|---0---0---0---0---|",
                    "E|---x---x---x---x---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            },
            'F': {
                'frets': ['1', '3', '3', '2', '1', '1'],
                'tab': [
                    "E|---1---1---1---1---|",
                    "B|---1---1---1---1---|",
                    "G|---2---2---2---2---|",
                    "D|---3---3---3---3---|",
                    "A|---3---3---3---3---|",
                    "E|---1---1---1---1---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Intermediate',
                'barre': True
            },
            'G': {
                'frets': ['3', '2', '0', '0', '3', '3'],
                'tab': [
                    "E|---3---3---3---3---|",
                    "B|---3---3---3---3---|",
                    "G|---0---0---0---0---|",
                    "D|---0---0---0---0---|",
                    "A|---2---2---2---2---|",
                    "E|---3---3---3---3---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            },
            'D': {
                'frets': ['x', 'x', '0', '2', '3', '2'],
                'tab': [
                    "E|---2---2---2---2---|",
                    "B|---3---3---3---3---|",
                    "G|---2---2---2---2---|",
                    "D|---0---0---0---0---|",
                    "A|---x---x---x---x---|",
                    "E|---x---x---x---x---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            },
            'Em': {
                'frets': ['0', '2', '2', '0', '0', '0'],
                'tab': [
                    "E|---0---0---0---0---|",
                    "B|---0---0---0---0---|",
                    "G|---0---0---0---0---|",
                    "D|---2---2---2---2---|",
                    "A|---2---2---2---2---|",
                    "E|---0---0---0---0---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            },
            'A': {
                'frets': ['x', '0', '2', '2', '2', '0'],
                'tab': [
                    "E|---0---0---0---0---|",
                    "B|---2---2---2---2---|",
                    "G|---2---2---2---2---|",
                    "D|---2---2---2---2---|",
                    "A|---0---0---0---0---|",
                    "E|---x---x---x---x---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            },
            'E': {
                'frets': ['0', '2', '2', '1', '0', '0'],
                'tab': [
                    "E|---0---0---0---0---|",
                    "B|---0---0---0---0---|",
                    "G|---1---1---1---1---|",
                    "D|---2---2---2---2---|",
                    "A|---2---2---2---2---|",
                    "E|---0---0---0---0---|"
                ],
                'strumming': 'D-D-U-U-D-U',
                'difficulty': 'Beginner'
            }
        }
        
        # Common strumming patterns
        self.strumming_patterns = {
            'basic': 'D-D-U-U-D-U',
            'folk': 'D-D-U-D-U',
            'rock': 'D-X-U-X-D-U',
            'pop': 'D-D-U-U-D-U-D-U',
            'ballad': 'D---U-D-U'
        }
        
        # Time signatures and their typical patterns
        self.time_signatures = {
            '4/4': 4,
            '3/4': 3,
            '2/4': 2,
            '6/8': 6
        }
    
    def generate_chord_progression_tab(self, chord_progression, key='C', time_sig='4/4', style='basic'):
        """Generate a basic tablature for a chord progression"""
        if not chord_progression:
            return None
        
        chords = [chord.strip() for chord in chord_progression.split(' - ')]
        
        # Filter out chords we don't have tabs for
        available_chords = [chord for chord in chords if chord in self.chord_tab_patterns]
        
        if not available_chords:
            return {
                'error': 'No tablature available for these chords',
                'missing_chords': chords,
                'suggestion': 'Try songs with basic open chords like C, Am, F, G, D, Em, A, E'
            }
        
        # Generate tab
        tab_result = {
            'chords': available_chords,
            'time_signature': time_sig,
            'strumming_pattern': self.strumming_patterns.get(style, 'D-D-U-U-D-U'),
            'difficulty': self._assess_difficulty(available_chords),
            'tab_notation': self._create_tab_notation(available_chords, style),
            'notes': []
        }
        
        # Add helpful notes
        barre_chords = [chord for chord in available_chords 
                       if self.chord_tab_patterns[chord].get('barre', False)]
        if barre_chords:
            tab_result['notes'].append(f"Contains barre chords: {', '.join(barre_chords)}")
        
        if len(available_chords) < len(chords):
            missing = [chord for chord in chords if chord not in available_chords]
            tab_result['notes'].append(f"Missing tabs for: {', '.join(missing)}")
        
        return tab_result
    
    def _create_tab_notation(self, chords, style):
        """Create ASCII tablature notation"""
        if not chords:
            return []
        
        # Create header
        tab_lines = [
            "Guitar Tablature",
            "=" * 50,
            f"Chords: {' - '.join(chords)}",
            f"Strumming: {self.strumming_patterns.get(style, 'D-D-U-U-D-U')}",
            "",
            "Legend: D = Down strum, U = Up strum, X = Muted strum",
            ""
        ]
        
        # Add chord progression tab
        measures_per_line = 4
        
        for i in range(0, len(chords), measures_per_line):
            line_chords = chords[i:i + measures_per_line]
            
            # Create chord names line
            chord_line = ""
            for chord in line_chords:
                chord_line += f"{chord:>8s}        "
            tab_lines.append(chord_line)
            
            # Create tab lines for each string (E to e)
            string_names = ['E', 'A', 'D', 'G', 'B', 'e']
            
            for string_idx, string_name in enumerate(string_names):
                string_line = f"{string_name}|"
                
                for chord in line_chords:
                    if chord in self.chord_tab_patterns:
                        fret = self.chord_tab_patterns[chord]['frets'][string_idx]
                        # Simple strumming pattern (4 strums per chord)
                        if fret == 'x':
                            string_line += "x-x-x-x-|"
                        elif fret == '0':
                            string_line += "0-0-0-0-|"
                        else:
                            string_line += f"{fret}-{fret}-{fret}-{fret}-|"
                    else:
                        string_line += "----------|"
                
                tab_lines.append(string_line)
            
            tab_lines.append("")  # Empty line between measures
        
        return tab_lines
    
    def _assess_difficulty(self, chords):
        """Assess the difficulty level of a chord progression"""
        if not chords:
            return "Unknown"
        
        difficulty_scores = []
        for chord in chords:
            if chord in self.chord_tab_patterns:
                if self.chord_tab_patterns[chord]['difficulty'] == 'Beginner':
                    difficulty_scores.append(1)
                elif self.chord_tab_patterns[chord]['difficulty'] == 'Intermediate':
                    difficulty_scores.append(2)
                else:
                    difficulty_scores.append(3)
        
        if not difficulty_scores:
            return "Unknown"
        
        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
        
        if avg_difficulty <= 1.2:
            return "Beginner"
        elif avg_difficulty <= 2.0:
            return "Intermediate"
        else:
            return "Advanced"
    
    def analyze_tab_potential(self):
        """Analyze how many songs we could generate tabs for"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT chord_progression FROM bimmuda_songs 
            WHERE chord_progression IS NOT NULL
        """)
        
        progressions = cursor.fetchall()
        conn.close()
        
        tab_stats = {
            'total_songs': len(progressions),
            'can_create_tabs': 0,
            'partial_tabs': 0,
            'no_tabs': 0,
            'beginner_friendly': 0,
            'intermediate': 0,
            'advanced': 0,
            'common_chord_combinations': defaultdict(int)
        }
        
        for progression_tuple in progressions:
            progression = progression_tuple[0]
            chords = [chord.strip() for chord in progression.split(' - ')]
            
            available_chords = [chord for chord in chords if chord in self.chord_tab_patterns]
            
            if len(available_chords) == len(chords):
                tab_stats['can_create_tabs'] += 1
                difficulty = self._assess_difficulty(available_chords)
                tab_stats[difficulty.lower() + '_friendly'] += 1
                
                # Track common combinations
                if len(available_chords) <= 4:  # Track only simple progressions
                    combo = ' - '.join(sorted(available_chords))
                    tab_stats['common_chord_combinations'][combo] += 1
                    
            elif available_chords:
                tab_stats['partial_tabs'] += 1
            else:
                tab_stats['no_tabs'] += 1
        
        return tab_stats
    
    def generate_sample_tabs(self, limit=5):
        """Generate sample tablatures for beginner-friendly songs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, year, chord_progression, genre_broad_1
            FROM bimmuda_songs 
            WHERE chord_progression IS NOT NULL 
            AND genre_broad_1 IN ('Rock', 'Pop', 'Country', 'Folk')
            ORDER BY year DESC
            LIMIT ?
        """, (limit * 3,))  # Get more than needed to filter for beginner-friendly
        
        songs = cursor.fetchall()
        conn.close()
        
        sample_tabs = []
        
        for title, artist, year, chords, genre in songs:
            chord_list = [chord.strip() for chord in chords.split(' - ')]
            available_chords = [chord for chord in chord_list if chord in self.chord_tab_patterns]
            
            # Prioritize songs with all chords available and beginner-friendly
            if len(available_chords) >= 3 and len(available_chords) == len(chord_list):
                tab_result = self.generate_chord_progression_tab(chords, style='basic')
                
                if tab_result and not tab_result.get('error') and tab_result['difficulty'] in ['Beginner', 'Intermediate']:
                    sample_tabs.append({
                        'title': title,
                        'artist': artist,
                        'year': year,
                        'genre': genre,
                        'original_chords': chords,
                        'tab_data': tab_result
                    })
                    
                    if len(sample_tabs) >= limit:
                        break
        
        return sample_tabs
    
    def export_tab_as_text(self, song_title, artist, tab_data, filename=None):
        """Export a tablature as a text file"""
        if not filename:
            safe_title = "".join(c for c in song_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_tab.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Guitar Tablature: {song_title} by {artist}\n")
            f.write("=" * 60 + "\n\n")
            
            if 'tab_notation' in tab_data:
                for line in tab_data['tab_notation']:
                    f.write(line + "\n")
            
            f.write("\n\nAdditional Information:\n")
            f.write(f"Difficulty: {tab_data.get('difficulty', 'Unknown')}\n")
            f.write(f"Strumming Pattern: {tab_data.get('strumming_pattern', 'N/A')}\n")
            
            if tab_data.get('notes'):
                f.write("\nNotes:\n")
                for note in tab_data['notes']:
                    f.write(f"- {note}\n")
        
        return filename

def main():
    print("Guitar Tablature Generator")
    print("=" * 30)
    
    generator = TablatureGenerator()
    
    # Analyze potential for tab generation
    print("1. ANALYZING TABLATURE POTENTIAL")
    print("-" * 40)
    stats = generator.analyze_tab_potential()
    
    print(f"Total songs with chords: {stats['total_songs']}")
    print(f"Can create complete tabs: {stats['can_create_tabs']} ({stats['can_create_tabs']/stats['total_songs']*100:.1f}%)")
    print(f"Can create partial tabs: {stats['partial_tabs']} ({stats['partial_tabs']/stats['total_songs']*100:.1f}%)")
    print(f"No tabs possible: {stats['no_tabs']} ({stats['no_tabs']/stats['total_songs']*100:.1f}%)")
    
    print(f"\nDifficulty Distribution:")
    print(f"  Beginner-friendly: {stats['beginner_friendly']}")
    print(f"  Intermediate: {stats['intermediate']}")
    print(f"  Advanced: {stats['advanced']}")
    
    print(f"\nMost Common Chord Combinations:")
    for combo, count in sorted(stats['common_chord_combinations'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {combo}: {count} songs")
    
    # Generate sample tablatures
    print(f"\n\n2. SAMPLE TABLATURES")
    print("-" * 30)
    samples = generator.generate_sample_tabs(limit=3)
    
    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. {sample['title']} by {sample['artist']} ({sample['year']})")
        print(f"   Genre: {sample['genre']}")
        print(f"   Chords: {sample['original_chords']}")
        print(f"   Difficulty: {sample['tab_data']['difficulty']}")
        print(f"   Strumming: {sample['tab_data']['strumming_pattern']}")
        
        if sample['tab_data'].get('notes'):
            print(f"   Notes: {'; '.join(sample['tab_data']['notes'])}")
    
    # Export a sample tab
    if samples:
        first_sample = samples[0]
        filename = generator.export_tab_as_text(
            first_sample['title'],
            first_sample['artist'],
            first_sample['tab_data']
        )
        print(f"\n3. SAMPLE TAB EXPORTED")
        print("-" * 25)
        print(f"Exported sample tab to: {filename}")
    
    print(f"\n\n4. TABLATURE INTEGRATION RECOMMENDATIONS")
    print("-" * 50)
    print("Recommended approach for adding tabs to website:")
    print(f"1. Focus on {stats['beginner_friendly']} beginner-friendly songs")
    print("2. Use simple chord progressions with open chords")
    print("3. Provide basic strumming patterns")
    print("4. Include difficulty ratings")
    print("5. Add chord fingering diagrams alongside tabs")
    print("6. Consider using jTab library for interactive tabs")
    
    coverage_percent = (stats['can_create_tabs'] / stats['total_songs'] * 100)
    print(f"\nTab Coverage: {coverage_percent:.1f}% of songs can have complete tablatures")

if __name__ == "__main__":
    main()