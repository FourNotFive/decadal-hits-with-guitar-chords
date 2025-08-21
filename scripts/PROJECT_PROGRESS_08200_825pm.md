# Guitar Chord Website Project - Progress Summary

**Date:** August 20, 2025  
**Project Status:** Foundation Complete - Ready for Website Development

## 🎯 PROJECT GOALS

Create a **decade-based guitar chord website** that allows users to:
- Browse top songs organized by decade (1960s, 1970s, 1980s, etc.)
- Select a song and view its chord progression
- See guitar tabs and chord diagrams
- View song information (potentially Wikipedia data)
- Possibly include sheet music

**Target User Experience:** User selects decade → browses top songs → clicks song → sees complete chord/tab/info display

## 📊 CURRENT DATA STATUS

### ✅ COMPLETED DATA PROCESSING
- **32,025 unique Billboard songs** (deduplicated from 349,495 chart entries)
- **890 McGill songs with detailed chord progressions** (processed and stored)
- **381 BiMMuDa songs with MIDI data** (loaded but not yet integrated)
- **Average 134.9 chords per McGill song**

### 📁 PROJECT STRUCTURE
```
Music_Project_Clean/
├── data/
│   ├── databases/
│   │   ├── billboard_data.db (BiMMuDa data - 381 songs)
│   │   ├── music_database.db (Main database - 61.3 MB)
│   │   └── music_database_backup.db (Backup - 12.5 MB)
│   ├── bimmuda/ (BiMMuDa MIDI files)
│   └── mcgill/
│       ├── annotations/annotations/ (890 chord annotation folders)
│       └── metadata/metadata/ (890 metadata folders)
├── scripts/ (Processing scripts)
├── archive/ (Archive folder)
└── doc/ (Documentation)
```

## 🗄️ DATABASE SCHEMA

### Main Database (`music_database.db`):
- **`billboard_hot100`** - 349,495 chart entries with weekly positions
- **`unique_songs`** - 32,025 deduplicated songs (perfect for decade browsing)
- **`mcgill_chord_data`** - 890 songs with chord progressions
- **`chordonomicon_data`** - Existing chord data
- **`song_chord_data`** - Empty table for future integration

### BiMMuDa Database (`billboard_data.db`):
- **`bimmuda_songs`** - 381 songs with MIDI analysis data

## 🎵 CHORD DATA FORMAT

McGill chord progressions are stored as pipe-separated sequences:
- Example: `A:min | C:maj | F:maj | G:maj | A:min | C:maj`
- 4 different annotation types per song: majmin.lab, majmin7.lab, etc.
- Time-stamped chord changes with start/end times
- Classic progressions identified (vi-IV-I-V type patterns)

## 🚧 INTEGRATION STATUS

### ✅ COMPLETED INTEGRATIONS:
1. Billboard Hot 100 data → `billboard_hot100` table
2. McGill chord annotations → `mcgill_chord_data` table  
3. BiMMuDa MIDI data → `billboard_data.db`
4. Song deduplication → `unique_songs` table

### ❌ PENDING INTEGRATIONS:
1. **McGill ↔ Billboard matching** - Need to link chord data to Billboard songs
2. **BiMMuDa ↔ Billboard matching** - Need to link MIDI data to Billboard songs  
3. **Decade categorization** - Group songs by decades based on chart dates
4. **Top songs identification** - Identify actual "top songs" per decade

## 🔧 TECHNICAL SETUP

### Environment:
- **IDE:** VS Code with workspace in `Music_Project_Clean`
- **Python:** 3.13 (confirmed working)
- **Database:** SQLite3
- **OS:** Windows (PowerShell terminal in VS Code)

### Key Scripts Created:
- `process_mcgill_chords.py` - Processes McGill chord files into database
- `check_chord_data.py` - Verifies chord data processing

## 🎯 IMMEDIATE NEXT STEPS

### Phase 1: Website Foundation (NEXT)
1. **Create decade categorization system**
   - Analyze Billboard chart dates to group songs by decades
   - Identify top songs per decade (peak position, weeks on chart, etc.)

2. **Build basic web interface**
   - HTML/CSS/JavaScript frontend
   - Python Flask/FastAPI backend
   - Display decades → songs → chord progressions

### Phase 2: Enhanced Features
3. **Add guitar chord diagrams** - Visual chord charts
4. **Generate guitar tabs** - Convert chord progressions to tablature
5. **Integrate song metadata** - Artist info, Wikipedia data
6. **BiMMuDa integration** - Add MIDI analysis features

### Phase 3: Polish & Deploy
7. **Responsive design** - Mobile-friendly interface
8. **Search functionality** - Find songs by artist, title, chords
9. **Export features** - PDF tabs, chord sheets
10. **Web deployment** - Host online for public use

## 💡 KEY DESIGN DECISIONS MADE

1. **Decade-based navigation** - Primary user flow through time periods
2. **McGill as chord source** - Highest quality chord annotation data
3. **Simplified chord display** - Focus on major/minor chord progressions
4. **Billboard as song authority** - Ensures "top songs" are actually popular hits

## 🔍 DATA QUALITY NOTES

- McGill covers ~890 songs vs 32,025 Billboard songs (2.8% overlap expected)
- Need matching strategy: fuzzy string matching on artist/title
- Some McGill files contain "X" (unknown) and "N" (no chord) markers
- Chord progressions show clear patterns suitable for guitar playing

## 📝 FOR NEXT SESSION

**To continue this project effectively, the next assistant needs:**

1. **Context**: Building decade-based guitar chord website from processed music data
2. **Current status**: Foundation complete, ready for website development
3. **Immediate goal**: Create decade categorization and basic web interface
4. **Technical setup**: VS Code in `Music_Project_Clean` folder, Python 3.13
5. **Key insight**: Focus on linking McGill chord data to Billboard decade categories

**Quick startup commands:**
```bash
cd Music_Project_Clean
cd scripts
python check_chord_data.py  # Verify current data status
```

This project has solid data foundations and is ready for the exciting website development phase! 🎸