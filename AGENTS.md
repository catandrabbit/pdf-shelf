# AGENTS.md - PDF Shelf

## Project Overview

PDF Shelf is a lightweight, zero-dependency local PDF book library manager. It consists of:

- `index.html` — Single-file web UI (HTML + CSS + JS, no frameworks)
- `scan.py` — Python scanner that indexes PDFs and generates `data.js`
- `data.js` — Auto-generated book metadata (gitignored)
- `covers/` — Auto-generated cover thumbnails (gitignored)

## Tech Stack

- **Frontend**: Vanilla HTML5 + CSS3 + JavaScript (zero dependencies)
- **Scanner**: Python 3.8+ with optional PyMuPDF dependency
- **Storage**: Browser `localStorage` for reading history and book status

## Project Structure

```
pdf-shelf/
├── index.html           # Main UI
├── scan.py              # PDF scanner
├── config.example.json  # Example config
├── config.json          # User config (gitignored)
├── requirements.txt     # Python deps
├── data.js              # Generated (gitignored)
├── covers/              # Generated (gitignored)
├── title_overrides.json # Manual title overrides (gitignored)
├── LICENSE              # MIT
└── README.md            # Documentation
```

## Development Guidelines

### Code Style
- Single `index.html` file — all HTML/CSS/JS inline
- No build tools, no bundlers, no frameworks
- Python scanner uses only standard library + optional PyMuPDF
- All user data stored in browser `localStorage`, no server

### Key Conventions
- Book IDs: `book_0000`, `book_0001`, etc. (sequential, zero-padded 4 digits)
- Cover images: `covers/book_XXXX.png`
- Folder path separator: `/` (forward slash, even on Windows)
- Title format: `Book Title (Edition / Volume)`

### When Modifying scan.py
- Keep CLI argument parsing via `argparse`
- Support both config.json and CLI arguments
- Never hardcode file paths
- Use relative paths in generated data.js

### When Modifying index.html
- Keep everything in a single file
- All UI text should be user-facing (no hardcoded project names)
- Category colors are in `CATEGORY_COLORS` object
- Settings stored in `localStorage` with `pdfshelf_` prefix
