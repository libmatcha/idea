"""
Tests for the SimpleMatch matcher.
"""

import pytest
from matcha import match, find, find_all


class TestMatchBasic:
    """Test basic matching functionality."""
    
    def test_literal_match(self):
        """Test matching literal characters only."""
        assert match("hello", "hello")
        assert not match("hello", "world")
        assert not match("hello", "hello!")
    
    def test_simple_pattern(self):
        """Test matching simple pattern."""
        assert match("[str::]", "hello")
        assert match("[str::]", "WORLD")
        assert not match("[str::]", "hello123")


class TestMatchExamples:
    """Test the examples from requirements."""
    
    def test_email_pattern(self):
        """Test email matching with TLD length constraint."""
        # >=2<=4 means 2-4 characters (com, co, info, etc.)
        pattern = "[anum::]@[anum::].[str::>=2<=4]"
        
        assert match(pattern, "example@mail.com")  # com = 3 chars
        assert match(pattern, "user123@domain.co")  # co = 2 chars
        assert match(pattern, "test@site.info")     # info = 4 chars
        assert not match(pattern, "invalid@domain.x")  # Too short (1 char)
        assert not match(pattern, "invalid@domain.travel")  # Too long (6 chars)
    
    def test_email_pattern_exclusive(self):
        """Test the original example with >1<3 (exclusive = exactly 2 chars)."""
        pattern = "[anum::]@[anum::].[str::>1<3]"
        
        assert match(pattern, "example@mail.co")  # co = 2 chars
        assert not match(pattern, "example@mail.com")  # com = 3 chars (>1<3 means only 2)
    
    def test_capital_letters(self):
        """Test capital letters: [str:A-Z:]"""
        pattern = "[str:A-Z:]"
        
        assert match(pattern, "MARK")
        assert match(pattern, "HELLO")
        assert not match(pattern, "Mark")  # Has lowercase
        assert not match(pattern, "HELLO123")  # Has numbers
    
    def test_capital_min_length(self):
        """Test capital with min length: [str:A-Z:>=5]"""
        pattern = "[str:A-Z:>=5]"
        
        assert match(pattern, "SAJJAD")  # 6 letters
        assert match(pattern, "HELLO")   # 5 letters
        assert not match(pattern, "MARK")  # 4 letters
    
    def test_starts_with_s(self):
        """Test names starting with S|s: [str:S|s:1][str::]"""
        pattern = "[str:S|s:1][str::]"
        
        assert match(pattern, "Sajjad")
        assert match(pattern, "sadiq")
        assert not match(pattern, "Mark")  # Doesn't start with S


class TestMatchTypes:
    """Test different character types."""
    
    def test_alphanumeric(self):
        """Test anum type."""
        assert match("[anum::]", "hello123")
        assert match("[anum::]", "ABC")
        assert not match("[anum::]", "hello@world")  # Has @
    
    def test_numeric(self):
        """Test dec type."""
        assert match("[dec::]", "12345")
        assert not match("[dec::]", "123abc")
    
    def test_hexadecimal(self):
        """Test hex type."""
        assert match("[hex::]", "1a2b3c")
        assert match("[hex::]", "DEADBEEF")
        assert not match("[hex::]", "1g2h")  # g, h not hex
    
    def test_binary(self):
        """Test bin type."""
        assert match("[bin::]", "10101010")
        assert not match("[bin::]", "102")  # 2 not binary
    
    def test_octal(self):
        """Test oct type."""
        assert match("[oct::]", "01234567")
        assert not match("[oct::]", "0189")  # 8, 9 not octal


class TestMatchLength:
    """Test length constraints."""
    
    def test_exact_length(self):
        """Test exact length constraint."""
        pattern = "[str::3]"
        
        assert match(pattern, "abc")
        assert not match(pattern, "ab")
        assert not match(pattern, "abcd")
    
    def test_min_length(self):
        """Test minimum length."""
        pattern = "[str::>=3]"
        
        assert match(pattern, "abc")
        assert match(pattern, "abcdef")
        assert not match(pattern, "ab")
    
    def test_max_length(self):
        """Test maximum length."""
        pattern = "[str::<=3]"
        
        assert match(pattern, "a")
        assert match(pattern, "abc")
        assert not match(pattern, "abcd")
    
    def test_range_length(self):
        """Test length range."""
        pattern = "[str::>=2<=4]"
        
        assert not match(pattern, "a")
        assert match(pattern, "ab")
        assert match(pattern, "abcd")
        assert not match(pattern, "abcde")


class TestFind:
    """Test find functionality."""
    
    def test_find_first(self):
        """Test finding first match."""
        assert find("[dec::]", "abc123def456") == "123"
    
    def test_find_not_found(self):
        """Test when no match found."""
        assert find("[dec::]", "no numbers here") is None
    
    def test_find_at_start(self):
        """Test finding at start of string."""
        assert find("[str:A-Z:]", "HELLO world") == "HELLO"


class TestFindAll:
    """Test find_all functionality."""
    
    def test_find_all_multiple(self):
        """Test finding multiple matches."""
        result = find_all("[dec::]", "abc123def456ghi789")
        assert result == ["123", "456", "789"]
    
    def test_find_all_none(self):
        """Test when no matches found."""
        result = find_all("[dec::]", "no numbers")
        assert result == []
    
    def test_find_all_words(self):
        """Test finding words."""
        result = find_all("[str:A-Z:]", "HELLO there WORLD")
        assert result == ["HELLO", "WORLD"]


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_text(self):
        """Test matching empty text."""
        assert not match("[str::]", "")
    
    def test_empty_pattern_literals(self):
        """Test pattern with only empty literals."""
        assert match("", "")
        assert not match("", "text")
    
    def test_special_chars_literal(self):
        """Test matching special characters as literals."""
        assert match("[anum::]@[anum::]", "test@domain")
        assert match("[dec::]-[dec::]-[dec::]", "123-456-789")
    
    def test_escaped_brackets(self):
        """Test escaped brackets."""
        assert match("\\[test\\]", "[test]")


class TestBacktracking:
    """Test backtracking behavior."""
    
    def test_greedy_backtrack(self):
        """Test that greedy matching backtracks correctly."""
        # Pattern: some letters, then @, then more letters
        pattern = "[str::]@[str::]"
        
        assert match(pattern, "hello@world")
        assert not match(pattern, "hello")  # No @
    
    def test_multiple_patterns(self):
        """Test multiple variable-length patterns."""
        pattern = "[str::][dec::][str::]"
        
        assert match(pattern, "abc123def")
        assert match(pattern, "a1b")
        assert not match(pattern, "abc")  # No number
