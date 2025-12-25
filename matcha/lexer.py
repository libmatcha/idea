"""
Lexer for SimpleMatch patterns.

Tokenizes pattern strings into a stream of tokens (LITERAL and PATTERN).
"""

from typing import Iterator
from matcha.tokens import (
    Token, TokenType, CharType, LengthConstraint, DEFAULT_CHAR_SETS
)


class LexerError(Exception):
    """Raised when the lexer encounters invalid syntax."""
    def __init__(self, message: str, position: int):
        self.position = position
        super().__init__(f"{message} at position {position}")


class Lexer:
    """
    Tokenizes a SimpleMatch pattern string.
    
    Example:
        lexer = Lexer("[anum::]@[str::>=2]")
        tokens = list(lexer.tokenize())
    """
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.pos = 0
    
    def tokenize(self) -> Iterator[Token]:
        """
        Generate tokens from the pattern string.
        
        Yields:
            Token objects representing each part of the pattern.
        
        Raises:
            LexerError: If the pattern contains invalid syntax.
        """
        while self.pos < len(self.pattern):
            if self.pattern[self.pos] == '[':
                yield self._parse_pattern_token()
            elif self.pattern[self.pos] == '\\':
                yield self._parse_escape()
            else:
                yield self._parse_literal()
    
    def _parse_literal(self) -> Token:
        """Parse a single literal character."""
        char = self.pattern[self.pos]
        self.pos += 1
        return Token(token_type=TokenType.LITERAL, value=char)
    
    def _parse_escape(self) -> Token:
        """Parse an escape sequence (e.g., \\[, \\])."""
        if self.pos + 1 >= len(self.pattern):
            raise LexerError("Escape sequence at end of pattern", self.pos)
        
        self.pos += 1  # Skip backslash
        char = self.pattern[self.pos]
        self.pos += 1
        return Token(token_type=TokenType.LITERAL, value=char)
    
    def _parse_pattern_token(self) -> Token:
        """
        Parse a pattern token [type:range:length].
        
        Returns:
            A Token with parsed type, range, and length constraint.
        """
        start_pos = self.pos
        self.pos += 1  # Skip opening bracket
        
        # Find closing bracket
        end = self.pattern.find(']', self.pos)
        if end == -1:
            raise LexerError("Unclosed pattern bracket", start_pos)
        
        content = self.pattern[self.pos:end]
        self.pos = end + 1  # Move past closing bracket
        
        # Parse type:range:length
        parts = content.split(':')
        if len(parts) != 3:
            raise LexerError(
                f"Pattern must have format [type:range:length], got [{content}]",
                start_pos
            )
        
        type_str, range_str, length_str = parts
        
        # Parse type
        char_type = self._parse_char_type(type_str, start_pos)
        
        # Parse range (or use default)
        char_set, negated, literals = self._parse_range(range_str, char_type)
        
        # Parse length constraint
        length_constraint = self._parse_length(length_str, start_pos)
        
        return Token(
            token_type=TokenType.PATTERN,
            value=f"[{content}]",
            char_type=char_type,
            char_set=char_set,
            length=length_constraint,
            negated=negated,
            literals=literals
        )
    
    def _parse_char_type(self, type_str: str, pos: int) -> CharType:
        """Parse the character type from the pattern."""
        type_str = type_str.strip().lower()
        try:
            return CharType(type_str)
        except ValueError:
            valid_types = [t.value for t in CharType]
            raise LexerError(
                f"Invalid type '{type_str}'. Valid types: {valid_types}",
                pos
            )
    
    def _parse_range(self, range_str: str, char_type: CharType) -> tuple[str, bool, list[str]]:
        """
        Parse the character range, or return default for the type.
        
        Supports:
        - Empty: use default for type
        - Range: A-Z, a-z, 0-9
        - Alternatives: S|s, A|B|C
        - Combined: A-Za-z
        - X type: returns None (matches any character)
        - NOT: !A-Z (matches anything except A-Z)
        - Literals: `black`|`WHITE` (matches exact strings)
        
        Returns:
            tuple of (char_set, negated, literals)
        """
        range_str = range_str.strip()
        
        # X type matches any character - return None to signal wildcard
        if char_type == CharType.X:
            return None, False, None
        
        if not range_str:
            return DEFAULT_CHAR_SETS[char_type], False, None
        
        # Check for negation prefix
        negated = False
        if range_str.startswith('!'):
            negated = True
            range_str = range_str[1:]
        
        # Check if this is a literal pattern (contains backticks)
        if '`' in range_str:
            literals = self._parse_literals(range_str)
            return None, negated, literals
        
        # Parse character set
        char_set = set()
        i = 0
        
        while i < len(range_str):
            char = range_str[i]
            
            # Check for pipe-separated alternatives
            if char == '|':
                i += 1
                continue
            
            # Check for range like A-Z
            if i + 2 < len(range_str) and range_str[i + 1] == '-':
                start_char = char
                end_char = range_str[i + 2]
                
                # Add all characters in range
                for code in range(ord(start_char), ord(end_char) + 1):
                    char_set.add(chr(code))
                
                i += 3
            else:
                # Single character
                char_set.add(char)
                i += 1
        
        return ''.join(sorted(char_set)), negated, None
    
    def _parse_literals(self, range_str: str) -> list[str]:
        """
        Parse literal strings from backtick-delimited format.
        
        Example: `black`|`WHITE` -> ["black", "WHITE"]
        """
        literals = []
        i = 0
        
        while i < len(range_str):
            if range_str[i] == '`':
                # Find closing backtick
                end = range_str.find('`', i + 1)
                if end == -1:
                    # Unclosed backtick, treat rest as literal
                    literals.append(range_str[i + 1:])
                    break
                literals.append(range_str[i + 1:end])
                i = end + 1
            elif range_str[i] == '|':
                i += 1
            else:
                i += 1
        
        return literals if literals else None
    
    def _parse_length(self, length_str: str, pos: int) -> LengthConstraint:
        """
        Parse length constraint string.
        
        Supports:
        - Empty: 1 or more (default)
        - "5": exactly 5
        - ">=5": 5 or more
        - "<=5": 5 or less
        - ">5": more than 5
        - "<5": less than 5
        - ">1<5": between 2 and 4 (exclusive)
        - ">=1<=5": between 1 and 5 (inclusive)
        """
        length_str = length_str.strip()
        
        if not length_str:
            return LengthConstraint(min_len=1, max_len=None)
        
        # Check for exact length (just a number)
        if length_str.isdigit():
            return LengthConstraint(exact_len=int(length_str))
        
        min_len = None
        max_len = None
        i = 0
        
        while i < len(length_str):
            if length_str[i:i+2] == '>=':
                i += 2
                num, i = self._extract_number(length_str, i, pos)
                min_len = num
            elif length_str[i:i+2] == '<=':
                i += 2
                num, i = self._extract_number(length_str, i, pos)
                max_len = num
            elif length_str[i] == '>':
                i += 1
                num, i = self._extract_number(length_str, i, pos)
                min_len = num + 1  # Exclusive: >5 means min is 6
            elif length_str[i] == '<':
                i += 1
                num, i = self._extract_number(length_str, i, pos)
                max_len = num - 1  # Exclusive: <5 means max is 4
            else:
                raise LexerError(
                    f"Invalid length constraint: {length_str}",
                    pos
                )
        
        return LengthConstraint(min_len=min_len if min_len is not None else 1, max_len=max_len)
    
    def _extract_number(self, s: str, start: int, pos: int) -> tuple[int, int]:
        """Extract a number from string starting at position."""
        end = start
        while end < len(s) and s[end].isdigit():
            end += 1
        
        if end == start:
            raise LexerError(f"Expected number in length constraint", pos)
        
        return int(s[start:end]), end
