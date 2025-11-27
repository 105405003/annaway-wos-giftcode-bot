#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PATCH A1: Guild Isolation - Core Alliance Query Fixes
修補 A1: Guild 隔離 - 核心聯盟查詢修復

This patch ensures ALL alliance queries include discord_server_id filtering
此補丁確保所有聯盟查詢都包含 discord_server_id 篩選
"""

import re

# ============================================================================
# PATCH 1: cogs/alliance.py - view_alliances
# ============================================================================
def patch_alliance_view_alliances():
    """修復 view_alliances 確保即使是 is_initial=1 也要篩選 guild"""
    file_path = 'cogs/alliance.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 view_alliances 中的查詢邏輯
    old_pattern = r'''        try:
            if is_initial == 1:
                query = """
                    SELECT a\.alliance_id, a\.name, COALESCE\(s\.interval, 0\) as interval
                    FROM alliance_list a
                    LEFT JOIN alliancesettings s ON a\.alliance_id = s\.alliance_id
                    ORDER BY a\.alliance_id ASC
                """
                self\.c\.execute\(query\)
            else:
                query = """
                    SELECT a\.alliance_id, a\.name, COALESCE\(s\.interval, 0\) as interval
                    FROM alliance_list a
                    LEFT JOIN alliancesettings s ON a\.alliance_id = s\.alliance_id
                    WHERE a\.discord_server_id = \?
                    ORDER BY a\.alliance_id ASC
                """
                self\.c\.execute\(query, \(guild_id,\)\)'''
    
    new_code = '''        try:
            # ✨ A1 FIX: 所有用戶（包括 global admin）都只能看到當前 guild 的聯盟
            query = """
                SELECT a.alliance_id, a.name, COALESCE(s.interval, 0) as interval
                FROM alliance_list a
                LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
                WHERE a.discord_server_id = ?
                ORDER BY a.alliance_id ASC
            """
            self.c.execute(query, (guild_id,))'''
    
    if re.search(old_pattern, content, re.DOTALL):
        content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Patched {file_path}: view_alliances")
        return True
    else:
        print(f"⚠️  Pattern not found in {file_path}, may already be patched")
        return False

# ============================================================================
# PATCH 2: cogs/alliance.py - alliance_autocomplete
# ============================================================================
def patch_alliance_autocomplete():
    """修復 alliance_autocomplete 加上 guild 篩選"""
    file_path = 'cogs/alliance.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_code = '''    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str):
        self.c.execute("SELECT alliance_id, name FROM alliance_list")
        alliances = self.c.fetchall()
        return [
            app_commands.Choice(name=f"{name} (ID: {alliance_id})", value=str(alliance_id))
            for alliance_id, name in alliances if current.lower() in name.lower()
        ][:25]'''
    
    new_code = '''    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str):
        # ✨ A1 FIX: 只顯示當前 guild 的聯盟
        guild_id = interaction.guild.id if interaction.guild else None
        if guild_id:
            self.c.execute(
                "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ?",
                (guild_id,)
            )
        else:
            self.c.execute("SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = -1")
        alliances = self.c.fetchall()
        return [
            app_commands.Choice(name=f"{name} (ID: {alliance_id})", value=str(alliance_id))
            for alliance_id, name in alliances if current.lower() in name.lower()
        ][:25]'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Patched {file_path}: alliance_autocomplete")
        return True
    else:
        print(f"⚠️  alliance_autocomplete pattern not found, may already be patched")
        return False

# ============================================================================
# PATCH 3: cogs/alliance.py - delete_alliance
# ============================================================================
def patch_alliance_delete():
    """修復 delete_alliance 加上 guild 篩選"""
    file_path = 'cogs/alliance.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_code = '''    async def delete_alliance(self, interaction: discord.Interaction):
        try:
            self.c.execute("SELECT alliance_id, name FROM alliance_list ORDER BY name")
            alliances = self.c.fetchall()'''
    
    new_code = '''    async def delete_alliance(self, interaction: discord.Interaction):
        try:
            # ✨ A1 FIX: 只顯示當前 guild 的聯盟供刪除
            guild_id = interaction.guild.id if interaction.guild else None
            if guild_id:
                self.c.execute(
                    "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
                    (guild_id,)
                )
            else:
                self.c.execute("SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = -1 ORDER BY name")
            alliances = self.c.fetchall()'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Patched {file_path}: delete_alliance")
        return True
    else:
        print(f"⚠️  delete_alliance pattern not found, may already be patched")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("APPLYING PATCH A1: Guild Isolation - Core Fixes")
    print("=" * 80)
    print()
    
    results = []
    results.append(("view_alliances", patch_alliance_view_alliances()))
    results.append(("alliance_autocomplete", patch_alliance_autocomplete()))
    results.append(("delete_alliance", patch_alliance_delete()))
    
    print()
    print("=" * 80)
    print("PATCH SUMMARY")
    print("=" * 80)
    for name, success in results:
        status = "✅" if success else "⚠️ "
        print(f"{status} {name}")
    
    total = len(results)
    success_count = sum(1 for _, s in results if s)
    print()
    print(f"Applied {success_count}/{total} patches successfully")
    
    if success_count == total:
        print("\n✅ ALL PATCHES APPLIED - Ready for testing")
    else:
        print("\n⚠️  Some patches may have already been applied or code structure changed")
        print("Please manually verify the files")







