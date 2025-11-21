#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOTFIX: Fix i18n error in gift_operations.py
修復 gift_operations.py 中的 i18n 錯誤
"""

import re

def fix_i18n_scope_error():
    """修復 update_embed_description 中的 _ 變數作用域錯誤"""
    
    file_path = 'cogs/gift_operations.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 update_embed_description 函數定義
    # 在函數開頭添加 from i18n_manager import _
    
    old_pattern = r'(def update_embed_description\(include_errors=False\):)\s+(base_description = \()'
    
    new_code = r'\1\n                from i18n_manager import _  # HOTFIX: Import _ in nested function scope\n                \2'
    
    content = re.sub(old_pattern, new_code, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed i18n scope error in update_embed_description")
    return True

def fix_traceback_import():
    """修復 traceback 變數錯誤"""
    
    file_path = 'cogs/gift_operations.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 確保在文件頂部有 import traceback
    if 'import traceback' not in content[:1000]:  # 檢查前 1000 字符
        # 在其他 imports 後添加
        import_pattern = r'(from i18n_manager import.*?\n)'
        content = re.sub(import_pattern, r'\1import traceback\n', content, count=1)
        print("✓ Added 'import traceback' to imports")
    
    # 檢查 use_giftcode_for_alliance 中的異常處理
    # 確保 traceback.format_exc() 前有導入
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("HOTFIX: Fixing gift_operations.py errors")
    print("=" * 70)
    print()
    
    try:
        fix_i18n_scope_error()
        fix_traceback_import()
        
        print()
        print("=" * 70)
        print("✅ HOTFIX COMPLETED")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Restart bot: pkill -f 'python.*main.py' && cd ~/wos_bot && nohup python main.py > bot.log 2>&1 &")
        print("  2. Wait for next auto-retry (台灣時間 20:00)")
        print("  3. Check logs: tail -50 log/gift_ops.txt")
        print()
        
    except Exception as e:
        print(f"❌ HOTFIX FAILED: {e}")
        import traceback
        traceback.print_exc()




