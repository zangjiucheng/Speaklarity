# Speaklarity Backend

This folder contains the backend logic for Speaklarity, a project focused on voice and accent analysis, grammar checking, and text alignment for spoken language.

## Main Features
- **Accent Check**: Analyze audio files to assess accent and pronunciation.
- **Grammar Check**: Evaluate spoken or written text for grammatical accuracy.
- **Text Alignment**: Align spoken audio with reference text for comparison.
- **Utilities**: Helper functions for audio and text processing.

## Key Files
- `accent_check.py`: Functions for accent and pronunciation analysis.
- `align_text.py`: Tools for aligning audio with text.
- `grammar_check.py`: Grammar checking logic.
- `process.py`: Main processing pipeline for audio and text.
- `util.py`: Utility functions used across modules.
- `route.py`: API routes and backend endpoints.

## Usage
1. Place your audio files in this directory (e.g., `audio.wav`).
2. Install dependencies:
   ```bash
   pip install -r requirement.txt
   ```
3. Run backend scripts as needed, for example:
   ```bash
   python accent_check.py
   ```

## Notes
- See each script for specific usage and options.
- For API usage, refer to `route.py`.

---
For more details, see the code comments in each file.
