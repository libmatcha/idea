"""
Matcher engine for SimpleMatch patterns.

Matches text against a parsed AST using backtracking for variable-length patterns.
"""

from dataclasses import dataclass
from typing import Optional, List
from matcha.parser import Parser, AST, LiteralNode, PatternNode


@dataclass
class MatchResult:
    """Result of a pattern match."""
    matched: bool
    value: str = ""
    start: int = 0
    end: int = 0
    
    def __bool__(self) -> bool:
        return self.matched


class Matcher:
    """
    Matches text against a SimpleMatch AST.
    
    Uses backtracking to handle variable-length patterns.
    """
    
    def __init__(self, ast: AST):
        self.ast = ast
    
    def match_full(self, text: str) -> MatchResult:
        """
        Match the entire text against the pattern.
        
        Returns:
            MatchResult with matched=True if entire text matches.
        """
        success, end_pos = self._match_at(text, 0, 0)
        
        if success and end_pos == len(text):
            return MatchResult(matched=True, value=text, start=0, end=len(text))
        
        return MatchResult(matched=False)
    
    def find_first(self, text: str) -> Optional[MatchResult]:
        """
        Find the first match in the text.
        
        Returns:
            MatchResult if found, None if no match.
        """
        for start in range(len(text)):
            success, end_pos = self._match_at(text, start, 0)
            
            if success:
                return MatchResult(
                    matched=True,
                    value=text[start:end_pos],
                    start=start,
                    end=end_pos
                )
        
        return None
    
    def find_all(self, text: str) -> List[MatchResult]:
        """
        Find all non-overlapping matches in the text.
        
        Returns:
            List of MatchResult for each match found.
        """
        results = []
        pos = 0
        
        while pos < len(text):
            success, end_pos = self._match_at(text, pos, 0)
            
            if success:
                results.append(MatchResult(
                    matched=True,
                    value=text[pos:end_pos],
                    start=pos,
                    end=end_pos
                ))
                pos = end_pos  # Move past this match
            else:
                pos += 1
        
        return results
    
    def _match_at(self, text: str, text_pos: int, ast_idx: int) -> tuple[bool, int]:
        """
        Try to match starting at text_pos with AST starting at ast_idx.
        
        Uses recursive backtracking for variable-length patterns.
        
        Returns:
            (success, end_position) tuple
        """
        # Base case: consumed all AST nodes
        if ast_idx >= len(self.ast):
            return True, text_pos
        
        node = self.ast[ast_idx]
        
        if isinstance(node, LiteralNode):
            # Must match exact character
            if text_pos >= len(text):
                return False, text_pos
            
            if text[text_pos] != node.value:
                return False, text_pos
            
            return self._match_at(text, text_pos + 1, ast_idx + 1)
        
        elif isinstance(node, PatternNode):
            # Try to match variable-length pattern with backtracking
            return self._match_pattern(text, text_pos, ast_idx, node)
        
        return False, text_pos
    
    def _match_pattern(
        self, text: str, text_pos: int, ast_idx: int, node: PatternNode
    ) -> tuple[bool, int]:
        """
        Match a pattern node with backtracking.
        
        Tries matching from max_len down to min_len to find a valid continuation.
        """
        # Handle literal string matching (e.g., `black`|`WHITE`)
        if node.literals:
            return self._match_literals(text, text_pos, ast_idx, node)
        
        # char_set=None means X type (matches any character)
        is_wildcard = node.char_set is None and not node.literals
        char_set = set(node.char_set) if node.char_set else None
        negated = node.negated
        
        # Count how many consecutive characters match the pattern
        match_len = 0
        pos = text_pos
        
        while pos < len(text):
            char = text[pos]
            # Determine if this character matches
            if is_wildcard:
                matches = True
            elif negated:
                # Negated: match if char is NOT in char_set
                matches = char not in char_set
            else:
                # Normal: match if char IS in char_set
                matches = char in char_set
            
            if matches:
                match_len += 1
                pos += 1
                
                # Stop if we've reached max length
                if node.max_len is not None and match_len >= node.max_len:
                    break
            else:
                break
        
        # Try lengths from max to min (greedy with backtracking)
        max_try = match_len
        min_try = node.min_len
        
        # Handle min_len=0 (optional patterns) - range needs to include 0
        for try_len in range(max_try, min_try - 1, -1):
            # Ensure we don't go below 0
            if try_len < 0:
                continue
            # Check if this length satisfies constraints
            if try_len < node.min_len:
                continue
            if node.max_len is not None and try_len > node.max_len:
                continue
            
            # Try to match rest of pattern with this length
            success, end_pos = self._match_at(text, text_pos + try_len, ast_idx + 1)
            if success:
                return True, end_pos
        
        # Special case: if min_len is 0 and we haven't tried 0 yet
        if node.min_len == 0 and match_len == 0:
            success, end_pos = self._match_at(text, text_pos, ast_idx + 1)
            if success:
                return True, end_pos
        
        return False, text_pos
    
    def _match_literals(
        self, text: str, text_pos: int, ast_idx: int, node: PatternNode
    ) -> tuple[bool, int]:
        """
        Match literal strings from a list of alternatives.
        
        Example: node.literals = ["black", "WHITE"] matches either "black" or "WHITE"
        """
        for literal in node.literals:
            if text[text_pos:].startswith(literal):
                # Found a matching literal, try to continue with rest of pattern
                success, end_pos = self._match_at(text, text_pos + len(literal), ast_idx + 1)
                if success:
                    return True, end_pos
        
        return False, text_pos


def match(pattern: str, text: str) -> bool:
    """
    Check if the entire text matches the pattern.
    
    Args:
        pattern: SimpleMatch pattern string
        text: Text to match against
    
    Returns:
        True if the entire text matches the pattern.
    
    Example:
        >>> match("[str:A-Z:]", "HELLO")
        True
        >>> match("[str:A-Z:]", "Hello")
        False
    """
    ast = Parser(pattern).parse()
    matcher = Matcher(ast)
    result = matcher.match_full(text)
    return result.matched


def find(pattern: str, text: str) -> Optional[str]:
    """
    Find the first match of the pattern in the text.
    
    Args:
        pattern: SimpleMatch pattern string
        text: Text to search in
    
    Returns:
        The matched substring, or None if no match.
    
    Example:
        >>> find("[dec::]", "abc123def")
        '123'
    """
    ast = Parser(pattern).parse()
    matcher = Matcher(ast)
    result = matcher.find_first(text)
    return result.value if result else None


def find_all(pattern: str, text: str) -> List[str]:
    """
    Find all non-overlapping matches of the pattern in the text.
    
    Args:
        pattern: SimpleMatch pattern string
        text: Text to search in
    
    Returns:
        List of matched substrings.
    
    Example:
        >>> find_all("[dec::]", "abc123def456")
        ['123', '456']
    """
    ast = Parser(pattern).parse()
    matcher = Matcher(ast)
    results = matcher.find_all(text)
    return [r.value for r in results]
