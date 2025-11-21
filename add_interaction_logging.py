#!/usr/bin/env python3
"""在 alliance.py 的 on_interaction 中添加詳細日誌"""

with open('wos_bot/cogs/alliance.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 on_interaction 的位置
if '@commands.Cog.listener()' in content and 'async def on_interaction' in content:
    # 在 on_interaction 函數開始處添加日誌
    old_code = '''    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle all interactions for this cog"""
        try:'''
    
    new_code = '''    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle all interactions for this cog"""
        try:
            print(f"[alliance.on_interaction] 收到交互: type={interaction.type}, custom_id={getattr(interaction.data, 'custom_id', 'N/A') if hasattr(interaction, 'data') else 'N/A'}")
            if interaction.type == discord.InteractionType.component:
                custom_id = interaction.data.get('custom_id', '')
                print(f"[alliance.on_interaction] 按鈕點擊: custom_id='{custom_id}', user={interaction.user.display_name}")'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open('wos_bot/cogs/alliance.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 已添加詳細的 interaction 日誌")
        print("請重啟 bot 並重新測試")
    else:
        print("❌ 找不到正確的 on_interaction 位置")
        print("請手動檢查 cogs/alliance.py")
else:
    print("❌ 找不到 on_interaction 方法")


