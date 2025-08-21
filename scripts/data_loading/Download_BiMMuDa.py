#!/usr/bin/env python3
"""
Simple script to download BiMMuDa dataset and explore what's inside
Baby steps approach! 👶
"""

import os
import requests
import zipfile

def download_bimmuda():
    """Download the BiMMuDa dataset from GitHub"""
    print("📥 Downloading BiMMuDa dataset...")
    print("This might take a few minutes...")
    
    # GitHub repository zip download URL
    url = "https://github.com/madelinehamilton/BiMMuDa/archive/refs/heads/main.zip"
    
    # Download the zip file
    print("Downloading zip file...")
    response = requests.get(url)
    
    # Save to disk
    with open("BiMMuDa.zip", "wb") as f:
        f.write(response.content)
    print("✅ Downloaded BiMMuDa.zip")
    
    # Extract the zip file
    print("📂 Extracting files...")
    with zipfile.ZipFile("BiMMuDa.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    
    # Rename the extracted folder to something simpler
    if os.path.exists("BiMMuDa-main"):
        try:
            os.rename("BiMMuDa-main", "BiMMuDa")
        except PermissionError:
            print("⚠️  Windows permission issue - that's okay!")
            print("📁 Using 'BiMMuDa-main' folder instead")
    
    print("✅ Files extracted to 'BiMMuDa' folder")

def explore_folder_structure():
    """Look at what we downloaded"""
    print("\n" + "="*50)
    print("📁 EXPLORING WHAT WE DOWNLOADED")
    print("="*50)
    
    # Check both possible folder names
    bimmuda_folder = None
    if os.path.exists("BiMMuDa"):
        bimmuda_folder = "BiMMuDa"
    elif os.path.exists("BiMMuDa-main"):
        bimmuda_folder = "BiMMuDa-main"
    
    if not bimmuda_folder:
        print("❌ BiMMuDa folder not found. Did the download work?")
        return
    
    print(f"📂 Main folder contents ({bimmuda_folder}):")
    for item in os.listdir(bimmuda_folder):
        item_path = os.path.join(bimmuda_folder, item)
        if os.path.isdir(item_path):
            print(f"   📁 {item}/")
        else:
            print(f"   📄 {item}")
    
    # Look inside the dataset folder
    dataset_path = os.path.join(bimmuda_folder, "bimmuda_dataset")
    if os.path.exists(dataset_path):
        print(f"\n📂 Dataset folder contents (first few years):")
        years = sorted([d for d in os.listdir(dataset_path) if d.isdigit()])[:5]
        for year in years:
            print(f"   📁 {year}/")
            year_path = os.path.join(dataset_path, year)
            songs_in_year = len([d for d in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, d))])
            print(f"      ({songs_in_year} songs)")
    
    return bimmuda_folder  # Return the folder name for other functions

def peek_at_a_song(bimmuda_folder):
    """Look at one specific song to understand the structure"""
    print("\n" + "="*50)
    print("🔍 LOOKING AT ONE EXAMPLE SONG")
    print("="*50)
    
    # Let's look at a song from 1960 - "The Theme from A Summer Place"
    song_path = os.path.join(bimmuda_folder, "bimmuda_dataset", "1960", "1960_01")
    
    if not os.path.exists(song_path):
        print("❌ Example song not found")
        return
    
    print("📂 Looking at: 1960_01 - 'The Theme from A Summer Place'")
    print("📄 Files in this song folder:")
    
    for filename in os.listdir(song_path):
        file_path = os.path.join(song_path, filename)
        file_size = os.path.getsize(file_path)
        
        if filename.endswith(".mid"):
            print(f"   🎵 {filename} ({file_size} bytes) - MIDI melody file")
        elif filename.endswith(".mscz"):
            print(f"   🎼 {filename} ({file_size} bytes) - MuseScore file")
        elif filename.endswith(".txt"):
            print(f"   📝 {filename} ({file_size} bytes) - Lyrics file")
        else:
            print(f"   📄 {filename} ({file_size} bytes)")

def check_metadata(bimmuda_folder):
    """Look at the metadata files"""
    print("\n" + "="*50)
    print("📊 CHECKING METADATA")
    print("="*50)
    
    metadata_path = os.path.join(bimmuda_folder, "metadata")
    if not os.path.exists(metadata_path):
        print("❌ Metadata folder not found")
        return
    
    print("📂 Metadata folder contents:")
    for filename in os.listdir(metadata_path):
        file_path = os.path.join(metadata_path, filename)
        if filename.endswith(".csv"):
            print(f"   📊 {filename}")
            
            # Count lines to see how many songs
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"      → {len(lines)-1} data rows (plus header)")

def main():
    """Run all the baby steps"""
    print("🚀 BABY STEPS: Getting to know BiMMuDa")
    print("This script will:")
    print("1. Download the BiMMuDa dataset")
    print("2. Show you what folders and files are inside")
    print("3. Look at one example song")
    print("4. Check the metadata files")
    print("\nLet's go!")
    
    # Step 1: Download
    if not os.path.exists("BiMMuDa") and not os.path.exists("BiMMuDa-main"):
        download_bimmuda()
    else:
        print("✅ BiMMuDa folder already exists, skipping download")
    
    # Step 2: Explore structure
    bimmuda_folder = explore_folder_structure()
    
    if bimmuda_folder:
        # Step 3: Look at one song
        peek_at_a_song(bimmuda_folder)
        
        # Step 4: Check metadata
        check_metadata(bimmuda_folder)
    
    print("\n" + "="*50)
    print("🎉 DONE! Now you know what BiMMuDa contains:")
    print("   • MIDI files with melodies from Billboard hits")
    print("   • One folder per year (1950-2022)")
    print("   • Each song has multiple files (melody, sections, etc.)")
    print("   • Metadata CSV files with song info")
    print("\nNext baby step: We can look at the metadata or play a MIDI file!")

if __name__ == "__main__":
    main()