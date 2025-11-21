#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pack A1 Deployment Package
打包 A1 部署套件
"""

import zipfile
import os
from datetime import datetime
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'A1_deployment_package_{timestamp}.zip'

print("")
print("=" * 70)
print("  A1 Guild Isolation Deployment Package")
print("=" * 70)
print("")

# Files to include
files_to_pack = {
    # Modified cogs
    'cogs/alliance.py': 'cogs/alliance.py',
    'cogs/alliance_member_operations.py': 'cogs/alliance_member_operations.py',
    'cogs/statistics.py': 'cogs/statistics.py',
    'cogs/changes.py': 'cogs/changes.py',
    'cogs/permission_management.py': 'cogs/permission_management.py',
    
    # Migration script
    'migrations/001_add_guild_isolation.py': 'migrations/001_add_guild_isolation.py',
    
    # Documentation
    'TASK_COMPLETION_REPORT.md': 'TASK_COMPLETION_REPORT.md',
    'TESTING_A1_GUILD_ISOLATION.md': 'TESTING_A1_GUILD_ISOLATION.md',
    'DEPLOY_A1_A2_A3.md': 'DEPLOY_A1_A2_A3.md',
    
    # Patches (optional, for reference)
    'patches/A1_guild_isolation_core.py': 'patches/A1_guild_isolation_core.py',
    'patches/A1_guild_isolation_complete.sh': 'patches/A1_guild_isolation_complete.sh',
}

try:
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        packed_count = 0
        missing_count = 0
        
        print("[Packing Files]")
        print("-" * 70)
        
        for source, target in files_to_pack.items():
            if os.path.exists(source):
                zipf.write(source, target)
                file_size = os.path.getsize(source)
                print(f"  [+] {source:<50} {file_size:>8} bytes")
                packed_count += 1
            else:
                print(f"  [!] {source:<50} MISSING")
                missing_count += 1
        
        print("-" * 70)
        
        # Add README for deployment
        readme_content = """# A1 Guild Isolation Deployment Package
        # A1 Guild 隔離部署套件
        
        ## 📦 Package Contents
        
        - Modified cogs (5 files)
        - Migration script (1 file)
        - Documentation (3 files)
        - Patch scripts (2 files, optional)
        
        ## 🚀 Quick Deployment
        
        ### On VM:
        
        1. Upload this package to VM
        2. Extract: `unzip A1_deployment_package_*.zip`
        3. Copy files: `cp -r cogs/* ~/wos_bot/cogs/ && cp -r migrations ~/wos_bot/`
        4. Run migration: `python ~/wos_bot/migrations/001_add_guild_isolation.py`
        5. Restart bot: `pkill -f 'python.*main.py' && cd ~/wos_bot && nohup python main.py > bot.log 2>&1 &`
        
        ### Testing:
        
        See `TESTING_A1_GUILD_ISOLATION.md` for comprehensive test suite.
        
        ## 📊 Verification
        
        ```sql
        -- Check indexes
        SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='alliance_list';
        
        -- Check data
        SELECT discord_server_id, COUNT(*) FROM alliance_list GROUP BY discord_server_id;
        ```
        
        ## 📞 Support
        
        See `DEPLOY_A1_A2_A3.md` for troubleshooting and rollback procedures.
        """
        
        zipf.writestr('README.txt', readme_content)
        print(f"  [+] {'README.txt':<50} (generated)")
    
    # Package summary
    total_size = os.path.getsize(output_file)
    
    print("")
    print("=" * 70)
    print("  Package Created Successfully!")
    print("=" * 70)
    print("")
    print(f"File: {output_file}")
    print(f"Size: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    print(f"Files packed: {packed_count}")
    if missing_count > 0:
        print(f"Files missing: {missing_count} (WARNING)")
    print("")
    
    print("Next Steps:")
    print("  1. Upload to VM:")
    print(f"     gcloud compute scp {output_file} wos-giftcode-bot:~/")
    print("")
    print("  2. Or use Google Cloud Console:")
    print("     SSH > Upload File > Select this zip")
    print("")
    print("  3. On VM, extract and deploy:")
    print(f"     unzip {output_file}")
    print("     cd A1_deployment_package_*/")
    print("     # Follow README.txt instructions")
    print("")
    print("=" * 70)
    print("")
    
except Exception as e:
    print(f"\nERROR: Failed to create package: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




