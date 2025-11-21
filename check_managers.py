#!/usr/bin/env python3
"""檢查 Discord 伺服器中的 Manager 身分組成員"""

import discord
from discord.ext import commands
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 嘗試從多個位置載入環境變數
env_paths = [
    Path.home() / 'wos_bot' / 'bot_config.env',  # ~/wos_bot/bot_config.env
    Path('wos_bot/bot_config.env'),               # 從當前目錄
    Path('bot_config.env'),                       # 從當前目錄
    Path('../bot_config.env'),                    # 從上層目錄
]

TOKEN = None
for env_path in env_paths:
    print(f'🔍 檢查: {env_path}')
    if env_path.exists():
        print(f'   ✓ 文件存在')
        load_dotenv(env_path)
        TOKEN = os.getenv('BOT_TOKEN')
        if TOKEN:
            print(f'   ✅ 成功載入 TOKEN (長度: {len(TOKEN)})')
            break
        else:
            print(f'   ⚠️  文件存在但沒有 BOT_TOKEN')
    else:
        print(f'   ✗ 文件不存在')

if not TOKEN:
    print('\n❌ 錯誤: 無法找到 BOT_TOKEN')
    print('請確認 bot_config.env 文件存在且包含 BOT_TOKEN')
    sys.exit(1)

# 設置 intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ 機器人已登入: {bot.user.name} (ID: {bot.user.id})')
    print(f'\n📊 伺服器列表:')
    print('=' * 80)
    
    for guild in bot.guilds:
        print(f'\n🏰 伺服器: {guild.name} (ID: {guild.id})')
        print(f'   成員總數: {guild.member_count}')
        
        # 查找 Annaway_Admin 身分組
        admin_role = discord.utils.get(guild.roles, name="Annaway_Admin")
        if admin_role:
            admin_members = admin_role.members
            print(f'\n   👑 Annaway_Admin 身分組 (ID: {admin_role.id})')
            print(f'      成員數: {len(admin_members)}')
            for member in admin_members:
                print(f'      - {member.name} (ID: {member.id})')
        else:
            print(f'\n   ⚠️  未找到 Annaway_Admin 身分組')
        
        # 查找 Annaway_Manager 身分組
        manager_role = discord.utils.get(guild.roles, name="Annaway_Manager")
        if manager_role:
            manager_members = manager_role.members
            print(f'\n   👔 Annaway_Manager 身分組 (ID: {manager_role.id})')
            print(f'      成員數: {len(manager_members)}')
            for member in manager_members:
                print(f'      - {member.name} (ID: {member.id})')
        else:
            print(f'\n   ⚠️  未找到 Annaway_Manager 身分組')
        
        print('   ' + '-' * 76)
    
    print('\n' + '=' * 80)
    print('✅ 檢查完成！')
    
    await bot.close()

if __name__ == '__main__':
    bot.run(TOKEN)

