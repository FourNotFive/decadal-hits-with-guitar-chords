#!/usr/bin/env python3
"""
Simple MIDI Chord Extractor
Extracts guitar chords from MIDI files for the website
"""

import os
import pretty_midi
from collections import Counter

def midi_to_chords(midi_file_path):
    """Extract chord progression from MIDI file"""
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file_path)
        
        # Get all notes from all instruments
        all_notes = []
        for instrument in midi_data.instruments:
            if not instrument.is_drum:
                all_notes.extend(instrument.notes)
        
        if not all_notes:
            return None
            
        # Sort notes by start time
        all_notes.sort(key=lambda x: x.start)
        
        # Group notes into 2-second windows to find chords
        chords = []
        window_size = 2.0  # 2 seconds
        current_time = 0
        
        while current_time < max(note.end for note in all_notes):
            # Get notes playing in this time window
            window_notes = []
            for note in all_notes:
                if note.start <= current_time < note.end or (current_time <= note.start < current_time + window_size):
                    window_notes.append(note.pitch % 12)  # Get pitch class (0-11)
            
            if len(window_notes) >= 2:  # Need at least 2 notes for a chord
                # Find most common pitch classes in this window
                pitch_counts = Counter(window_notes)
                chord_pitches = [pitch for pitch, count in pitch_counts.most_common(6) if count >= 1]
                
                if chord_pitches:
                    chord_name = pitches_to_chord_name(chord_pitches)
                    if chord_name and chord_name not in chords:
                        chords.append(chord_name)
            
            current_time += window_size
        
        return " - ".join(chords[:8])  # Return up to 8 chords
        
    except Exception as e:
        print(f"Error processing {midi_file_path}: {e}")
        return None

def pitches_to_chord_name(pitches):
    """Convert MIDI pitch classes to chord name"""
    # Map pitch classes to note names
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Common chord patterns (simplified)
    chord_patterns = {
        frozenset([0, 4, 7]): 'C',           # C major
        frozenset([0, 3, 7]): 'Cm',          # C minor
        frozenset([1, 5, 8]): 'C#',          # C# major
        frozenset([1, 4, 8]): 'C#m',         # C# minor
        frozenset([2, 6, 9]): 'D',           # D major
        frozenset([2, 5, 9]): 'Dm',          # D minor
        frozenset([3, 7, 10]): 'D#',         # D# major
        frozenset([3, 6, 10]): 'D#m',        # D# minor
        frozenset([4, 8, 11]): 'E',          # E major
        frozenset([4, 7, 11]): 'Em',         # E minor
        frozenset([5, 9, 0]): 'F',           # F major
        frozenset([5, 8, 0]): 'Fm',          # F minor
        frozenset([6, 10, 1]): 'F#',         # F# major
        frozenset([6, 9, 1]): 'F#m',         # F# minor
        frozenset([7, 11, 2]): 'G',          # G major
        frozenset([7, 10, 2]): 'Gm',         # G minor
        frozenset([8, 0, 3]): 'G#',          # G# major
        frozenset([8, 11, 3]): 'G#m',        # G# minor
        frozenset([9, 1, 4]): 'A',           # A major
        frozenset([9, 0, 4]): 'Am',          # A minor
        frozenset([10, 2, 5]): 'A#',         # A# major
        frozenset([10, 1, 5]): 'A#m',        # A# minor
        frozenset([11, 3, 6]): 'B',          # B major
        frozenset([11, 2, 6]): 'Bm',         # B minor
    }
    
    # Try to find the best matching chord
    pitch_set = frozenset(pitches[:3])  # Use first 3 pitches
    
    if pitch_set in chord_patterns:
        return chord_patterns[pitch_set]
    
    # If no exact match, return the root note
    if pitches:
        return note_names[pitches[0]]
    
    return None

def process_all_midis():
    """Process all MIDI files in the source_midis folder"""
    midi_folder = "../data/bimmuda/BiMMuDa-main/source_midis"
    
    print("Extracting chords from MIDI files...")
    
    # Song mappings to match MIDI files to website songs
    midi_to_song = {
        "All-Shook-Up-1.mid": ("All Shook Up", "Elvis Presley"),
        "AllIHaveToDoIsDream.mid": ("All I Have to Do Is Dream", "The Everly Brothers"),
        "California-Dreaming.mid": ("California Dreamin'", "The Mamas & The Papas"),
        "HeyJude.mid": ("Hey Jude", "The Beatles"),
        "I-Get-Around-1.mid": ("I Get Around", "The Beach Boys"),
        "JoyToTheWorld.mid": ("Joy to the World", "Three Dog Night"),
        "Paula Abdul - Straight Up L.mid": ("Straight Up", "Paula Abdul")
    }
    
    results = []
    
    for midi_file in os.listdir(midi_folder):
        if midi_file.endswith('.mid'):
            midi_path = os.path.join(midi_folder, midi_file)
            print(f"Processing: {midi_file}")
            
            chords = midi_to_chords(midi_path)
            
            if chords and midi_file in midi_to_song:
                song_title, artist = midi_to_song[midi_file]
                results.append((song_title, artist, chords, midi_file))
                print(f"  -> {song_title} by {artist}: {chords}")
            else:
                print(f"  -> Failed to extract chords from {midi_file}")
    
    return results

if __name__ == "__main__":
    results = process_all_midis()
    print(f"\nExtracted chords from {len(results)} songs!")
    
    # Show results
    for song_title, artist, chords, midi_file in results:
        print(f"{song_title} by {artist}: {chords}")