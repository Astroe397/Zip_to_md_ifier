# Zip to Markdown (`zip_to_md.py`)

A standalone Python utility script that automatically scans a target directory for `.zip` archives and unpacks their contents into structured, single-file Markdown (`.md`) documents.

It creates an ASCII folder hierarchy overview at the beginning of each Markdown file and formats every internal file into readable Markdown text or syntactically highlighted code blocks.

---

## Features

* **Directory Structure Visualization**: Renders a complete ASCII file tree at the top of the output Markdown file to provide instant project overview.
* **Smart Language Identification**: Maps common extensions (`.py`, `.js`, `.kt`, `.rs`, `.sql`, etc.) to their respective code fence identifiers for syntax highlighting.
* **Adaptive Code Fencing**: Dynamically calculates the required backtick length (e.g., ```` ``` ```` or ```` ```` ``` ````) to safely enclose code containing embedded backticks without syntax breakage.
* **Clean Formatting**:
  * Markdown files (`.md`, `.markdown`) are embedded directly into the document.
  * Binary files (e.g., images, executables, compiled code) are safely detected and rendered with size metadata instead of raw bytecode.
  * Filters out OS-specific metadata folders (`__MACOSX`, `.DS_Store`).

---

## Requirements

* **Python**: `3.10` or higher (uses union type hint syntax `str | None`).
* **Dependencies**: Standard Library only (`sys`, `zipfile`, `pathlib`). No external `pip` packages required.

---

## Usage

### 1. Process Current Directory
Run the script without arguments to search for and convert all `.zip` files in the directory where `zip_to_md.py` is located:

```bash
python zip_to_md.py
```

### 2. Process Specific Directory
Pass a folder path as an argument to scan a specific target directory:

```bash
python zip_to_md.py /path/to/target/folder
```

---

## Output Example

For an archive named `project.zip`, the script outputs a file named `project.md` with the following structure:

````markdown
# Project Structure

```text
project.zip/
├── src/
│   ├── index.js
│   └── styles.css
└── README.md
```

# Read Me

Welcome to the project documentation...

# src/index.js

```javascript
console.log("Hello, world!");
```

# src/styles.css

```css
body {
  margin: 0;
}
```
````

---

## Supported File Extensions & Mappings

| Extension | Language Identifier | Extension | Language Identifier |
| :--- | :--- | :--- | :--- |
| `.py` | `python` | `.kt`, `.kts` | `kotlin` |
| `.js` | `javascript` | `.c`, `.cpp` | `c`, `cpp` |
| `.ts` | `typescript` | `.go` | `go` |
| `.html` | `html` | `.rs` | `rust` |
| `.css` | `css` | `.rb` | `ruby` |
| `.json` | `json` | `.php` | `php` |
| `.yml`, `.yaml` | `yaml` | `.sql` | `sql` |
| `.toml` | `toml` | `.xml` | `xml` |
| `.sh` | `bash` | `.java` | `java` |