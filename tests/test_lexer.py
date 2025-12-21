"""
Tests for the SimpleMatch lexer.
"""

import pytest
from matcha.lexer import Lexer, LexerError
from matcha.tokens import TokenType, CharType


class TestLexerBasic:
    """Test basic lexer functionality."""
    
    def test_literal_only(self):
        """Test tokenizing literal characters."""
        lexer = Lexer("hello")
        tokens = list(lexer.tokenize())
        
        assert len(tokens) == 5
        assert all(t.token_type == TokenType.LITERAL for t in tokens)
        assert "".join(t.value for t in tokens) == "hello"
    
    def test_single_pattern(self):
        """Test tokenizing a single pattern token."""
        lexer = Lexer("[str::]")
        tokens = list(lexer.tokenize())
        
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.PATTERN
        assert tokens[0].char_type == CharType.STR
    
    def test_pattern_with_literals(self):
        """Test pattern mixed with literals."""
        lexer = Lexer("[anum::]@[anum::]")
        tokens = list(lexer.tokenize())
        
        assert len(tokens) == 3
        assert tokens[0].token_type == TokenType.PATTERN
        assert tokens[1].token_type == TokenType.LITERAL
        assert tokens[1].value == "@"
        assert tokens[2].token_type == TokenType.PATTERN


class TestLexerTypes:
    """Test character type parsing."""
    
    @pytest.mark.parametrize("type_str,expected", [
        ("str", CharType.STR),
        ("anum", CharType.ANUM),

        ("hex", CharType.HEX),
        ("oct", CharType.OCT),
        ("dec", CharType.DEC),
        ("bin", CharType.BIN),
    ])
    def test_all_types(self, type_str: str, expected: CharType):
        """Test all supported character types."""
        lexer = Lexer(f"[{type_str}::]")
        tokens = list(lexer.tokenize())
        
        assert tokens[0].char_type == expected


class TestLexerRanges:
    """Test range parsing."""
    
    def test_default_range_str(self):
        """Test default range for str type."""
        lexer = Lexer("[str::]")
        tokens = list(lexer.tokenize())
        
        char_set = tokens[0].char_set
        assert 'a' in char_set
        assert 'Z' in char_set
        assert '0' not in char_set
    
    def test_custom_range(self):
        """Test custom range A-Z."""
        lexer = Lexer("[str:A-Z:]")
        tokens = list(lexer.tokenize())
        
        char_set = tokens[0].char_set
        assert 'A' in char_set
        assert 'Z' in char_set
        assert 'a' not in char_set
    
    def test_alternative_chars(self):
        """Test pipe-separated alternatives."""
        lexer = Lexer("[str:S|s:]")
        tokens = list(lexer.tokenize())
        
        char_set = tokens[0].char_set
        assert 'S' in char_set
        assert 's' in char_set
        assert len(char_set) == 2


class TestLexerLength:
    """Test length constraint parsing."""
    
    def test_default_length(self):
        """Test default length (1 or more)."""
        lexer = Lexer("[str::]")
        tokens = list(lexer.tokenize())
        
        length = tokens[0].length
        assert length.min_len == 1
        assert length.max_len is None
    
    def test_exact_length(self):
        """Test exact length constraint."""
        lexer = Lexer("[str::5]")
        tokens = list(lexer.tokenize())
        
        length = tokens[0].length
        assert length.exact_len == 5
    
    def test_min_length(self):
        """Test minimum length constraint."""
        lexer = Lexer("[str::>=5]")
        tokens = list(lexer.tokenize())
        
        length = tokens[0].length
        assert length.min_len == 5
        assert length.max_len is None
    
    def test_max_length(self):
        """Test maximum length constraint."""
        lexer = Lexer("[str::<=5]")
        tokens = list(lexer.tokenize())
        
        length = tokens[0].length
        assert length.max_len == 5
    
    def test_range_length_exclusive(self):
        """Test exclusive range >1<5."""
        lexer = Lexer("[str::>1<5]")
        tokens = list(lexer.tokenize())
        
        length = tokens[0].length
        assert length.min_len == 2  # >1 means min is 2
        assert length.max_len == 4  # <5 means max is 4
    
    def test_range_length_inclusive(self):
        """Test inclusive range >=1<=5."""
        lexer = Lexer("[str::>=1<=5]")
        tokens = list(lexer.tokenize())
        
        length = tokens[0].length
        assert length.min_len == 1
        assert length.max_len == 5


class TestLexerEscape:
    """Test escape sequence handling."""
    
    def test_escape_bracket(self):
        """Test escaping opening bracket."""
        lexer = Lexer("\\[test\\]")
        tokens = list(lexer.tokenize())
        
        assert len(tokens) == 6
        assert tokens[0].value == "["
        assert tokens[5].value == "]"


class TestLexerErrors:
    """Test error handling."""
    
    def test_unclosed_bracket(self):
        """Test error on unclosed bracket."""
        lexer = Lexer("[str::")
        
        with pytest.raises(LexerError) as exc:
            list(lexer.tokenize())
        
        assert "Unclosed" in str(exc.value)
    
    def test_invalid_type(self):
        """Test error on invalid type."""
        lexer = Lexer("[invalid::]")
        
        with pytest.raises(LexerError) as exc:
            list(lexer.tokenize())
        
        assert "Invalid type" in str(exc.value)
    
    def test_invalid_format(self):
        """Test error on wrong format."""
        lexer = Lexer("[str]")  # Missing colons
        
        with pytest.raises(LexerError) as exc:
            list(lexer.tokenize())
        
        assert "format" in str(exc.value).lower()
