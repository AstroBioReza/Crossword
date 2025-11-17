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
4. PDF export with customizable title, description, and logos
5. PDF preview before saving
6. Multi-line description support
7. Automatic grid trimming (removes excess black cells)

Main Components:
----------------
- CrosswordGenerator: Core logic for generating crossword grids
- CrosswordGUI: Tkinter-based interactive interface
- PDF Export: ReportLab-based PDF generation with A4 formatting

Usage:
------
1. Define your words and clues as a list of tuples: [(word, clue), ...]
2. Call generate_crossword() to create the puzzle grid
3. Create a CrosswordGUI instance and run() it
4. Users can:
   - Solve the puzzle interactively
   - Check their answers
   - Preview the PDF
   - Export to PDF with custom title, description, and logos

Author: Mohammad Reza Shahjahan
Date: November 2025
Version: 2.0
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import os
import tempfile


# ============================================================================
# CROSSWORD GENERATION FUNCTIONS
# ============================================================================

def generate_crossword(words_and_clues, height=15, width=15):
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
    gen = CrosswordGenerator(height, width)
    words_and_clues = sorted(words_and_clues, key=lambda x: len(x[0]), reverse=True)
    
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
        
    return gen


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
        
        # Add title and description fields at the top
        top_frame = tk.Frame(self.root, bg='white', padx=10, pady=5)
        top_frame.pack(fill='x')
        
        tk.Label(top_frame, text="Puzzle Title:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=2)
        self.title_entry = tk.Entry(top_frame, font=('Arial', 10), width=50)
        self.title_entry.grid(row=0, column=1, sticky='ew', pady=2)
        self.title_entry.insert(0, "Crossword Puzzle")
        
        tk.Label(top_frame, text="Description:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='nw', pady=2)
        desc_frame = tk.Frame(top_frame, bg='white')
        desc_frame.grid(row=1, column=1, sticky='ew', pady=2)
        self.description_entry = tk.Text(desc_frame, font=('Arial', 9), width=50, height=2, wrap='word')
        self.description_entry.pack(fill='both', expand=True)
        self.description_entry.insert('1.0', "Fill in the crossword using the clues below")
        
        # Logo selection fields
        tk.Label(top_frame, text="Left Logo:", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=2)
        logo_left_frame = tk.Frame(top_frame, bg='white')
        logo_left_frame.grid(row=2, column=1, sticky='ew', pady=2)
        self.left_logo_path = tk.StringVar(value="")
        tk.Entry(logo_left_frame, textvariable=self.left_logo_path, font=('Arial', 9), state='readonly').pack(side='left', fill='x', expand=True)
        tk.Button(logo_left_frame, text="Browse", command=lambda: self.select_logo('left'), font=('Arial', 8)).pack(side='left', padx=(5, 0))
        
        tk.Label(top_frame, text="Right Logo:", font=('Arial', 10, 'bold'), bg='white').grid(row=3, column=0, sticky='w', pady=2)
        logo_right_frame = tk.Frame(top_frame, bg='white')
        logo_right_frame.grid(row=3, column=1, sticky='ew', pady=2)
        self.right_logo_path = tk.StringVar(value="")
        tk.Entry(logo_right_frame, textvariable=self.right_logo_path, font=('Arial', 9), state='readonly').pack(side='left', fill='x', expand=True)
        tk.Button(logo_right_frame, text="Browse", command=lambda: self.select_logo('right'), font=('Arial', 8)).pack(side='left', padx=(5, 0))
        
        top_frame.grid_columnconfigure(1, weight=1)
        
        # Use PanedWindow for resizable sections
        paned_window = tk.PanedWindow(self.root, orient='horizontal', sashrelief='raised', sashwidth=5)
        paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side: puzzle and button
        left_frame = tk.Frame(paned_window)
        paned_window.add(left_frame, stretch='always')
        
        # Right side: clues
        clues_container = tk.Frame(paned_window)
        paned_window.add(clues_container, stretch='always')
        
        # Create puzzle area with scrollbars in left frame
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
                    
                    # Entry box for user input (create FIRST so number appears on top)
                    entry = tk.Entry(cell_frame, width=2, font=('Arial', 14, 'bold'), justify='center', 
                                     bd=0, highlightthickness=1, highlightbackground='gray',
                                     relief='flat', takefocus=True) 
                    entry.pack(expand=True, fill='both', padx=4, pady=4)
                    self.entries[r][c] = entry
                    
                    # Bind key events for single character limit and navigation
                    entry.bind('<KeyRelease>', lambda e, row=r, col=c: self.on_key_release(e, row, col))
                    entry.bind('<FocusIn>', lambda e, row=r, col=c: self.on_focus(e, row, col))
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

        # Add scrollable clues section
        clues_canvas = tk.Canvas(clues_container, bg='white')
        clues_scrollbar = tk.Scrollbar(clues_container, orient='vertical', command=clues_canvas.yview)
        clues_frame = tk.Frame(clues_canvas, bg='white')
        
        clues_canvas.create_window((0, 0), window=clues_frame, anchor='nw')
        clues_canvas.configure(yscrollcommand=clues_scrollbar.set)
        
        clues_scrollbar.pack(side='right', fill='y')
        clues_canvas.pack(side='left', fill='both', expand=True)
        
        def configure_clues_scroll(event):
            clues_canvas.configure(scrollregion=clues_canvas.bbox('all'))
        clues_frame.bind('<Configure>', configure_clues_scroll)
        
        tk.Label(clues_frame, text="ACROSS →", font=('Arial', 12, 'bold'), bg='white').pack(anchor='nw', pady=(0, 5))
        across_text = "\n".join(across)
        tk.Label(clues_frame, text=across_text, justify='left', anchor='nw', bg='white').pack(anchor='nw')
        
        tk.Label(clues_frame, text="\nDOWN ↓", font=('Arial', 12, 'bold'), bg='white').pack(anchor='nw', pady=(10, 5))
        down_text = "\n".join(down)
        tk.Label(clues_frame, text=down_text, justify='left', anchor='nw', bg='white').pack(anchor='nw')

        # --- 4. Buttons (under the puzzle on the left) ---
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        check_button = tk.Button(buttons_frame, text="Check Answers", command=self.check, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        check_button.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        preview_button = tk.Button(buttons_frame, text="Preview PDF", command=self.preview_pdf, bg="#FF9800", fg="white", font=('Arial', 10, 'bold'))
        preview_button.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        pdf_button = tk.Button(buttons_frame, text="Export to PDF", command=self.export_to_pdf, bg="#2196F3", fg="white", font=('Arial', 10, 'bold'))
        pdf_button.pack(side='left', fill='x', expand=True)

    def check(self):
        """Checks the user's input against the generated grid."""
        incorrect_count = 0
        
        for r in range(self.gen.height):
            for c in range(self.gen.width):
                if self.gen.grid[r][c] != '#':
                    entry = self.entries[r][c]
                    user_input = entry.get().strip().upper()
                    
                    if user_input != self.gen.grid[r][c]:
                        incorrect_count += 1
                        entry.config(bg="#FFC0CB") # Light red/pink
                    else:
                        entry.config(bg="#90EE90") # Light green
        
        for r in range(self.gen.height):
            for c in range(self.gen.width):
                if self.gen.grid[r][c] != '#' and not self.entries[r][c].get().strip() and self.entries[r][c].cget('bg') != 'lightgray':
                    self.entries[r][c].config(bg='white')
        
        if incorrect_count == 0:
            messagebox.showinfo("Result", "✅ Congratulations! You solved the puzzle correctly.")
        else:
            messagebox.showinfo("Result", f"❌ Not all answers are correct yet. {incorrect_count} errors remain. Keep trying!")

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
            if self.current_direction == 'across':
                self.move_right(row, col)
            else:  # down
                self.move_down(row, col)
    
    def on_backspace(self, event, row, col):
        """Handle backspace - clear current cell and move to previous cell."""
        entry = self.entries[row][col]
        
        # Clear the current cell
        entry.delete(0, tk.END)
        
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
        
        # If both directions are available (cross section), keep current direction
        if has_across and has_down:
            # Only change direction if clicking on a different cell
            # If clicking the same cell again, keep the current direction
            if not hasattr(self, 'last_focused_cell') or self.last_focused_cell != (row, col):
                # Moving to a new cell - keep current direction if it's valid
                # Otherwise default to across
                if not hasattr(self, 'current_direction') or self.current_direction not in ['across', 'down']:
                    self.current_direction = 'across'
                # else: keep current_direction as is
            # If clicking same cell, keep current direction (no change)
        elif has_down:
            self.current_direction = 'down'
        elif has_across:
            self.current_direction = 'across'
        
        self.last_focused_cell = (row, col)
    
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
        """Create the PDF content (used by both export and preview)."""
        # Get user-entered title and description
        puzzle_title = self.title_entry.get() or "Crossword Puzzle"
        puzzle_description = self.description_entry.get('1.0', 'end-1c').strip() or ""
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, puzzle_title)
        
        current_y = height - 60
        
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
        max_grid_width = width - 100
        max_grid_height = 400
        
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
        c.setLineWidth(0.5)
        for r in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                x = start_x + (col - min_col) * cell_size
                y = start_y + (max_row - r) * cell_size
                
                if self.gen.grid[r][col] == '#':
                    # Skip black cells - don't draw them
                    continue
                else:
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=1)
                    c.setFillColorRGB(0, 0, 0)
                    
                    if (r, col) in self.number_map:
                        c.setFont("Helvetica-Bold", max(6, cell_size * 0.25))
                        c.drawString(x + 2, y + cell_size - max(8, cell_size * 0.3), 
                                   str(self.number_map[(r, col)]))
        
        # Draw clues
        clues_start_y = start_y - 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, clues_start_y, "ACROSS")
        
        c.setFont("Helvetica", 9)
        y_position = clues_start_y - 15
        
        for clue in self.across_clues:
            if y_position < 120:
                break
            c.drawString(50, y_position, clue[:60])
            y_position -= 12
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(width / 2 + 25, clues_start_y, "DOWN")
        
        c.setFont("Helvetica", 9)
        y_position = clues_start_y - 15
        
        for clue in self.down_clues:
            if y_position < 120:
                break
            c.drawString(width / 2 + 25, y_position, clue[:60])
            y_position -= 12
        
        # Draw description at the bottom (centered, support multiple lines)
        if puzzle_description:
            c.setFont("Helvetica-Oblique", 7)
            desc_lines = puzzle_description.split('\n')
            desc_y = 30
            for line in reversed(desc_lines):  # Draw from bottom to top
                if line.strip():  # Only draw non-empty lines
                    c.drawCentredString(width / 2, desc_y, line.strip())
                    desc_y += 12  # Move up for next line
        
        # Draw logos at the bottom
        logo_size = 60
        logo_y = 20
        
        # Left logo
        left_logo = self.left_logo_path.get()
        if left_logo and os.path.exists(left_logo):
            try:
                c.drawImage(left_logo, 50, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Right logo
        right_logo = self.right_logo_path.get()
        if right_logo and os.path.exists(right_logo):
            try:
                c.drawImage(right_logo, width - 50 - logo_size, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
            except:
                pass
    
    def preview_pdf(self):
        """Generate a preview of the PDF and open it."""
        try:
            # Create a temporary PDF file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_filename = temp_file.name
            temp_file.close()
            
            # Generate PDF
            c = pdf_canvas.Canvas(temp_filename, pagesize=A4)
            width, height = A4
            self.create_pdf_content(c, width, height)
            c.save()
            
            # Open the PDF with default viewer
            os.startfile(temp_filename)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create preview:\n{str(e)}")

    def export_to_pdf(self):
        """
        Export the crossword puzzle to a PDF file.
        
        Creates an A4-sized PDF with:
        - Custom title at top
        - Trimmed crossword grid (no excess black cells)
        - Numbered cells matching the clues
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
            # A4 size in points (595 x 842)
            c = pdf_canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
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

if __name__ == "__main__":
    """
    Example usage demonstrating how to create and display a crossword puzzle.
    
    To use this script:
    1. Modify the words_and_clues_list with your own words and clues
    2. Adjust GRID_SIZE to accommodate your longest words
    3. Run the script to generate and display the puzzle
    4. In the GUI:
       - Enter your title and description
       - Optionally select logos
       - Solve the puzzle or export to PDF
    """
    
    # Define your words and clues as (word, clue) tuples
    words_and_clues_list = [
        ("NaturalSelection", "Natural way organisms evolve to suit their environment"),
        ("Exoplanet", "The name of a planet that orbits another star"),
        ("Life", "Main subject of astrobiology"),
        ("Organism", "The name for a living thing"),
        ("Water", "One of the required conditions for life"),
        ("Sun", "The name of our nearest star"),
        ("Moon", "The name of an object that orbits a planet"),
        ("Biology", "Study of living things"),
        ("Speciation", "Formation of new species"),
        ("Alphahelix", "One type of folding"),
        ("Metabolism", "Chemical process of living things"),
        ("Abiotic", "Non-living things"),
        ("Autotroph", "An organism that makes its own food"),
        ("Habitablezone", "The region in a planetary system where liquid water "),
        ("Mariner", "First mission to Mars"),
        ("Viking", "First life detection program"),
        ("Murchison", "First meteorite containing organic matter"),
        ("FruitFly", "First living entity sent to space"),
        ("Stromatolites", "Earliest evidence of life on Earth"),
        ("Arecibo", "The world's largest single-aperture telescope"),
        ("Panspermia", "Hypothesis that life brought to earth from space"),
        ("Extremophile", "Organisms that can survive in extreme environments"),
        ("ASU", "Home of edgy scientists!"),
        ("Iron", "Most abundant metal in solar system"),
        ("Oxygen", "Most abundant element in earth's crust"),
        ("Iceage", "A time of widespread glaciation"),
        ("SnowballEarth", "Theory that Earth's oceans and land surfaces were covered in ice"),
        ("ALH", "Martian meteorite that was found in Antarctica in 1984"),
        ("ARC", "Ames Research Center"),
        ("Biosphere", "The layer of a planet where life exists"),
        ("GOE", "Turning point in Earth's history, when molecular oxygen first appeared"),
        ("SETI", "Search for Extraterrestrial Intelligence"),
        ("REZA", "The Creator of all of these!"),
        ("JamesWebb", "The largest, most powerful and most complex telescope ever launched into space")
    ]
    
    # Set grid size based on your longest word (add some buffer space)
    GRID_SIZE = 38
    
    # Generate the crossword puzzle
    gen = generate_crossword(words_and_clues_list, height=GRID_SIZE, width=GRID_SIZE)
    
    # Launch the GUI if puzzle generation was successful
    if gen and len(gen.placements) > 0:
        print(f"Successfully generated crossword with {len(gen.placements)} words.")
        gui = CrosswordGUI(gen)
        gui.run()
    else:
        print("Failed to generate a usable crossword.")
