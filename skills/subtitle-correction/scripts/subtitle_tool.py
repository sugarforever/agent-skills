#!/usr/bin/env python3
"""
Subtitle Validation and Correction Tool

This script validates corrected subtitle files against originals and can also
assist with the correction process by identifying common speech recognition errors.

Usage:
    # Validate corrected file against original
    python subtitle_tool.py validate original.srt corrected.srt

    # Show diff between files (text changes only)
    python subtitle_tool.py diff original.srt corrected.srt

    # Analyze a file for potential errors
    python subtitle_tool.py analyze input.srt --terms "LangChain,OpenAI,Agent"
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict


@dataclass
class SubtitleEntry:
    """Represents a single subtitle entry."""
    index: int
    start_time: str
    end_time: str
    text: str
    raw_timestamp_line: str  # Preserve exact formatting


def parse_srt(filepath: str) -> List[SubtitleEntry]:
    """Parse an SRT file into a list of SubtitleEntry objects."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []
    # Split by double newlines (or more), handling various line ending styles
    blocks = re.split(r'\n\n+', content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue

        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        # Parse timestamp line
        timestamp_line = lines[1].strip()
        timestamp_match = re.match(
            r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',
            timestamp_line
        )

        if not timestamp_match:
            continue

        start_time = timestamp_match.group(1)
        end_time = timestamp_match.group(2)
        text = '\n'.join(lines[2:]) if len(lines) > 2 else ''

        entries.append(SubtitleEntry(
            index=index,
            start_time=start_time,
            end_time=end_time,
            text=text,
            raw_timestamp_line=timestamp_line
        ))

    return entries


def validate_correction(original_path: str, corrected_path: str) -> Tuple[bool, List[str]]:
    """
    Validate that a corrected subtitle file maintains structural integrity.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    original = parse_srt(original_path)
    corrected = parse_srt(corrected_path)

    # Check 1: Same number of entries
    if len(original) != len(corrected):
        issues.append(f"Entry count mismatch: original={len(original)}, corrected={len(corrected)}")
        return False, issues

    # Check 2: Validate each entry
    for i, (orig, corr) in enumerate(zip(original, corrected)):
        # Check index
        if orig.index != corr.index:
            issues.append(f"Entry {i+1}: Index mismatch (orig={orig.index}, corr={corr.index})")

        # Check timestamps (must be EXACTLY the same)
        if orig.start_time != corr.start_time:
            issues.append(f"Entry {orig.index}: Start time changed from '{orig.start_time}' to '{corr.start_time}'")

        if orig.end_time != corr.end_time:
            issues.append(f"Entry {orig.index}: End time changed from '{orig.end_time}' to '{corr.end_time}'")

        # Check raw timestamp line preservation
        if orig.raw_timestamp_line != corr.raw_timestamp_line:
            issues.append(f"Entry {orig.index}: Timestamp line formatting changed")

    is_valid = len(issues) == 0
    return is_valid, issues


def show_diff(original_path: str, corrected_path: str) -> List[Dict]:
    """
    Show text differences between original and corrected files.
    Only shows entries where text has changed.
    """
    original = parse_srt(original_path)
    corrected = parse_srt(corrected_path)

    diffs = []

    for orig, corr in zip(original, corrected):
        if orig.text != corr.text:
            diffs.append({
                'index': orig.index,
                'timestamp': f"{orig.start_time} --> {orig.end_time}",
                'original': orig.text,
                'corrected': corr.text
            })

    return diffs


# Common speech recognition error patterns
ERROR_PATTERNS = {
    # Chinese phonetic errors
    '绘画': ('会话', 'session/conversation context'),
    '源数据': ('元数据', 'metadata'),
    '本科': ('本课', 'this lesson'),
    '事例': ('示例', 'example'),
    '中间键': ('中间件', 'middleware'),
    '详细': ('消息', 'message (context-dependent)'),

    # LangChain ecosystem
    r'[Ll]uncheon': ('langchain', 'LangChain package'),
    r'蓝[犬卷]': ('LangChain', 'LangChain framework'),
    r'[Ll]antern': ('LangChain', 'LangChain framework'),
    r'land\s*GRAPH': ('langgraph', 'LangGraph package'),
    r'LAN\s*GRAPH': ('langgraph', 'LangGraph package'),

    # OpenAI
    r'open\s*EI': ('OpenAI', 'OpenAI'),
    r'open\s*Email': ('OpenAI', 'OpenAI'),

    # Memory components
    r'[Aa]\s*memory\s*[Ss]erver': ('MemorySaver', 'Memory component'),
    r'amneserver': ('MemorySaver', 'Memory component'),
    r'check\s*point(?!er)': ('checkpointer', 'Checkpointer component'),
    r'Sharepoint': ('checkpointer', 'Checkpointer component'),

    # Code terms
    r'wrong\s*time': ('runtime', 'runtime'),
    r'confict': ('config', 'configuration'),
}


def analyze_file(filepath: str, custom_terms: Optional[List[str]] = None) -> List[Dict]:
    """
    Analyze a subtitle file for potential speech recognition errors.

    Args:
        filepath: Path to the SRT file
        custom_terms: Optional list of expected terms to help identify errors

    Returns:
        List of potential issues found
    """
    entries = parse_srt(filepath)
    potential_issues = []

    for entry in entries:
        text = entry.text
        entry_issues = []

        # Check against known error patterns
        for pattern, (correction, description) in ERROR_PATTERNS.items():
            if re.search(pattern, text):
                entry_issues.append({
                    'pattern': pattern,
                    'suggestion': correction,
                    'description': description
                })

        # Check for "underscore" that should be "_"
        if 'underscore' in text.lower():
            entry_issues.append({
                'pattern': 'underscore',
                'suggestion': '_',
                'description': 'Likely a variable name with underscore'
            })

        if entry_issues:
            potential_issues.append({
                'index': entry.index,
                'timestamp': f"{entry.start_time} --> {entry.end_time}",
                'text': text,
                'issues': entry_issues
            })

    return potential_issues


def main():
    parser = argparse.ArgumentParser(description='Subtitle validation and analysis tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate corrected file against original')
    validate_parser.add_argument('original', help='Original SRT file')
    validate_parser.add_argument('corrected', help='Corrected SRT file')

    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show text differences between files')
    diff_parser.add_argument('original', help='Original SRT file')
    diff_parser.add_argument('corrected', help='Corrected SRT file')
    diff_parser.add_argument('--limit', type=int, default=50, help='Max differences to show')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze file for potential errors')
    analyze_parser.add_argument('input', help='Input SRT file')
    analyze_parser.add_argument('--terms', help='Comma-separated list of expected terms')

    args = parser.parse_args()

    if args.command == 'validate':
        print(f"Validating: {args.corrected}")
        print(f"Against:    {args.original}\n")

        is_valid, issues = validate_correction(args.original, args.corrected)

        if is_valid:
            print("✅ Validation PASSED")
            print("   - Entry counts match")
            print("   - All timestamps preserved")
            print("   - All indices preserved")
        else:
            print("❌ Validation FAILED")
            print(f"   Found {len(issues)} issue(s):\n")
            for issue in issues[:20]:  # Limit output
                print(f"   - {issue}")
            if len(issues) > 20:
                print(f"   ... and {len(issues) - 20} more issues")

        sys.exit(0 if is_valid else 1)

    elif args.command == 'diff':
        diffs = show_diff(args.original, args.corrected)

        print(f"Found {len(diffs)} text changes:\n")

        for diff in diffs[:args.limit]:
            print(f"[{diff['index']}] {diff['timestamp']}")
            print(f"  - {diff['original']}")
            print(f"  + {diff['corrected']}")
            print()

        if len(diffs) > args.limit:
            print(f"... and {len(diffs) - args.limit} more changes")

    elif args.command == 'analyze':
        custom_terms = args.terms.split(',') if args.terms else None
        issues = analyze_file(args.input, custom_terms)

        print(f"Found {len(issues)} entries with potential issues:\n")

        for item in issues[:30]:
            print(f"[{item['index']}] {item['timestamp']}")
            print(f"  Text: {item['text'][:60]}...")
            for issue in item['issues']:
                print(f"    → '{issue['pattern']}' might be '{issue['suggestion']}' ({issue['description']})")
            print()

        if len(issues) > 30:
            print(f"... and {len(issues) - 30} more entries with potential issues")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
