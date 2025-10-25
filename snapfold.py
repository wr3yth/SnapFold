#!/usr/bin/env python3
"""
SnapFold — Project Snapshot to Markdown
Compactly bundle your HTML/CSS/JS project into a single markdown snapshot.
"""

import os
import re
import time
import json
from pathlib import Path
from datetime import datetime

# ───────────────────────────────
# Terminal color codes
# ───────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"

# ───────────────────────────────
# Default configuration
# ───────────────────────────────
DEFAULT_CONFIG = {
    "input": ".",
    "output": "SnapFold.md",
    "format": "md",
    "theme": "default",
    "ignore": ["node_modules", ".git", "snapfold.py"],
    "max_file_size": 2 * 1024 * 1024,  # 2 MB
    "only_formats": ["html", "css", "js"],
    "enable_only_formats": False,
    "include_tree": True,
    "naming_mode": "increment",  # timestamp | increment | overwrite
}

# ───────────────────────────────
# Config file helpers
# ───────────────────────────────
def create_default_config(path="snapfold.config"):
    """Create default config file if not found."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("""# SnapFold configuration file
# Default configuration is safe and optimized for most projects.
# Edit values as needed. Save and rerun SnapFold.

input = .
output = SnapFold.md
format = md
theme = default

# Folders or files to ignore (comma-separated)
ignore = node_modules, .git, snapfold.py

# Maximum file size to include (supports MB/KB)
max_file_size = 2MB

# Limit to these file types only (set enable_only_formats = true to activate)
only_formats = html, css, js
enable_only_formats = false

# Include tree overview at top of file
include_tree = true

# Output file naming method: timestamp | increment | overwrite
naming_mode = increment
""")
        print(f"{C.YELLOW}⚙️  snapfold.config created.{C.RESET}")
        print(f"{C.DIM}Default configuration is designed to be fast and ignore large files.{C.RESET}")
        print(f"Press {C.BOLD}Y{C.RESET} to continue with default settings, or {C.BOLD}N{C.RESET} to halt and edit snapfold.config.")
        choice = input("> ").strip().lower()
        if choice != "y":
            print(f"{C.CYAN}🛑 Process halted. You can edit snapfold.config manually.{C.RESET}")
            exit(0)
    else:
        print(f"{C.CYAN}⚙️ Using snapfold.config{C.RESET}")


def parse_config_file(path):
    """Parse .config files with key=value syntax."""
    conf = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#", ";")):
                continue
            if "=" in line:
                key, value = map(str.strip, line.split("=", 1))

                # Handle booleans
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"

                # Handle human-readable sizes (e.g. "2MB")
                elif re.match(r"^[0-9]", value):
                    match = re.match(r"^([0-9.]+)\s*(kb|mb|gb)?$", value.lower())
                    if match:
                        num = float(match.group(1))
                        unit = match.group(2) or ""
                        mult = {"kb": 1024, "mb": 1024**2, "gb": 1024**3}.get(unit, 1)
                        value = int(num * mult)

                # Handle lists
                elif "," in value:
                    value = [v.strip() for v in value.split(",")]

                conf[key] = value
    return conf


def load_config():
    """Load config with defaults."""
    create_default_config()
    config = DEFAULT_CONFIG.copy()
    config.update(parse_config_file("snapfold.config"))
    return config

# ───────────────────────────────
# File system helpers
# ───────────────────────────────
def list_files(root, config):
    """Recursively gather files."""
    ignore = set(config["ignore"])
    collected = []
    root = Path(root)

    for path in root.rglob("*"):
        if path.is_file():
            if any(ig in path.parts for ig in ignore):
                continue
            if path.stat().st_size > config["max_file_size"]:
                continue
            if config["enable_only_formats"]:
                ext = path.suffix.lstrip(".").lower()
                if ext not in config["only_formats"]:
                    continue
            collected.append(path)
    return collected


def get_unique_output_path(config):
    """Determine output path based on naming_mode."""
    out = Path(config["output"]).resolve()
    folder = out.parent
    stem = out.stem
    ext = out.suffix or ".md"
    naming_mode = str(config.get("naming_mode", "timestamp")).lower()

    folder.mkdir(parents=True, exist_ok=True)

    if naming_mode == "timestamp":
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        return folder / f"{stem}-{ts}{ext}"

    elif naming_mode == "increment":
        i = 1
        final_path = folder / f"{stem}{ext}"
        while final_path.exists():
            i += 1
            final_path = folder / f"{stem}({i}){ext}"
        return final_path

    elif naming_mode == "overwrite":
        return folder / f"{stem}{ext}"

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return folder / f"{stem}-{ts}{ext}"

# ───────────────────────────────
# Output helpers
# ───────────────────────────────
def generate_tree(root, files):
    """Generate folder tree view."""
    tree = {}
    for f in files:
        rel = Path(f).relative_to(root)
        parts = rel.parts
        cur = tree
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = None

    def render(subtree, prefix=""):
        out = ""
        for i, (name, val) in enumerate(sorted(subtree.items())):
            connector = "└── " if i == len(subtree) - 1 else "├── "
            out += prefix + connector + name + "\n"
            if isinstance(val, dict):
                ext = "    " if i == len(subtree) - 1 else "│   "
                out += render(val, prefix + ext)
        return out

    return render(tree)


def bundle_files(files, root, config):
    """Bundle all files into one markdown."""
    md = "# 📦 SnapFold Project Snapshot\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    if config["include_tree"]:
        md += "## 📁 Project Structure\n"
        md += "```\n" + generate_tree(root, files) + "```\n\n"

    for f in files:
        rel = Path(f).relative_to(root)
        md += f"---\n### `{rel}`\n```{f.suffix.lstrip('.')}\n"
        try:
            content = Path(f).read_text(encoding="utf-8")
        except Exception as e:
            content = f"[Error reading file: {e}]"
        md += content + "\n```\n\n"

    return md


def save_output(md, config):
    """Save markdown to file."""
    path = get_unique_output_path(config)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n{C.GREEN}✨ Output saved as:{C.RESET} {C.BOLD}{path.name}{C.RESET}")
    print(f"{C.DIM}📂 {path.parent}{C.RESET}")

    return path

# ───────────────────────────────
# Progress bar
# ───────────────────────────────
def progress_bar(current, total, width=30):
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percent = (current / total) * 100
    print(f"\rBundling [{bar}] {percent:5.1f}%", end="", flush=True)

# ───────────────────────────────
# Main execution
# ───────────────────────────────
def main():
    start_time = time.time()
    config = load_config()
    root = Path(config["input"]).resolve()
    files = list_files(root, config)

    print(f"\n{C.GREEN}🚀 SnapFold running...{C.RESET}")
    print(f"Scanning: {root}\n")

    total = len(files)
    for i, _ in enumerate(files, 1):
        progress_bar(i, total)
        time.sleep(0.01)  # Smooth animation

    md = bundle_files(files, root, config)
    save_output(md, config)

    elapsed = time.time() - start_time
    print(f"{C.BOLD}⏱️  Completed in {elapsed:.2f} seconds{C.RESET}\n")


if __name__ == "__main__":
    main()
