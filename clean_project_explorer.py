#!/usr/bin/env python3
"""
Clean Project Explorer - Check your newly organized project
"""

import os
import sqlite3
from pathlib import Path

def explore_clean_structure():
    """Explore the clean project structure"""
    print("🎵 EXPLORING YOUR CLEAN PROJECT")
    print("=" * 50)
    
    current_dir = Path.cwd()
    print(f"📍 Current directory: {current_dir}")
    
    # Check main folders
    expected_folders = ['data', 'scripts', 'archive', 'docs']
    
    for folder in expected_folders:
        if os.path.exists(folder):
            print(f"✅ {folder}/")
            
            # Count contents
            for subfolder in os.listdir(folder):
                subfolder_path = Path(folder) / subfolder
                if subfolder_path.is_dir():
                    file_count = sum(1 for _ in subfolder_path.rglob('*') if _.is_file())
                    print(f"   📁 {subfolder}/ ({file_count} files)")
                else:
                    print(f"   📄 {subfolder}")
        else:
            print(f"❌ {folder}/ (missing)")

def check_databases():
    """Check the database files"""
    print(f"\n💾 DATABASE CHECK:")
    print("=" * 30)
    
    db_dir = Path("data/databases")
    if not db_dir.exists():
        print("❌ No databases directory found")
        return
    
    for db_file in db_dir.glob("*.db"):
        size_mb = db_file.stat().st_size / (1024*1024)
        print(f"📊 {db_file.name} ({size_mb:.1f} MB)")
        
        # Quick table check
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   📋 {table[0]}: {count:,} rows")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Error reading {db_file.name}: {e}")

def check_chord_data():
    """Check McGill chord data"""
    print(f"\n🎼 CHORD DATA CHECK:")
    print("=" * 30)
    
    mcgill_dir = Path("data/mcgill")
    if not mcgill_dir.exists():
        print("❌ No McGill directory found")
        return
    
    # Count .lab files
    lab_files = list(mcgill_dir.rglob("*.lab"))
    print(f"🎵 Chord annotation files (.lab): {len(lab_files)}")
    
    if lab_files:
        # Show directory structure
        print("📁 Sample structure:")
        for lab_file in lab_files[:3]:
            rel_path = lab_file.relative_to(mcgill_dir)
            print(f"   📄 {rel_path}")
        if len(lab_files) > 3:
            print(f"   ... and {len(lab_files) - 3} more files")

def check_melody_data():
    """Check BiMMuDa melody data"""
    print(f"\n🎵 MELODY DATA CHECK:")
    print("=" * 30)
    
    bimmuda_dir = Path("data/bimmuda")
    if bimmuda_dir.exists():
        midi_files = list(bimmuda_dir.rglob("*.mid*"))
        csv_files = list(bimmuda_dir.rglob("*.csv"))
        
        print(f"🎹 MIDI files: {len(midi_files)}")
        print(f"📊 CSV metadata files: {len(csv_files)}")
        
        for csv_file in csv_files:
            rel_path = csv_file.relative_to(bimmuda_dir)
            print(f"   📋 {rel_path}")
    else:
        print("⚠️  BiMMuDa data not moved yet - still need to copy from ../BiMMuDa-main/")

def suggest_next_steps():
    """Suggest what to do next"""
    print(f"\n🎯 NEXT BABY STEPS:")
    print("=" * 30)
    
    # Check what we have
    has_chord_data = Path("data/mcgill").exists()
    has_databases = Path("data/databases").exists()
    has_bimmuda = Path("data/bimmuda").exists()
    
    step = 1
    
    if not has_bimmuda:
        print(f"{step}. 📂 Copy BiMMuDa data:")
        print(f"   Copy ../BiMMuDa-main/ to data/bimmuda/")
        print(f"   Copy ../billboard_data.db to data/databases/")
        step += 1
    
    if has_chord_data and has_databases:
        print(f"{step}. 🎼 Load McGill chord data:")
        print(f"   python scripts/data_loading/simple_mcgill_loader.py")
        step += 1
    
    print(f"{step}. 🔗 Start connecting melody + chord data")
    print(f"{step+1}. 📊 Create your first analysis!")

def main():
    """Main exploration function"""
    explore_clean_structure()
    check_databases()
    check_chord_data()
    check_melody_data()
    suggest_next_steps()
    
    print(f"\n✨ Your project is beautifully organized!")
    print(f"📖 Check README.md for full documentation")

if __name__ == "__main__":
    main()
