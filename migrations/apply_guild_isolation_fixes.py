#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to help identify and fix alliance queries missing guild_id filtering.

This script scans Python files and identifies SELECT queries on alliance_list
that don't include discord_server_id filtering.

Usage:
    python migrations/apply_guild_isolation_fixes.py --scan
    python migrations/apply_guild_isolation_fixes.py --check cogs/gift_operations.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Pattern to find SELECT queries on alliance_list
QUERY_PATTERN = re.compile(
    r'SELECT\s+.*?\s+FROM\s+alliance_list(?:\s+WHERE\s+([^"\']+?))?["\']',
    re.IGNORECASE | re.DOTALL
)

# Pattern to check if discord_server_id is in WHERE clause
GUILD_FILTER_PATTERN = re.compile(r'discord_server_id\s*=', re.IGNORECASE)


def scan_file(filepath: Path) -> List[Tuple[int, str, bool]]:
    """
    Scan a Python file for alliance_list queries.
    
    Returns:
        List of (line_number, query, has_guild_filter) tuples
    """
    results = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Find all queries
        for match in QUERY_PATTERN.finditer(content):
            query = match.group(0)
            where_clause = match.group(1) if match.group(1) else ""
            
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            
            # Check if it has guild filtering
            has_guild_filter = bool(GUILD_FILTER_PATTERN.search(where_clause))
            
            # Skip if it's just getting name by alliance_id (might be OK)
            # but mark it for review
            is_id_lookup = 'alliance_id' in where_clause and 'name' in query.upper()
            
            results.append((line_num, query.strip(), has_guild_filter, is_id_lookup))
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return results


def scan_directory(directory: Path = Path('cogs')) -> dict:
    """
    Scan all Python files in a directory.
    
    Returns:
        Dict mapping filepath to list of query results
    """
    all_results = {}
    
    for py_file in directory.glob('*.py'):
        if py_file.name.startswith('__'):
            continue
            
        results = scan_file(py_file)
        if results:
            all_results[py_file] = results
            
    return all_results


def print_report(all_results: dict):
    """Print a report of findings."""
    print("\n" + "="*80)
    print("GUILD ISOLATION SCAN REPORT")
    print("="*80)
    
    total_queries = 0
    missing_filter = 0
    needs_review = 0
    
    for filepath, results in sorted(all_results.items()):
        print(f"\n[FILE] {filepath}")
        print("-" * 80)
        
        for line_num, query, has_guild_filter, is_id_lookup in results:
            total_queries += 1
            
            if has_guild_filter:
                status = "[OK]"
            elif is_id_lookup:
                status = "[REVIEW]"
                needs_review += 1
            else:
                status = "[MISSING]"
                missing_filter += 1
                
            # Truncate long queries and remove special chars
            display_query = query[:100] + "..." if len(query) > 100 else query
            # Remove any non-ASCII characters that might cause encoding issues
            display_query = display_query.encode('ascii', 'replace').decode('ascii')
            
            print(f"  Line {line_num:4d} | {status:20s} | {display_query}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total queries found:        {total_queries}")
    print(f"[+] Already filtered:       {total_queries - missing_filter - needs_review}")
    print(f"[-] Missing guild filter:   {missing_filter}")
    print(f"[?] Needs manual review:    {needs_review}")
    print()
    
    if missing_filter > 0:
        print("[!] ACTION REQUIRED: Some queries are missing guild_id filtering.")
        print("    These queries may leak data across guilds!")
        print()
        
    if needs_review > 0:
        print("[i] Some queries look up alliance name by ID.")
        print("    These might be OK if the alliance_id is already validated,")
        print("    but should be reviewed to ensure the alliance belongs to current guild.")
        print()


def generate_fix_suggestions(filepath: Path, results: List[Tuple]):
    """Generate suggested fixes for a file."""
    print(f"\n[FIX] SUGGESTED FIXES FOR: {filepath}")
    print("="*80)
    
    for line_num, query, has_guild_filter, is_id_lookup in results:
        if has_guild_filter:
            continue  # Already OK
            
        print(f"\nLine {line_num}:")
        print(f"  Current: {query}")
        
        if is_id_lookup:
            # Suggest adding AND discord_server_id = ?
            print("  Suggested: Add 'AND discord_server_id = ?' to WHERE clause")
            print("  Make sure to pass guild_id as parameter!")
        else:
            # Suggest adding WHERE discord_server_id = ?
            if 'WHERE' in query.upper():
                print("  Suggested: Add 'AND discord_server_id = ?' to WHERE clause")
            else:
                print("  Suggested: Add 'WHERE discord_server_id = ?' before closing quote")
            print("  Make sure to pass guild_id as parameter!")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrations/apply_guild_isolation_fixes.py --scan")
        print("  python migrations/apply_guild_isolation_fixes.py --check <filepath>")
        print("  python migrations/apply_guild_isolation_fixes.py --fix <filepath>")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == '--scan':
        print("Scanning all cogs for alliance_list queries...")
        results = scan_directory(Path('cogs'))
        print_report(results)
        
    elif command == '--check' and len(sys.argv) > 2:
        filepath = Path(sys.argv[2])
        print(f"Checking {filepath}...")
        results = scan_file(filepath)
        if results:
            print_report({filepath: results})
        else:
            print(f"No alliance_list queries found in {filepath}")
            
    elif command == '--fix' and len(sys.argv) > 2:
        filepath = Path(sys.argv[2])
        results = scan_file(filepath)
        if results:
            generate_fix_suggestions(filepath, results)
        else:
            print(f"No alliance_list queries found in {filepath}")
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()

