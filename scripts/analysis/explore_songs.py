#!/usr/bin/env python3
"""
Baby Step 2: Let's look at what songs are actually in BiMMuDa!
"""

import os
import csv

def find_bimmuda_folder():
    """Find the BiMMuDa folder (could be named BiMMuDa or BiMMuDa-main)"""
    if os.path.exists("BiMMuDa"):
        return "BiMMuDa"
    elif os.path.exists("BiMMuDa-main"):
        return "BiMMuDa-main"
    else:
        return None

def show_some_songs():
    """Show some actual songs we can explore"""
    print("🎵 Let's see what songs we actually have!")
    
    bimmuda_folder = find_bimmuda_folder()
    if not bimmuda_folder:
        print("❌ BiMMuDa folder not found")
        return
    
    # Look in the first few years to find some songs
    dataset_path = os.path.join(bimmuda_folder, "bimmuda_dataset")
    
    print("\n📂 Songs from the 1950s:")
    for year in ["1950", "1951", "1952"]:
        year_path = os.path.join(dataset_path, year)
        if os.path.exists(year_path):
            print(f"\n   📅 {year}:")
            song_folders = [f for f in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, f))]
            for song_folder in sorted(song_folders)[:3]:  # Show first 3 songs
                print(f"      📁 {song_folder}")
    
    return bimmuda_folder

def look_at_metadata():
    """Let's peek at the metadata to understand what we have"""
    print("\n" + "="*50)
    print("📊 WHAT'S IN THE METADATA?")
    print("="*50)
    
    bimmuda_folder = find_bimmuda_folder()
    if not bimmuda_folder:
        return
    
    # Look at the song metadata
    metadata_file = os.path.join(bimmuda_folder, "metadata", "bimmuda_per_song_metadata.csv")
    
    # First, let's see what columns we actually have
    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        first_row = next(reader)
        print("🔍 Columns in metadata file:")
        for column in first_row.keys():
            print(f"   📊 {column}")
    
    print("\n📋 First 10 songs in the dataset:")
    
    # Now let's show the actual data, adapting to whatever columns exist
    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:  # Show first 10 songs
                break
            
            # Try different possible column names
            title = row.get('title', row.get('Title', 'Unknown Title'))
            artist = row.get('artist', row.get('Artist', 'Unknown Artist'))
            
            # Try to find year/rank info
            year_info = "?"
            rank_info = "?"
            
            # Look for any column that might contain year or folder info
            for key, value in row.items():
                if 'year' in key.lower():
                    year_info = value
                elif 'rank' in key.lower():
                    rank_info = value
                elif 'folder' in key.lower():
                    if '_' in str(value):
                        parts = str(value).split('_')
                        if len(parts) >= 2:
                            year_info = parts[0]
                            rank_info = parts[1]
            
            print(f"   {year_info} | #{rank_info} | {title} | {artist}")

def pick_a_song_to_explore():
    """Let's pick one song and look at all its files"""
    print("\n" + "="*50)
    print("🔍 LET'S EXPLORE ONE SONG IN DETAIL")
    print("="*50)
    
    bimmuda_folder = find_bimmuda_folder()
    if not bimmuda_folder:
        return
    
    # Let's try the actual folder structure we found (numbered folders)
    song_options = [
        ("1950", "1"),  # "Goodnight Irene" 
        ("1950", "2"),  # "Mona Lisa"
        ("1950", "3"),  # "Third Man Theme" (instrumental!)
        ("1951", "1"),  # "Too Young"
        ("1951", "2"),  # "Because of You"
    ]
    
    for year, song_number in song_options:
        song_path = os.path.join(bimmuda_folder, "bimmuda_dataset", year, song_number)
        
        if os.path.exists(song_path):
            print(f"✅ Found song folder: {year}/{song_number}")
            print(f"📂 Looking inside: {song_path}")
            print("📄 Files in this song:")
            
            files_found = []
            total_size = 0
            for filename in os.listdir(song_path):
                file_path = os.path.join(song_path, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    if filename.endswith(".mid"):
                        file_type = "🎵 MIDI melody file"
                    elif filename.endswith(".mscz"):
                        file_type = "🎼 MuseScore score file"
                    elif filename.endswith(".txt"):
                        file_type = "📝 Lyrics file"
                    else:
                        file_type = "📄 Other file"
                    
                    print(f"   {filename} ({file_size:,} bytes) - {file_type}")
                    files_found.append(filename)
            
            print(f"\n📊 Total files: {len(files_found)}, Total size: {total_size:,} bytes")
            
            # Show what we can do with these files
            midi_files = [f for f in files_found if f.endswith('.mid')]
            if midi_files:
                print(f"\n🎵 Found {len(midi_files)} MIDI file(s)!")
                for midi_file in midi_files:
                    print(f"   • {midi_file}")
                    
                print(f"\n💡 You could play these MIDI files in any MIDI player!")
                print(f"   (Windows Media Player, VLC, online MIDI players, etc.)")
            
            lyrics_files = [f for f in files_found if f.endswith('.txt')]
            if lyrics_files:
                print(f"\n📝 Found lyrics file: {lyrics_files[0]}")
                print("💡 You could open this in Notepad to see the lyrics!")
            
            # Get the song title from metadata for this year/position
            metadata_file = os.path.join(bimmuda_folder, "metadata", "bimmuda_per_song_metadata.csv")
            with open(metadata_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                position_counter = 0
                for row in reader:
                    if row['Year'] == year:
                        position_counter += 1
                        if position_counter == int(song_number):
                            print(f"\n🎼 This is: '{row['Title']}' by {row['Artist']} ({year})")
                            break
            
            return song_path  # Return the path so we can use it later
            
    print("❌ Couldn't find any of the test songs to explore")
    return None

def simple_next_steps():
    """Show what we can do next"""
    print("\n" + "="*50)
    print("🚀 WHAT CAN WE DO NEXT?")
    print("="*50)
    print("Now that we know what's in BiMMuDa, we can:")
    print()
    print("🎵 Baby Step #3 Options:")
    print("   A) Play a MIDI file to hear a melody")
    print("   B) Look at the metadata in Excel/Google Sheets") 
    print("   C) Compare song titles with your McGill data")
    print("   D) Create a simple script to list all songs")
    print()
    print("💡 The metadata files are CSV - you can open them in Excel!")
    print(f"   📊 bimmuda_per_song_metadata.csv - List of all songs")
    print(f"   📊 bimmuda_per_melody_metadata.csv - Details about melodies")
    print()
    print("Which would you like to try next? 🤔")

def main():
    print("🍼 BABY STEP #2: Exploring the Songs in BiMMuDa")
    print("Let's see what songs are actually available!")
    
    # Step 1: Show some actual songs
    bimmuda_folder = show_some_songs()
    
    if bimmuda_folder:
        # Step 2: Look at metadata
        look_at_metadata()
        
        # Step 3: Pick one song to explore in detail
        song_path = pick_a_song_to_explore()
        
        # Step 4: Show next steps
        simple_next_steps()
    else:
        print("❌ Can't find BiMMuDa folder. Did Step 1 work?")

if __name__ == "__main__":
    main()
