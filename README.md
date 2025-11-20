# Crossword Puzzle Generator and Solver - Version 3.0

## Overview

An interactive crossword puzzle generator and solver designed for educational purposes. This Python application automatically generates crossword puzzles from word lists, provides an intuitive GUI for solving, and exports puzzles to professional PDF format with a unique **Secret Code** feature.

**Author:** M. Reza Shahjahan  
**Version:** 3.0  
**Date:** November 2025

---

## Features

### Core Functionality
- **Automatic Crossword Generation** - Intelligent word placement with optimized intersections
- **Secret Code System** - Randomly selected cells spell a hidden word for bonus challenge
- **Interactive GUI** - Tkinter-based interface with smooth keyboard navigation
- **CSV Input Support** - Load custom word lists from CSV files
- **Real-time Progress Tracking** - Visual feedback showing completion percentage
- **Timer** - Tracks time spent solving the puzzle (starts on first click)
- **Answer Checking** - Instant validation with color-coded feedback
- **PDF Export** - Professional US Letter format (8.5" × 11") with customizable elements
- **PDF Preview** - View before saving

### Secret Code Feature 
- **Random Selection** - One word from your puzzle is automatically chosen as the secret code
- **Highlighted Cells** - Secret code cells appear with light blue background in the GUI
- **Thick Borders** - Secret cells marked with 2pt borders in PDF output
- **Vertical Clue** - Secret code clue displayed along the left edge of PDF
- **Bonus Challenge** - Puzzle isn't complete until the secret code is entered correctly
- **Dynamic Generation** - Different secret word selected each time from CSV files

### GUI Features
- **Smart Navigation**
  - Arrow keys for directional movement
  - Auto-advance after typing
  - Backspace to delete and move backward
  - Enter to move down
  - Automatic direction detection (across/down)
  
- **Visual Enhancements**
  - Numbered cells matching clue numbers (yellow labels)
  - Color-coded feedback (green=correct, pink=incorrect, light blue=secret cells)
  - Word and clue highlighting on cell selection
  - Scrollable puzzle grid and clues panel
  - Progress indicator showing filled cells
  - Timer display (HH:MM:SS format)
  - Secret code input field with real-time validation

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
python CrosswordV3.py yourfile.csv
```

**CSV Format Requirements:**
- Must contain two columns: `words` and `clues`
- Secret word will be randomly selected from this list
- Example:

```csv
words,clues
Python,A popular programming language
Algorithm,Step-by-step problem-solving procedure
Function,Reusable block of code
```

### Method 2: Using Default Word List

```bash
python CrosswordV3.py
```

Runs with the built-in astrobiology-themed word list (48 words).
Secret word defaults to "EMERGENCE" with predefined clue.

---

## How to Solve a Puzzle

1. **Start the Timer** - Click on any cell to begin timing
2. **Navigate** - Use arrow keys or mouse clicks
3. **Type Letters** - Automatically advances to next cell
4. **Notice Secret Cells** - Light blue cells form the secret code
5. **Toggle Direction** - Click the same cell twice to switch between across/down
6. **View Secret Clue** - Click "The Secret Code" button for the clue
7. **Enter Secret Code** - Type the word formed by highlighted cells
8. **Check Answers** - Click "Check Answers" button for validation
9. **Win** - Complete all cells AND enter correct secret code
10. **Export** - Save to PDF with custom title, description, and logos

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
| View Secret Clue | Click "The Secret Code" button |
| Enter Secret Code | Type in secret code field |

---

## PDF Export Features

- **US Letter size format** (612 × 792 points / 8.5" × 11")
- **Customizable elements:**
  - Puzzle title (top center, 16pt bold)
  - Multi-line description (bottom right, 6pt italic)
  - Left and right logos (bottom corners, 40×40 size)
- **Secret Code Display:**
  - Vertical text along left edge (6pt black font)
  - Shows full clue: "The secret code: [description]"
  - Positioned at x=10 for edge proximity
- **Cell Borders:**
  - Thin borders (0.5pt) for normal cells
  - Thick borders (2pt) for secret code cells
  - Two-pass rendering for consistent appearance
- **Automatic grid optimization:**
  - Removes excess black cells
  - Centers the puzzle
  - Scales to fit page
- **Organized clues:**
  - ACROSS and DOWN sections (9pt bold headers)
  - Numbered to match grid (7.5pt text)
  - Automatic text truncation for long clues

---

## Code Structure

### Main Components

#### 1. `generate_crossword(words_and_clues, height, width, is_csv)`
Generates the crossword grid from word list.
- Sorts words by length (longest first)
- Places first word horizontally in center
- Finds intersections for remaining words
- Selects secret word and cells
- Returns `CrosswordGenerator` object

#### 2. `select_secret_word_from_list(words_and_clues, is_csv)`
Manages secret code selection.
- Randomly picks one word from CSV files
- Uses default "EMERGENCE" for built-in list
- Sets global SECRET_WORD and SECRET_CLUE
- Reports selection to console

#### 3. `select_secret_cells(gen, secret_word)`
Chooses random cells for secret code.
- Collects all non-black cells
- Shuffles and selects required number
- Returns list of (row, col) coordinates

#### 4. `CrosswordGenerator` Class
Manages grid and word placement logic.
- **Attributes:**
  - `secret_cells` - List of (row, col) tuples for secret code
- **Methods:**
  - `is_valid_placement()` - Validates word positions
  - `place_word()` - Places word on grid
  - `find_and_place_word()` - Finds optimal position

#### 5. `CrosswordGUI` Class
Interactive interface with full puzzle-solving features.
- **Attributes:**
  - `secret_word` - The secret code word
  - `secret_clue` - The secret code clue text
  - `secret_cells` - List of secret cell positions
  - `secret_entry` - Entry widget for secret code input
- **Key Methods:**
  - `check()` - Validates answers AND secret code
  - `check_secret_code()` - Real-time secret code validation
  - `show_secret_clue()` - Displays secret clue popup
  - `update_timer()` - Updates elapsed time display
  - `create_pdf_content()` - Creates PDF with secret code features
  - `export_to_pdf()` - Creates PDF file
  - `preview_pdf()` - Opens temporary PDF preview

#### 6. `load_words_from_csv(csv_file)`
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

### Default Secret Word
Modify the defaults if not using CSV:

```python
DEFAULT_SECRET_WORD = "EMERGENCE"
DEFAULT_SECRET_CLUE = "The secret code: A phenomenon where..."
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

## Secret Code System Details

### How It Works
1. **Word Selection:**
   - CSV files: Random selection from your word list
   - Default list: Uses "EMERGENCE" (9 letters)

2. **Cell Selection:**
   - Collects all non-black cells from generated puzzle
   - Randomly shuffles the list
   - Selects first N cells (where N = length of secret word)

3. **GUI Display:**
   - Secret cells have light blue (#ADD8E6) background
   - Button reveals the secret clue
   - Entry field validates in real-time (turns green when correct)

4. **PDF Output:**
   - Thin borders (0.5pt) drawn on all cells first
   - Thick borders (2pt) overlaid on secret cells second
   - Vertical clue text positioned at left edge (x=10, y varies)

5. **Win Condition:**
   - All cells must be filled correctly
   - Secret code must match exactly (case-insensitive)
   - Timer stops when both conditions met

---

## Timer Functionality

- **Starts:** When user clicks on any cell for the first time
- **Displays:** HH:MM:SS format in real-time
- **Updates:** Every second via root.after() callback
- **Stops:** When puzzle is 100% complete and secret code is correct
- **Shows:** Final time in congratulation message

---

## CSV Input Feature

Allows dynamic puzzle generation from external files:
- No code modification needed
- Different secret word selected each time
- Easy to create multiple puzzles
- Great for educational environments
- Supports any number of words (grid size permitting)

**Console Output Example:**
```
Loading words from CSV file: astrobio_terms.csv
Loaded 50 words from CSV file.
Secret word selected from CSV: EXOPLANET (9 letters)
Successfully generated crossword with 48 words.
Secret code initialized with 9 cells.
```

---

## Tips for Best Results

1. **Word Selection:**
   - Use words of varying lengths (5-15 letters)
   - Include common letters for better intersections (E, A, T, O, R, etc.)
   - Aim for 20-50 words for optimal puzzles
   - Choose memorable words for secret code

2. **Grid Size:**
   - Set to 2× longest word length minimum
   - Increase if many words fail to place
   - Default 40×40 works for most puzzles

3. **Secret Code:**
   - Medium-length words (7-12 letters) work best
   - Too short = too easy, too long = hard to spot
   - Clue should be descriptive but not give away the answer

4. **PDF Export:**
   - Use PNG/JPG logos for best quality
   - Keep logos simple (40×40 display size)
   - Test with "Preview PDF" before final export
   - Verify secret code cells have thick borders

---

## Error Handling

The script includes comprehensive validation:
- ✓ CSV format validation
- ✓ Missing column detection
- ✓ Empty word/clue detection
- ✓ Grid dimension validation
- ✓ File not found handling
- ✓ PDF generation error catching
- ✓ Secret cell availability check
- ✓ Logo file existence verification

---

## Version History

**v3.0** (November 2025)
- Added Secret Code feature with highlighted cells
- Changed PDF page size from A4 to US Letter (8.5" × 11")
- Secret code clue displayed vertically on PDF left edge
- Thick borders (2pt) for secret cells in PDF
- Two-pass border rendering for consistent appearance
- Secret code validation in GUI
- Updated documentation with secret code details
- Improved timer and progress tracking

**v2.0** (November 2025)
- Added CSV input support
- Added timer functionality
- Interactive GUI with Tkinter
- PDF export with customization
- Real-time answer checking
- Multi-line description support

**v1.0**
- Basic crossword generation
- Simple console output

---

## Educational Use Case

Originally designed for **Astrobiology education** with 48 terms covering:
- Space exploration (Mars rovers, telescopes, spacecraft)
- Exoplanets and habitability zones
- Origins of life theories (panspermia, clay theory)
- Extremophiles and metabolism
- Famous missions and discoveries (Viking, Mariner, James Webb)
- Planetary science (Titan, Europa, Enceladus)

Perfect for:
- Classroom activities with competitive element (secret code)
- Study aids with built-in challenge
- Science competitions
- Educational workshops
- Team-building exercises

---

## Example Output

**Console:**
```
Loading words from CSV file: astrobio_terms.csv
Loaded 50 words from CSV file.
Secret word selected from CSV: METABOLISM (10 letters)
Successfully generated crossword with 48 words.
Secret code initialized with 10 cells.
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
**Solution:** Use absolute file paths, check file formats (PNG, JPG, GIF, BMP)

**Issue:** Timer not starting  
**Solution:** Click on a cell to begin timing

**Issue:** Secret code cells not highlighted  
**Solution:** Check console for "Secret code initialized" message; ensure enough cells available

**Issue:** Secret code borders not showing in PDF  
**Solution:** Verify secret_cells list is populated; check PDF viewer zoom level

**Issue:** Secret clue text cut off in PDF  
**Solution:** Clue is truncated at 230 characters; edit SECRET_CLUE for shorter text

---

## Advanced Customization

### Change Secret Cell Color
Edit in `__init__` method of CrosswordGUI:
```python
bg_color = '#ADD8E6' if is_secret_cell else 'white'  # Change #ADD8E6 to any hex color
```

### Adjust Secret Code Border Thickness
Edit in `create_pdf_content` method:
```python
c.setLineWidth(2)  # Change 2 to desired thickness (in points)
```

### Modify Secret Clue Position
Edit in `create_pdf_content` method:
```python
c.translate(10, clues_start_y - 10)  # Adjust x (10) and y offset (-10)
```

### Change Secret Clue Font Size
```python
c.setFont("Helvetica-Bold", 6)  # Change 6 to desired size
```

---

## Contact

For questions, improvements, or bug reports, please visit the GitHub repository or contact the author.

**Happy Puzzling!**
