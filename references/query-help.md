# Google Scholar Query Reference

## Raw Query Syntax

Use Google Scholar's native query syntax directly:

```bash
# Exact phrase
google-scholar-tool search '"job satisfaction"'

# Boolean OR
google-scholar-tool search '"HRM" OR "human resource management"'

# Boolean AND (implicit)
google-scholar-tool search '"HRM" "job satisfaction"'

# Boolean AND (explicit)
google-scholar-tool search '"HRM" AND "job satisfaction"'

# Combined OR and AND
google-scholar-tool search '"HRM" OR "human resource management" AND "job satisfaction"'

# Title filter
google-scholar-tool search '"job satisfaction" intitle:"Netherlands"'

# Exclude terms
google-scholar-tool search '"machine learning" -education'

# Author filter
google-scholar-tool search 'author:"Einstein"'

# Publication filter
google-scholar-tool search 'source:"Nature"'

# Complex query
google-scholar-tool search '"HRM" OR "human resource management" AND "job satisfaction" intitle:"Netherlands" -education'
```

## Helper Options (Alternative)

Use CLI options to build queries programmatically:

```bash
# Exact phrase with --exact
google-scholar-tool search "HRM" --exact "job satisfaction"
# Equivalent: "HRM" AND "job satisfaction"

# Title filter with --intitle
google-scholar-tool search "HRM" --intitle "Netherlands"
# Equivalent: "HRM" intitle:"Netherlands"

# Exclude terms with --exclude
google-scholar-tool search "machine learning" --exclude "education"
# Equivalent: "machine learning" -education

# Multiple exact phrases
google-scholar-tool search "AI" --exact "healthcare" --exact "diagnosis"
# Equivalent: "AI" AND "healthcare" AND "diagnosis"

# Combined options
google-scholar-tool search "HRM" --exact "job satisfaction" --intitle "Netherlands" --exclude "education"
# Equivalent: "HRM" AND "job satisfaction" intitle:"Netherlands" -education

# Year filter (not available in raw syntax)
google-scholar-tool search "deep learning" --year-start 2020 --year-end 2024
```

## When to Use Each

| Use Case | Recommended |
|----------|-------------|
| Simple query | Raw syntax |
| Complex Boolean | Raw syntax |
| Scripting/automation | Helper options |
| Year filtering | Helper options (only way) |
| Multiple exact phrases | Helper options |

## Query Operators Reference

| Operator | Raw Syntax | Helper Option |
|----------|------------|---------------|
| Exact phrase | `"phrase"` | `--exact "phrase"` |
| OR | `term1 OR term2` | In query string |
| AND | `term1 AND term2` | `--exact` adds AND |
| Exclude | `-term` | `--exclude "term"` |
| In title | `intitle:"term"` | `--intitle "term"` |
| Author | `author:"name"` | In query string |
| Source | `source:"journal"` | In query string |
| Year range | N/A | `--year-start --year-end` |

## Examples from Course Material

From "Hoe vind ik relevante wetenschappelijke bronnen?":

```bash
# Basic: HRM and job satisfaction
google-scholar-tool search '"human resource management" OR HRM AND "job satisfaction"'

# With Netherlands filter
google-scholar-tool search '"human resource management" OR HRM AND "job satisfaction" intitle:"the Netherlands"'

# Using helper options
google-scholar-tool search "HRM OR human resource management" \
    --exact "job satisfaction" \
    --intitle "the Netherlands"
```

## Output Options

```bash
# Default: human-readable
google-scholar-tool search "AI"

# JSON output (for scripting)
google-scholar-tool search "AI" --json-output

# Limit results
google-scholar-tool search "AI" --limit 5

# Quiet mode (no output)
google-scholar-tool search "AI" -q
```
