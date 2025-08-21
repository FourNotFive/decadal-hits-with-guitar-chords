#!/usr/bin/env python3
"""
Quick script to update GitHub with our progress
"""

import os
import subprocess
from datetime import datetime

def run_git_commands():
    """Run git commands to update the repository"""
    print("🚀 Updating GitHub with project progress...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True, check=True)
        print("✅ Git repository detected")
        
        # Add all files
        print("📁 Adding files to git...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Create a meaningful commit message
        today = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"🎵 Major Progress: BiMMuDa Integration Complete ({today})\n\n✅ Successfully integrated 381 Billboard songs with MIDI melodies\n✅ Created comprehensive SQLite database\n✅ Ready for McGill chord data integration\n\nDatabase now contains 72 years of Billboard hits (1950-2022) with:\n- Song metadata (title, artist, year, genre)\n- Music theory data (keys, time signatures, BPM)\n- MIDI file paths for melody playback\n- Lyrics availability flags\n\nNext: Add chord progressions from McGill dataset"
        
        # Commit changes
        print("💾 Committing changes...")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to GitHub
        print("📤 Pushing to GitHub...")
        result = subprocess.run(['git', 'push'], 
                              capture_output=True, text=True, check=True)
        
        print("🎉 Successfully updated GitHub!")
        print(f"📊 Commit message preview:")
        print(f"   🎵 Major Progress: BiMMuDa Integration Complete ({today})")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        print("💡 Manual steps:")
        print("   1. git add .")
        print(f"   2. git commit -m \"BiMMuDa Integration Complete - 381 songs loaded\"")
        print("   3. git push")
        return False
    
    except FileNotFoundError:
        print("❌ Git not found. Please install Git or update manually:")
        print("💡 Manual GitHub update steps:")
        print("   1. Copy PROJECT_PROGRESS.md to your repository")
        print("   2. Add and commit your new files")
        print("   3. Push to GitHub")
        return False

def check_files_ready():
    """Check if our key files are ready to commit"""
    print("📋 Checking files to commit...")
    
    key_files = [
        "PROJECT_PROGRESS.md",
        "billboard_data.db", 
        "Download_BiMMuDa.py",
        "explore_songs.py", 
        "add_bimmuda_to_db.py"
    ]
    
    found_files = []
    missing_files = []
    
    for file in key_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size:,} bytes)")
            found_files.append(file)
        else:
            print(f"   ⚠️  {file} (not found)")
            missing_files.append(file)
    
    print(f"\n📊 Ready to commit: {len(found_files)} files")
    if missing_files:
        print(f"⚠️  Missing: {len(missing_files)} files (optional)")
    
    return len(found_files) > 0

def main():
    print("📝 GitHub Update Assistant")
    print("This will commit your BiMMuDa integration progress!")
    print()
    
    # Check if files are ready
    if not check_files_ready():
        print("❌ No files ready to commit")
        return
    
    print("\n🤔 Ready to update GitHub?")
    print("This will:")
    print("   • Add PROJECT_PROGRESS.md documenting your success")
    print("   • Commit your database and Python scripts") 
    print("   • Push everything to your GitHub repository")
    
    response = input("\nProceed with GitHub update? (y/n): ").lower()
    
    if response in ['y', 'yes']:
        success = run_git_commands()
        
        if success:
            print("\n🎊 FANTASTIC! Your progress is now on GitHub!")
            print("🔗 Check your repository to see the updates")
            print("\n📈 What you accomplished:")
            print("   ✅ Downloaded 381 Billboard hit songs with MIDI melodies")
            print("   ✅ Created professional SQLite database")
            print("   ✅ Built robust data processing scripts")
            print("   ✅ Documented everything clearly")
            print("   ✅ Ready for next phase!")
        else:
            print("\n💡 Don't worry - you can update GitHub manually:")
            print("   1. Copy PROJECT_PROGRESS.md to your repo")
            print("   2. Add your .py files and .db file")
            print("   3. Commit with message about BiMMuDa integration")
            print("   4. Push to GitHub")
    else:
        print("👍 No problem! You can update GitHub later.")
        print("Your progress is documented in PROJECT_PROGRESS.md")

if __name__ == "__main__":
    main()
