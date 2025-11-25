"""
Interactive Crossword Puzzle Generator and Solver
=================================================

M. Reza shahjahan has designed this code to generate crossword puzzles from a list of words and clues related to Astrobiology for educational purposes.
provides an interactive GUI for solving them, and exports puzzles to PDF format.

Features:
---------
1. Automatic crossword grid generation with word placement optimization
2. Interactive GUI with keyboard navigation (arrow keys, auto-advance)
3. Real-time answer checking with visual feedback
4. Secret code feature - randomly selected cells that spell a hidden word
5. PDF export with customizable title, description, and logos (US Letter size)
6. PDF preview before saving
7. Multi-line description support
8. Automatic grid trimming (removes excess black cells)
9. Progress tracking and timer functionality
10. Secret code cells highlighted with thick borders in PDF

Main Components:
----------------
- CrosswordGenerator: Core logic for generating crossword grids with secret cell selection
- CrosswordGUI: Tkinter-based interactive interface with secret code input
- PDF Export: ReportLab-based PDF generation with US Letter (8.5" × 11") formatting

Usage:
------
1. Define your words and clues as a list of tuples: [(word, clue), ...]
   OR provide a CSV file with 'words' and 'clues' columns
2. Call generate_crossword() to create the puzzle grid
   - A secret word is automatically selected from the word list (or use default)
   - Random cells are selected and highlighted for the secret code
3. Create a CrosswordGUI instance and run() it
4. Users can:
   - Solve the puzzle interactively with color-coded feedback
   - Track progress and time spent
   - Enter the secret code formed by highlighted cells
   - Check their answers
   - Preview the PDF
   - Export to PDF with custom title, description, and logos

Author: Mohammad Reza Shahjahan
Date: November 2025
Version: 3.0
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import random
import json
import pandas as pd
import sys
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import os
import tempfile
import time


# ============================================================================
# SECRET CODE CONFIGURATION
# ============================================================================

# Default secret word (used if no CSV file provided)
DEFAULT_SECRET_WORD = "EMERGENCE"
DEFAULT_SECRET_CLUE = "The secret code: A phenomenon where a system's complex, novel properties arise from the interactions of its simpler parts, even though those properties are not present in the individual components."

# These will be set dynamically based on word list
SECRET_WORD = DEFAULT_SECRET_WORD
SECRET_CLUE = DEFAULT_SECRET_CLUE


# ============================================================================
# CROSSWORD GENERATION FUNCTIONS
# ============================================================================

def select_secret_word_from_list(words_and_clues, is_csv=False):
    """
    Randomly select a word and clue from the list to be the secret code.
    If is_csv is False (using default list), use the hardcoded EMERGENCE secret.
    
    Parameters:
    -----------
    words_and_clues : list of tuple
        List of (word, clue) tuples
    is_csv : bool
        True if words came from CSV file, False if using default list
    
    Returns:
    --------
    tuple
        (secret_word, secret_clue) selected from the list
    """
    global SECRET_WORD, SECRET_CLUE
    
    if is_csv and words_and_clues and len(words_and_clues) > 0:
        # CSV file provided - randomly select one word/clue pair
        selected = random.choice(words_and_clues)
        SECRET_WORD = selected[0].upper().replace(" ", "")  # Remove spaces, uppercase
        SECRET_CLUE = f"The secret code: {selected[1]}"
        print(f"Secret word selected from CSV: {SECRET_WORD} ({len(SECRET_WORD)} letters)")
    else:
        # No CSV file - use default EMERGENCE
        SECRET_WORD = DEFAULT_SECRET_WORD
        SECRET_CLUE = DEFAULT_SECRET_CLUE
        print("Using default secret word: EMERGENCE")
    
    return SECRET_WORD, SECRET_CLUE


def generate_crossword(words_and_clues, height=15, width=15, is_csv=False):
    """
    Generate a crossword puzzle grid from a list of words and clues.
    
    This function creates a crossword puzzle by placing words on a grid,
    ensuring they intersect at common letters. The first word is placed
    horizontally in the center, and subsequent words are placed to maximize
    intersections.
    
    Parameters:
    -----------
    words_and_clues : list of tuple
        List of (word, clue) tuples. Words will be converted to uppercase.
        Example: [("PYTHON", "A programming language"), ("CODE", "Program instructions")]
    
    height : int, optional (default=15)
        Height of the crossword grid in cells
    
    width : int, optional (default=15)
        Width of the crossword grid in cells
    
    is_csv : bool, optional (default=False)
        True if words came from CSV file, False if using default list
    
    Returns:
    --------
    CrosswordGenerator or None
        A CrosswordGenerator object with the completed puzzle, or None if
        generation fails. The generator contains the grid and word placements.
    
    Example:
    --------
    >>> words = [("PYTHON", "Programming language"), ("LOOP", "Iteration")]
    >>> puzzle = generate_crossword(words, height=10, width=10)
    >>> if puzzle:
    ...     print(f"Placed {len(puzzle.placements)} words")
    """
    # Select secret word from the list before generating puzzle
    select_secret_word_from_list(words_and_clues, is_csv)
    
    try:
        # Validate input
        if not words_and_clues:
            print("Error: No words provided.")
            return None
        
        if height <= 0 or width <= 0:
            print("Error: Grid dimensions must be positive.")
            return None
        
        # Validate word format
        for item in words_and_clues:
            if not isinstance(item, tuple) or len(item) != 2:
                print(f"Error: Invalid format for word entry: {item}")
                return None
            if not item[0] or not isinstance(item[0], str):
                print(f"Error: Invalid word: {item[0]}")
                return None
        
        gen = CrosswordGenerator(height, width)
        words_and_clues = sorted(words_and_clues, key=lambda x: len(x[0]), reverse=True)
    except Exception as e:
        print(f"Error initializing crossword: {str(e)}")
        return None
    
    if not words_and_clues: 
        return None
    
    # Place the first (longest) word horizontally in the center
    word, clue = words_and_clues[0]
    row = height // 2
    col = (width - len(word)) // 2
    vertical = False
    
    if not gen.place_word(word.upper(), row, col, vertical, False):
        return None
        
    gen.placements.append((row, col, vertical, word.upper(), clue))
    remaining = words_and_clues[1:]
    
    # Try to place remaining words with intersections
    for w_c in remaining:
        word, clue = w_c
        word = word.upper() 
        pos = gen.find_and_place_word(word, True) 
        
        if pos is None:
            continue
            
        row, col, vertical = pos
        gen.placements.append((row, col, vertical, word, clue))
    
    # Report statistics
    placed = len(gen.placements)
    total = len(words_and_clues)
    if placed < total:
        print(f"Warning: Only placed {placed}/{total} words. Consider increasing grid size.")
    
    # Select random cells for secret word
    gen.secret_cells = select_secret_cells(gen, SECRET_WORD)
    if gen.secret_cells:
        print(f"Secret code initialized with {len(gen.secret_cells)} cells.")
        
    return gen


def select_secret_cells(gen, secret_word):
    """
    Select cells from the puzzle grid that contain the letters to spell the secret word.
    
    This function finds cells in the crossword that contain each letter of the secret word,
    ensuring that the highlighted cells actually spell out the secret word when read.
    
    Parameters:
    -----------
    gen : CrosswordGenerator
        The generated crossword puzzle
    secret_word : str
        The secret word to spell out
    
    Returns:
    --------
    list of tuple
        List of (row, col) coordinates for cells that contain the letters of the secret word,
        or empty list if not enough matching cells available
    """
    selected_cells = []
    
    # For each letter in the secret word, find a cell containing that letter
    for letter in secret_word:
        # Collect all cells that contain this letter and haven't been selected yet
        available_cells = []
        for r in range(gen.height):
            for c in range(gen.width):
                if gen.grid[r][c] == letter and (r, c) not in selected_cells:
                    available_cells.append((r, c))
        
        # If no cells available with this letter, we can't complete the secret word
        if not available_cells:
            print(f"Warning: Could not find cell with letter '{letter}' for secret word '{secret_word}'")
            return []
        
        # Randomly select one cell with this letter
        selected_cell = random.choice(available_cells)
        selected_cells.append(selected_cell)
    
    return selected_cells


# ============================================================================
# CROSSWORD GENERATOR CLASS
# ============================================================================

class CrosswordGenerator:
    """
    Crossword puzzle grid generator with intelligent word placement.
    
    This class manages the crossword grid and provides methods for placing
    words with proper validation, ensuring words don't overlap incorrectly
    and maintain proper spacing between parallel words.
    
    Attributes:
    -----------
    height : int
        Number of rows in the grid
    width : int
        Number of columns in the grid
    grid : list of list
        2D array representing the crossword grid. '#' for empty cells,
        letters for filled cells
    placements : list of tuple
        List of (row, col, vertical, word, clue) for each placed word
    
    Methods:
    --------
    is_valid_placement(word, row, col, vertical, require_intersection)
        Check if a word can be placed at the given position
    place_word(word, row, col, vertical, require_intersection)
        Place a word on the grid if valid
    find_and_place_word(word, require_intersection)
        Find a valid position for a word and place it
    """
    def __init__(self, height, width):
        """
        Initialize a new crossword grid.
        
        Parameters:
        -----------
        height : int
            Number of rows in the grid
        width : int
            Number of columns in the grid
        """
        self.height = height
        self.width = width
        self.grid = [['#' for _ in range(width)] for _ in range(height)]
        self.placements = []
        self.secret_cells = []  # Will store (row, col) tuples for secret code cells
    
    # ... (include is_valid_placement and find_and_place_word from the previous revision)
    def is_valid_placement(self, word, row, col, vertical, require_intersection=False):
        word_len = len(word)
        intersected = False
        
        if vertical:
            if row + word_len > self.height:
                return False
        else:
            if col + word_len > self.width:
                return False

        # Check space before the word
        if (vertical and row > 0 and self.grid[row - 1][col] != '#') or \
           (not vertical and col > 0 and self.grid[row][col - 1] != '#'):
            return False

        # Check space after the word
        if (vertical and row + word_len < self.height and self.grid[row + word_len][col] != '#') or \
           (not vertical and col + word_len < self.width and self.grid[row][col + word_len] != '#'):
            return False

        # Check cell-by-cell conflicts and intersections
        for i in range(word_len):
            r = row + i if vertical else row
            c = col + i if not vertical else col
            
            cell = self.grid[r][c]
            char = word[i]
            
            if cell != '#' and cell != char:
                return False
            
            if cell != '#':
                intersected = True
            
            # Cross-word separation check
            if cell == '#':
                if vertical:
                    # Check left and right
                    if c > 0 and self.grid[r][c - 1] != '#': return False
                    if c < self.width - 1 and self.grid[r][c + 1] != '#': return False
                else: # Horizontal
                    # Check up and down
                    if r > 0 and self.grid[r - 1][c] != '#': return False
                    if r < self.height - 1 and self.grid[r + 1][c] != '#': return False

        if require_intersection and not intersected:
            return False

        return True

    def place_word(self, word, row, col, vertical, require_intersection=False):
        """
        Place a word on the grid if the placement is valid.
        
        Parameters:
        -----------
        word : str
            The word to place (should be uppercase)
        row : int
            Starting row position
        col : int
            Starting column position
        vertical : bool
            True for vertical placement, False for horizontal
        require_intersection : bool, optional
            If True, word must intersect with existing words
        
        Returns:
        --------
        bool
            True if word was placed successfully, False otherwise
        """
        if not self.is_valid_placement(word, row, col, vertical, require_intersection):
            return False

        for i in range(len(word)):
            r = row + i if vertical else row
            c = col + i if not vertical else col
            self.grid[r][c] = word[i]
            
        return True

    def find_and_place_word(self, word, require_intersection):
        """
        Find a valid position for a word and place it on the grid.
        
        This method attempts to find intersections with existing words,
        or if no intersections are found (or required), tries all positions.
        
        Parameters:
        -----------
        word : str
            The word to place (should be uppercase)
        require_intersection : bool
            If True, only places where word intersects existing words
        
        Returns:
        --------
        tuple or None
            (row, col, vertical) if placement successful, None otherwise
        """
        if require_intersection:
            for p_r, p_c, p_vertical, p_word, _ in self.placements:
                for existing_i, existing_char in enumerate(p_word):
                    for new_i, new_char in enumerate(word):
                        if existing_char == new_char:
                            if p_vertical:
                                new_r = p_r + existing_i
                                new_c = p_c - new_i
                                new_vertical = False
                            else:
                                new_r = p_r - new_i
                                new_c = p_c + existing_i
                                new_vertical = True
                            
                            if self.place_word(word, new_r, new_c, new_vertical, True):
                                return new_r, new_c, new_vertical
        
        directions = [False, True]
        for vertical in directions:
            for row in range(self.height):
                for col in range(self.width):
                    if self.place_word(word, row, col, vertical, require_intersection):
                        return row, col, vertical
        
        return None


# ============================================================================
# INTERACTIVE GUI CLASS
# ============================================================================

class CrosswordGUI:
    """
    Interactive GUI for solving crossword puzzles.
    
    Provides a Tkinter-based interface with:
    - Scrollable crossword grid with numbered cells
    - Automatic keyboard navigation (arrows, auto-advance)
    - Real-time answer checking with color feedback
    - Clues panel with ACROSS and DOWN sections
    - PDF export with preview functionality
    - Customizable title, description, and logos
    
    Attributes:
    -----------
    gen : CrosswordGenerator
        The puzzle generator containing the grid and placements
    root : tk.Tk
        Main Tkinter window
    entries : list of list
        2D array of Entry widgets for the grid
    current_direction : str
        Current typing direction ('across' or 'down')
    number_map : dict
        Maps (row, col) to clue numbers
    across_clues : list
        List of across clues with numbers
    down_clues : list
        List of down clues with numbers
    
    Navigation Controls:
    --------------------
    - Arrow keys: Move between cells
    - Type letter: Auto-advance in current direction
    - Backspace: Delete and move backward
    - Enter: Move down
    - Tab: Next cell
    
    Methods:
    --------
    check()
        Check all answers and provide visual feedback
    export_to_pdf()
        Save puzzle to PDF file
    preview_pdf()
        Preview PDF before saving
    run()
        Start the GUI main loop
    """
    def __init__(self, gen):
        """
        Initialize the crossword GUI.
        
        Parameters:
        -----------
        gen : CrosswordGenerator
            The generated crossword puzzle to display
        """
        self.gen = gen
        self.root = tk.Tk()
        self.root.title("Interactive Crossword Puzzle")
        self.entries = [[None for _ in range(gen.width)] for _ in range(gen.height)]
        self.current_direction = 'across'  # Track current direction: 'across' or 'down'
        
        # Initialize timer (will start on first click)
        self.start_time = None
        self.timer_running = False
        self.timer_started = False
        
        # Secret code tracking
        self.secret_word = SECRET_WORD
        self.secret_clue = SECRET_CLUE
        self.secret_cells = gen.secret_cells if hasattr(gen, 'secret_cells') else []
        
        # Use PanedWindow for resizable sections
        paned_window = tk.PanedWindow(self.root, orient='horizontal', sashrelief='raised', sashwidth=5)
        paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side: puzzle only (no controls)
        left_frame = tk.Frame(paned_window)
        paned_window.add(left_frame, stretch='always')
        
        # Right side: controls and clues
        right_container = tk.Frame(paned_window)
        paned_window.add(right_container, stretch='always')
        
        # Create puzzle area with scrollbars in left frame (no controls above or below)
        puzzle_frame = tk.Frame(left_frame)
        puzzle_frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(puzzle_frame, bg='white')
        v_scrollbar = tk.Scrollbar(puzzle_frame, orient='vertical', command=canvas.yview)
        h_scrollbar = tk.Scrollbar(puzzle_frame, orient='horizontal', command=canvas.xview)
        
        grid_frame = tk.Frame(canvas)
        
        # Create scrollable window
        canvas.create_window((0, 0), window=grid_frame, anchor='nw')
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        canvas.pack(side='left', fill='both', expand=True)
        
        # Configure canvas to update scrollregion
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        grid_frame.bind('<Configure>', configure_scroll_region)
        
        # Add mouse wheel scrolling support only when hovering over puzzle area
        self.puzzle_scroll_active = False
        
        def on_puzzle_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_puzzle_shift_mousewheel(event):
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        def enable_puzzle_scroll(event):
            self.puzzle_scroll_active = True
            self.root.bind_all("<MouseWheel>", on_puzzle_mousewheel)
            self.root.bind_all("<Shift-MouseWheel>", on_puzzle_shift_mousewheel)
        
        def disable_puzzle_scroll(event):
            self.puzzle_scroll_active = False
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Shift-MouseWheel>")
        
        # Bind mouse enter/leave events for puzzle area
        puzzle_frame.bind("<Enter>", enable_puzzle_scroll)
        puzzle_frame.bind("<Leave>", disable_puzzle_scroll)
        canvas.bind("<Enter>", enable_puzzle_scroll)
        canvas.bind("<Leave>", disable_puzzle_scroll)

        # --- 1. Assign Numbers and Prepare Clues ---
        sorted_placements = sorted(self.gen.placements, key=lambda p: (p[0], p[1]))
        number_map = {}
        for i, p in enumerate(sorted_placements, 1):
            r, c = p[0], p[1]
            number_map[(r, c)] = i

        # --- 2. Create Grid Cells ---
        for r in range(gen.height):
            for c in range(gen.width):
                # Use a small frame for each cell to hold number and entry box
                cell_frame = tk.Frame(grid_frame, borderwidth=2, relief="solid", bg='white')
                cell_frame.grid(row=r, column=c, sticky="nsew")

                if gen.grid[r][c] == '#':
                    # Black block
                    cell_frame.config(bg='black')
                else:
                    # White cell for a letter
                    # Check if this is a secret cell
                    is_secret_cell = (r, c) in self.secret_cells
                    
                    # Entry box for user input (create FIRST so number appears on top)
                    # Secret cells have red border, normal cells have gray border
                    entry = tk.Entry(cell_frame, width=2, font=('Arial', 14, 'bold'), justify='center', 
                                     bd=0, highlightthickness=2 if is_secret_cell else 1, 
                                     highlightbackground='red' if is_secret_cell else 'gray',
                                     relief='flat', takefocus=True, bg='white') 
                    entry.pack(expand=True, fill='both', padx=4, pady=4)
                    self.entries[r][c] = entry
                    
                    # Bind key events for single character limit and navigation
                    entry.bind('<KeyRelease>', lambda e, row=r, col=c: self.on_key_release(e, row, col))
                    entry.bind('<FocusIn>', lambda e, row=r, col=c: self.on_focus(e, row, col))
                    entry.bind('<Button-1>', lambda e, row=r, col=c: self.on_click(e, row, col))
                    entry.bind('<BackSpace>', lambda e, row=r, col=c: self.on_backspace(e, row, col))
                    entry.bind('<Return>', lambda e, row=r, col=c: self.move_down(row, col))
                    entry.bind('<Up>', lambda e, row=r, col=c: self.move_up(row, col))
                    entry.bind('<Down>', lambda e, row=r, col=c: self.move_down(row, col))
                    entry.bind('<Left>', lambda e, row=r, col=c: self.move_left(row, col))
                    entry.bind('<Right>', lambda e, row=r, col=c: self.move_right(row, col))
                    
                    # Add number if start (create AFTER entry so it's on top)
                    if (r, c) in number_map:
                        # Number label with much better visibility
                        num_label = tk.Label(cell_frame, text=str(number_map[(r, c)]), 
                                             font=('Arial', 6, 'bold'), 
                                             bg='yellow', fg='black', 
                                             padx=3, pady=2, borderwidth=1, relief='solid')
                        # Use place() to position the number label in the top-left corner (on top of entry)
                        num_label.place(x=2, y=2, anchor='nw')
                        num_label.lift()  # Ensure it's on top
                    
                # Standard size for all cells (smaller for larger grids)
                cell_size = max(25, min(40, 600 // max(gen.height, gen.width)))
                grid_frame.grid_columnconfigure(c, weight=1, minsize=cell_size)
                grid_frame.grid_rowconfigure(r, weight=1, minsize=cell_size)

        # --- 3. Create Clues Section ---
        across = []
        down = []
        for p in sorted_placements:
            pr, pc, vertical, word, clue = p
            num = number_map[(pr, pc)]
            if not vertical:
                across.append(f"{num}. {clue}")
            else:
                down.append(f"{num}. {clue}")
        
        # Store for PDF export
        self.number_map = number_map
        self.across_clues = across
        self.down_clues = down
        
        # --- 4. Title, Description, and Logo fields (at top of right side) ---
        controls_top_frame = tk.Frame(right_container, bg='white', padx=5, pady=5)
        controls_top_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(controls_top_frame, text="Puzzle Title:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=2)
        self.title_entry = tk.Entry(controls_top_frame, font=('Arial', 9), width=30)
        self.title_entry.grid(row=0, column=1, sticky='ew', pady=2)
        self.title_entry.insert(0, "Astrobiology Crossword")
        
        tk.Label(controls_top_frame, text="Description:", font=('Arial', 9, 'bold'), bg='white').grid(row=1, column=0, sticky='nw', pady=2)
        self.description_entry = tk.Text(controls_top_frame, font=('Arial', 8), width=30, height=2, wrap='word')
        self.description_entry.grid(row=1, column=1, sticky='ew', pady=2)
        self.description_entry.insert('1.0', "Designed by M. Reza Shahjahan\nGithub.com/AstroBioReza/Crossword")
        
        tk.Label(controls_top_frame, text="Left Logo:", font=('Arial', 9, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=2)
        logo_left_frame = tk.Frame(controls_top_frame, bg='white')
        logo_left_frame.grid(row=2, column=1, sticky='ew', pady=2)
        self.left_logo_path = tk.StringVar(value="")
        tk.Entry(logo_left_frame, textvariable=self.left_logo_path, font=('Arial', 8), state='readonly').pack(side='left', fill='x', expand=True)
        tk.Button(logo_left_frame, text="Browse", command=lambda: self.select_logo('left'), font=('Arial', 7)).pack(side='left', padx=(3, 0))
        
        tk.Label(controls_top_frame, text="Right Logo:", font=('Arial', 9, 'bold'), bg='white').grid(row=3, column=0, sticky='w', pady=2)
        logo_right_frame = tk.Frame(controls_top_frame, bg='white')
        logo_right_frame.grid(row=3, column=1, sticky='ew', pady=2)
        self.right_logo_path = tk.StringVar(value="")
        tk.Entry(logo_right_frame, textvariable=self.right_logo_path, font=('Arial', 8), state='readonly').pack(side='left', fill='x', expand=True)
        tk.Button(logo_right_frame, text="Browse", command=lambda: self.select_logo('right'), font=('Arial', 7)).pack(side='left', padx=(3, 0))
        
        controls_top_frame.grid_columnconfigure(1, weight=1)
        
        # Progress and Timer (in one line)
        progress_frame = tk.Frame(right_container, bg='white')
        progress_frame.pack(fill='x', pady=(0, 5))
        
        self.progress_label = tk.Label(progress_frame, text="Progress: 0%", font=('Arial', 8, 'bold'), bg='#E3F2FD', fg='#1976D2', pady=2)
        self.progress_label.pack(side='left', fill='x', expand=True, padx=(0, 2))
        self.update_progress()
        
        self.timer_label = tk.Label(progress_frame, text="Time: 00:00:00", font=('Arial', 8, 'bold'), bg='#FFF3E0', fg='#E65100', pady=2)
        self.timer_label.pack(side='left', fill='x', expand=True, padx=(2, 0))
        self.update_timer()
        
        # Create mapping from cell positions to clue numbers and words
        self.cell_to_clues = {}  # Maps (row, col) to list of (clue_num, direction)
        self.cell_to_words = {}  # Maps (row, col) to list of word cell positions
        for p in sorted_placements:
            pr, pc, vertical, word, clue = p
            clue_num = number_map[(pr, pc)]
            direction = 'down' if vertical else 'across'
            word_cells = []
            for i in range(len(word)):
                r = pr + i if vertical else pr
                c = pc if vertical else pc + i
                word_cells.append((r, c))
                if (r, c) not in self.cell_to_clues:
                    self.cell_to_clues[(r, c)] = []
                self.cell_to_clues[(r, c)].append((clue_num, direction))
            
            # Store word cells for each cell in the word
            for r, c in word_cells:
                if (r, c) not in self.cell_to_words:
                    self.cell_to_words[(r, c)] = {}
                self.cell_to_words[(r, c)][direction] = word_cells

        # Add scrollable clues section (middle of right side)
        clues_scroll_container = tk.Frame(right_container)
        clues_scroll_container.pack(fill='both', expand=True, pady=(0, 10))
        
        clues_canvas = tk.Canvas(clues_scroll_container, bg='white')
        clues_scrollbar = tk.Scrollbar(clues_scroll_container, orient='vertical', command=clues_canvas.yview)
        clues_frame = tk.Frame(clues_canvas, bg='white')
        
        clues_canvas.create_window((0, 0), window=clues_frame, anchor='nw')
        clues_canvas.configure(yscrollcommand=clues_scrollbar.set)
        
        clues_scrollbar.pack(side='right', fill='y')
        clues_canvas.pack(side='left', fill='both', expand=True)
        
        def configure_clues_scroll(event):
            clues_canvas.configure(scrollregion=clues_canvas.bbox('all'))
        clues_frame.bind('<Configure>', configure_clues_scroll)
        
        # Add mouse wheel scrolling support for clues area
        def on_clues_mousewheel(event):
            clues_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def enable_clues_scroll(event):
            self.root.bind_all("<MouseWheel>", on_clues_mousewheel)
        
        def disable_clues_scroll(event):
            self.root.unbind_all("<MouseWheel>")
        
        # Bind mouse enter/leave events for clues area
        clues_scroll_container.bind("<Enter>", enable_clues_scroll)
        clues_scroll_container.bind("<Leave>", disable_clues_scroll)
        clues_canvas.bind("<Enter>", enable_clues_scroll)
        clues_canvas.bind("<Leave>", disable_clues_scroll)
        
        # Store clue labels for highlighting
        self.clue_labels = {}
        
        tk.Label(clues_frame, text="ACROSS →", font=('Arial', 12, 'bold'), bg='white').pack(anchor='nw', pady=(0, 5))
        for i, clue_text in enumerate(across):
            clue_num = int(clue_text.split('.')[0])
            label = tk.Label(clues_frame, text=clue_text, justify='left', anchor='nw', bg='white', font=('Arial', 10))
            label.pack(anchor='nw')
            self.clue_labels[(clue_num, 'across')] = label
        
        tk.Label(clues_frame, text="\nDOWN ↓", font=('Arial', 12, 'bold'), bg='white').pack(anchor='nw', pady=(10, 5))
        for i, clue_text in enumerate(down):
            clue_num = int(clue_text.split('.')[0])
            label = tk.Label(clues_frame, text=clue_text, justify='left', anchor='nw', bg='white', font=('Arial', 10))
            label.pack(anchor='nw')
            self.clue_labels[(clue_num, 'down')] = label

        # --- 5. Secret Code (below clues) ---
        secret_frame = tk.Frame(right_container, bg='#F3E5F5', pady=5, padx=5)
        secret_frame.pack(fill='x', pady=(10, 0))
        
        secret_button = tk.Button(secret_frame, text="The Secret Code", command=self.show_secret_clue, 
                                   bg="#9C27B0", fg="white", font=('Arial', 9, 'bold'), width=15)
        secret_button.pack(side='left', padx=(0, 5))
        
        self.secret_entry = tk.Entry(secret_frame, font=('Arial', 9), width=20)
        self.secret_entry.pack(side='left', fill='x', expand=True)
        self.secret_entry.bind('<KeyRelease>', lambda e: self.check_secret_code())
        
        # --- 6. Buttons (at bottom of right side) ---
        buttons_frame = tk.Frame(right_container)
        buttons_frame.pack(fill='x', pady=(5, 0))
        
        clear_button = tk.Button(buttons_frame, text="Clear All", command=self.clear_all, bg="#F44336", fg="white", font=('Arial', 9, 'bold'))
        clear_button.pack(side='left', fill='x', expand=True, padx=(0, 3))
        
        check_button = tk.Button(buttons_frame, text="Check Answers", command=self.check, bg="#4CAF50", fg="white", font=('Arial', 9, 'bold'))
        check_button.pack(side='left', fill='x', expand=True, padx=(0, 3))
        
        preview_button = tk.Button(buttons_frame, text="Preview PDF", command=self.preview_pdf, bg="#FF9800", fg="white", font=('Arial', 9, 'bold'))
        preview_button.pack(side='left', fill='x', expand=True, padx=(0, 3))
        
        pdf_button = tk.Button(buttons_frame, text="Export to PDF", command=self.export_to_pdf, bg="#2196F3", fg="white", font=('Arial', 9, 'bold'))
        pdf_button.pack(side='left', fill='x', expand=True)

    def clear_all(self):
        """Clear all entries in the puzzle."""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all entries?"):
            for r in range(self.gen.height):
                for c in range(self.gen.width):
                    if self.entries[r][c] is not None:
                        self.entries[r][c].delete(0, tk.END)
                        # Restore white background for all cells (border remains red for secret cells)
                        self.entries[r][c].config(bg='white')
            self.secret_entry.delete(0, tk.END)
            self.update_progress()
    
    def show_secret_clue(self):
        """Display the secret code clue in a popup window."""
        messagebox.showinfo("Secret Code Clue", self.secret_clue)
    
    def check_secret_code(self):
        """Check if the entered secret code is correct."""
        entered = self.secret_entry.get().strip().upper()
        if entered == self.secret_word:
            self.secret_entry.config(bg='#90EE90')  # Light green
        elif entered:
            self.secret_entry.config(bg='white')
        else:
            self.secret_entry.config(bg='white')
    
    def update_progress(self):
        """Update the progress label showing completion percentage."""
        total_cells = 0
        filled_cells = 0
        
        for r in range(self.gen.height):
            for c in range(self.gen.width):
                if self.gen.grid[r][c] != '#':
                    total_cells += 1
                    if self.entries[r][c] and self.entries[r][c].get().strip():
                        filled_cells += 1
        
        if total_cells > 0:
            percentage = int((filled_cells / total_cells) * 100)
            self.progress_label.config(text=f"Progress: {percentage}% ({filled_cells}/{total_cells} cells)")
    
    def update_timer(self):
        """Update the timer display showing elapsed time."""
        if self.timer_running and self.start_time is not None:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        # Schedule next update in 1 second (even if not running, to start when needed)
        self.root.after(1000, self.update_timer)
    

    
    def check(self):
        """Checks the user's input against the generated grid."""
        incorrect_count = 0
        empty_count = 0
        
        for r in range(self.gen.height):
            for c in range(self.gen.width):
                if self.gen.grid[r][c] != '#':
                    entry = self.entries[r][c]
                    user_input = entry.get().strip().upper()
                    
                    if not user_input:
                        empty_count += 1
                    elif user_input != self.gen.grid[r][c]:
                        incorrect_count += 1
                        entry.config(bg="#FFC0CB") # Light red/pink
                    else:
                        entry.config(bg="#90EE90") # Light green
        
        for r in range(self.gen.height):
            for c in range(self.gen.width):
                if self.gen.grid[r][c] != '#' and not self.entries[r][c].get().strip() and self.entries[r][c].cget('bg') != 'lightgray':
                    # Restore white background (border remains red for secret cells)
                    self.entries[r][c].config(bg='white')
        
        # Check secret code
        secret_correct = self.secret_entry.get().strip().upper() == self.secret_word
        
        if incorrect_count == 0 and empty_count == 0 and secret_correct:
            # Stop timer
            self.timer_running = False
            if self.start_time is not None:
                elapsed = int(time.time() - self.start_time)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                messagebox.showinfo("Result", f"✅ Congratulations! You solved the puzzle correctly!\n\n⏱️ Time spent: {time_str}")
            else:
                messagebox.showinfo("Result", "✅ Congratulations! You solved the puzzle correctly!")
        else:
            error_msg = ""
            if empty_count > 0:
                error_msg += f"{empty_count} empty cell(s). "
            if incorrect_count > 0:
                error_msg += f"{incorrect_count} error(s) remain. "
            if not secret_correct:
                error_msg += "Secret code missing or incorrect. "
            messagebox.showinfo("Result", f"❌ Not all answers are correct yet. {error_msg}Keep trying!")

    def select_logo(self, position):
        """Open file dialog to select a logo image."""
        filename = filedialog.askopenfilename(
            title=f"Select {position.capitalize()} Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            if position == 'left':
                self.left_logo_path.set(filename)
            else:
                self.right_logo_path.set(filename)
    
    def limit_to_one_char(self, event, row, col):
        """Limit entry to one character and convert to uppercase."""
        entry = self.entries[row][col]
        text = entry.get().upper()
        
        # Keep only the last character if more than one
        if len(text) > 1:
            entry.delete(0, tk.END)
            entry.insert(0, text[-1])
        elif len(text) == 1:
            entry.delete(0, tk.END)
            entry.insert(0, text)
    
    def on_key_release(self, event, row, col):
        """Handle key release event - limit to one char and move cursor."""
        # Ignore special keys like arrows, shift, ctrl, etc.
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Shift_L', 'Shift_R', 
                            'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 
                            'Caps_Lock', 'Tab', 'Escape', 'BackSpace', 'Delete']:
            return
        
        # Limit to one character and convert to uppercase
        self.limit_to_one_char(event, row, col)
        
        # After typing a letter, move to the next cell based on current direction
        entry = self.entries[row][col]
        if entry.get().strip():  # Only move if a character was entered
            self.update_progress()
            if self.current_direction == 'across':
                self.move_right(row, col)
            else:  # down
                self.move_down(row, col)
    
    def on_backspace(self, event, row, col):
        """Handle backspace - clear current cell and move to previous cell."""
        entry = self.entries[row][col]
        
        # Clear the current cell
        entry.delete(0, tk.END)
        self.update_progress()
        
        # Move to previous cell based on current direction
        if self.current_direction == 'across':
            self.move_left(row, col)
        else:  # down
            self.move_up(row, col)
        
        # Prevent default backspace behavior
        return 'break'
    
    def on_focus(self, event, row, col):
        """Handle focus event - determine direction based on available words."""
        # Check if both across and down words exist at this position
        has_across = self.has_word_across(row, col)
        has_down = self.has_word_down(row, col)
        
        # Set initial direction when moving to a new cell
        if not hasattr(self, 'last_focused_cell') or self.last_focused_cell != (row, col):
            if has_across and has_down:
                # Default to across for new cells
                if not hasattr(self, 'current_direction') or self.current_direction not in ['across', 'down']:
                    self.current_direction = 'across'
            elif has_down:
                self.current_direction = 'down'
            elif has_across:
                self.current_direction = 'across'
            
            self.last_focused_cell = (row, col)
            # Highlight the corresponding clue
            self.highlight_clue(row, col)
    
    def on_click(self, event, row, col):
        """Handle mouse click - toggle between clues if cell has multiple clues."""
        # Start timer on first click
        if not self.timer_started:
            self.start_time = time.time()
            self.timer_running = True
            self.timer_started = True
        
        # Check if this cell has multiple clues
        cell_clues = self.cell_to_clues.get((row, col), [])
        
        # If clicking the same cell and it has multiple clues, toggle direction
        if hasattr(self, 'last_focused_cell') and self.last_focused_cell == (row, col) and len(cell_clues) > 1:
            # Get available directions for this cell
            available_directions = [direction for _, direction in cell_clues]
            
            # Toggle between available directions
            if 'across' in available_directions and 'down' in available_directions:
                self.current_direction = 'down' if self.current_direction == 'across' else 'across'
                self.highlight_clue(row, col)
    
    def highlight_clue(self, row, col):
        """Highlight the clue and entire word corresponding to the current cell and direction."""
        # Clear all previous highlights
        for label in self.clue_labels.values():
            label.config(bg='white', font=('Arial', 10))
        
        # Clear all cell highlights
        for r in range(self.gen.height):
            for c in range(self.gen.width):
                if self.entries[r][c] is not None:
                    current_bg = self.entries[r][c].cget('bg')
                    if current_bg in ['#E3F2FD', '#90EE90', '#FFC0CB']:
                        if current_bg == '#90EE90':  # Keep correct answers green
                            continue
                        elif current_bg == '#FFC0CB':  # Keep incorrect answers pink
                            continue
                        else:
                            # Restore white background (border remains red for secret cells)
                            self.entries[r][c].config(bg='white')
                    elif current_bg not in ['lightgray', 'black']:
                        # Restore white background (border remains red for secret cells)
                        self.entries[r][c].config(bg='white')
        
        # Get clues for this cell
        cell_clues = self.cell_to_clues.get((row, col), [])
        
        # Find and highlight the clue matching current direction
        for clue_num, direction in cell_clues:
            if direction == self.current_direction:
                if (clue_num, direction) in self.clue_labels:
                    self.clue_labels[(clue_num, direction)].config(bg='#FFFF99', font=('Arial', 10, 'bold'))
                
                # Highlight all cells in the current word
                if (row, col) in self.cell_to_words and direction in self.cell_to_words[(row, col)]:
                    word_cells = self.cell_to_words[(row, col)][direction]
                    for r, c in word_cells:
                        if self.entries[r][c] is not None:
                            current_bg = self.entries[r][c].cget('bg')
                            if current_bg not in ['#90EE90', '#FFC0CB']:
                                self.entries[r][c].config(bg='#E3F2FD')
                break
    
    def has_word_across(self, row, col):
        """Check if there's a horizontal word at this position."""
        # Check if there's at least one more cell to the left or right
        if col > 0 and self.entries[row][col-1] is not None:
            return True
        if col < self.gen.width - 1 and self.entries[row][col+1] is not None:
            return True
        return False
    
    def has_word_down(self, row, col):
        """Check if there's a vertical word at this position."""
        # Check if there's at least one more cell above or below
        if row > 0 and self.entries[row-1][col] is not None:
            return True
        if row < self.gen.height - 1 and self.entries[row+1][col] is not None:
            return True
        return False
    
    def move_up(self, row, col):
        """Move focus to the cell above."""
        for next_row in range(row - 1, -1, -1):
            if self.entries[next_row][col] is not None:
                self.entries[next_row][col].focus_set()
                self.current_direction = 'down'
                return
    
    def move_down(self, row, col):
        """Move focus to the cell below when Enter is pressed."""
        # Find the next valid cell below
        for next_row in range(row + 1, self.gen.height):
            if self.entries[next_row][col] is not None:
                self.entries[next_row][col].focus_set()
                self.current_direction = 'down'
                return
        
        # If no cell below, wrap to top of the same column
        for next_row in range(0, row):
            if self.entries[next_row][col] is not None:
                self.entries[next_row][col].focus_set()
                self.current_direction = 'down'
                return
    
    def move_left(self, row, col):
        """Move focus to the cell on the left."""
        for next_col in range(col - 1, -1, -1):
            if self.entries[row][next_col] is not None:
                self.entries[row][next_col].focus_set()
                self.current_direction = 'across'
                return
    
    def move_right(self, row, col):
        """Move focus to the cell on the right."""
        for next_col in range(col + 1, self.gen.width):
            if self.entries[row][next_col] is not None:
                self.entries[row][next_col].focus_set()
                self.current_direction = 'across'
                return

    def create_pdf_content(self, c, width, height):
        """
        Create the PDF content (used by both export and preview).
        
        Generates a complete crossword puzzle PDF with:
        - Title and custom description
        - Trimmed grid with proper cell sizing
        - Thin borders for normal cells, thick borders for secret code cells
        - Secret code clue text along the left edge (vertical, black)
        - Numbered cells for word starts
        - ACROSS and DOWN clues with proper formatting
        - Optional logos in bottom corners
        """
        # Get user-entered title and description
        puzzle_title = self.title_entry.get() or "Crossword Puzzle"
        puzzle_description = self.description_entry.get('1.0', 'end-1c').strip() or ""
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 25, puzzle_title)
        
        current_y = height - 40
        
        # Find the bounds of non-black cells to trim the grid
        min_row, max_row = self.gen.height, -1
        min_col, max_col = self.gen.width, -1
        
        for r in range(self.gen.height):
            for col in range(self.gen.width):
                if self.gen.grid[r][col] != '#':
                    min_row = min(min_row, r)
                    max_row = max(max_row, r)
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)
        
        # Calculate trimmed grid dimensions
        trimmed_height = max_row - min_row + 1
        trimmed_width = max_col - min_col + 1
        
        # Calculate grid dimensions
        max_grid_width = (width - 40) * 0.85
        max_grid_height = 650 * 0.85
        
        cell_size = min(
            max_grid_width / trimmed_width,
            max_grid_height / trimmed_height
        )
        
        # Center the grid
        grid_width = cell_size * trimmed_width
        grid_height = cell_size * trimmed_height
        start_x = (width - grid_width) / 2
        start_y = current_y - grid_height
        
        # Draw grid (only the trimmed portion)
        # First pass: draw all cells with normal borders
        for r in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                x = start_x + (col - min_col) * cell_size
                y = start_y + (max_row - r) * cell_size
                
                if self.gen.grid[r][col] == '#':
                    # Skip black cells - don't draw them
                    continue
                else:
                    # Draw cell with thin border
                    c.setLineWidth(0.5)
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=1)
                    c.setFillColorRGB(0, 0, 0)
                    
                    if (r, col) in self.number_map:
                        num_font_size = max(4.5, int(cell_size * 0.22))
                        c.setFont("Helvetica-Bold", num_font_size)
                        c.drawString(x + 2, y + cell_size - num_font_size - 1, str(self.number_map[(r, col)]))
        
        # Second pass: draw thick borders around secret cells
        c.setLineWidth(2)
        for r, col in self.secret_cells:
            if min_row <= r <= max_row and min_col <= col <= max_col:
                x = start_x + (col - min_col) * cell_size
                y = start_y + (max_row - r) * cell_size
                c.rect(x, y, cell_size, cell_size, fill=0, stroke=1)
        
        # Draw clues
        clues_start_y = start_y - 8
        
        # Draw vertical "The secret code:" text on the left side (counter-clockwise)
        c.saveState()
        c.translate(10, 110)  # Position near bottom of page (20 points from bottom edge)
        c.rotate(90)  # Rotate counter-clockwise
        c.setFont("Helvetica-Bold", 6)  # Smaller font (was 9, now 6)
        c.setFillColorRGB(0, 0, 0)  # Black color
        c.drawString(0, 0, self.secret_clue[:230])  # Show full text including "The secret code:"
        c.restoreState()
        
        # Draw all words on the right side (vertical, rotated 90 degrees)
        all_words = []
        for p in self.gen.placements:
            word = p[3]  # Get the word from placement tuple
            if word not in all_words:
                all_words.append(word)
        words_string = "-".join([w.lower() for w in all_words])
        
        c.saveState()
        c.translate(width - 5, 7)  # Position on right side
        c.rotate(90)  # Rotate counter-clockwise
        c.setFont("Helvetica", 4)  # Small font size
        c.setFillColorRGB(0, 0, 0)  # Black color
        c.drawString(0, 0, words_string)
        c.restoreState()
        
        # Draw description on the right side between logos and ACROSS clues
        if puzzle_description:
            c.setFont("Helvetica-Oblique", 6)
            desc_lines = puzzle_description.split('\n')
            desc_y = 8
            desc_x = width - 240  # Fixed X position
            for line in reversed(desc_lines):  # Draw from bottom to top
                if line.strip():  # Only draw non-empty lines
                    c.drawCentredString(desc_x, desc_y, line.strip())
                    desc_y += 8  # Move up for next line
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(30, clues_start_y, "ACROSS")
        
        c.setFont("Helvetica", 7.5)
        y_position = clues_start_y - 10
        max_clue_width = (width / 2) - 60  # Maximum width for clues
        
        for clue in self.across_clues:
            if y_position < 8:  # Lower threshold to fit more clues
                break
            # Properly truncate to fit width - use correct font size (7.5)
            truncated = clue
            while c.stringWidth(truncated, "Helvetica", 7.5) > max_clue_width and len(truncated) > 10:
                truncated = truncated[:-4] + "..."
            c.drawString(30, y_position, truncated)
            y_position -= 8.5  # Tighter spacing
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(width / 2 + 10, clues_start_y, "DOWN")
        
        c.setFont("Helvetica", 7.5)
        y_position = clues_start_y - 12
        
        for clue in self.down_clues:
            if y_position < 55:  # Lower threshold to fit more clues
                break
            # Properly truncate to fit width - use correct font size (7.5)
            truncated = clue
            while c.stringWidth(truncated, "Helvetica", 7.5) > max_clue_width and len(truncated) > 10:
                truncated = truncated[:-4] + "..."
            c.drawString(width / 2 + 10, y_position, truncated)
            y_position -= 8.5  # Tighter spacing
        
        # Draw logos at the bottom left (smaller, side by side)
        logo_size = 40
        logo_y = 8
        
        # Left logo (positioned on right side)
        left_logo = self.left_logo_path.get()
        if left_logo and os.path.exists(left_logo):
            try:
                c.drawImage(left_logo, width - 15 - (logo_size * 2) - 5, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Right logo (positioned next to left logo on right side with spacing)
        right_logo = self.right_logo_path.get()
        if right_logo and os.path.exists(right_logo):
            try:
                c.drawImage(right_logo, width - 15 - logo_size, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
            except:
                pass
    
    def preview_pdf(self):
        """
        Generate a preview of the PDF and open it.
        
        Creates a temporary PDF file with the current puzzle configuration
        and opens it in the system's default PDF viewer for preview.
        """
        try:
            # Create a temporary PDF file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_filename = temp_file.name
            temp_file.close()
            
            # Generate PDF
            c = pdf_canvas.Canvas(temp_filename, pagesize=LETTER)
            width, height = LETTER
            self.create_pdf_content(c, width, height)
            c.save()
            
            # Open the PDF with default viewer
            os.startfile(temp_filename)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create preview:\n{str(e)}")

    def export_to_pdf(self):
        """
        Export the crossword puzzle to a PDF file.
        
        Creates a US Letter-sized (8.5" × 11") PDF with:
        - Custom title at top
        - Trimmed crossword grid (no excess black cells)
        - Numbered cells matching the clues
        - Secret code cells marked with thick borders
        - Secret code clue displayed vertically on the left edge
        - ACROSS and DOWN clues in two columns
        - Custom description at bottom
        - Optional logos in bottom corners
        
        The user is prompted to select a save location.
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="crossword_puzzle.pdf"
        )
        
        if not filename:
            return
        
        try:
            # LETTER size in points (612 x 792)
            c = pdf_canvas.Canvas(filename, pagesize=LETTER)
            width, height = LETTER
            
            self.create_pdf_content(c, width, height)
            
            c.save()
            messagebox.showinfo("Success", f"Crossword puzzle saved to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF:\n{str(e)}")
    
    def run(self):
        """Start the GUI main event loop."""
        self.root.mainloop()



# ============================================================================
# MAIN EXECUTION
# ============================================================================

def load_words_from_csv(csv_file):
    """
    Load words and clues from a CSV file.
    
    Parameters:
    -----------
    csv_file : str
        Path to CSV file with 'words' and 'clues' columns
    
    Returns:
    --------
    list of tuple
        List of (word, clue) tuples, or None if loading fails
    """
    try:
        df = pd.read_csv(csv_file)
        
        # Check if required columns exist
        if 'words' not in df.columns or 'clues' not in df.columns:
            print("Error: CSV file must contain 'words' and 'clues' columns.")
            return None
        
        # Remove rows with missing values
        df = df.dropna(subset=['words', 'clues'])
        
        # Convert to list of tuples
        words_and_clues = [(str(row['words']), str(row['clues'])) for _, row in df.iterrows()]
        
        print(f"Loaded {len(words_and_clues)} words from CSV file.")
        return words_and_clues
        
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return None
    except Exception as e:
        print(f"Error loading CSV file: {str(e)}")
        return None

if __name__ == "__main__":
    """
    Example usage demonstrating how to create and display a crossword puzzle.
    
    To use this script:
    1. Run with a CSV file argument: python crossword.py input.csv
       - CSV must have 'words' and 'clues' columns
    2. Or run without arguments to use the default word list
    3. Adjust GRID_SIZE to accommodate your longest words
    4. In the GUI:
       - Enter your title and description
       - Optionally select logos
       - Solve the puzzle or export to PDF
    """
    
    # Check if CSV file is provided as command line argument
    is_from_csv = False
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"Loading words from CSV file: {csv_file}")
        words_and_clues_list = load_words_from_csv(csv_file)
        
        if words_and_clues_list is None:
            print("Failed to load CSV file. Exiting.")
            sys.exit(1)
        is_from_csv = True
    else:
        print("No CSV file provided. Using default word list.")
        # Define your words and clues as (word, clue) tuples
        words_and_clues_list = [
        ("NaturalSelection", "The process by which organisms become better adapted to their environment."),
        ("Exoplanet", "The name of a planet that orbits another star."),
        ("Life", "a self-sustaining chemical system capable of undergoing Darwinian evolution."),
        ("Organism", "A living entity with one or more cells."),
        ("Water", "One of the required compounds for life."),
        ("Sun", "The name of our nearest star."),
        ("Moon", "The name of an object that orbits a planet."),
        ("Biology", "The study of living things."),
        ("Speciation", "Formation of new species."),
        ("Extremophile", "Organisms that can survive in extreme environments."),
        ("Metabolism", "The chemical process of life."),
        ("Abiotic", "Not living."),
        ("Autotroph", "An organism that makes its own food."),
        ("Habitablezone", "The region in a planetary system where liquid water can exist."),
        ("Mariner", "NASA probes that explored Venus, Mars, and Mercury"),
        ("Viking", "The first life detection program."),
        ("Murchison", "The first meteorite containing organic matter."),
        ("FruitFly", "The first living entity sent to space."),
        ("Stromatolites", "The layered rocks made by ancient microbial mats."),
        ("Arecibo", "The world's largest single-aperture telescope."),
        ("Panspermia", "The hypothesis that life on Earth originated from extraterrestrial sources."),
        ("Claytheory", "A theory proposes that early life emerged on the surface of clay minerals"),
        ("ASU", "Home of edgy scientists!"),
        ("Iron", "The most abundant metal in the solar system."),
        ("Oxygen", "The most abundant element in the Earth's crust."),
        ("Iceage", "A time of widespread glaciation."),
        ("SnowballEarth", "The theory that Earth's oceans and land surfaces were covered in ice."),
        ("ALH", "The martian meteorite that was found in Antarctica in 1984."),
        ("ARC", "Ames Research Center."),
        ("Biosphere", "The layer of a planet where life exists."),
        ("GOE", "The turning point in Earth's history, when molecular oxygen first appeared."),
        ("SETI", "Search for Extraterrestrial Intelligence."),
        ("REZA", "The Creator of all of these!"),
        ("JamesWebb", "The most powerful telescope ever launched into space."),
        ("Curiosity", "The mars rover that landed in Gale Crater in 2012."),
        ("Perseverance", "The mars rover that landed in Jezero Crater in 2021."),
        ("Ingenuity", "The first helicopter to fly on another planet."),
        ("Titan", "The largest moon of Saturn and second largest in the solar system."),
        ("Europa", "One of Jupiter's moons that may have a subsurface ocean."),
        ("Enceladus", "One of Saturn's moons that has geysers ejecting water ice."),
        ("Methane", "A simple organic molecule found on Titan and Mars."),
        ("Volatile", "A substance that vaporizes at a relatively low temperature."),
        ("Hadean", "The earliest eon in Earth's history, before the Archean."),
        ("Homeostasis", "The ability of an organism to maintain a stable internal environment."),
        ("LUCA", "The Last Universal Common Ancestor of all life on Earth."),
        ("SuperEarth", "A rocky exoplanet with 1–10 times Earth’s mass."),
        ("Rogue", "A free-floating planet not orbiting any star."),
        ("Exomoon", "A natural satellite orbiting an exoplanet."),
        ("Hycean", "A hypothetical class of ocean-covered planets with hydrogen-rich atmospheres."),
        ("Fermi", "The paradox asking Why no aliens detected despite billions of exoplanets?")
        ]
    
    # Set grid size based on your longest word (add some buffer space)
    GRID_SIZE = 40
    
    # Generate the crossword puzzle
    gen = generate_crossword(words_and_clues_list, height=GRID_SIZE, width=GRID_SIZE, is_csv=is_from_csv)
    
    # Launch the GUI if puzzle generation was successful
    if gen and len(gen.placements) > 0:
        print(f"Successfully generated crossword with {len(gen.placements)} words.")
        gui = CrosswordGUI(gen)
        gui.run()
    else:
        print("Failed to generate a usable crossword.")
