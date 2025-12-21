"""
SimpleMatch - A human-readable pattern matching library.

Alternative to regex with intuitive [type:range:length] syntax.

Example usage:
    from simplematch import match, find, find_all

    # Match entire string
    match("[anum::]@[anum::].[str::>1<3]", "example@mail.com")  # True

    # Find first match in text
    find("[str:A-Z:>=3]", "Hello WORLD today")  # "WORLD"

    # Find all matches
    find_all("[dec::]", "abc123def456")  # ["123", "456"]
"""

from matcha.matcher import match, find, find_all
from matcha.lexer import Lexer
from matcha.parser import Parser

__all__ = ["match", "find", "find_all", "Lexer", "Parser"]
__version__ = "0.1.0"
