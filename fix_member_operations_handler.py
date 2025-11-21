#!/usr/bin/env python3
"""修復 alliance.py 中的 member_operations 按鈕處理邏輯"""

with open('wos_bot/cogs/alliance.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到並替換第 785-786 行
for i, line in enumerate(lines):
    if 'elif custom_id == "member_operations":' in line:
        # 找到了目標行（索引 i 是這一行）
        # 下一行應該是 await self.bot.get_cog...
        if i + 1 < len(lines) and 'await self.bot.get_cog("AllianceMemberOperations")' in lines[i + 1]:
            # 替換這兩行
            indent = '                '  # 16 個空格
            lines[i] = f'{indent}elif custom_id == "member_operations":\n'
            lines[i + 1] = f'{indent}    try:\n'
            
            # 插入新的代碼
            new_code = [
                f'{indent}        print(f"[alliance.on_interaction] Processing member_operations for user={{interaction.user.display_name}}")\n',
                f'{indent}        member_ops_cog = self.bot.get_cog("AllianceMemberOperations")\n',
                f'{indent}        if member_ops_cog:\n',
                f'{indent}            await member_ops_cog.handle_member_operations(interaction)\n',
                f'{indent}        else:\n',
                f'{indent}            print("[alliance.on_interaction] ERROR: AllianceMemberOperations cog not found!")\n',
                f'{indent}            await interaction.response.send_message(\n',
                f'{indent}                "❌ 成員操作模組未找到，請聯繫管理員",\n',
                f'{indent}                ephemeral=True\n',
                f'{indent}            )\n',
                f'{indent}    except Exception as e:\n',
                f'{indent}        print(f"[alliance.on_interaction] ERROR in member_operations: {{e}}")\n',
                f'{indent}        import traceback\n',
                f'{indent}        traceback.print_exc()\n',
                f'{indent}        if not interaction.response.is_done():\n',
                f'{indent}            await interaction.response.send_message(\n',
                f'{indent}                f"❌ 處理成員操作時發生錯誤: {{str(e)}}",\n',
                f'{indent}                ephemeral=True\n',
                f'{indent}            )\n',
            ]
            
            # 插入新代碼，替換原來的第 i+1 行
            lines[i + 1:i + 2] = new_code
            
            print("✅ 已修復 member_operations 按鈕處理邏輯")
            print(f"   修改位置: 第 {i + 1} 行")
            break
else:
    print("❌ 找不到 member_operations 處理邏輯")
    exit(1)

# 寫回文件
with open('wos_bot/cogs/alliance.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ 修復完成！")
print("請重啟 bot 並重新測試")


