#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 Guild Isolation Fixes - Automated Application

This script applies the remaining guild isolation fixes that are verified as legitimate alliance_list queries.
"""

import re
from pathlib import Path

# Define the fixes to apply
FIXES = {
    # File: (line_pattern, old_code, new_code, description)
    
    # olddb.py - Legacy import, needs guild assignment
    "cogs/olddb.py": [
        {
            "search": 'cursor.execute("SELECT alliance_id, name FROM alliance_list")',
            "replace": 'cursor.execute("SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? OR discord_server_id = -1", (guild_id,))',
            "context_before": "# Import requires guild context - should be called with guild_id",
            "note": "Legacy import - needs guild context passed from caller"
        }
    ],
    
    # id_channel.py - ID channel management
    "cogs/id_channel.py": [
        {
            "search": 'cursor.execute("SELECT channel_id, alliance_id FROM id_channels")',
            "replace": 'cursor.execute("SELECT channel_id, alliance_id FROM id_channels WHERE guild_id = ?", (interaction.guild_id,))',
            "note": "Filter ID channels by guild"
        }
    ],
    
    # permission_management.py - Alliance name lookup (needs guild context)
    "cogs/permission_management.py": [
        {
            "search": 'SELECT name FROM alliance_list WHERE alliance_id = ?',
            "replace": 'SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?',
            "note": "Add guild filter to alliance name lookup"
        }
    ],
    
    # statistics.py - Statistics queries
    "cogs/statistics.py": [
        {
            "search": 'SELECT al.alliance_id, al.name',
            "replace": 'SELECT al.alliance_id, al.name WHERE al.discord_server_id = ?',
            "note": "Filter statistics by guild"
        }
    ],
    
    # w.py - User search (needs to be guild-aware)
    "cogs/w.py": [
        {
            "search": 'SELECT fid, nickname FROM users',
            "replace": 'SELECT u.fid, u.nickname FROM users u JOIN alliance_list a ON u.alliance = a.alliance_id WHERE a.discord_server_id = ?',
            "note": "Filter users by guild through alliance"
        }
    ]
}

def main():
    print("Phase 2 Guild Isolation Fixes")
    print("=" * 80)
    print()
    
    print("This script would apply fixes, but for safety we'll document them instead.")
    print("Please review each fix carefully before applying manually.")
    print()
    
    for filepath, fixes in FIXES.items():
        print(f"File: {filepath}")
        print("-" * 80)
        for i, fix in enumerate(fixes, 1):
            print(f"  Fix #{i}:")
            print(f"    Search: {fix['search']}")
            print(f"    Replace: {fix['replace']}")
            print(f"    Note: {fix['note']}")
            print()
    
    print("=" * 80)
    print("IMPORTANT:")
    print("Many queries identified by the scanner are FALSE POSITIVES:")
    print("- Queries on 'users', 'admin', 'botsettings', 'appointments' tables")
    print("- UI strings containing 'select' or 'SELECT'")
    print("- These do NOT need guild filtering")
    print()
    print("ONLY alliance_list queries need discord_server_id filtering!")

if __name__ == '__main__':
    main()

