# Crossword Puzzle Generator and Solver - Version 3.0

## Overview

An interactive crossword puzzle generator and solver designed for educational purposes. This Python application automatically generates crossword puzzles from word lists, provides an intuitive GUI for solving, and exports puzzles to professional PDF format.

**Author:** M.Reza Shahjahan  
**Version:** 3.0  
**Date:** November 2025

---

## Features

### Core Functionality
- **Automatic Crossword Generation** - Intelligent word placement with optimized intersections
- **Interactive GUI** - Tkinter-based interface with smooth keyboard navigation
- **CSV Input Support** - Load custom word lists from CSV files
- **Real-time Progress Tracking** - Visual feedback showing completion percentage
- **Timer** - Tracks time spent solving the puzzle (starts on first click)
- **Answer Checking** - Instant validation with color-coded feedback
- **PDF Export** - Professional A4 format with customizable elements
- **PDF Preview** - View before saving

### GUI Features
- **Smart Navigation**
  - Arrow keys for directional movement
  - Auto-advance after typing
  - Backspace to delete and move backward
  - Enter to move down
  - Automatic direction detection (across/down)
  
- **Visual Enhancements**
  - Numbered cells matching clue numbers
  - Color-coded feedback (green=correct, pink=incorrect)
  - Word and clue highlighting on cell selection
  - Scrollable puzzle grid and clues panel
  - Progress indicator showing filled cells

- **Customization Options**
  - Custom puzzle title
  - Multi-line description support
  - Left and right logo placement
  - Automatic grid trimming (removes excess black cells)

---

## Requirements

```python
tkinter          # GUI framework (included with Python)
pandas           # CSV file handling
reportlab        # PDF generation
```

### Installation

```bash
pip install pandas reportlab
```

---

## Usage

### Method 1: Using a CSV File

```bash
python crosswordV3.py yourfile.csv
```

**CSV Format Requirements:**
- Must contain two columns: `words` and `clues`
- Example:

```csv
words,clues
Python,A popular programming language
Algorithm,Step-by-step problem-solving procedure
Function,Reusable block of code
```

### Method 2: Using Default Word List

```bash
python crosswordV3.py
```

Runs with the built-in astrobiology-themed word list (50 words).

---

## How to Solve a Puzzle

1. **Start the Timer** - Click on any cell to begin timing
2. **Navigate** - Use arrow keys or mouse clicks
3. **Type Letters** - Automatically advances to next cell
4. **Toggle Direction** - Click the same cell twice to switch between across/down
5. **Check Answers** - Click "Check Answers" button for validation
6. **Clear All** - Reset the entire puzzle
7. **Export** - Save to PDF with custom title, description, and logos

---

## GUI Controls

| Action | Key/Method |
|--------|------------|
| Move Up | ↑ Arrow Key |
| Move Down | ↓ Arrow Key or Enter |
| Move Left | ← Arrow Key |
| Move Right | → Arrow Key |
| Delete & Move Back | Backspace |
| Toggle Direction | Click same cell twice |
| Auto-advance | Type any letter |

---

## PDF Export Features

- **A4 size format** (595 × 842 points)
- **Customizable elements:**
  - Puzzle title (top center)
  - Multi-line description (bottom)
  - Left and right logos (bottom corners, 40×40 size)
- **Automatic grid optimization:**
  - Removes excess black cells
  - Centers the puzzle
  - Scales to fit page
- **Organized clues:**
  - ACROSS and DOWN sections
  - Numbered to match grid
  - Automatic text truncation for long clues

---

## Code Structure

### Main Components

#### 1. `generate_crossword(words_and_clues, height, width)`
Generates the crossword grid from word list.
- Sorts words by length (longest first)
- Places first word horizontally in center
- Finds intersections for remaining words
- Returns `CrosswordGenerator` object

#### 2. `CrosswordGenerator` Class
Manages grid and word placement logic.
- **Methods:**
  - `is_valid_placement()` - Validates word positions
  - `place_word()` - Places word on grid
  - `find_and_place_word()` - Finds optimal position

#### 3. `CrosswordGUI` Class
Interactive interface with full puzzle-solving features.
- **Key Methods:**
  - `check()` - Validates answers with visual feedback
  - `update_timer()` - Updates elapsed time display
  - `export_to_pdf()` - Creates PDF file
  - `preview_pdf()` - Opens temporary PDF preview

#### 4. `load_words_from_csv(csv_file)`
Loads words and clues from CSV file.
- Validates required columns
- Removes rows with missing data
- Returns list of (word, clue) tuples

---

## Configuration

### Grid Size
Adjust based on your longest word:

```python
GRID_SIZE = 40  # Recommended for words up to ~20 characters
```

### Default Word List
Modify the `words_and_clues_list` in the main section:

```python
words_and_clues_list = [
    ("WORD1", "Clue for word 1"),
    ("WORD2", "Clue for word 2"),
    # ... add more
]
```

---

## Timer Functionality (New in v3.0)

- **Starts:** When user clicks on any cell for the first time
- **Displays:** HH:MM:SS format in real-time
- **Stops:** When puzzle is 100% complete and correct
- **Shows:** Final time in congratulation message

---

## CSV Input Feature (New in v3.0)

Allows dynamic puzzle generation from external files:
- No code modification needed
- Easy to create multiple puzzles
- Great for educational environments
- Supports any number of words (grid size permitting)

---

## Tips for Best Results

1. **Word Selection:**
   - Use words of varying lengths
   - Include common letters for better intersections
   - Aim for 20-50 words for optimal puzzles

2. **Grid Size:**
   - Set to 2× longest word length
   - Increase if many words fail to place

3. **PDF Export:**
   - Use PNG/JPG logos for best quality
   - Keep logos simple (40×40 display size)
   - Test with "Preview PDF" before final export

---

## Error Handling

The script includes comprehensive validation:
- ✓ CSV format validation
- ✓ Missing column detection
- ✓ Empty word/clue detection
- ✓ Grid dimension validation
- ✓ File not found handling
- ✓ PDF generation error catching

---

## Version History

**v3.0** (November 2025)
- Added CSV input support
- Added timer functionality
- Removed import/export word list buttons
- Timer starts on first cell click
- Improved congratulation message with time display

**v2.0** (November 2025)
- Interactive GUI with Tkinter
- PDF export with customization
- Real-time answer checking
- Multi-line description support

**v1.0**
- Basic crossword generation
- Simple console output

---

## Educational Use Case

Originally designed for **Astrobiology education** with 50 terms covering:
- Space exploration (Mars rovers, telescopes)
- Exoplanets and habitability
- Origins of life theories
- Extremophiles and metabolism
- Famous missions and discoveries

Perfect for:
- Classroom activities
- Study aids
- Science competitions
- Educational workshops

---

## Example Output

```
Loading words from CSV file: astrobio_terms.csv
Loaded 50 words from CSV file.
Successfully generated crossword with 48 words.
```

**On Completion:**
```
Congratulations! You solved the puzzle correctly!
Time spent: 00:15:42
```

---

## License & Credits

Created by **M. Reza Shahjahan**  
GitHub: [AstroBioReza/Crossword](https://github.com/AstroBioReza/Crossword)

Feel free to use and modify for educational purposes!

---

## Troubleshooting

**Issue:** Words not placing  
**Solution:** Increase `GRID_SIZE` value

**Issue:** CSV not loading  
**Solution:** Ensure columns named exactly `words` and `clues`

**Issue:** PDF logos not showing  
**Solution:** Use absolute file paths, check file formats (PNG, JPG)

**Issue:** Timer not starting  
**Solution:** Click on a cell to begin timing

---

## Contact

For questions, improvements, or bug reports, please visit the GitHub repository or contact the author.
