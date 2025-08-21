# Billboard Music Analysis Project

## 📁 Project Structure

```
Music_Project_Clean/
├── data/                   # All data files
│   ├── databases/         # SQLite database files
│   │   ├── music_database.db      # Main database (Billboard Hot 100 + metadata)
│   │   └── billboard_data.db      # BiMMuDa song metadata
│   ├── mcgill/           # McGill Billboard chord progressions
│   │   └── [3,560 .lab chord annotation files]
│   └── bimmuda/          # BiMMuDa melody data
│       └── [1,545 MIDI files + metadata CSVs]
├── scripts/              # Python scripts organized by purpose
│   ├── data_loading/     # Scripts for downloading/loading data
│   ├── analysis/         # Data analysis and exploration scripts  
│   └── utilities/        # Helper and maintenance scripts
├── archive/              # Backup and old files
└── docs/                 # Documentation and progress reports
```

## 🎯 Quick Start

1. **Database Location**: `data/databases/music_database.db`
2. **Chord Data**: `data/mcgill/` (3,560 .lab files) 
3. **Melody Data**: `data/bimmuda/` (1,545 MIDI files)
4. **Main Scripts**: `scripts/analysis/explore_songs.py`

## 🔗 Data Integration

- ✅ Billboard Hot 100 data (349K entries)
- ✅ McGill chord progressions (3,560 songs)
- ✅ BiMMuDa melodies (381 Billboard hits)
- 🎯 **Goal**: Connect songs with BOTH melody AND chord data

## 🚀 Next Steps

1. Load McGill chord data into database
2. Match songs across datasets
3. Create analysis and visualization tools
