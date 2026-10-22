#!/usr/bin/env python3
"""
zip_to_md.py

Looks for .zip files in the current directory (or a directory you pass in).
For each one, creates a .md file with the same name (app.zip -> app.md)
containing a header for every file inside the zip, followed by its contents.

Usage:
    python zip_to_md.py            # scan the folder the script is in
    python zip_to_md.py /some/dir  # scan a specific folder
"""

import sys
import zipfile
from pathlib import Path, PurePosixPath

# File extension -> code fence language
LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".sh": "bash",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".sql": "sql",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".c": "c",
    ".cpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".txt": "text",
}

# Files that are already markdown-ish are inserted as-is, not fenced
MARKDOWN_EXTS = {".md", ".markdown"}


def make_header(name: str) -> str:
    """Header for a file section.

    Uses the full path inside the zip so same-named files in different folders
    (two build.gradle.kts, five ic_launcher_foreground.png...) can be told apart.
    README files are labelled 'Read Me'; if one is nested, its path is added.
    """
    path = name.replace("\\", "/")
    if Path(path).stem.lower() == "readme":
        return "Read Me" if "/" not in path else f"Read Me ({path})"
    return path


def format_size(num_bytes: int) -> str:
    """Human-friendly file size, e.g. 4.2 KB."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def read_text(data: bytes) -> str | None:
    """Decode bytes as text, or return None if the file looks binary."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        if "\x00" in text:
            return None
        return text
    return None


def fence_for(content: str) -> str:
    """Pick a backtick fence longer than any run of backticks in the content."""
    longest = 0
    run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def is_skipped(info: zipfile.ZipInfo) -> bool:
    """Skip folder entries and macOS junk."""
    if info.is_dir():
        return True
    if "__MACOSX" in info.filename or Path(info.filename).name == ".DS_Store":
        return True
    return False


def build_tree(paths: list[str]) -> dict:
    """Turn a list of file paths into a nested dict. Files are leaves (None)."""
    tree: dict = {}
    for path in paths:
        parts = PurePosixPath(path.replace("\\", "/")).parts
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None
    return tree


def render_tree(node: dict, prefix: str = "") -> list[str]:
    """Render the nested dict as an ASCII tree (folders first, then files)."""
    lines = []
    entries = sorted(node.items(), key=lambda kv: (kv[1] is None, kv[0].lower()))
    for i, (name, child) in enumerate(entries):
        last = i == len(entries) - 1
        connector = "└── " if last else "├── "
        if child is None:
            lines.append(f"{prefix}{connector}{name}")
        else:
            lines.append(f"{prefix}{connector}{name}/")
            extension = "    " if last else "│   "
            lines.extend(render_tree(child, prefix + extension))
    return lines


def zip_to_markdown(zip_path: Path) -> Path:
    md_path = zip_path.with_suffix(".md")
    sections = []

    with zipfile.ZipFile(zip_path) as zf:
        infos = [info for info in zf.infolist() if not is_skipped(info)]

        # Directory structure overview at the top of the .md
        tree_lines = [f"{zip_path.name}/"]
        tree_lines += render_tree(build_tree([info.filename for info in infos]))
        sections.append(
            "# Project Structure\n\n```text\n" + "\n".join(tree_lines) + "\n```\n"
        )

        for info in infos:

            ext = Path(info.filename).suffix.lower()
            header = make_header(info.filename)
            text = read_text(zf.read(info))

            if text is None:
                body = f"*Binary file ({format_size(info.file_size)}) - contents not included.*"
            elif ext in MARKDOWN_EXTS:
                body = text.strip()
            else:
                fence = fence_for(text)
                lang = LANGUAGES.get(ext, "")
                body = f"{fence}{lang}\n{text.rstrip()}\n{fence}"

            sections.append(f"# {header}\n\n{body}\n")

    md_path.write_text("\n".join(sections), encoding="utf-8")
    return md_path


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent

    if not folder.is_dir():
        print(f"Not a directory: {folder}")
        sys.exit(1)

    zips = sorted(folder.glob("*.zip"))
    if not zips:
        print(f"No .zip files found in {folder}")
        return

    for zip_path in zips:
        try:
            md_path = zip_to_markdown(zip_path)
            print(f"{zip_path.name} -> {md_path.name}")
        except zipfile.BadZipFile:
            print(f"Skipped {zip_path.name}: not a valid zip file")


if __name__ == "__main__":
    main()
