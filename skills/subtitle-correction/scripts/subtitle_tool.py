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
from difflib import SequenceMatcher


# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    STRIKETHROUGH = '\033[9m'
    RESET = '\033[0m'

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output."""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.CYAN = cls.BOLD = cls.DIM = cls.STRIKETHROUGH = cls.RESET = ''


def word_level_diff(original: str, corrected: str, use_color: bool = True) -> str:
    """
    Generate a word-level diff between original and corrected text.

    Returns a string with inline markers showing what changed:
    - Deletions shown in red with strikethrough: [-deleted-]
    - Additions shown in green: {+added+}

    Example:
        original:  "这款工具用了Lantern框架"
        corrected: "这款工具用了LangChain框架"
        output:    "这款工具用了[-Lantern-]{+LangChain+}框架"
    """
    if not use_color:
        Colors.disable()

    # Tokenize: split into words/characters while preserving structure
    # For mixed Chinese/English, we tokenize character-by-character for Chinese
    # and word-by-word for English
    def tokenize(text: str) -> List[str]:
        tokens = []
        current_word = ""
        for char in text:
            if char.isascii() and char.isalnum():
                current_word += char
            else:
                if current_word:
                    tokens.append(current_word)
                    current_word = ""
                if char.strip():  # Non-whitespace
                    tokens.append(char)
                elif char == ' ':
                    tokens.append(char)
        if current_word:
            tokens.append(current_word)
        return tokens

    orig_tokens = tokenize(original)
    corr_tokens = tokenize(corrected)

    matcher = SequenceMatcher(None, orig_tokens, corr_tokens)
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(''.join(orig_tokens[i1:i2]))
        elif tag == 'delete':
            deleted = ''.join(orig_tokens[i1:i2])
            result.append(f"{Colors.RED}{Colors.STRIKETHROUGH}[-{deleted}-]{Colors.RESET}")
        elif tag == 'insert':
            inserted = ''.join(corr_tokens[j1:j2])
            result.append(f"{Colors.GREEN}{{+{inserted}+}}{Colors.RESET}")
        elif tag == 'replace':
            deleted = ''.join(orig_tokens[i1:i2])
            inserted = ''.join(corr_tokens[j1:j2])
            result.append(f"{Colors.RED}{Colors.STRIKETHROUGH}[-{deleted}-]{Colors.RESET}")
            result.append(f"{Colors.GREEN}{{+{inserted}+}}{Colors.RESET}")

    return ''.join(result)


def word_level_diff_html(original: str, corrected: str) -> str:
    """
    Generate word-level diff as HTML with inline styling.
    Returns HTML string with <del> and <ins> tags for changes.
    """
    def tokenize(text: str) -> List[str]:
        tokens = []
        current_word = ""
        for char in text:
            if char.isascii() and char.isalnum():
                current_word += char
            else:
                if current_word:
                    tokens.append(current_word)
                    current_word = ""
                if char.strip():
                    tokens.append(char)
                elif char == ' ':
                    tokens.append(char)
        if current_word:
            tokens.append(current_word)
        return tokens

    import html
    orig_tokens = tokenize(original)
    corr_tokens = tokenize(corrected)

    matcher = SequenceMatcher(None, orig_tokens, corr_tokens)
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(html.escape(''.join(orig_tokens[i1:i2])))
        elif tag == 'delete':
            deleted = html.escape(''.join(orig_tokens[i1:i2]))
            result.append(f'<del>{deleted}</del>')
        elif tag == 'insert':
            inserted = html.escape(''.join(corr_tokens[j1:j2]))
            result.append(f'<ins>{inserted}</ins>')
        elif tag == 'replace':
            deleted = html.escape(''.join(orig_tokens[i1:i2]))
            inserted = html.escape(''.join(corr_tokens[j1:j2]))
            result.append(f'<del>{deleted}</del>')
            result.append(f'<ins>{inserted}</ins>')

    return ''.join(result)


def generate_html_diff(original_path: str, corrected_path: str, output_path: str) -> Tuple[int, int]:
    """
    Generate an HTML diff report showing all entries with changes highlighted.

    Returns:
        Tuple of (total_entries, changed_entries)
    """
    import html

    original = parse_srt(original_path)
    corrected = parse_srt(corrected_path)

    # Build lookup for corrected entries
    corr_map = {e.index: e for e in corrected}

    changed_count = 0
    rows = []

    for orig in original:
        corr = corr_map.get(orig.index)
        if corr and orig.text != corr.text:
            changed_count += 1
            is_changed = True
            diff_html = word_level_diff_html(orig.text, corr.text)
        else:
            is_changed = False
            diff_html = html.escape(orig.text) if orig else ""

        rows.append({
            'index': orig.index,
            'timestamp': f"{orig.start_time} --> {orig.end_time}",
            'original': html.escape(orig.text),
            'corrected': html.escape(corr.text) if corr else "",
            'diff': diff_html,
            'changed': is_changed
        })

    # Calculate percentage
    change_percent = round((changed_count / len(original)) * 100, 1) if original else 0

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subtitle Diff Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0F172A;
            --bg-secondary: #1E293B;
            --bg-tertiary: #334155;
            --text-primary: #F1F5F9;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --accent-blue: #3B82F6;
            --accent-cyan: #22D3EE;
            --accent-purple: #A855F7;
            --delete-bg: rgba(239, 68, 68, 0.2);
            --delete-text: #FCA5A5;
            --delete-border: #EF4444;
            --insert-bg: rgba(34, 197, 94, 0.2);
            --insert-text: #86EFAC;
            --insert-border: #22C55E;
            --border-color: #334155;
            --glow-blue: 0 0 20px rgba(59, 130, 246, 0.3);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 24px;
        }}

        /* Header */
        .header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
        }}

        .logo {{
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--glow-blue);
        }}

        .logo svg {{
            width: 28px;
            height: 28px;
            color: white;
        }}

        .header-text h1 {{
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--text-primary), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header-text p {{
            font-size: 14px;
            color: var(--text-secondary);
        }}

        /* File paths */
        .file-paths {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .file-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .file-icon {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        .file-icon.original {{
            background: rgba(239, 68, 68, 0.1);
            color: var(--delete-text);
        }}

        .file-icon.corrected {{
            background: rgba(34, 197, 94, 0.1);
            color: var(--insert-text);
        }}

        .file-icon svg {{
            width: 20px;
            height: 20px;
        }}

        .file-info {{
            overflow: hidden;
        }}

        .file-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}

        .file-path {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
        }}

        .stat-card.total::before {{
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
        }}

        .stat-card.changed::before {{
            background: linear-gradient(90deg, #F59E0B, #EF4444);
        }}

        .stat-card.unchanged::before {{
            background: linear-gradient(90deg, var(--insert-border), var(--accent-cyan));
        }}

        .stat-icon {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 12px;
        }}

        .stat-card.total .stat-icon {{
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent-blue);
        }}

        .stat-card.changed .stat-icon {{
            background: rgba(245, 158, 11, 0.1);
            color: #FBBF24;
        }}

        .stat-card.unchanged .stat-icon {{
            background: rgba(34, 197, 94, 0.1);
            color: var(--insert-border);
        }}

        .stat-icon svg {{
            width: 22px;
            height: 22px;
        }}

        .stat-number {{
            font-size: 32px;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1;
            margin-bottom: 4px;
        }}

        .stat-label {{
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .stat-badge {{
            position: absolute;
            top: 16px;
            right: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
        }}

        /* Legend & Jump Links */
        .actions-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: flex-start;
            margin-bottom: 24px;
            padding: 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }}

        .legend {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-shrink: 0;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .legend del {{
            background: var(--delete-bg);
            color: var(--delete-text);
            text-decoration: line-through;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
        }}

        .legend ins {{
            background: var(--insert-bg);
            color: var(--insert-text);
            text-decoration: none;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(34, 197, 94, 0.3);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
        }}

        .jump-links {{
            flex: 1;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
        }}

        .jump-label {{
            font-size: 13px;
            color: var(--text-muted);
            margin-right: 4px;
        }}

        .jump-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 36px;
            height: 28px;
            padding: 0 10px;
            background: var(--bg-tertiary);
            color: var(--accent-cyan);
            text-decoration: none;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.15s;
            border: 1px solid transparent;
        }}

        .jump-link:hover {{
            background: rgba(34, 211, 238, 0.1);
            border-color: var(--accent-cyan);
            transform: translateY(-1px);
        }}

        .no-changes {{
            color: var(--text-muted);
            font-style: italic;
        }}

        /* Table */
        .table-wrapper {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        thead {{
            background: var(--bg-tertiary);
        }}

        th {{
            padding: 14px 16px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }}

        td {{
            padding: 16px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
            font-size: 14px;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr {{
            transition: background 0.15s;
        }}

        tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}

        tr.changed {{
            background: rgba(245, 158, 11, 0.03);
        }}

        tr.changed:hover {{
            background: rgba(245, 158, 11, 0.06);
        }}

        /* Entry Index */
        .entry-index {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            white-space: nowrap;
        }}

        .change-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .change-dot.changed {{
            background: #FBBF24;
            box-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
        }}

        .change-dot.unchanged {{
            background: var(--bg-tertiary);
        }}

        .entry-num {{
            color: var(--accent-blue);
        }}

        /* Timestamp */
        .timestamp {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--text-muted);
            white-space: nowrap;
            padding: 4px 8px;
            background: var(--bg-primary);
            border-radius: 4px;
        }}

        /* Text cells */
        .text-cell {{
            min-width: 180px;
            word-break: break-word;
            color: var(--text-secondary);
            line-height: 1.7;
        }}

        .diff-cell {{
            min-width: 220px;
            line-height: 1.7;
        }}

        .unchanged-text {{
            color: var(--text-muted);
        }}

        /* Diff styling */
        del {{
            background: var(--delete-bg);
            color: var(--delete-text);
            text-decoration: line-through;
            padding: 1px 4px;
            border-radius: 3px;
            font-family: inherit;
        }}

        ins {{
            background: var(--insert-bg);
            color: var(--insert-text);
            text-decoration: none;
            padding: 1px 4px;
            border-radius: 3px;
            font-family: inherit;
        }}

        /* Scroll to top */
        .scroll-top {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 44px;
            height: 44px;
            background: var(--accent-blue);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            transition: all 0.2s;
            opacity: 0;
            visibility: hidden;
        }}

        .scroll-top.visible {{
            opacity: 1;
            visibility: visible;
        }}

        .scroll-top:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        }}

        .scroll-top svg {{
            width: 20px;
            height: 20px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 16px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .file-paths {{
                grid-template-columns: 1fr;
            }}

            .actions-bar {{
                flex-direction: column;
            }}

            .table-wrapper {{
                overflow-x: auto;
            }}

            table {{
                min-width: 800px;
            }}
        }}

        /* Smooth scroll */
        html {{
            scroll-behavior: smooth;
        }}

        /* Target highlight animation */
        tr:target {{
            animation: highlight 2s ease-out;
        }}

        @keyframes highlight {{
            0% {{ background: rgba(59, 130, 246, 0.3); }}
            100% {{ background: transparent; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                </svg>
            </div>
            <div class="header-text">
                <h1>Subtitle Diff Report</h1>
                <p>Speech recognition correction comparison</p>
            </div>
        </div>

        <!-- File Paths -->
        <div class="file-paths">
            <div class="file-card">
                <div class="file-icon original">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                </div>
                <div class="file-info">
                    <div class="file-label">Original</div>
                    <div class="file-path">{html.escape(original_path)}</div>
                </div>
            </div>
            <div class="file-card">
                <div class="file-icon corrected">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <polyline points="9 15 11 17 15 13"/>
                    </svg>
                </div>
                <div class="file-info">
                    <div class="file-label">Corrected</div>
                    <div class="file-path">{html.escape(corrected_path)}</div>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7"/>
                        <rect x="14" y="3" width="7" height="7"/>
                        <rect x="14" y="14" width="7" height="7"/>
                        <rect x="3" y="14" width="7" height="7"/>
                    </svg>
                </div>
                <div class="stat-number">{len(original)}</div>
                <div class="stat-label">Total Entries</div>
            </div>
            <div class="stat-card changed">
                <div class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                </div>
                <div class="stat-number">{changed_count}</div>
                <div class="stat-label">Changed</div>
                <div class="stat-badge">{change_percent}%</div>
            </div>
            <div class="stat-card unchanged">
                <div class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                        <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                </div>
                <div class="stat-number">{len(original) - changed_count}</div>
                <div class="stat-label">Unchanged</div>
                <div class="stat-badge">{round(100 - change_percent, 1)}%</div>
            </div>
        </div>

        <!-- Actions Bar -->
        <div class="actions-bar">
            <div class="legend">
                <div class="legend-item">
                    <del>removed</del>
                    <span>Deleted</span>
                </div>
                <div class="legend-item">
                    <ins>added</ins>
                    <span>Inserted</span>
                </div>
            </div>
            <div class="jump-links">
                <span class="jump-label">Jump to:</span>
                {''.join(f'<a href="#entry-{r["index"]}" class="jump-link">{r["index"]}</a>' for r in rows if r['changed']) or '<span class="no-changes">No changes detected</span>'}
            </div>
        </div>

        <!-- Table -->
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 100px;">#</th>
                        <th style="width: 200px;">Timestamp</th>
                        <th>Original</th>
                        <th>Corrected</th>
                        <th>Diff View</th>
                    </tr>
                </thead>
                <tbody>
'''

    for row in rows:
        changed_class = 'changed' if row['changed'] else ''
        dot_class = 'changed' if row['changed'] else 'unchanged'
        diff_display = row['diff'] if row['changed'] else f'<span class="unchanged-text">{row["original"]}</span>'

        html_content += f'''                <tr id="entry-{row['index']}" class="{changed_class}">
                    <td>
                        <div class="entry-index">
                            <span class="change-dot {dot_class}"></span>
                            <span class="entry-num">{row['index']}</span>
                        </div>
                    </td>
                    <td><span class="timestamp">{row['timestamp']}</span></td>
                    <td class="text-cell">{row['original']}</td>
                    <td class="text-cell">{row['corrected']}</td>
                    <td class="diff-cell">{diff_display}</td>
                </tr>
'''

    html_content += '''                </tbody>
            </table>
        </div>
    </div>

    <!-- Scroll to top button -->
    <button class="scroll-top" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"/>
        </svg>
    </button>

    <script>
        // Show/hide scroll to top button
        window.addEventListener('scroll', () => {
            const btn = document.querySelector('.scroll-top');
            if (window.scrollY > 300) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        });
    </script>
</body>
</html>
'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return len(original), changed_count


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
    diff_parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    diff_parser.add_argument('--simple', action='store_true', help='Use simple line-based diff instead of word-level')
    diff_parser.add_argument('--html', metavar='OUTPUT', help='Generate HTML diff report to specified file')
    diff_parser.add_argument('--all', action='store_true', help='Show all entries (not just changed ones) in terminal output')

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
        # HTML output mode
        if args.html:
            total, changed = generate_html_diff(args.original, args.corrected, args.html)
            print(f"✅ HTML diff report generated: {args.html}")
            print(f"   Total entries: {total}")
            print(f"   Changed: {changed}")
            print(f"   Unchanged: {total - changed}")
            print(f"\n   Open in browser to view the full comparison.")
            sys.exit(0)

        # Terminal output mode
        use_color = not args.no_color and sys.stdout.isatty()

        if args.all:
            # Show all entries (changed and unchanged)
            original = parse_srt(args.original)
            corrected = parse_srt(args.corrected)
            corr_map = {e.index: e for e in corrected}

            changed_count = sum(1 for o in original if corr_map.get(o.index) and o.text != corr_map[o.index].text)

            if use_color:
                print(f"{Colors.BOLD}Subtitle Diff Report (Full){Colors.RESET}")
                print(f"{Colors.DIM}Original:  {args.original}{Colors.RESET}")
                print(f"{Colors.DIM}Corrected: {args.corrected}{Colors.RESET}")
                print()
                print(f"Total entries: {len(original)}, Changed: {Colors.CYAN}{changed_count}{Colors.RESET}\n")
                print(f"{Colors.DIM}Legend: {Colors.RED}[-deleted-]{Colors.RESET} {Colors.GREEN}{{+added+}}{Colors.RESET}\n")
            else:
                print(f"Subtitle Diff Report (Full)")
                print(f"Original:  {args.original}")
                print(f"Corrected: {args.corrected}")
                print()
                print(f"Total entries: {len(original)}, Changed: {changed_count}\n")
                print("Legend: [-deleted-] {+added+}\n")

            for orig in original[:args.limit]:
                corr = corr_map.get(orig.index)
                is_changed = corr and orig.text != corr.text

                if use_color:
                    marker = f"{Colors.YELLOW}*{Colors.RESET}" if is_changed else " "
                    print(f"{marker} {Colors.BLUE}[{orig.index}]{Colors.RESET} {Colors.DIM}{orig.start_time} --> {orig.end_time}{Colors.RESET}")
                else:
                    marker = "*" if is_changed else " "
                    print(f"{marker} [{orig.index}] {orig.start_time} --> {orig.end_time}")

                if is_changed:
                    inline_diff = word_level_diff(orig.text, corr.text, use_color)
                    print(f"    {inline_diff}")
                else:
                    if use_color:
                        print(f"    {Colors.DIM}{orig.text}{Colors.RESET}")
                    else:
                        print(f"    {orig.text}")
                print()

            if len(original) > args.limit:
                print(f"... and {len(original) - args.limit} more entries")

        else:
            # Show only changed entries (default)
            diffs = show_diff(args.original, args.corrected)

            if use_color:
                print(f"{Colors.BOLD}Subtitle Diff Report{Colors.RESET}")
                print(f"{Colors.DIM}Original:  {args.original}{Colors.RESET}")
                print(f"{Colors.DIM}Corrected: {args.corrected}{Colors.RESET}")
                print()
                print(f"Found {Colors.CYAN}{len(diffs)}{Colors.RESET} text changes:\n")
                print(f"{Colors.DIM}Legend: {Colors.RED}[-deleted-]{Colors.RESET} {Colors.GREEN}{{+added+}}{Colors.RESET}\n")
            else:
                print(f"Subtitle Diff Report")
                print(f"Original:  {args.original}")
                print(f"Corrected: {args.corrected}")
                print()
                print(f"Found {len(diffs)} text changes:\n")
                print("Legend: [-deleted-] {+added+}\n")

            for diff in diffs[:args.limit]:
                if use_color:
                    print(f"{Colors.BLUE}[{diff['index']}]{Colors.RESET} {Colors.DIM}{diff['timestamp']}{Colors.RESET}")
                else:
                    print(f"[{diff['index']}] {diff['timestamp']}")

                if args.simple:
                    if use_color:
                        print(f"  {Colors.RED}- {diff['original']}{Colors.RESET}")
                        print(f"  {Colors.GREEN}+ {diff['corrected']}{Colors.RESET}")
                    else:
                        print(f"  - {diff['original']}")
                        print(f"  + {diff['corrected']}")
                else:
                    inline_diff = word_level_diff(diff['original'], diff['corrected'], use_color)
                    print(f"  {inline_diff}")
                print()

            if len(diffs) > args.limit:
                print(f"... and {len(diffs) - args.limit} more changes")

            # Hint about HTML output
            if use_color:
                print(f"\n{Colors.DIM}Tip: Use --html report.html to generate a full HTML comparison report{Colors.RESET}")

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
