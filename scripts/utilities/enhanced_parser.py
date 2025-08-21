#!/usr/bin/env python3
"""
Enhanced McGill Chord Data Parser
Focuses on extracting actual song titles, artists, and chord progressions
"""

import os
import sqlite3
import re
from pathlib import Path
from collections import defaultdict

def analyze_lab_files():
    """Analyze .lab files which contain chord annotations"""
    print("🎵 ANALYZING .LAB FILES (Chord Annotations)")
    print("=" * 50)
    
    lab_files = []
    cocopops_path = Path("CoCoPops-Billboard-legacy")
    
    # Find all .lab files
    for root, dirs, files in os.walk(cocopops_path):
        for file in files:
            if file.endswith('.lab'):
                lab_files.append(os.path.join(root, file))
    
    print(f"Found {len(lab_files)} .lab files")
    
    # Sample first 10 .lab files
    chord_data = []
    for i, lab_file in enumerate(lab_files[:10]):
        try:
            with open(lab_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract filename for song identification
            filename = os.path.basename(lab_file)
            
            # Parse chord annotations
            chords = extract_chords_from_lab(content)
            
            chord_data.append({
                'filename': filename,
                'filepath': lab_file,
                'chords': chords,
                'content_sample': content[:200]
            })
            
            print(f"\n📄 {filename}")
            print(f"   Path: {lab_file}")
            print(f"   Chords found: {chords[:5]}...")  # First 5 chords
            print(f"   Sample: {content[:100].replace(chr(10), '\\n')}")
            
        except Exception as e:
            print(f"Error reading {lab_file}: {e}")
    
    return chord_data

def analyze_hum_files():
    """Analyze .hum files which contain Humdrum format with song info"""
    print("\n🎵 ANALYZING .HUM FILES (Humdrum Format)")
    print("=" * 50)
    
    hum_files = []
    cocopops_path = Path("CoCoPops-Billboard-legacy")
    
    # Find all .hum files
    for root, dirs, files in os.walk(cocopops_path):
        for file in files:
            if file.endswith('.hum'):
                hum_files.append(os.path.join(root, file))
    
    print(f"Found {len(hum_files)} .hum files")
    
    # Sample first 10 .hum files
    hum_data = []
    for i, hum_file in enumerate(hum_files[:10]):
        try:
            with open(hum_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            filename = os.path.basename(hum_file)
            
            # Extract song info from filename
            song_info = parse_filename_for_song_info(filename)
            
            hum_data.append({
                'filename': filename,
                'filepath': hum_file,
                'song_info': song_info,
                'content_sample': content[:300]
            })
            
            print(f"\n📄 {filename}")
            print(f"   Artist: {song_info.get('artist', 'Unknown')}")
            print(f"   Song: {song_info.get('title', 'Unknown')}")
            print(f"   Year: {song_info.get('year', 'Unknown')}")
            print(f"   Sample: {content[:150].replace(chr(10), '\\n')}")
            
        except Exception as e:
            print(f"Error reading {hum_file}: {e}")
    
    return hum_data

def extract_chords_from_lab(content):
    """Extract chord progressions from .lab file content"""
    chords = []
    lines = content.strip().split('\n')
    
    for line in lines:
        # Lab format: timestamp1 timestamp2 chord
        parts = line.split('\t')
        if len(parts) >= 3 and parts[2] != 'N':  # 'N' means no chord
            chord = parts[2]
            if chord and chord not in ['N', '']:
                chords.append(chord)
    
    return chords

def parse_filename_for_song_info(filename):
    """Parse song info from filename like 'ABBA_Chiquitita_1979.hum'"""
    # Remove extension
    name = filename.replace('.hum', '').replace('.lab', '')
    
    # Try to split by underscores
    parts = name.split('_')
    
    info = {}
    if len(parts) >= 3:
        info['artist'] = parts[0].replace('_', ' ')
        info['title'] = parts[1].replace('_', ' ')
        # Last part might be year
        if parts[-1].isdigit() and len(parts[-1]) == 4:
            info['year'] = parts[-1]
            info['title'] = '_'.join(parts[1:-1]).replace('_', ' ')
    elif len(parts) == 2:
        info['artist'] = parts[0].replace('_', ' ')
        info['title'] = parts[1].replace('_', ' ')
    
    return info

def analyze_billboard_index():
    """Analyze the Billboard index file for song matching"""
    print("\n📊 ANALYZING BILLBOARD INDEX")
    print("=" * 50)
    
    index_file = "CoCoPops-Billboard-legacy/OriginalData/billboard-2.0-index.csv"
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        print(f"Found {len(lines)} lines in Billboard index")
        
        # Sample first 10 lines
        for i, line in enumerate(lines[:10]):
            print(f"Line {i+1}: {line}")
        
        return lines
        
    except Exception as e:
        print(f"Error reading Billboard index: {e}")
        return []

def create_enhanced_chord_table():
    """Create enhanced table with proper song matching"""
    print("\n🗄️ CREATING ENHANCED CHORD DATABASE TABLE")
    print("=" * 50)
    
    conn = sqlite3.connect('music_database.db')
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS mcgill_chord_data')
    
    # Create new enhanced table
    cursor.execute('''
        CREATE TABLE mcgill_chord_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            artist TEXT,
            song_title TEXT,
            year INTEGER,
            chord_progression TEXT,
            file_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Created mcgill_chord_data table")

def main():
    print("🎵 ENHANCED McGILL CHORD DATA ANALYSIS")
    print("=" * 60)
    
    # Create enhanced database table
    create_enhanced_chord_table()
    
    # Analyze different file types
    lab_data = analyze_lab_files()
    hum_data = analyze_hum_files() 
    billboard_index = analyze_billboard_index()
    
    print("\n🎯 SUMMARY:")
    print(f"✓ Found {len(lab_data)} .lab chord files")
    print(f"✓ Found {len(hum_data)} .hum song files") 
    print(f"✓ Found Billboard index with song metadata")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Parse all .hum files for complete song list")
    print("2. Match .lab chord files with song metadata")
    print("3. Link McGill songs to Billboard unique_songs table")
    print("4. Build comprehensive chord database")
    
    return {
        'lab_data': lab_data,
        'hum_data': hum_data,
        'billboard_index': billboard_index
    }

if __name__ == "__main__":
    results = main()