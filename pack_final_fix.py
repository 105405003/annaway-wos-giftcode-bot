#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pack final fix files"""
import zipfile
from datetime import datetime
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output = f'final_fix_{timestamp}.zip'

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('cogs/gift_operations.py')
    z.write('check_managers.py')

size = os.path.getsize(output)

print("")
print("=" * 60)
print("  Fix Package Created!")
print("=" * 60)
print("")
print(f"File: {output}")
print(f"Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
print("")
print("Fixed Issues:")
print("  [X] gift_operations.py - datetime timezone error")
print("  [X] check_managers.py - TOKEN loading issue")
print("")
print("Upload to VM and run:")
print(f"  cd ~")
print(f"  unzip -o {output}")
print(f"  cp cogs/gift_operations.py wos_bot/cogs/")
print(f"  cp check_managers.py wos_bot/")
print(f"  cd wos_bot")
print(f"  pkill -f 'python.*main.py'")
print(f"  sleep 2")
print(f"  source bot_venv/bin/activate")
print(f"  nohup python main.py > bot.log 2>&1 &")
print(f"  sleep 5")
print(f"  tail -50 log/gift_ops.txt | grep '自動重試'")
print("")
print("Test check_managers.py:")
print("  cd wos_bot")
print("  source bot_venv/bin/activate")
print("  python check_managers.py")
print("")
print("=" * 60)
print("")

