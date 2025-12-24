# google-scholar-tool

<p align="center">
  <img src=".github/assets/logo-256.png" alt="Google Scholar Tool Logo" width="256" height="256">
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.14+-blue.svg" alt="Python Version"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Code style: ruff"></a>
  <a href="https://github.com/python/mypy"><img src="https://img.shields.io/badge/type%20checked-mypy-blue.svg" alt="Type checked: mypy"></a>
  <a href="https://www.anthropic.com/claude"><img src="https://img.shields.io/badge/AI-Generated-blueviolet.svg" alt="AI Generated"></a>
  <a href="https://www.anthropic.com/claude/code"><img src="https://img.shields.io/badge/Built_with-Claude_Code-5A67D8.svg" alt="Built with Claude Code"></a>
</p>

A CLI tool for querying Google Scholar for academic research.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Search Operators](#search-operators)
- [Multi-Level Verbosity Logging](#multi-level-verbosity-logging)
- [Shell Completion](#shell-completion)
- [Development](#development)
- [Testing](#testing)
- [Security](#security)
- [Known Limitations](#known-limitations)
- [License](#license)

## About

`google-scholar-tool` is a CLI tool for searching Google Scholar publications and authors. It supports Boolean operators, exact phrase matching, and advanced query syntax for academic research.

## Features

- Search Google Scholar publications
- Boolean operators (AND, OR)
- Exact phrase matching with quotes
- Title filters with `intitle:`
- Term exclusion with minus (-)
- Year range filtering
- JSON output for scripting
- Dry-run mode (default) for query preview
- Multi-level verbosity logging (-v/-vv/-vvv)
- Shell completion for bash, zsh, and fish

## Installation

### Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install from source

```bash
git clone https://github.com/dnvriend/google-scholar-tool.git
cd google-scholar-tool
uv tool install .
```

### Verify installation

```bash
google-scholar-tool --version
```

## Usage

### Search Publications

```bash
# Basic search (dry-run by default)
google-scholar-tool search "machine learning"

# Execute the search
google-scholar-tool search "machine learning" --no-dry-run

# Search with exact phrase
google-scholar-tool search "HRM" --exact "job satisfaction" --no-dry-run

# Search with Boolean OR
google-scholar-tool search "HRM OR human resource management" \
    --exact "job satisfaction" --no-dry-run

# Filter by title
google-scholar-tool search "HRM" --exact "job satisfaction" \
    --intitle "the Netherlands" --no-dry-run

# Exclude terms
google-scholar-tool search "machine learning" --exclude "education" --no-dry-run

# Filter by year range
google-scholar-tool search "deep learning" \
    --year-start 2020 --year-end 2024 --no-dry-run

# Output as JSON
google-scholar-tool search "AI" --json-output --no-dry-run --limit 5

# Limit results
google-scholar-tool search "neural networks" --limit 3 --no-dry-run
```

### Search Authors

```bash
# Search by name (dry-run by default)
google-scholar-tool author "John Doe"

# Execute the search
google-scholar-tool author "John Doe" --no-dry-run

# Get author by Scholar ID
google-scholar-tool author --scholar-id "XrH4VJUAAAAJ" --no-dry-run

# JSON output
google-scholar-tool author "researcher" --json-output --no-dry-run
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Enable verbose output (count: -v/-vv/-vvv) |
| `--quiet` | `-q` | Suppress all output except errors |
| `--version` | | Show version |
| `--help` | `-h` | Show help |

### Search Options

| Option | Short | Description |
|--------|-------|-------------|
| `--exact` | `-e` | Exact phrase (can repeat) |
| `--exclude` | `-x` | Term to exclude (can repeat) |
| `--intitle` | `-t` | Term must appear in title |
| `--limit` | `-l` | Max results (default: 10) |
| `--year-start` | | Filter from this year |
| `--year-end` | | Filter up to this year |
| `--json-output` | `-j` | Output as JSON |
| `--dry-run` | `-n` | Show query without executing (default) |
| `--no-dry-run` | | Execute the query |
| `--stdin` | `-s` | Read query from stdin |

## Search Operators

The tool supports Google Scholar search operators:

| Operator | Example | Description |
|----------|---------|-------------|
| `OR` | `HRM OR "human resource management"` | Match either term |
| Quotes | `"job satisfaction"` | Exact phrase match |
| `intitle:` | `--intitle "Netherlands"` | Term in title |
| Minus | `--exclude "education"` | Exclude term |
| Year range | `--year-start 2020 --year-end 2024` | Publication date filter |

### Example: Academic Research Query

From the course material on finding scientific sources:

```bash
# Build the query: (HRM OR "human resource management") AND "job satisfaction"
google-scholar-tool search "HRM OR human resource management" \
    --exact "job satisfaction" --no-dry-run

# Add title filter: intitle:"the Netherlands"
google-scholar-tool search "HRM" --exact "job satisfaction" \
    --intitle "the Netherlands" --no-dry-run
```

## Multi-Level Verbosity Logging

| Flag | Level | Output |
|------|-------|--------|
| (none) | WARNING | Errors and warnings only |
| `-v` | INFO | + High-level operations |
| `-vv` | DEBUG | + Detailed info |
| `-vvv` | TRACE | + Library internals |

```bash
# See operations and progress
google-scholar-tool -v search "test" --no-dry-run

# Full debugging
google-scholar-tool -vv search "test" --no-dry-run
```

## Shell Completion

```bash
# Bash
eval "$(google-scholar-tool completion bash)"

# Zsh
eval "$(google-scholar-tool completion zsh)"

# Fish
google-scholar-tool completion fish | source
```

## Development

```bash
# Install dependencies
make install

# Run all checks
make check

# Run full pipeline
make pipeline
```

### Available Commands

```bash
make format          # Format code
make lint            # Run linting
make typecheck       # Type checking
make test            # Run tests
make security        # Security scans
make pipeline        # Full pipeline
```

## Testing

```bash
# Run all tests
make test

# Run with verbose output
uv run pytest tests/ -v
```

## Security

```bash
# Run all security checks
make security

# Individual checks
make security-bandit       # Python security linting
make security-pip-audit    # Dependency CVE scanning
make security-gitleaks     # Secret detection
```

## Known Limitations

- **Author Search Rate Limiting**: Google Scholar may redirect author searches to login pages during heavy use. Publication search is more reliable.
- **No Proxy Configuration**: For heavy usage, consider configuring a proxy in the `scholarly` library to avoid rate limiting.
- **scholarly Library Warnings**: The underlying `scholarly` library may show deprecation warnings on Python 3.14.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Dennis Vriend** - [@dnvriend](https://github.com/dnvriend)

---

**Generated with AI**

This project was generated using [Claude Code](https://www.anthropic.com/claude/code).
