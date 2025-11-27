#!/usr/bin/env python3
"""
測試 Manager 權限的獨立腳本
直接讀取資料庫和模擬 Discord 角色檢查
"""

import sqlite3
from pathlib import Path

# Manager 用戶資訊
MANAGER_USER_ID = 1241708134311747674  # buli3620
GUILD_ID = 1354505516193419454  # 1496 SvS

print("=" * 60)
print("Manager 權限診斷腳本")
print("=" * 60)
print()

# 1. 檢查 admin 表
print("1️⃣ 檢查 admin 表")
print("-" * 60)
try:
    with sqlite3.connect('wos_bot/db/settings.sqlite') as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, is_initial FROM admin WHERE id = ?", (MANAGER_USER_ID,))
        result = cursor.fetchone()
        if result:
            print(f"✅ 用戶在 admin 表中")
            print(f"   ID: {result[0]}")
            print(f"   is_initial: {result[1]}")
        else:
            print(f"❌ 用戶不在 admin 表中")
            print(f"   這是正常的，Manager 應該通過 Discord 角色驗證")
except Exception as e:
    print(f"❌ 錯誤: {e}")
print()

# 2. 檢查 adminserver 表（特殊權限）
print("2️⃣ 檢查 adminserver 表（Manager 特殊聯盟權限）")
print("-" * 60)
try:
    with sqlite3.connect('wos_bot/db/settings.sqlite') as db:
        cursor = db.cursor()
        cursor.execute("SELECT alliances_id FROM adminserver WHERE admin = ?", (MANAGER_USER_ID,))
        alliances = cursor.fetchall()
        if alliances:
            print(f"✅ 找到 {len(alliances)} 個特殊權限聯盟:")
            for alliance_id, in alliances:
                print(f"   - 聯盟 ID: {alliance_id}")
        else:
            print(f"ℹ️  沒有設定特殊權限聯盟")
            print(f"   Manager 預設可以操作當前 guild 的所有聯盟")
except Exception as e:
    print(f"❌ 錯誤: {e}")
print()

# 3. 檢查 alliance_list 表
print("3️⃣ 檢查 alliance_list 表")
print("-" * 60)
try:
    with sqlite3.connect('wos_bot/db/alliance.sqlite') as db:
        cursor = db.cursor()
        
        # 檢查是否有 discord_server_id 欄位
        cursor.execute("PRAGMA table_info(alliance_list)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'discord_server_id' not in columns:
            print("❌ alliance_list 表缺少 discord_server_id 欄位！")
            print("   需要執行 A1 遷移腳本")
        else:
            print("✅ alliance_list 表有 discord_server_id 欄位")
            
            # 查詢當前 guild 的聯盟
            cursor.execute(
                "SELECT alliance_id, name, discord_server_id FROM alliance_list WHERE discord_server_id = ?",
                (GUILD_ID,)
            )
            alliances = cursor.fetchall()
            
            if alliances:
                print(f"✅ 當前 guild ({GUILD_ID}) 有 {len(alliances)} 個聯盟:")
                for alliance_id, name, server_id in alliances:
                    print(f"   - ID: {alliance_id}, 名稱: {name}, Server ID: {server_id}")
            else:
                print(f"❌ 當前 guild ({GUILD_ID}) 沒有聯盟")
                
                # 列出所有聯盟
                cursor.execute("SELECT alliance_id, name, discord_server_id FROM alliance_list")
                all_alliances = cursor.fetchall()
                if all_alliances:
                    print(f"\n   所有聯盟:")
                    for alliance_id, name, server_id in all_alliances:
                        print(f"   - ID: {alliance_id}, 名稱: {name}, Server ID: {server_id}")
except Exception as e:
    print(f"❌ 錯誤: {e}")
print()

# 4. 檢查 cog 檔案是否有 HOTFIX
print("4️⃣ 檢查 cog 檔案是否包含 HOTFIX")
print("-" * 60)
files_to_check = [
    'wos_bot/cogs/alliance_member_operations.py',
    'wos_bot/cogs/changes.py',
    'wos_bot/cogs/statistics.py'
]

for filepath in files_to_check:
    try:
        path = Path(filepath)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            if 'HOTFIX: 支援 Manager 角色' in content:
                print(f"✅ {filepath.split('/')[-1]} 包含 HOTFIX")
            else:
                print(f"❌ {filepath.split('/')[-1]} 不包含 HOTFIX - 需要重新部署！")
        else:
            print(f"❌ {filepath} 不存在")
    except Exception as e:
        print(f"❌ {filepath}: {e}")
print()

# 5. 總結
print("=" * 60)
print("📋 診斷總結")
print("=" * 60)
print()
print("如果看到以下情況，Manager 應該可以正常使用：")
print("✅ 用戶不在 admin 表中（或 is_initial = 0）")
print("✅ alliance_list 表有 discord_server_id 欄位")
print("✅ 當前 guild 有聯盟")
print("✅ 所有 cog 檔案都包含 HOTFIX")
print()
print("如果出現以下情況，需要修復：")
print("❌ alliance_list 缺少 discord_server_id → 執行 A1 遷移腳本")
print("❌ 當前 guild 沒有聯盟 → 新增聯盟或檢查 discord_server_id")
print("❌ cog 檔案不包含 HOTFIX → 重新部署 hotfix4")
print()







