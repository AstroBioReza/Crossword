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
