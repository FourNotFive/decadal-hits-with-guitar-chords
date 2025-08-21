#!/usr/bin/env python3
"""
McGill Chord Data Loader - Baby Steps Approach
===============================================

This script loads McGill Billboard chord annotation files (.lab) into the database
using a methodical, baby-steps approach:

1. Start with just 3-5 sample files
2. Parse and verify the .lab format
3. Create the database table structure
4. Load sample data and verify
5. Scale up gradually to all 3,560 files

Usage:
    python load_mcgill_chords.py --sample    # Load 5 sample files first
    python load_mcgill_chords.py --all       # Load all files (after testing)

Location: scripts/data_loading/load_mcgill_chords.py
"""

import sqlite3
import argparse
from pathlib import Path
import sys
import re
from datetime import datetime

# Add project root to path so we can import from other modules
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def setup_database_table(db_path):
    """Create the mcgill_chords table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table for McGill chord data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mcgill_chords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_filename TEXT NOT NULL,
            song_id TEXT,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            duration REAL,
            chord_label TEXT NOT NULL,
            chord_simplified TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_song_filename ON mcgill_chords(song_filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chord_label ON mcgill_chords(chord_label)')
    
    conn.commit()
    conn.close()
    print("✅ Database table 'mcgill_chords' ready")

def parse_lab_file(file_path):
    """
    Parse a single .lab chord annotation file.
    
    Format: start_time end_time chord_label
    Example: 0.000000 2.090000 N
             2.090000 4.180000 C:maj
    
    Returns list of (start_time, end_time, chord_label) tuples
    """
    chord_data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Split on whitespace
                parts = line.split()
                
                if len(parts) != 3:
                    print(f"⚠️  Warning: Line {line_num} in {file_path.name} has {len(parts)} parts: {line}")
                    continue
                
                try:
                    start_time = float(parts[0])
                    end_time = float(parts[1])
                    chord_label = parts[2]
                    
                    # Basic validation
                    if end_time <= start_time:
                        print(f"⚠️  Warning: Invalid time range in {file_path.name} line {line_num}")
                        continue
                    
                    chord_data.append((start_time, end_time, chord_label))
                    
                except ValueError as e:
                    print(f"⚠️  Warning: Could not parse line {line_num} in {file_path.name}: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []
    
    return chord_data

def simplify_chord_label(chord_label):
    """
    Simplify chord labels for basic analysis.
    Examples: 'C:maj' -> 'C', 'F#:min' -> 'F#m', 'N' -> 'N' (no chord)
    """
    if chord_label == 'N':
        return 'N'  # No chord
    
    # Basic chord simplification
    # This is a starting point - we can enhance this later
    chord_label = chord_label.replace(':maj', '')
    chord_label = chord_label.replace(':min', 'm')
    chord_label = chord_label.replace(':7', '7')
    
    # Extract just the root note for now (can be enhanced)
    match = re.match(r'^([A-G][#b]?)', chord_label)
    if match:
        return match.group(1)
    
    return chord_label

def load_chord_file_to_db(file_path, db_path, verbose=False):
    """Load a single chord file into the database."""
    
    # Parse the chord file
    chord_data = parse_lab_file(file_path)
    
    if not chord_data:
        print(f"❌ No chord data found in {file_path.name}")
        return 0
    
    # Extract song info from filename
    song_filename = file_path.stem  # filename without extension
    song_id = song_filename  # Can be enhanced with better ID extraction
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert chord data
    inserted_count = 0
    for start_time, end_time, chord_label in chord_data:
        duration = end_time - start_time
        chord_simplified = simplify_chord_label(chord_label)
        
        cursor.execute('''
            INSERT INTO mcgill_chords 
            (song_filename, song_id, start_time, end_time, duration, chord_label, chord_simplified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (song_filename, song_id, start_time, end_time, duration, chord_label, chord_simplified))
        
        inserted_count += 1
    
    conn.commit()
    conn.close()
    
    if verbose:
        print(f"✅ Loaded {inserted_count} chord annotations from {file_path.name}")
    
    return inserted_count

def get_sample_files(mcgill_dir, count=5):
    """Get a small sample of .lab files for testing."""
    lab_files = list(Path(mcgill_dir).glob("*.lab"))
    
    if not lab_files:
        print(f"❌ No .lab files found in {mcgill_dir}")
        return []
    
    print(f"📁 Found {len(lab_files)} total .lab files")
    
    # Return first N files for predictable testing
    sample_files = lab_files[:count]
    print(f"🎯 Selected {len(sample_files)} files for sample loading:")
    for f in sample_files:
        print(f"   • {f.name}")
    
    return sample_files

def verify_loaded_data(db_path):
    """Quick verification of loaded data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count total records
    cursor.execute("SELECT COUNT(*) FROM mcgill_chords")
    total_count = cursor.fetchone()[0]
    
    # Count unique songs
    cursor.execute("SELECT COUNT(DISTINCT song_filename) FROM mcgill_chords")
    unique_songs = cursor.fetchone()[0]
    
    # Sample of chord labels
    cursor.execute("SELECT chord_label, COUNT(*) as count FROM mcgill_chords GROUP BY chord_label ORDER BY count DESC LIMIT 10")
    top_chords = cursor.fetchall()
    
    # Sample record
    cursor.execute("SELECT * FROM mcgill_chords LIMIT 1")
    sample_record = cursor.fetchone()
    
    conn.close()
    
    print("\n📊 DATA VERIFICATION:")
    print(f"   Total chord annotations: {total_count:,}")
    print(f"   Unique songs loaded: {unique_songs}")
    print(f"   Top chord labels: {', '.join([f'{chord}({count})' for chord, count in top_chords[:5]])}")
    
    if sample_record:
        print(f"   Sample record: {sample_record[1]} | {sample_record[4]:.2f}s | {sample_record[6]}")
    
    return total_count > 0

def main():
    parser = argparse.ArgumentParser(description="Load McGill chord data - Baby Steps Approach")
    parser.add_argument("--sample", action="store_true", help="Load only 5 sample files for testing")
    parser.add_argument("--all", action="store_true", help="Load all .lab files (use after --sample testing)")
    parser.add_argument("--count", type=int, default=5, help="Number of sample files to load (default: 5)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    mcgill_dir = project_root / "data" / "mcgill"
    db_path = project_root / "data" / "databases" / "music_database.db"
    
    print("🎵 McGill Chord Data Loader - Baby Steps Approach")
    print(f"📁 McGill directory: {mcgill_dir}")
    print(f"🗄️  Database: {db_path}")
    print("-" * 60)
    
    # Verify paths exist
    if not mcgill_dir.exists():
        print(f"❌ McGill directory not found: {mcgill_dir}")
        return
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    # Set up database table
    setup_database_table(db_path)
    
    # Determine which files to process
    if args.sample or not args.all:
        # Baby steps: load sample files first
        files_to_process = get_sample_files(mcgill_dir, args.count)
        print(f"\n🎯 BABY STEP MODE: Loading {len(files_to_process)} sample files")
    else:
        # Load all files
        files_to_process = list(mcgill_dir.glob("*.lab"))
        print(f"\n🚀 FULL MODE: Loading all {len(files_to_process)} files")
    
    if not files_to_process:
        print("❌ No files to process")
        return
    
    # Process files
    total_loaded = 0
    successful_files = 0
    
    print("\n📥 Loading chord data...")
    for i, file_path in enumerate(files_to_process, 1):
        if args.verbose or len(files_to_process) <= 10:
            print(f"Processing {i}/{len(files_to_process)}: {file_path.name}")
        elif i % 100 == 0:
            print(f"Processed {i}/{len(files_to_process)} files...")
        
        loaded_count = load_chord_file_to_db(file_path, db_path, args.verbose)
        
        if loaded_count > 0:
            total_loaded += loaded_count
            successful_files += 1
    
    print(f"\n✅ LOADING COMPLETE!")
    print(f"   Files processed: {successful_files}/{len(files_to_process)}")
    print(f"   Total chord annotations loaded: {total_loaded:,}")
    
    # Verify the loaded data
    if total_loaded > 0:
        verify_loaded_data(db_path)
        
        if args.sample:
            print(f"\n🎯 BABY STEP SUCCESS! Sample data loaded and verified.")
            print(f"💡 Next step: Run with --all to load all {len(list(mcgill_dir.glob('*.lab')))} files")
        else:
            print(f"\n🚀 FULL LOADING COMPLETE! All McGill chord data ready for analysis.")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
