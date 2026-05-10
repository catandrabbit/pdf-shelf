# PDF Shelf

[中文说明](README.zh-CN.md) | English

A lightweight, zero-dependency local PDF book library manager. Browse, search, and read your PDF collection directly in the browser.

![PDF Shelf](https://img.shields.io/badge/status-stable-green) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.8+-yellow)

## 截图预览

<div align="center">

![PDF Shelf 效果图](https://github.com/catandrabbit/pdf-shelf/blob/main/screenshot.png?raw=true)

*左侧浏览文件夹和书籍，右侧直接预览PDF内容*

</div>

> **提示**：如果您的实际效果与截图有差异，可以使用 AI Agent（如 Claude、Cursor、Copilot 等）对 `index.html` 进行优化调整，以达到更理想的视觉效果。

## Features

- **Zero Framework** — Single HTML file, no build step, works with `file://` protocol
- **Folder Hierarchy** — Browse books by folder structure with breadcrumb navigation
- **Cover Wall** — Responsive grid with PDF cover thumbnails (auto-extracted)
- **Inline Reader** — Preview PDFs in a resizable side panel
- **Reading Status** — Mark books as Want/Reading/Finished/Favorite
- **Recent History** — Automatically tracks your last 20 opened books
- **Search** — Full-text search across titles and authors
- **Category Colors** — Color-coded categories for visual distinction
- **Customizable** — Settings panel for title, subtitle, and more

## Quick Start

### Prerequisites

- **Python 3.8+** (for the scanner)
- **PyMuPDF** (optional, for cover extraction)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install PyMuPDF
```

> If PyMuPDF is not installed, the scanner will still work but won't extract cover images.

### Step 2: Configure

Copy the example config and edit it:

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "library_dir": "/path/to/your/pdf/folder",
  "app_title": "My Library",
  "app_subtitle": "PDF Book Collection"
}
```

Or skip config and pass the directory directly:

### Step 3: Scan

```bash
# With config.json
python scan.py

# Or pass directory directly
python scan.py /path/to/your/pdfs

# With options
python scan.py /path/to/pdfs --output-dir ./output
```

The scanner will:
1. Recursively scan for `.pdf` files
2. Standardize book titles (remove numbering prefixes, extract edition/volume info)
3. Extract cover thumbnails (if PyMuPDF is installed)
4. Generate `data.js` and `covers/` directory

### Step 4: Open

Open `index.html` in your browser. Double-click works — no web server needed.

## Configuration

### config.json

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `library_dir` | string | `""` | Path to your PDF library directory |
| `output_dir` | string | `"."` | Where to write `data.js` and `covers/` |
| `category_suffix` | string | `"书"` | Folder names ending with this = category |
| `ignore_dirs` | array | `[".obsidian", ...]` | Directory names to skip |
| `ignore_files` | array | `["desktop.ini", ...]` | File names to skip |
| `cover_size` | array | `[300, 400]` | Cover thumbnail dimensions (px) |
| `app_title` | string | `"PDF Shelf"` | Browser tab and header title |
| `app_subtitle` | string | `"Local Digital Library"` | Header subtitle text |

### Title Overrides

Create `title_overrides.json` to manually set book titles:

```json
{
  "book_0001": "My Custom Title",
  "book_0042": "Another Override"
}
```

Book IDs are printed during scan (e.g., `book_0001`). Run scan again after editing.

### CLI Arguments

```
python scan.py [library_dir] [options]

Options:
  --config, -c FILE    Path to config JSON (default: config.json)
  --output-dir, -o DIR Output directory for data.js and covers/
```

## Project Structure

```
pdf-shelf/
├── index.html           # Main web UI (single file, no dependencies)
├── scan.py              # Python scanner script
├── config.example.json  # Example configuration
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT License
├── README.md            # This file
│
├── data.js              # Generated book data (gitignored)
├── covers/              # Generated cover thumbnails (gitignored)
└── config.json          # Your personal config (gitignored)
```

## Customization

### Category Colors

Edit the `CATEGORY_COLORS` object in `index.html`:

```javascript
const CATEGORY_COLORS = {
    'Science': ['#2e7d32', '#43a047'],
    'History': ['#c62828', '#e53935'],
    'Novel':   ['#1565c0', '#1976d2'],
    // Add more categories as needed
};
```

### Header Title

Use the Settings button in the header, or edit `config.json` and re-scan.

## Browser Compatibility

- Chrome / Edge (recommended)
- Firefox
- Safari

> Note: PDF preview in the side panel requires the browser's built-in PDF viewer. Some browsers may block `file://` PDF loading — in that case, use a local server or use the "Open" button to open in your system PDF reader.

## Tips

- **Incremental scanning**: The scanner only creates new cover thumbnails — existing ones are preserved
- **Large libraries**: Works well with 1000+ books
- **Portable**: The entire folder can be moved — just keep `index.html`, `scan.py`, and your generated files together
- **No server needed**: Everything runs locally, no data is uploaded anywhere

## License

[MIT](LICENSE)
