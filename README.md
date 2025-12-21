# Matcha

A simple, human-readable pattern matching library as an alternative to regex.

## Installation

```bash
# Using uv
uv add matcha

# Or using pip
pip install matcha
```

## Quick Start

```python
from matcha import match, find, find_all

# Match entire string against pattern
match("[str:A-Z:]", "HELLO")  # True
match("[str:A-Z:]", "Hello")  # False (has lowercase)

# Find first occurrence in text
find("[dec::]", "abc123def456")  # "123"

# Find all occurrences
find_all("[dec::]", "abc123def456")  # ["123", "456"]
```

## Pattern Syntax

The core token format is: `[type:range:length]`

### Types

| Type | Default Range | Description |
|------|--------------|-------------|
| `str` | `a-zA-Z` | Alphabetic characters |
| `anum` | `a-zA-Z0-9` | Alphanumeric characters |
| `dec` | `0-9` | Decimal/numeric digits |
| `hex` | `0-9a-fA-F` | Hexadecimal characters |
| `oct` | `0-7` | Octal digits |
| `bin` | `01` | Binary digits |

### Range (Optional)

Customize the character set:

```python
# Only uppercase letters
"[str:A-Z:]"

# Only S or s
"[str:S|s:]"

# Custom combination
"[str:A-Za-z0-9_:]"
```

### Length (Optional)

Constrain the length of matches:

| Syntax | Meaning |
|--------|---------|
| (empty) | 1 or more characters |
| `5` | Exactly 5 characters |
| `>=5` | 5 or more characters |
| `<=5` | 5 or fewer characters |
| `>1<5` | Between 2 and 4 (exclusive) |
| `>=1<=5` | Between 1 and 5 (inclusive) |

## Examples

### Email Matching

```python
pattern = "[anum::]@[anum::].[str::>=2<=4]"

match(pattern, "example@mail.com")   # True
match(pattern, "user@domain.co")     # True
match(pattern, "invalid@domain.x")   # False (TLD too short)
```

### Capital Names (5+ letters)

```python
pattern = "[str:A-Z:>=5]"

match(pattern, "SAJJAD")  # True (6 letters)
match(pattern, "HELLO")   # True (5 letters)
match(pattern, "MARK")    # False (4 letters)
```

### Names Starting with S

```python
pattern = "[str:S|s:1][str::]"

match(pattern, "Sajjad")  # True
match(pattern, "sadiq")   # True
match(pattern, "Mark")    # False
```

### Hex Color Codes

```python
pattern = "#[hex::6]"

match(pattern, "#ff0000")  # True
match(pattern, "#DEADBE")  # True
match(pattern, "#123")     # False (too short)
```

### Phone Numbers

```python
pattern = "[dec::3]-[dec::3]-[dec::4]"

match(pattern, "123-456-7890")  # True
```

### Binary Bytes

```python
pattern = "[bin::8]"

match(pattern, "10101010")  # True
match(pattern, "12345678")  # False (not binary)
```

## API Reference

### `match(pattern, text) -> bool`

Check if the entire text matches the pattern.

### `find(pattern, text) -> str | None`

Find the first match in the text, or None if not found.

### `find_all(pattern, text) -> list[str]`

Find all non-overlapping matches in the text.

## Escaping Special Characters

Use backslash to escape special characters:

```python
match("\\[test\\]", "[test]")  # True
```

## License

MIT
