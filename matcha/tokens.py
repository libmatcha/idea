"""
Token definitions and character class defaults for SimpleMatch.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import string


class TokenType(Enum):
    """Types of tokens in a pattern."""
    LITERAL = auto()    # Literal character to match exactly
    PATTERN = auto()    # Pattern token [type:range:length]


class CharType(Enum):
    """Character class types with their default ranges."""
    STR = "str"      # Alphabetic: a-zA-Z
    ANUM = "anum"    # Alphanumeric: a-zA-Z0-9
    HEX = "hex"      # Hexadecimal: 0-9a-fA-F
    OCT = "oct"      # Octal: 0-7
    DEC = "dec"      # Decimal: 0-9
    BIN = "bin"      # Binary: 01
    X = "x"          # Any character (wildcard)


# Default character sets for each type
DEFAULT_CHAR_SETS: dict[CharType, str] = {
    CharType.STR: string.ascii_letters,                    # a-zA-Z
    CharType.ANUM: string.ascii_letters + string.digits,   # a-zA-Z0-9
    CharType.HEX: string.hexdigits,                        # 0-9a-fA-F
    CharType.OCT: "01234567",                              # 0-7
    CharType.DEC: string.digits,                           # 0-9
    CharType.BIN: "01",                                    # 0-1
}


@dataclass
class LengthConstraint:
    """Represents length constraints for a pattern token."""
    min_len: Optional[int] = 1       # Minimum length (None = no minimum)
    max_len: Optional[int] = None    # Maximum length (None = no maximum)
    exact_len: Optional[int] = None  # Exact length (overrides min/max if set)
    
    def matches(self, length: int) -> bool:
        """Check if a length satisfies this constraint."""
        if self.exact_len is not None:
            return length == self.exact_len
        
        if self.min_len is not None and length < self.min_len:
            return False
        if self.max_len is not None and length > self.max_len:
            return False
        
        return True
    
    def get_min(self) -> int:
        """Get minimum allowed length."""
        if self.exact_len is not None:
            return self.exact_len
        return self.min_len if self.min_len is not None else 1
    
    def get_max(self) -> Optional[int]:
        """Get maximum allowed length (None = unbounded)."""
        if self.exact_len is not None:
            return self.exact_len
        return self.max_len


@dataclass
class Token:
    """A token in the pattern."""
    token_type: TokenType
    value: str  # For LITERAL: the character; For PATTERN: the raw [type:range:length]
    
    # Only for PATTERN tokens
    char_type: Optional[CharType] = None
    char_set: Optional[str] = None  # Resolved character set to match against
    length: Optional[LengthConstraint] = None
    negated: bool = False  # If True, match characters NOT in char_set
    literals: Optional[list[str]] = None  # Literal strings to match (e.g., [`black`|`WHITE`])
    
    def __repr__(self) -> str:
        if self.token_type == TokenType.LITERAL:
            return f"LITERAL({self.value!r})"
        neg = "!" if self.negated else ""
        if self.literals:
            return f"PATTERN(type={self.char_type.value}, literals={self.literals}, len={self.length})"
        return f"PATTERN(type={self.char_type.value}, chars={neg}{self.char_set!r}, len={self.length})"

