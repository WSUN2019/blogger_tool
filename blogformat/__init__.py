"""
blogformat — Blogger-compatible HTML formatter

Usage:
    python -m blogformat input.txt
    python -m blogformat input.txt -t ocean -o out.html
    python -m blogformat --list-themes
"""
from .themes import Theme, THEMES
from .parser import Post, Section, parse_input, parse_blocks, parse_list_item, parse_stats
from .renderer import render, inline_format

__all__ = [
    "Theme", "THEMES",
    "Post", "Section", "parse_input", "parse_blocks", "parse_list_item", "parse_stats",
    "render", "inline_format",
]
