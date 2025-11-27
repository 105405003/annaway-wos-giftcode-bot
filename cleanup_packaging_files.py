#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup script to remove/organize packaging and deployment files.

This script helps clean up the Annaway fork by removing unnecessary
packaging scripts and deployment files from the original project.

Run with --dry-run to see what would be deleted without actually deleting.
"""

import os
import shutil
from pathlib import Path
from typing import List

# Files and directories to remove
FILES_TO_REMOVE = [
    # Packaging scripts from original project
    'pack_A1_deployment.py',
    'pack_final_fix.py',
    'pack_for_deploy.ps1',
    'pack_for_ssh.py',
    'pack_hotfix.py',
    'pack_hotfix2.py',
    'pack_updates.py',
    'quick_pack.py',
    
    # Diagnostic/fix scripts
    'add_interaction_logging.py',
    'fix_indentation.py',
    'fix_member_operations_handler.py',
    'check_managers.py',
    '完整診斷腳本.sh',
    'deploy_check.sh',
    'quick_deploy.sh',
    
    # Test packages
    'test_discord_members.zip',
    'diagnostic_package_manager.zip',
    
    # Hotfix packages (keep latest, remove old ones if you want)
    # Uncomment to remove:
    # 'hotfix_gift_ops_20251010_172235.zip',
    # 'hotfix2_manager_fix_20251010_175436.zip',
    # 'hotfix3_manager_access_20251010_180815.zip',
    # 'hotfix4_all_cogs_manager_20251010_182323.zip',
    # 'hotfix4_all_cogs_manager_20251010_182404.zip',
    # 'hotfix5_members_intent_20251010_185057.zip',
    # 'hotfix6_indent_fix_20251010_185639.zip',
    # 'hotfix7_final_fix_20251010_190454.zip',
    # 'hotfix8_token_fix_20251010_190900.zip',
    
    # Update packages (old deployment zips)
    # Uncomment to remove:
    # 'A1_deployment_package_20251010_170618.zip',
    # 'final_fix_20251009_161553.zip',
    # 'final_fix_20251009_161611.zip',
    # 'update_files_20251009_155027.zip',
    # 'update_files_20251009_155109.zip',
    # 'update_files_20251009_155559.zip',
    # 'WOS_Bot_Deploy.zip',
    
    # Generated batch zips (keep latest if needed for server)
    # Uncomment to remove old ones:
    # 'wos_bot_batch_add_20251121_151338.zip',
    # 'wos_bot_batch_add_20251121_153212.zip',
    # 'wos_bot_batch_add_20251121_155516.zip',
    # 'wos_bot_batch_add_20251121_165635.zip',
    # 'wos_bot_batch_add_20251121_170124.zip',
    # 'wos_bot_batch_add_20251127_220134.zip',  # Latest
]

DIRS_TO_REMOVE = [
    'cogs.bak',  # Backup directory
    'db.bak',    # Database backup (if you have recent backups elsewhere)
    'update',    # Update files from original project
    'patches',   # Patch files from original project
]

# Generated/temporary files
TEMP_PATTERNS = [
    'guild_scan_report.txt',
    'pack_output.txt',
]


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    try:
        return path.stat().st_size
    except:
        return 0


def format_size(bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def get_dir_size(path: Path) -> int:
    """Get total size of directory."""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += get_file_size(item)
    except:
        pass
    return total


def remove_files(dry_run: bool = True):
    """Remove packaging and deployment files."""
    removed_files = []
    removed_dirs = []
    total_size = 0
    
    print("=" * 80)
    print("CLEANUP SCRIPT FOR ANNAWAY FORK")
    print("=" * 80)
    print()
    
    if dry_run:
        print("[DRY RUN] No files will actually be deleted")
        print()
    else:
        print("[!] LIVE MODE - Files will be permanently deleted!")
        print()
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        print()
    
    # Remove files
    print("Files to remove:")
    print("-" * 80)
    for filename in FILES_TO_REMOVE:
        path = Path(filename)
        if path.exists():
            size = get_file_size(path)
            total_size += size
            print(f"  [-] {filename} ({format_size(size)})")
            removed_files.append(filename)
            if not dry_run:
                try:
                    path.unlink()
                    print(f"      ✓ Deleted")
                except Exception as e:
                    print(f"      ✗ Error: {e}")
        else:
            print(f"  [ ] {filename} (not found)")
    
    print()
    
    # Remove directories
    print("Directories to remove:")
    print("-" * 80)
    for dirname in DIRS_TO_REMOVE:
        path = Path(dirname)
        if path.exists() and path.is_dir():
            size = get_dir_size(path)
            total_size += size
            print(f"  [-] {dirname}/ ({format_size(size)})")
            removed_dirs.append(dirname)
            if not dry_run:
                try:
                    shutil.rmtree(path)
                    print(f"      ✓ Deleted")
                except Exception as e:
                    print(f"      ✗ Error: {e}")
        else:
            print(f"  [ ] {dirname}/ (not found)")
    
    print()
    
    # Remove temporary files
    print("Temporary files:")
    print("-" * 80)
    for pattern in TEMP_PATTERNS:
        for path in Path('.').glob(pattern):
            size = get_file_size(path)
            total_size += size
            print(f"  [-] {path} ({format_size(size)})")
            removed_files.append(str(path))
            if not dry_run:
                try:
                    path.unlink()
                    print(f"      ✓ Deleted")
                except Exception as e:
                    print(f"      ✗ Error: {e}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files that would be removed:       {len(removed_files)}")
    print(f"Directories that would be removed: {len(removed_dirs)}")
    print(f"Total space that would be freed:   {format_size(total_size)}")
    print()
    
    if dry_run:
        print("To actually delete these files, run:")
        print("  python cleanup_packaging_files.py --live")
    else:
        print("[+] Cleanup completed!")
    print()


if __name__ == '__main__':
    import sys
    
    dry_run = '--live' not in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nUsage:")
        print("  python cleanup_packaging_files.py          # Dry run (show what would be deleted)")
        print("  python cleanup_packaging_files.py --live   # Actually delete files")
        sys.exit(0)
    
    remove_files(dry_run=dry_run)

