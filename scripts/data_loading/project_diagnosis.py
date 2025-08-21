#!/usr/bin/env python3
"""
Project Diagnosis Script
========================python inspect_chord_data.py

This script helps locate your data files and verify project structure.
Run this first to understand what we're working with.

Usage: python diagnose_project.py
"""

import os
from pathlib import Path
import sqlite3
import glob

def find_databases():
    """Find all SQLite database files in the project area."""
    print("🔍 SEARCHING FOR DATABASE FILES...")
    
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    
    # Search patterns
    search_areas = [
        current_dir,
        parent_dir,
        current_dir / "data",
        current_dir / "data" / "databases", 
        parent_dir / "data",
        parent_dir / "data" / "databases"
    ]
    
    databases_found = []
    
    for area in search_areas:
        if area.exists():
            for db_file in area.glob("*.db"):
                size_mb = db_file.stat().st_size / (1024 * 1024)
                databases_found.append((db_file, size_mb))
                print(f"   📊 {db_file} ({size_mb:.1f} MB)")
    
    # Also search more broadly
    print("\n🔍 BROADER SEARCH (within parent directories)...")
    for db_file in Path.cwd().parent.glob("**/*.db"):
        if db_file.name.endswith('.db'):
            size_mb = db_file.stat().st_size / (1024 * 1024)
            if (db_file, size_mb) not in databases_found:
                databases_found.append((db_file, size_mb))
                print(f"   📊 {db_file} ({size_mb:.1f} MB)")
    
    return databases_found

def check_database_contents(db_path):
    """Check what tables are in a database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n   Tables in {db_path.name}:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"     • {table[0]}: {count:,} records")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error reading {db_path.name}: {e}")

def find_mcgill_files():
    """Find McGill .lab chord files."""
    print("\n🎼 SEARCHING FOR MCGILL CHORD FILES...")
    
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    
    search_areas = [
        current_dir / "data" / "mcgill",
        current_dir / "mcgill",
        parent_dir / "data" / "mcgill",
        parent_dir / "mcgill",
        current_dir / "Music_Project" / "data" / "mcgill",
    ]
    
    for area in search_areas:
        if area.exists():
            lab_files = list(area.glob("*.lab"))
            if lab_files:
                print(f"   📁 Found {len(lab_files)} .lab files in: {area}")
                # Show a few examples
                for i, lab_file in enumerate(lab_files[:3]):
                    print(f"      • {lab_file.name}")
                if len(lab_files) > 3:
                    print(f"      • ... and {len(lab_files) - 3} more")
                return area
            else:
                print(f"   📂 Directory exists but empty: {area}")
        else:
            print(f"   ❌ Directory not found: {area}")
    
    # Broader search
    print(f"\n🔍 BROADER SEARCH for .lab files...")
    lab_files = list(Path.cwd().parent.glob("**/*.lab"))
    if lab_files:
        print(f"   📁 Found {len(lab_files)} .lab files scattered in parent directories")
        # Group by directory
        dirs = {}
        for f in lab_files:
            dir_name = f.parent
            if dir_name not in dirs:
                dirs[dir_name] = []
            dirs[dir_name].append(f)
        
        for dir_path, files in dirs.items():
            print(f"      📂 {dir_path}: {len(files)} files")
    
    return None

def find_bimmuda_files():
    """Find BiMMuDa data."""
    print("\n🎵 SEARCHING FOR BIMMUDA DATA...")
    
    # Look for BiMMuDa directories or database references
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    
    search_patterns = [
        "**/BiMMuDa*",
        "**/bimmuda*",
        "**/billboard_data.db"
    ]
    
    for pattern in search_patterns:
        matches = list(parent_dir.glob(pattern))
        for match in matches:
            if match.is_dir():
                midi_files = list(match.glob("**/*.mid"))
                print(f"   📁 BiMMuDa directory: {match} ({len(midi_files)} MIDI files)")
            else:
                size_mb = match.stat().st_size / (1024 * 1024)
                print(f"   📊 BiMMuDa database: {match} ({size_mb:.1f} MB)")

def show_current_structure():
    """Show the current directory structure."""
    print("\n📁 CURRENT PROJECT STRUCTURE:")
    current_dir = Path.cwd()
    print(f"   Current directory: {current_dir}")
    
    # Show key subdirectories
    key_dirs = ["data", "scripts", "docs", "archive"]
    for dir_name in key_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            subdir_count = len([x for x in dir_path.iterdir() if x.is_dir()])
            file_count = len([x for x in dir_path.iterdir() if x.is_file()])
            print(f"   📂 {dir_name}/: {subdir_count} subdirs, {file_count} files")
            
            # Show subdirectories
            for subdir in sorted([x for x in dir_path.iterdir() if x.is_dir()]):
                sub_files = len(list(subdir.iterdir()))
                print(f"      └── {subdir.name}/: {sub_files} items")
        else:
            print(f"   ❌ {dir_name}/: Not found")

def main():
    print("🔧 PROJECT DIAGNOSIS - Finding Your Data Files")
    print("=" * 60)
    
    # Show where we are
    show_current_structure()
    
    # Find databases
    databases = find_databases()
    
    # Check database contents
    for db_path, size_mb in databases:
        check_database_contents(db_path)
    
    # Find McGill files
    mcgill_dir = find_mcgill_files()
    
    # Find BiMMuDa data
    find_bimmuda_files()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED NEXT STEPS:")
    
    if databases:
        best_db = max(databases, key=lambda x: x[1])  # Largest database
        print(f"1. Use this database: {best_db[0]}")
    else:
        print("1. ❌ No databases found - need to create or locate them")
    
    if mcgill_dir:
        print(f"2. McGill chord files ready at: {mcgill_dir}")
    else:
        print("2. ❌ Need to locate McGill .lab chord files")
    
    print("3. Run the chord loader with correct paths")

if __name__ == "__main__":
    main()
