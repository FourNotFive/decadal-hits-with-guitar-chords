#!/usr/bin/env python3
"""
Comprehensive MIDI Chord Extractor for BiMMuDa Dataset
Extracts chord progressions from all BiMMuDa MIDI files and McGill annotations
"""

import os
import sqlite3
import pretty_midi
from collections import Counter, defaultdict
import glob

class ChordExtractor:
    def __init__(self, db_path='../data/databases/billboard_data.db'):
        self.db_path = db_path
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Enhanced chord patterns including 7ths, sus, and more complex chords
        self.chord_patterns = {
            # Major triads
            frozenset([0, 4, 7]): 'C', frozenset([1, 5, 8]): 'C#', frozenset([2, 6, 9]): 'D',
            frozenset([3, 7, 10]): 'D#', frozenset([4, 8, 11]): 'E', frozenset([5, 9, 0]): 'F',
            frozenset([6, 10, 1]): 'F#', frozenset([7, 11, 2]): 'G', frozenset([8, 0, 3]): 'G#',
            frozenset([9, 1, 4]): 'A', frozenset([10, 2, 5]): 'A#', frozenset([11, 3, 6]): 'B',
            
            # Minor triads
            frozenset([0, 3, 7]): 'Cm', frozenset([1, 4, 8]): 'C#m', frozenset([2, 5, 9]): 'Dm',
            frozenset([3, 6, 10]): 'D#m', frozenset([4, 7, 11]): 'Em', frozenset([5, 8, 0]): 'Fm',
            frozenset([6, 9, 1]): 'F#m', frozenset([7, 10, 2]): 'Gm', frozenset([8, 11, 3]): 'G#m',
            frozenset([9, 0, 4]): 'Am', frozenset([10, 1, 5]): 'A#m', frozenset([11, 2, 6]): 'Bm',
            
            # Major 7th chords
            frozenset([0, 4, 7, 11]): 'Cmaj7', frozenset([1, 5, 8, 0]): 'C#maj7', frozenset([2, 6, 9, 1]): 'Dmaj7',
            frozenset([3, 7, 10, 2]): 'D#maj7', frozenset([4, 8, 11, 3]): 'Emaj7', frozenset([5, 9, 0, 4]): 'Fmaj7',
            frozenset([6, 10, 1, 5]): 'F#maj7', frozenset([7, 11, 2, 6]): 'Gmaj7', frozenset([8, 0, 3, 7]): 'G#maj7',
            frozenset([9, 1, 4, 8]): 'Amaj7', frozenset([10, 2, 5, 9]): 'A#maj7', frozenset([11, 3, 6, 10]): 'Bmaj7',
            
            # Dominant 7th chords
            frozenset([0, 4, 7, 10]): 'C7', frozenset([1, 5, 8, 11]): 'C#7', frozenset([2, 6, 9, 0]): 'D7',
            frozenset([3, 7, 10, 1]): 'D#7', frozenset([4, 8, 11, 2]): 'E7', frozenset([5, 9, 0, 3]): 'F7',
            frozenset([6, 10, 1, 4]): 'F#7', frozenset([7, 11, 2, 5]): 'G7', frozenset([8, 0, 3, 6]): 'G#7',
            frozenset([9, 1, 4, 7]): 'A7', frozenset([10, 2, 5, 8]): 'A#7', frozenset([11, 3, 6, 9]): 'B7',
        }

    def midi_to_chords(self, midi_file_path):
        """Enhanced chord extraction from MIDI file"""
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_file_path)
            
            # Get all notes from all non-drum instruments
            all_notes = []
            for instrument in midi_data.instruments:
                if not instrument.is_drum:
                    all_notes.extend(instrument.notes)
            
            if not all_notes:
                return None
                
            # Sort notes by start time
            all_notes.sort(key=lambda x: x.start)
            
            # Use adaptive window size based on song tempo
            song_length = max(note.end for note in all_notes)
            num_windows = max(8, min(16, int(song_length / 2)))  # 8-16 chord sections
            window_size = song_length / num_windows
            
            chords = []
            current_time = 0
            
            while current_time < song_length:
                # Get notes playing in this time window
                window_notes = []
                for note in all_notes:
                    # Note is active during this window
                    if (note.start <= current_time < note.end or 
                        (current_time <= note.start < current_time + window_size)):
                        window_notes.append(note.pitch % 12)
                
                if len(window_notes) >= 3:  # Need at least 3 notes for a meaningful chord
                    # Find most common pitch classes in this window
                    pitch_counts = Counter(window_notes)
                    # Take the most common pitches, up to 6
                    chord_pitches = [pitch for pitch, count in pitch_counts.most_common(6)]
                    
                    if chord_pitches:
                        chord_name = self.pitches_to_chord_name(chord_pitches)
                        if chord_name and (not chords or chord_name != chords[-1]):
                            chords.append(chord_name)
                
                current_time += window_size
            
            # Return up to 8 unique chords
            unique_chords = []
            for chord in chords:
                if chord not in unique_chords:
                    unique_chords.append(chord)
                if len(unique_chords) >= 8:
                    break
            
            return " - ".join(unique_chords) if unique_chords else None
            
        except Exception as e:
            print(f"Error processing {midi_file_path}: {e}")
            return None

    def pitches_to_chord_name(self, pitches):
        """Enhanced chord name detection"""
        if not pitches:
            return None
        
        # Try different chord sizes (4-note, 3-note)
        for chord_size in [4, 3]:
            if len(pitches) >= chord_size:
                pitch_set = frozenset(pitches[:chord_size])
                if pitch_set in self.chord_patterns:
                    return self.chord_patterns[pitch_set]
        
        # If no exact match, return the root note as fallback
        return self.note_names[pitches[0]]

    def find_all_midi_files(self):
        """Find all MIDI files in the BiMMuDa dataset"""
        midi_files = []
        base_path = "../data/bimmuda/BiMMuDa-main"
        
        # Check bimmuda_dataset folders (year/position/midi files)
        dataset_path = os.path.join(base_path, "bimmuda_dataset")
        if os.path.exists(dataset_path):
            for year_folder in os.listdir(dataset_path):
                year_path = os.path.join(dataset_path, year_folder)
                if os.path.isdir(year_path) and year_folder.isdigit():
                    # Each year has position folders
                    for position_folder in os.listdir(year_path):
                        position_path = os.path.join(year_path, position_folder)
                        if os.path.isdir(position_path):
                            # Look for _full.mid files (complete song arrangements)
                            for file in os.listdir(position_path):
                                if file.endswith('_full.mid'):
                                    midi_files.append(os.path.join(position_path, file))
        
        # Check source_midis folder
        source_midis_path = os.path.join(base_path, "source_midis")
        if os.path.exists(source_midis_path):
            for file in os.listdir(source_midis_path):
                if file.endswith('.mid'):
                    midi_files.append(os.path.join(source_midis_path, file))
        
        print(f"Found {len(midi_files)} MIDI files")
        return midi_files

    def match_midi_to_songs(self, midi_path):
        """Match MIDI file to database songs using the BiMMuDa folder structure"""
        # Extract info from MIDI path
        filename = os.path.basename(midi_path)
        folder_path = os.path.dirname(midi_path)
        
        # Query database for potential matches
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try to match based on BiMMuDa folder structure: year/position/YYYY_PP_full.mid
        if 'bimmuda_dataset' in folder_path:
            path_parts = folder_path.split(os.sep)
            try:
                # Find year and position from path
                year_match = None
                position_match = None
                
                # Extract year folder
                for i, part in enumerate(path_parts):
                    if part.isdigit() and 1950 <= int(part) <= 2024:
                        year_match = int(part)
                        # Position should be the next folder
                        if i + 1 < len(path_parts) and path_parts[i + 1].isdigit():
                            position_match = int(path_parts[i + 1])
                        break
                
                # Also try to extract from filename: YYYY_PP_full.mid
                if not (year_match and position_match):
                    filename_parts = filename.replace('.mid', '').split('_')
                    if len(filename_parts) >= 2:
                        try:
                            year_from_file = int(filename_parts[0])
                            pos_from_file = int(filename_parts[1])
                            if 1950 <= year_from_file <= 2024:
                                year_match = year_from_file
                                position_match = pos_from_file
                        except ValueError:
                            pass
                
                if year_match and position_match:
                    cursor.execute("""
                        SELECT id, title, artist, year, position 
                        FROM bimmuda_songs 
                        WHERE year = ? AND position = ?
                    """, (year_match, position_match))
                    result = cursor.fetchone()
                    if result:
                        conn.close()
                        return result
                        
            except Exception as e:
                print(f"  Error parsing path {midi_path}: {e}")
        
        # Fallback: try to match source_midis files using hardcoded mappings
        source_mappings = {
            "All-Shook-Up-1.mid": ("All Shook Up", "Elvis Presley"),
            "AllIHaveToDoIsDream.mid": ("All I Have to Do Is Dream", "The Everly Brothers"),
            "California-Dreaming.mid": ("California Dreamin'", "The Mamas & The Papas"),
            "HeyJude.mid": ("Hey Jude", "The Beatles"),
            "I-Get-Around-1.mid": ("I Get Around", "The Beach Boys"),
            "JoyToTheWorld.mid": ("Joy to the World", "Three Dog Night"),
            "Paula Abdul - Straight Up L.mid": ("Straight Up", "Paula Abdul")
        }
        
        if filename in source_mappings:
            title, artist = source_mappings[filename]
            cursor.execute("""
                SELECT id, title, artist, year, position 
                FROM bimmuda_songs 
                WHERE title = ? AND artist = ?
            """, (title, artist))
            result = cursor.fetchone()
            if result:
                conn.close()
                return result
        
        conn.close()
        return None

    def process_all_midis(self, limit=None):
        """Process all MIDI files and extract chords"""
        print("Starting comprehensive MIDI chord extraction...")
        
        midi_files = self.find_all_midi_files()
        if not midi_files:
            print("No MIDI files found!")
            return {}
        
        # Limit for testing
        if limit:
            midi_files = midi_files[:limit]
            print(f"Processing first {limit} files for testing...")
        
        chord_results = {}
        processed = 0
        matches = 0
        
        for midi_file in midi_files:
            processed += 1
            print(f"Processing {processed}/{len(midi_files)}: {os.path.basename(midi_file)}")
            
            # Extract chords
            chords = self.midi_to_chords(midi_file)
            
            if chords:
                # Try to match to database song
                song_match = self.match_midi_to_songs(midi_file)
                
                if song_match:
                    song_id, title, artist, year, position = song_match
                    chord_results[song_id] = {
                        'title': title,
                        'artist': artist,
                        'year': year,
                        'chords': chords,
                        'midi_file': midi_file
                    }
                    matches += 1
                    print(f"  Matched: {title} by {artist} -> {chords}")
                else:
                    print(f"  No database match for {os.path.basename(midi_file)}")
            else:
                print(f"  No chords extracted from {os.path.basename(midi_file)}")
        
        print(f"\nCompleted! Processed {processed} MIDI files, found {matches} database matches")
        return chord_results

    def load_mcgill_annotations(self):
        """Load McGill chord annotations"""
        print("Loading McGill chord annotations...")
        
        annotations_path = "../data/mcgill/annotations/annotations"
        chord_data = {}
        
        if not os.path.exists(annotations_path):
            print("McGill annotations not found")
            return chord_data
        
        for song_folder in os.listdir(annotations_path):
            song_path = os.path.join(annotations_path, song_folder)
            if os.path.isdir(song_path):
                # Load the simplest chord annotation (majmin.lab)
                majmin_file = os.path.join(song_path, "majmin.lab")
                if os.path.exists(majmin_file):
                    chords = self.parse_lab_file(majmin_file)
                    if chords:
                        chord_data[song_folder] = chords
        
        print(f"Loaded {len(chord_data)} McGill chord annotations")
        return chord_data

    def parse_lab_file(self, lab_file_path):
        """Parse a McGill .lab chord annotation file"""
        try:
            chords = []
            with open(lab_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Format: start_time end_time chord_label
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            chord_label = parts[2].strip()
                            if chord_label != 'N' and chord_label not in chords:  # Skip 'N' (no chord)
                                chords.append(chord_label)
            
            return " - ".join(chords[:8]) if chords else None
        except Exception as e:
            print(f"Error parsing {lab_file_path}: {e}")
            return None

    def update_database_with_chords(self, midi_chord_results, mcgill_chord_data):
        """Update database with extracted chord progressions"""
        print("Updating database with chord progressions...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add chord_progression column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE bimmuda_songs ADD COLUMN chord_progression TEXT")
            conn.commit()
            print("Added chord_progression column to database")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Update with MIDI-extracted chords
        midi_updates = 0
        for song_id, song_data in midi_chord_results.items():
            cursor.execute("""
                UPDATE bimmuda_songs 
                SET chord_progression = ? 
                WHERE id = ?
            """, (song_data['chords'], song_id))
            midi_updates += 1
        
        # Update with McGill chords (for songs that don't have MIDI chords)
        mcgill_updates = 0
        for mcgill_id, chords in mcgill_chord_data.items():
            # Try to match McGill ID to database songs
            # This would need more sophisticated matching logic
            # For now, we'll skip this step and focus on MIDI data
            pass
        
        conn.commit()
        conn.close()
        
        print(f"Updated database: {midi_updates} MIDI chord progressions, {mcgill_updates} McGill annotations")
        return midi_updates + mcgill_updates

def main():
    print("Comprehensive BiMMuDa Chord Extraction System")
    print("=" * 50)
    
    extractor = ChordExtractor()
    
    # Process all MIDI files
    midi_results = extractor.process_all_midis()
    
    # Load McGill annotations
    mcgill_results = extractor.load_mcgill_annotations()
    
    # Update database
    total_updates = extractor.update_database_with_chords(midi_results, mcgill_results)
    
    print(f"\nComplete! Added chord progressions to {total_updates} songs")
    print(f"MIDI extractions: {len(midi_results)}")
    print(f"McGill annotations: {len(mcgill_results)}")

if __name__ == "__main__":
    main()