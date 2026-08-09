# gitbloom

Detect and prune stale Git-style comment blocks at the ends of files.

## About / description

`gitbloom` inspects configuration, source, and documentation files that accumulate
per-file trailing comment blocks over time. Rather than deleting comments manually—
or leaving old TODOs, rollback notes, and debug annotations sitting forever—it lets
you detect the oldest blocks by date marker, list them, and optionally rewrite the
file with only the recent ones.

## Features

- Detect Git-style comment blocks at the end of files.
- Identify the oldest dated block by `@date` markers, date-friendly timestamps, or
  relative body content.
- List detected stale blocks before editing any file.
- Rewrite files in place or emit a replacement to stdout.
- JSON output for automation and CI.

## Installation

```bash
python -m pip install -e .
```

After installing, `gitbloom` is on your `PATH`.

## Project structure

```
gitbloom/
├── README.md
├── LICENSE
├── pyproject.toml
├── src/
│   └── gitbloom/
│       ├── __init__.py
│       ├── cli.py
│       └── scanner.py
└── tests/
    └── test_gitbloom.py
```

## Usage

```text
Usage: gitbloom list  <files...>
   or: gitbloom prune <files...> [--keep N] [--date-format fmt]
   or: gitbloom --version
   or: gitbloom --help
```

List detected bloom blocks:

```bash
gitbloom list README.md src/app.py
```

Prune all but the most recent blocks:

```bash
gitbloom prune src/ --keep 1
```

Machine-readable output:

```bash
gitbloom list README.md --format json
gitbloom prune app.py --format json > result.json
```

## Tags / keywords

`cli` · `maintenance` · `comments` · `git` · `python` · `static-analysis`
