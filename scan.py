#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Shelf Scanner - Scan a local directory for PDF books and generate web data.
Usage:
    python scan.py /path/to/pdf/library
    python scan.py                          # uses config.json or prompts
    python scan.py --config config.json     # explicit config file
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

# ==================== Defaults ====================
DEFAULT_CATEGORY_SUFFIX = "书"
DEFAULT_IGNORE_DIRS = {".obsidian", ".trash", "z 档案库", "z 附件库"}
DEFAULT_IGNORE_FILES = {"desktop.ini", "梳理台.md"}
DEFAULT_COVER_SIZE = (300, 400)
CONFIG_FILE = "config.json"
DATA_FILE = "data.js"
COVERS_DIR = "covers"
# =============================================

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def load_config(config_path: str = None) -> dict:
    """Load config from JSON file, missing keys filled with defaults."""
    config = {
        "library_dir": "",
        "output_dir": ".",
        "category_suffix": DEFAULT_CATEGORY_SUFFIX,
        "ignore_dirs": list(DEFAULT_IGNORE_DIRS),
        "ignore_files": list(DEFAULT_IGNORE_FILES),
        "cover_size": list(DEFAULT_COVER_SIZE),
        "app_title": "PDF Shelf",
        "app_subtitle": "Local Digital Library",
    }
    path = Path(config_path) if config_path else Path(CONFIG_FILE)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            config.update({k: v for k, v in user_cfg.items() if v is not None})
        except Exception as e:
            print(f"[Warning] Failed to load config: {e}")
    return config


def should_ignore_dir(name: str, ignore_dirs: set) -> bool:
    return name.lower().strip() in ignore_dirs


def should_ignore_file(name: str, ignore_files: set) -> bool:
    lower = name.lower().strip()
    return lower in ignore_files or not lower.endswith(".pdf")


def extract_cover(pdf_path: str, cover_path: str, cover_size: tuple) -> bool:
    if not HAS_PYMUPDF:
        return False
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return False

        page = doc[0]
        rect = page.rect
        scale_x = cover_size[0] / rect.width
        scale_y = cover_size[1] / rect.height
        scale = max(scale_x, scale_y) * 1.5

        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        pix.save(cover_path)
        doc.close()
        return True
    except Exception as e:
        print(f"       [Cover failed] {os.path.basename(pdf_path)[:40]}: {e}")
        return False


def parse_raw_info(filename: str) -> dict:
    name_without_ext = filename[:-4] if filename.lower().endswith(".pdf") else filename
    parts = name_without_ext.split(" -- ")

    if len(parts) >= 2:
        raw_title = parts[0].strip()
        raw_author = parts[1].strip()
    else:
        raw_title = name_without_ext.strip()
        raw_author = ""

    return {"raw_title": raw_title, "raw_author": raw_author}


def standardize_title(raw_title: str, raw_author: str) -> dict:
    title = raw_title
    author = raw_author
    edition = ""
    volume = ""

    title = re.sub(r'^\d+[\s._\-]+', '', title)

    edition_match = re.search(r'[（(]?\s*(第[一二三四五六七八九十\d]+版|第\d+版|修订版)\s*[）)]?', title)
    if edition_match:
        edition = edition_match.group(1)
        title = title.replace(edition_match.group(0), '').strip()

    volume_patterns = [
        r'[（(]?\s*(第[一二三四五六七八九十\d]+卷|第\d+卷|Volume\s*\d+|Vol\.?\s*\d+|第[一二三四五六七八九十\d]+册|第\d+册)\s*[）)]?',
        r'[_\s]+([上中下])[_\s]*$',
    ]
    for pattern in volume_patterns:
        vol_match = re.search(pattern, title, re.IGNORECASE)
        if vol_match:
            volume = vol_match.group(1)
            title = title.replace(vol_match.group(0), '').strip()
            break

    title = title.replace('_', ' ').strip()
    title = re.sub(r'[\s\-_]+$', '', title)

    if author:
        author = re.sub(r'[\s]*[著编编著译翻译校注]', '', author).strip()
        author = re.sub(r'^[\(\[【](.+)[\)\]】]$', r'\1', author)
        author = re.sub(r'\s*[,，]\s*\d{4}.*$', '', author)
        author = re.sub(r'\s*--.*$', '', author)

    final_title = title
    suffix_parts = []
    if volume:
        suffix_parts.append(volume)
    if edition:
        suffix_parts.append(edition)

    if suffix_parts:
        final_title += "(" + " / ".join(suffix_parts) + ")"

    vol_en = re.search(r'Volume\s*(\d+)', title, re.IGNORECASE)
    if vol_en and not volume:
        final_title = re.sub(r'Volume\s*\d+', '', title, flags=re.IGNORECASE).strip()
        final_title += f"(Vol.{vol_en.group(1)})"

    return {
        "title": final_title,
        "author": author,
        "edition": edition,
        "volume": volume
    }


def load_overrides(output_dir: Path) -> dict:
    override_file = output_dir / "title_overrides.json"
    if override_file.exists():
        try:
            with open(override_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def scan_library(source_dir: str, config: dict) -> dict:
    books = []
    categories = set()
    title_counter = {}
    output_dir = Path(config["output_dir"])
    overrides = load_overrides(output_dir)

    ignore_dirs = set(config["ignore_dirs"])
    ignore_files = set(config["ignore_files"])
    category_suffix = config["category_suffix"]
    cover_size = tuple(config["cover_size"])

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[Error] Library directory does not exist: {source_dir}")
        return {"categories": [], "books": []}

    covers_dir = output_dir / COVERS_DIR
    covers_dir.mkdir(exist_ok=True)

    print(f"[Scan] Scanning: {source_dir}")

    for item in sorted(source_path.iterdir()):
        if not item.is_dir():
            continue
        if should_ignore_dir(item.name, ignore_dirs):
            print(f"  [Skip] Ignored dir: {item.name}")
            continue
        if not item.name.endswith(category_suffix):
            print(f"  [Skip] Non-category dir: {item.name}")
            continue

        category = item.name
        categories.add(category)
        print(f"  [Category] {category}")

        for root, dirs, files in os.walk(item):
            dirs[:] = [d for d in dirs if not should_ignore_dir(d, ignore_dirs)]

            for file in sorted(files):
                if should_ignore_file(file, ignore_files):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(source_path)

                try:
                    size = file_path.stat().st_size
                except (OSError, FileNotFoundError) as e:
                    print(f"       [Skip] Cannot access: {file[:50]}... ({e})")
                    continue

                parts = list(rel_path.parts)
                folder_path = "/".join(parts[:-1])
                subcategory = parts[1] if len(parts) > 2 else ""

                raw = parse_raw_info(file)
                std = standardize_title(raw["raw_title"], raw["raw_author"])

                book_id = f"book_{len(books):04d}"

                if book_id in overrides:
                    std["title"] = overrides[book_id]

                base_title = std["title"]
                if base_title in title_counter:
                    title_counter[base_title] += 1
                    std["title"] = f"{base_title} ({title_counter[base_title]})"
                else:
                    title_counter[base_title] = 0

                cover_filename = f"{book_id}.png"
                cover_path = covers_dir / cover_filename
                cover_rel = f"{COVERS_DIR}/{cover_filename}"
                has_cover = False

                if HAS_PYMUPDF:
                    if not cover_path.exists():
                        has_cover = extract_cover(str(file_path), str(cover_path), cover_size)
                    else:
                        has_cover = True

                book = {
                    "id": book_id,
                    "title": std["title"],
                    "rawTitle": raw["raw_title"],
                    "author": std["author"] or "Unknown",
                    "category": category,
                    "subcategory": subcategory,
                    "folderPath": folder_path,
                    "relPath": str(rel_path).replace("\\", "/"),
                    "filename": file,
                    "size": size,
                    "sizeStr": format_size(size),
                    "cover": cover_rel if has_cover else "",
                    "hasCover": has_cover
                }
                books.append(book)

        cat_count = sum(1 for b in books if b["category"] == category)
        print(f"       -> {cat_count} books in this category")

    print(f"\n[Done] Found {len(categories)} categories, {len(books)} books total")

    return {
        "categories": sorted(list(categories)),
        "books": books,
        "scanTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "appTitle": config.get("app_title", "PDF Shelf"),
        "appSubtitle": config.get("app_subtitle", "Local Digital Library"),
        "hasCovers": HAS_PYMUPDF
    }


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def generate_data_js(data: dict) -> str:
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return f"""// PDF Shelf - Book Data
// Generated: {data['scanTime']}
// This file is auto-generated by scan.py. Do not edit manually.

const LIBRARY_DATA = {json_str};
"""


def main():
    parser = argparse.ArgumentParser(
        description="PDF Shelf - Scan a directory for PDF books and generate web data."
    )
    parser.add_argument(
        "library_dir",
        nargs="?",
        help="Path to the directory containing PDF books."
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help=f"Path to config JSON file (default: {CONFIG_FILE})"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory for data.js and covers/ (default: same as config or current dir)"
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.output_dir:
        config["output_dir"] = args.output_dir

    if args.library_dir:
        config["library_dir"] = args.library_dir

    if not config["library_dir"]:
        print("=" * 60)
        print("  PDF Shelf - Scanner")
        print("=" * 60)
        print()
        print("[Error] No library directory specified.")
        print()
        print("Usage:")
        print("  python scan.py /path/to/pdf/library")
        print("  python scan.py --config config.json")
        print()
        print("Create a config.json based on config.example.json:")
        print('  {"library_dir": "/path/to/your/pdfs"}')
        print()
        sys.exit(1)

    print("=" * 60)
    print("  PDF Shelf - Scanner")
    print("=" * 60)
    print(f"  Library: {config['library_dir']}")
    print(f"  Output:  {config['output_dir']}")
    print(f"  PyMuPDF: {'Available' if HAS_PYMUPDF else 'Not installed (covers disabled)'}")
    print("=" * 60)

    data = scan_library(config["library_dir"], config)

    if not data["books"]:
        print("\n[Warning] No books found")
        return

    output_dir = Path(config["output_dir"])
    data_file = output_dir / DATA_FILE

    js_content = generate_data_js(data)

    with open(data_file, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\n[Saved] Data written to: {data_file}")
    print(f"        {len(data['books'])} books total")
    print(f"        Cover extraction: {'Enabled' if data['hasCovers'] else 'Disabled'}")
    if data["hasCovers"]:
        cover_count = sum(1 for b in data["books"] if b["hasCover"])
        print(f"        Covers extracted: {cover_count}")

    print("\n[Stats] Category breakdown:")
    for cat in data["categories"]:
        count = sum(1 for b in data["books"] if b["category"] == cat)
        print(f"   - {cat}: {count}")

    print(f"\n[Next]  Open index.html in a browser to view your library")
    print("=" * 60)


if __name__ == "__main__":
    main()
