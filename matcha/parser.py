"""
Parser for SimpleMatch patterns.

Converts a token stream into an Abstract Syntax Tree (AST).
"""

from dataclasses import dataclass, field
from typing import List, Union, Optional
from matcha.lexer import Lexer
from matcha.tokens import Token, TokenType


@dataclass
class LiteralNode:
    """AST node for a literal character to match exactly."""
    value: str
    
    def __repr__(self) -> str:
        return f"Literal({self.value!r})"


@dataclass
class PatternNode:
    """AST node for a pattern token [type:range:length]."""
    char_set: Optional[str]
    min_len: int
    max_len: int | None  # None means unbounded
    negated: bool = False  # If True, match characters NOT in char_set
    literals: Optional[list[str]] = None  # Literal strings to match
    
    def __repr__(self) -> str:
        max_str = str(self.max_len) if self.max_len else "∞"
        neg = "!" if self.negated else ""
        if self.literals:
            return f"Pattern(literals={self.literals}, len={self.min_len}-{max_str})"
        return f"Pattern(chars={neg}{self.char_set!r}, len={self.min_len}-{max_str})"


# AST is a list of nodes
ASTNode = Union[LiteralNode, PatternNode]
AST = List[ASTNode]


class ParseError(Exception):
    """Raised when the parser encounters invalid syntax."""
    pass


class Parser:
    """
    Parses a SimpleMatch pattern into an AST.
    
    Example:
        parser = Parser("[anum::]@[str::>=2]")
        ast = parser.parse()
    """
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.lexer = Lexer(pattern)
    
    def parse(self) -> AST:
        """
        Parse the pattern into an AST.
        
        Returns:
            List of AST nodes representing the pattern.
        
        Raises:
            ParseError: If the pattern is invalid.
        """
        ast: AST = []
        
        for token in self.lexer.tokenize():
            node = self._token_to_node(token)
            ast.append(node)
        
        return ast
    
    def _token_to_node(self, token: Token) -> ASTNode:
        """Convert a token to an AST node."""
        if token.token_type == TokenType.LITERAL:
            return LiteralNode(value=token.value)
        
        # PATTERN token
        length = token.length
        return PatternNode(
            char_set=token.char_set,
            min_len=length.get_min(),
            max_len=length.get_max(),
            negated=token.negated,
            literals=token.literals
        )

