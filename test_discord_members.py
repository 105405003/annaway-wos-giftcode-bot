#!/usr/bin/env python3
"""
測試 Discord Members Intent 是否正常工作
"""

import discord
import os
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
env_paths = [
    Path('wos_bot/bot_config.env'),
    Path('bot_config.env'),
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已載入環境變數: {env_path}")
        break
else:
    print("❌ 找不到 bot_config.env")
    exit(1)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    print("❌ 找不到 BOT_TOKEN")
    exit(1)

print(f"✅ BOT_TOKEN: {TOKEN[:20]}...")
print()

# 設定 intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # 重要！

print(f"🔍 Intents 設定:")
print(f"   - message_content: {intents.message_content}")
print(f"   - members: {intents.members}")
print()

client = discord.Client(intents=intents)

GUILD_ID = 1354505516193419454  # 1496 SvS
MANAGER_USER_ID = 1241708134311747674  # buli3620

@client.event
async def on_ready():
    print(f"✅ Bot 已登入: {client.user}")
    print()
    
    # 取得 guild
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print(f"❌ 找不到 guild {GUILD_ID}")
        await client.close()
        return
    
    print(f"✅ 找到 guild: {guild.name} (ID: {guild.id})")
    print(f"   - 成員數量: {guild.member_count}")
    print()
    
    # 檢查是否需要 fetch members
    print(f"🔍 當前快取的成員數量: {len(guild.members)}")
    if len(guild.members) < guild.member_count:
        print(f"⚠️  快取成員少於實際成員，嘗試 fetch...")
        try:
            await guild.chunk()
            print(f"✅ Fetch 成功，現在有 {len(guild.members)} 個成員在快取中")
        except Exception as e:
            print(f"❌ Fetch 失敗: {e}")
    print()
    
    # 查找 Manager 用戶
    print(f"🔍 查找 Manager 用戶 (ID: {MANAGER_USER_ID})")
    member = guild.get_member(MANAGER_USER_ID)
    
    if not member:
        print(f"❌ 找不到用戶！可能是 Members Intent 未啟用")
        print(f"   請確認：")
        print(f"   1. Discord Developer Portal 已啟用 SERVER MEMBERS INTENT")
        print(f"   2. main.py 中有設定 intents.members = True")
    else:
        print(f"✅ 找到用戶: {member.display_name}")
        print(f"   - 用戶名稱: {member.name}")
        print(f"   - 暱稱: {member.display_name}")
        print(f"   - ID: {member.id}")
        print()
        
        # 列出所有角色
        print(f"🎭 用戶的所有角色:")
        for role in member.roles:
            print(f"   - {role.name} (ID: {role.id})")
        print()
        
        # 檢查特定角色
        print(f"🔍 檢查特定角色:")
        has_manager = discord.utils.get(member.roles, name="Annaway_Manager") is not None
        has_admin = discord.utils.get(member.roles, name="Annaway_Admin") is not None
        
        print(f"   - Annaway_Manager: {'✅ 有' if has_manager else '❌ 沒有'}")
        print(f"   - Annaway_Admin: {'✅ 有' if has_admin else '❌ 沒有'}")
        print()
        
        if has_manager or has_admin:
            print("✅ 用戶有 Manager 或 Admin 角色，應該可以使用所有功能")
        else:
            print("❌ 用戶沒有 Manager 或 Admin 角色")
            print()
            print("🔍 伺服器中的所有角色:")
            for role in guild.roles:
                print(f"   - {role.name} (ID: {role.id})")
    
    print()
    print("=" * 60)
    print("診斷完成！")
    print("=" * 60)
    
    await client.close()

try:
    print("🚀 正在連接 Discord...")
    print()
    client.run(TOKEN)
except Exception as e:
    print(f"❌ 連接失敗: {e}")
    import traceback
    traceback.print_exc()


