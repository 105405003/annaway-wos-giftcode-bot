import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
from i18n_manager import i18n, _
from utils.permissions import requires_annaway_role, requires_annaway_role_button
from .login_handler import LoginHandler

class AllianceMemberOperations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 連接資料庫
        self.conn_alliance = sqlite3.connect('db/alliance.sqlite')
        self.c_alliance = self.conn_alliance.cursor()
        
        self.conn_users = sqlite3.connect('db/users.sqlite')
        self.c_users = self.conn_users.cursor()
        
        self.conn_settings = sqlite3.connect('db/settings.sqlite')
        self.c_settings = self.conn_settings.cursor()
        
        # 初始化 LoginHandler
        self.login_handler = LoginHandler()
        
        # 熔爐等級映射
        self.level_mapping = {
            31: "30-1", 32: "30-2", 33: "30-3", 34: "30-4",
            35: "FC 1", 36: "FC 1 - 1", 37: "FC 1 - 2", 38: "FC 1 - 3", 39: "FC 1 - 4",
            40: "FC 2", 41: "FC 2 - 1", 42: "FC 2 - 2", 43: "FC 2 - 3", 44: "FC 2 - 4",
            45: "FC 3", 46: "FC 3 - 1", 47: "FC 3 - 2", 48: "FC 3 - 3", 49: "FC 3 - 4",
            50: "FC 4", 51: "FC 4 - 1", 52: "FC 4 - 2", 53: "FC 4 - 3", 54: "FC 4 - 4",
            55: "FC 5", 56: "FC 5 - 1", 57: "FC 5 - 2", 58: "FC 5 - 3", 59: "FC 5 - 4",
            60: "FC 6", 61: "FC 6 - 1", 62: "FC 6 - 2", 63: "FC 6 - 3", 64: "FC 6 - 4",
            65: "FC 7", 66: "FC 7 - 1", 67: "FC 7 - 2", 68: "FC 7 - 3", 69: "FC 7 - 4",
            70: "FC 8", 71: "FC 8 - 1", 72: "FC 8 - 2", 73: "FC 8 - 3", 74: "FC 8 - 4",
            75: "FC 9", 76: "FC 9 - 1", 77: "FC 9 - 2", 78: "FC 9 - 3", 79: "FC 9 - 4",
            80: "FC 10", 81: "FC 10 - 1", 82: "FC 10 - 2", 83: "FC 10 - 3", 84: "FC 10 - 4"
        }
    
    @app_commands.command(name="add", description="新增成員到聯盟（所有人都可以使用）")
    @app_commands.describe(
        oper1="聯盟簡稱或名稱",
        oper2="玩家 FID"
    )
    async def add_command(self, interaction: discord.Interaction, oper1: str, oper2: str):
        """所有用戶都可以使用的新增成員命令"""
        try:
            # 驗證 FID 是否為數字
            if not oper2.isdigit():
                await interaction.response.send_message(
                    "❌ FID 必須是數字",
                    ephemeral=True
                )
                return
            
            fid = int(oper2)
            
            # Get guild context for multi-guild isolation
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            guild_id = interaction.guild.id
            
            # 搜尋聯盟（支援模糊匹配）- filter by current guild
            self.c_alliance.execute(
                "SELECT alliance_id, name FROM alliance_list WHERE (name LIKE ? OR alliance_id = ?) AND discord_server_id = ?",
                (f"%{oper1}%", oper1, guild_id)
            )
            results = self.c_alliance.fetchall()
            
            if not results:
                await interaction.response.send_message(
                    f"❌ 找不到聯盟 `{oper1}`",
                    ephemeral=True
                )
                return
            
            if len(results) > 1:
                # 多個匹配，讓用戶選擇
                options_text = "\n".join([f"• {name} (ID: {aid})" for aid, name in results[:10]])
                await interaction.response.send_message(
                    f"找到多個匹配的聯盟，請使用完整名稱或 ID：\n\n{options_text}",
                    ephemeral=True
                )
                return
            
            alliance_id, alliance_name = results[0]
            
            # 發送處理中訊息
            await interaction.response.send_message(
                "⏳ 正在從 API 獲取玩家資料...",
                ephemeral=True
            )
            
            # 檢查是否已存在
            existing = self.c_users.execute(
                "SELECT nickname, furnace_lv, alliance FROM users WHERE fid = ?",
                (fid,)
            ).fetchone()
            
            if existing:
                nickname, furnace_lv, current_alliance = existing
                
                if current_alliance == str(alliance_id):
                    level_display = self.level_mapping.get(furnace_lv, str(furnace_lv)) if furnace_lv else "N/A"
                    await interaction.edit_original_response(
                        content=f"ℹ️ **{nickname}** (FID: `{fid}`, 熔爐: `{level_display}`) 已經在 **{alliance_name}** 中"
                    )
                    return
                else:
                    # 更新聯盟
                    self.c_users.execute(
                        "UPDATE users SET alliance = ? WHERE fid = ?",
                        (str(alliance_id), fid)
                    )
                    self.conn_users.commit()
                    
                    level_display = self.level_mapping.get(furnace_lv, str(furnace_lv)) if furnace_lv else "N/A"
                    embed = discord.Embed(
                        title="✅ 成員轉移成功",
                        description=f"**{nickname}** 已轉移到 **{alliance_name}**\n\n🆔 **FID:** `{fid}`\n🔥 **熔爐等級:** `{level_display}`",
                        color=discord.Color.green()
                    )
                    await interaction.edit_original_response(content=None, embed=embed)
                    return
            
            # 從 API 獲取玩家資料
            result = await self.login_handler.fetch_player_data(str(fid))
            
            if result['status'] == 'success':
                data = result['data']
                nickname = data.get('nickname')
                furnace_lv = data.get('stove_lv', 0)
                stove_lv_content = data.get('stove_lv_content', None)
                kid = data.get('kid', None)
                
                if nickname:
                    # 新增成員到資料庫
                    self.c_users.execute(
                        "INSERT INTO users (fid, nickname, furnace_lv, kid, stove_lv_content, alliance) VALUES (?, ?, ?, ?, ?, ?)",
                        (fid, nickname, furnace_lv, kid, stove_lv_content, str(alliance_id))
                    )
                    self.conn_users.commit()
                    
                    level_display = self.level_mapping.get(furnace_lv, str(furnace_lv))
                    embed = discord.Embed(
                        title="✅ 成員新增成功",
                        description=f"**{nickname}** 已成功新增到 **{alliance_name}**\n\n🆔 **FID:** `{fid}`\n🔥 **熔爐等級:** `{level_display}`",
                        color=discord.Color.green()
                    )
                    await interaction.edit_original_response(content=None, embed=embed)
                else:
                    await interaction.edit_original_response(
                        content="❌ API 返回的玩家資料不完整"
                    )
            elif result['status'] == 'not_found':
                await interaction.edit_original_response(
                    content=f"❌ 找不到 FID `{fid}` 的玩家（玩家不存在）"
                )
            else:
                error_msg = result.get('error_message', '未知錯誤')
                await interaction.edit_original_response(
                    content=f"❌ 獲取玩家資料失敗: {error_msg}"
                )
                
        except Exception as e:
            import traceback
            print(f"Error in add_command: {e}")
            traceback.print_exc()
            try:
                if interaction.response.is_done():
                    await interaction.edit_original_response(
                        content=f"❌ 新增成員時發生錯誤: {str(e)}"
                    )
                else:
                    await interaction.response.send_message(
                        f"❌ 新增成員時發生錯誤: {str(e)}",
                        ephemeral=True
                    )
            except:
                pass

    async def get_admin_alliances(self, user_id: int, guild_id: int):
        """獲取用戶有權限的聯盟列表"""
        try:
            # ✨ HOTFIX: 支援 Manager 角色（Discord 身分組驅動）
            # 先嘗試從 Discord 獲取用戶資訊
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member:
                    # 檢查是否有 Manager 或 Admin 角色
                    has_manager_role = discord.utils.get(member.roles, name="Annaway_Manager") is not None
                    has_admin_role = discord.utils.get(member.roles, name="Annaway_Admin") is not None
                    
                    print(f"[get_admin_alliances] 用戶: {member.display_name}")
                    print(f"[get_admin_alliances] Manager 角色: {has_manager_role}")
                    print(f"[get_admin_alliances] Admin 角色: {has_admin_role}")
                    
                    # Manager 或 Admin 角色用戶可以看到當前 guild 的聯盟
                    if has_manager_role or has_admin_role:
                        with sqlite3.connect('db/alliance.sqlite') as alliance_db:
                            cursor = alliance_db.cursor()
                            cursor.execute(
                                "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
                                (guild_id,)
                            )
                            alliances = cursor.fetchall()
                            print(f"[get_admin_alliances] 找到 {len(alliances)} 個聯盟")
                            
                            # 如果是 Admin 或有 adminserver 特殊權限，則為 global_admin
                            is_global = has_admin_role
                            
                            # 對於 Manager，檢查 adminserver 表中的特殊權限
                            special_alliances = []
                            if has_manager_role and not has_admin_role:
                                with sqlite3.connect('db/settings.sqlite') as settings_db:
                                    settings_cursor = settings_db.cursor()
                                    settings_cursor.execute(
                                        "SELECT alliances_id FROM adminserver WHERE admin = ?",
                                        (user_id,)
                                    )
                                    special_ids = [row[0] for row in settings_cursor.fetchall()]
                                    if special_ids:
                                        placeholders = ','.join('?' * len(special_ids))
                                        cursor.execute(
                                            f"SELECT alliance_id, name FROM alliance_list WHERE alliance_id IN ({placeholders}) AND discord_server_id = ? ORDER BY name",
                                            special_ids + [guild_id]
                                        )
                                        special_alliances = cursor.fetchall()
                                        print(f"[get_admin_alliances] Manager 特殊權限聯盟: {len(special_alliances)} 個")
                            
                            # Manager 只能看到有權限的聯盟（如果有設定 adminserver）
                            # 如果沒有設定 adminserver，則可以看到所有當前 guild 的聯盟
                            if has_manager_role and not has_admin_role and special_alliances:
                                return special_alliances, special_alliances, False
                            else:
                                return alliances, special_alliances, is_global
            
            # 舊邏輯（資料庫驅動）- 作為後備
            with sqlite3.connect('db/settings.sqlite') as settings_db:
                cursor = settings_db.cursor()
                cursor.execute("SELECT is_initial FROM admin WHERE id = ?", (user_id,))
                admin_result = cursor.fetchone()
                
                if not admin_result:
                    print(f"[get_admin_alliances] User {user_id} 沒有在 admin 表中，也沒有 Discord 角色")
                    return [], [], False
                    
                is_initial = admin_result[0]
                
            if is_initial == 1:
                # ✨ A1 FIX: 全域管理員也只能看到當前 guild 的聯盟
                with sqlite3.connect('db/alliance.sqlite') as alliance_db:
                    cursor = alliance_db.cursor()
                    cursor.execute(
                        "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
                        (guild_id,)
                    )
                    alliances = cursor.fetchall()
                    return alliances, [], True
            
            # 非全域管理員 - 獲取伺服器聯盟和特殊權限聯盟
            server_alliances = []
            special_alliances = []
            
            with sqlite3.connect('db/alliance.sqlite') as alliance_db:
                cursor = alliance_db.cursor()
                cursor.execute("""
                    SELECT DISTINCT alliance_id, name 
                    FROM alliance_list 
                    WHERE discord_server_id = ?
                    ORDER BY name
                """, (guild_id,))
                server_alliances = cursor.fetchall()
            
            with sqlite3.connect('db/settings.sqlite') as settings_db:
                cursor = settings_db.cursor()
                cursor.execute("""
                    SELECT alliances_id 
                    FROM adminserver 
                    WHERE admin = ?
                """, (user_id,))
                special_alliance_ids = cursor.fetchall()
                
            if special_alliance_ids:
                with sqlite3.connect('db/alliance.sqlite') as alliance_db:
                    cursor = alliance_db.cursor()
                    placeholders = ','.join('?' * len(special_alliance_ids))
                    cursor.execute(f"""
                        SELECT DISTINCT alliance_id, name
                        FROM alliance_list
                        WHERE alliance_id IN ({placeholders})
                        ORDER BY name
                    """, [aid[0] for aid in special_alliance_ids])
                    special_alliances = cursor.fetchall()
            
            # 合併伺服器聯盟和特殊權限聯盟，去除重複
            all_alliances = list({(aid, name) for aid, name in (server_alliances + special_alliances)})
            
            if not all_alliances and not special_alliances:
                return [], [], False
            
            return all_alliances, special_alliances, False
                
        except Exception as e:
            print(f"Error getting admin alliances: {e}")
            import traceback
            traceback.print_exc()
            return [], [], False

    async def handle_member_operations(self, interaction: discord.Interaction):
        """處理成員操作主選單"""
        try:
            alliances, _, is_global_admin = await self.get_admin_alliances(
                interaction.user.id,
                interaction.guild_id
            )
            
            if not alliances:
                await interaction.response.send_message(
                    "❌ 沒有可用的聯盟",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="👥 成員操作",
                description=(
                    "請選擇要執行的操作：\n\n"
                    "➕ **新增成員** - 將玩家加入聯盟\n"
                    "➖ **移除成員** - 從聯盟中移除玩家\n"
                    "🔄 **轉移成員** - 將成員轉移到其他聯盟\n"
                    "📋 **查看成員** - 查看聯盟成員列表\n"
                    "🔄 **更新成員資訊** - 手動更新成員的暱稱和熔爐等級\n"
                    "🏠 **主選單** - 返回主選單"
                ),
                color=discord.Color.blue()
            )
            
            view = MemberOperationsView(self)
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in handle_member_operations: {e}")
            await interaction.response.send_message(
                "❌ 載入成員操作時發生錯誤",
                ephemeral=True
            )


class MemberOperationsView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
        self.bot = cog.bot

    @discord.ui.button(label=_("add_member", "BUTTON"), emoji="➕", style=discord.ButtonStyle.success, row=0)
    async def add_member_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_alliance_selection(button_interaction, "add")

    @discord.ui.button(label=_("remove_member", "BUTTON"), emoji="➖", style=discord.ButtonStyle.danger, row=0)
    async def remove_member_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_alliance_selection(button_interaction, "remove")

    @discord.ui.button(label=_("transfer_member", "BUTTON"), emoji="🔄", style=discord.ButtonStyle.primary, row=0)
    async def transfer_member_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_alliance_selection(button_interaction, "transfer")

    @discord.ui.button(label=_("view_members", "BUTTON"), emoji="📋", style=discord.ButtonStyle.primary, row=1)
    async def view_members_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_alliance_selection(button_interaction, "view")

    @discord.ui.button(label=_("update_member_info", "BUTTON"), emoji="🔄", style=discord.ButtonStyle.secondary, row=1)
    async def update_members_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_alliance_selection(button_interaction, "update")

    @discord.ui.button(label=_("main_menu", "BUTTON"), emoji="🏠", style=discord.ButtonStyle.secondary, row=2)
    async def main_menu_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        try:
            alliance_cog = button_interaction.client.get_cog("Alliance")
            if alliance_cog:
                await alliance_cog._show_settings_menu(button_interaction, from_button=True)
            else:
                await button_interaction.response.send_message(
                    "❌ 無法載入主選單",
                    ephemeral=True
                )
        except Exception as e:
            if not any(error_code in str(e) for error_code in ["10062", "40060", "InteractionResponded"]):
                print(f"Error in main_menu_button: {e}")
            pass

    async def _handle_alliance_selection(self, button_interaction, context):
        """處理聯盟選擇"""
        try:
            alliances, _, _ = await self.cog.get_admin_alliances(
                button_interaction.user.id,
                button_interaction.guild_id
            )
            
            if not alliances:
                await button_interaction.response.send_message(
                    "❌ 沒有可用的聯盟",
                    ephemeral=True
                )
                return
            
            # 為每個聯盟添加成員數量
            alliances_with_counts = []
            for alliance_id, name in alliances:
                self.cog.c_users.execute(
                    "SELECT COUNT(*) FROM users WHERE alliance = ?",
                    (str(alliance_id),)
                )
                count = self.cog.c_users.fetchone()[0]
                alliances_with_counts.append((alliance_id, name, count))
            
            # 創建選擇聯盟的介面
            view = AllianceSelectView(alliances_with_counts, self.cog, context=context)
            
            title_map = {
                "add": "➕ 新增成員",
                "remove": "➖ 移除成員",
                "transfer": "🔄 轉移成員",
                "view": "📋 查看成員",
                "update": "🔄 更新成員資訊"
            }
            
            embed = discord.Embed(
                title=title_map.get(context, "👥 成員操作"),
                description="請選擇聯盟：",
                color=discord.Color.blue()
            )
            await button_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error in _handle_alliance_selection: {e}")
            import traceback
            traceback.print_exc()
            if not button_interaction.response.is_done():
                await button_interaction.response.send_message(
                    "❌ 處理時發生錯誤",
                    ephemeral=True
                )


class AllianceSelectView(discord.ui.View):
    def __init__(self, alliances_with_counts, cog=None, page=0, context="add"):
        super().__init__(timeout=300)
        self.alliances = alliances_with_counts
        self.cog = cog
        self.page = page
        self.context = context
        self.max_page = (len(alliances_with_counts) - 1) // 25 if alliances_with_counts else 0
        self.update_select_menu()

    def update_select_menu(self):
        # 移除舊的選單
        for item in self.children[:]:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)

        start_idx = self.page * 25
        end_idx = min(start_idx + 25, len(self.alliances))
        current_alliances = self.alliances[start_idx:end_idx]

        select = discord.ui.Select(
            placeholder=f"🏰 選擇聯盟... (第 {self.page + 1}/{self.max_page + 1} 頁)",
            options=[
                discord.SelectOption(
                    label=f"{name[:50]}",
                    value=str(alliance_id),
                    description=f"ID: {alliance_id} | 成員: {count}",
                    emoji="🏰"
                ) for alliance_id, name, count in current_alliances
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            try:
                alliance_id = int(select.values[0])
                
                if self.context == "add":
                    modal = AddMemberModal(alliance_id)
                    await interaction.response.send_modal(modal)
                elif self.context == "remove":
                    await self.show_members_for_removal(interaction, alliance_id)
                elif self.context == "transfer":
                    await self.show_members_for_transfer(interaction, alliance_id)
                elif self.context == "view":
                    await self.show_members_for_alliance(interaction, alliance_id)
                elif self.context == "update":
                    await self.update_alliance_members(interaction, alliance_id)
                    
            except Exception as e:
                print(f"Error in select_callback: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 處理選擇時發生錯誤",
                        ephemeral=True
                    )
        
        select.callback = select_callback
        self.add_item(select)
        
        # 更新翻頁按鈕狀態
        if hasattr(self, 'prev_button'):
            self.prev_button.disabled = self.page == 0
        if hasattr(self, 'next_button'):
            self.next_button.disabled = self.page == self.max_page
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """上一頁按鈕"""
        self.page = max(0, self.page - 1)
        self.update_select_menu()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """下一頁按鈕"""
        self.page = min(self.max_page, self.page + 1)
        self.update_select_menu()
        await interaction.response.edit_message(view=self)

    async def show_members_for_alliance(self, interaction, alliance_id):
        """顯示特定聯盟的成員列表"""
        try:
            cog = interaction.client.get_cog("AllianceMemberOperations")
            if not cog:
                await interaction.response.send_message(
                    "❌ 系統錯誤",
                    ephemeral=True
                )
                return
            
            # 獲取聯盟名稱
            cog.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ?",
                (alliance_id,)
            )
            alliance_result = cog.c_alliance.fetchone()
            alliance_name = alliance_result[0] if alliance_result else f"聯盟 {alliance_id}"
            
            # 獲取成員列表
            cog.c_users.execute(
                "SELECT fid, nickname, furnace_lv FROM users WHERE alliance = ? ORDER BY furnace_lv DESC, nickname",
                (str(alliance_id),)
            )
            members = cog.c_users.fetchall()
            
            if not members:
                await interaction.response.send_message(
                    f"ℹ️ 聯盟 **{alliance_name}** 目前沒有成員",
                    ephemeral=True
                )
                return
            
            # 使用分頁視圖顯示成員
            view = MemberListPaginationView(members, alliance_name, cog)
            embed = view.create_embed()
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error showing members: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 查看成員時發生錯誤",
                        ephemeral=True
                    )
            except:
                pass
    
    async def show_members_for_removal(self, interaction, alliance_id):
        """顯示可移除的成員列表"""
        try:
            cog = interaction.client.get_cog("AllianceMemberOperations")
            if not cog:
                await interaction.response.send_message(
                    "❌ 系統錯誤",
                    ephemeral=True
                )
                return
            
            # 獲取聯盟名稱
            cog.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ?",
                (alliance_id,)
            )
            alliance_result = cog.c_alliance.fetchone()
            alliance_name = alliance_result[0] if alliance_result else f"聯盟 {alliance_id}"
            
            # 獲取成員列表
            cog.c_users.execute(
                "SELECT fid, nickname, furnace_lv FROM users WHERE alliance = ? ORDER BY furnace_lv DESC, nickname",
                (str(alliance_id),)
            )
            members = cog.c_users.fetchall()
            
            if not members:
                await interaction.response.send_message(
                    f"ℹ️ 聯盟 **{alliance_name}** 目前沒有成員",
                    ephemeral=True
                )
                return
            
            # 創建成員選擇介面
            view = MemberSelectView(members, alliance_name, alliance_id, cog, context="remove")
            embed = discord.Embed(
                title=f"➖ {alliance_name} - 選擇要移除的成員",
                description=f"共有 {len(members)} 名成員\n請選擇要移除的成員：",
                color=discord.Color.red()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error showing members for removal: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ 載入成員列表時發生錯誤",
                    ephemeral=True
                )
    
    async def show_members_for_transfer(self, interaction, alliance_id):
        """顯示可轉移的成員列表"""
        try:
            cog = interaction.client.get_cog("AllianceMemberOperations")
            if not cog:
                await interaction.response.send_message(
                    "❌ 系統錯誤",
                    ephemeral=True
                )
                return
            
            # 獲取聯盟名稱
            cog.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ?",
                (alliance_id,)
            )
            alliance_result = cog.c_alliance.fetchone()
            alliance_name = alliance_result[0] if alliance_result else f"聯盟 {alliance_id}"
            
            # 獲取成員列表
            cog.c_users.execute(
                "SELECT fid, nickname, furnace_lv FROM users WHERE alliance = ? ORDER BY furnace_lv DESC, nickname",
                (str(alliance_id),)
            )
            members = cog.c_users.fetchall()
            
            if not members:
                await interaction.response.send_message(
                    f"ℹ️ 聯盟 **{alliance_name}** 目前沒有成員",
                    ephemeral=True
                )
                return
            
            # 創建成員選擇介面
            view = MemberSelectView(members, alliance_name, alliance_id, cog, context="transfer")
            embed = discord.Embed(
                title=f"🔄 {alliance_name} - 選擇要轉移的成員",
                description=f"共有 {len(members)} 名成員\n請選擇要轉移的成員：",
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error showing members for transfer: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ 載入成員列表時發生錯誤",
                    ephemeral=True
                )
    
    async def update_alliance_members(self, interaction, alliance_id):
        """更新聯盟成員資訊"""
        try:
            cog = interaction.client.get_cog("AllianceMemberOperations")
            if not cog:
                await interaction.response.send_message(
                    "❌ 系統錯誤",
                    ephemeral=True
                )
                return
            
            # 獲取聯盟名稱
            cog.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ?",
                (alliance_id,)
            )
            alliance_result = cog.c_alliance.fetchone()
            alliance_name = alliance_result[0] if alliance_result else f"聯盟 {alliance_id}"
            
            # 獲取成員列表
            cog.c_users.execute(
                "SELECT fid, nickname, furnace_lv FROM users WHERE alliance = ? ORDER BY furnace_lv DESC, nickname",
                (str(alliance_id),)
            )
            members = cog.c_users.fetchall()
            
            if not members:
                await interaction.response.send_message(
                    f"ℹ️ 聯盟 **{alliance_name}** 目前沒有成員",
                    ephemeral=True
                )
                return
            
            # 發送處理中訊息
            embed = discord.Embed(
                title=f"🔄 更新 {alliance_name} - 成員資訊",
                description=f"正在更新 {len(members)} 名成員的資訊...\n\n**進度:** `0/{len(members)}`",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            updated_count = 0
            error_count = 0
            
            for idx, (fid, old_nickname, old_furnace_lv) in enumerate(members, 1):
                # 更新進度
                embed.description = f"正在更新 {len(members)} 名成員的資訊...\n\n**進度:** `{idx}/{len(members)}`"
                await interaction.edit_original_response(embed=embed)
                
                # 從 API 獲取最新資料
                result = await cog.login_handler.fetch_player_data(str(fid))
                
                if result['status'] == 'success':
                    data = result['data']
                    new_nickname = data.get('nickname')
                    new_furnace_lv = data.get('stove_lv', 0)
                    stove_lv_content = data.get('stove_lv_content', None)
                    kid = data.get('kid', None)
                    
                    if new_nickname:
                        # 更新資料庫
                        cog.c_users.execute(
                            "UPDATE users SET nickname = ?, furnace_lv = ?, stove_lv_content = ?, kid = ? WHERE fid = ?",
                            (new_nickname, new_furnace_lv, stove_lv_content, kid, fid)
                        )
                        cog.conn_users.commit()
                        updated_count += 1
                else:
                    error_count += 1
                
                # 添加延遲以避免 API 限制
                await asyncio.sleep(cog.login_handler.request_delay)
            
            # 完成
            embed = discord.Embed(
                title="✅ 更新完成",
                description=(
                    f"**聯盟:** {alliance_name}\n"
                    f"**總成員數:** {len(members)}\n"
                    f"**成功更新:** {updated_count}\n"
                    f"**更新失敗:** {error_count}"
                ),
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            print(f"Error updating alliance members: {e}")
            import traceback
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ 更新成員資訊時發生錯誤",
                    ephemeral=True
                )


class AddMemberModal(discord.ui.Modal):
    def __init__(self, alliance_id):
        super().__init__(title=_("add_member", "BUTTON"))
        self.alliance_id = alliance_id
        
        self.uid_input = discord.ui.TextInput(
            label=_("fid_player_id", "LABEL"),
            placeholder="多個 FID 請用逗號分隔，例如: 12345,67890,11111",
            required=True,
            min_length=1,
            max_length=500,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.uid_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            input_value = self.uid_input.value.strip()
            
            # 檢查是否存在 cog
            cog = interaction.client.get_cog("AllianceMemberOperations")
            if not cog:
                await interaction.response.send_message(
                    "❌ 系統錯誤，請重新嘗試",
                    ephemeral=True
                )
                return
            
            # 解析 FID 列表 (支援逗號分隔、換行分隔)
            fid_list = []
            if ',' in input_value:
                # 逗號分隔
                fid_list = [fid.strip() for fid in input_value.split(',') if fid.strip()]
            elif '\n' in input_value:
                # 換行分隔
                fid_list = [fid.strip() for fid in input_value.split('\n') if fid.strip()]
            else:
                # 單一 FID
                fid_list = [input_value]
            
            # 驗證所有 FID 是否為數字
            invalid_fids = [fid for fid in fid_list if not fid.isdigit()]
            if invalid_fids:
                await interaction.response.send_message(
                    f"❌ 以下 FID 格式錯誤 (必須是數字):\n{', '.join(invalid_fids[:5])}{'...' if len(invalid_fids) > 5 else ''}",
                    ephemeral=True
                )
                return
            
            # 轉換為整數
            fid_list = [int(fid) for fid in fid_list]
            total_count = len(fid_list)
            
            # 發送初始進度訊息
            embed = discord.Embed(
                title="👥 批量新增成員進度",
                description=f"正在處理 **{total_count}** 位成員...\n\n**進度:** `0/{total_count}`",
                color=discord.Color.blue()
            )
            embed.add_field(name="✅ 成功新增", value="`0`", inline=True)
            embed.add_field(name="🔄 成功轉移", value="`0`", inline=True)
            embed.add_field(name="ℹ️ 已存在", value="`0`", inline=True)
            embed.add_field(name="❌ 失敗", value="`0`", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # 初始化統計
            success_count = 0
            transfer_count = 0
            exists_count = 0
            failed_count = 0
            processed_count = 0
            
            success_list = []
            transfer_list = []
            failed_list = []
            
            # 處理每個 FID
            for fid in fid_list:
                try:
                    # 檢查是否已存在
                    existing = cog.c_users.execute(
                        "SELECT nickname, furnace_lv, alliance FROM users WHERE fid = ?",
                        (fid,)
                    ).fetchone()
                    
                    if existing:
                        nickname, furnace_lv, current_alliance = existing
                        level_display = cog.level_mapping.get(furnace_lv, str(furnace_lv)) if furnace_lv else "N/A"
                        
                        if current_alliance == str(self.alliance_id):
                            # 已在此聯盟
                            exists_count += 1
                        else:
                            # 轉移到此聯盟
                            cog.c_users.execute(
                                "UPDATE users SET alliance = ? WHERE fid = ?",
                                (str(self.alliance_id), fid)
                            )
                            cog.conn_users.commit()
                            transfer_count += 1
                            transfer_list.append(f"{nickname} ({level_display})")
                    else:
                        # 從 API 獲取玩家資料
                        result = await cog.login_handler.fetch_player_data(str(fid))
                        
                        if result['status'] == 'success':
                            data = result['data']
                            nickname = data.get('nickname')
                            furnace_lv = data.get('stove_lv', 0)
                            stove_lv_content = data.get('stove_lv_content', None)
                            kid = data.get('kid', None)
                            
                            if nickname:
                                # 新增成員
                                cog.c_users.execute(
                                    "INSERT INTO users (fid, nickname, furnace_lv, kid, stove_lv_content, alliance) VALUES (?, ?, ?, ?, ?, ?)",
                                    (fid, nickname, furnace_lv, kid, stove_lv_content, str(self.alliance_id))
                                )
                                cog.conn_users.commit()
                                
                                level_display = cog.level_mapping.get(furnace_lv, str(furnace_lv))
                                success_count += 1
                                success_list.append(f"{nickname} ({level_display})")
                            else:
                                failed_count += 1
                                failed_list.append(f"FID {fid}: 資料不完整")
                        else:
                            failed_count += 1
                            error_msg = result.get('error_message', '未知錯誤')
                            failed_list.append(f"FID {fid}: {error_msg}")
                    
                    processed_count += 1
                    
                    # 每處理 5 個更新一次進度 (或處理完成時)
                    if processed_count % 5 == 0 or processed_count == total_count:
                        embed.description = f"正在處理 **{total_count}** 位成員...\n\n**進度:** `{processed_count}/{total_count}`"
                        embed.set_field_at(0, name="✅ 成功新增", value=f"`{success_count}`", inline=True)
                        embed.set_field_at(1, name="🔄 成功轉移", value=f"`{transfer_count}`", inline=True)
                        embed.set_field_at(2, name="ℹ️ 已存在", value=f"`{exists_count}`", inline=True)
                        embed.set_field_at(3, name="❌ 失敗", value=f"`{failed_count}`", inline=True)
                        
                        await interaction.edit_original_response(embed=embed)
                    
                    # 避免 API 限制，稍微延遲
                    if processed_count < total_count:
                        await asyncio.sleep(0.5)
                        
                except Exception as e:
                    failed_count += 1
                    failed_list.append(f"FID {fid}: {str(e)}")
                    processed_count += 1
            
            # 最終結果
            embed.title = "✅ 批量新增完成"
            embed.description = f"已處理 **{total_count}** 位成員"
            embed.color = discord.Color.green()
            
            # 添加詳細列表
            if success_list:
                embed.add_field(
                    name=f"✅ 新增成功 ({len(success_list)})",
                    value="\n".join(success_list[:10]) + (f"\n... 還有 {len(success_list)-10} 位" if len(success_list) > 10 else ""),
                    inline=False
                )
            
            if transfer_list:
                embed.add_field(
                    name=f"🔄 轉移成功 ({len(transfer_list)})",
                    value="\n".join(transfer_list[:10]) + (f"\n... 還有 {len(transfer_list)-10} 位" if len(transfer_list) > 10 else ""),
                    inline=False
                )
            
            if failed_list:
                embed.add_field(
                    name=f"❌ 失敗 ({len(failed_list)})",
                    value="\n".join(failed_list[:5]) + (f"\n... 還有 {len(failed_list)-5} 個錯誤" if len(failed_list) > 5 else ""),
                    inline=False
                )
            
            await interaction.edit_original_response(embed=embed)
            
            # ✨ 新功能：為新增/轉移的成員自動兌換所有已驗證的禮品碼
            if success_count > 0 or transfer_count > 0:
                try:
                    gift_cog = interaction.client.get_cog("GiftOperations")
                    if gift_cog:
                        # 查詢所有已驗證的禮品碼
                        gift_cog.cursor.execute("""
                            SELECT giftcode 
                            FROM gift_codes 
                            WHERE validation_status = 'validated'
                        """)
                        valid_codes = [row[0] for row in gift_cog.cursor.fetchall()]
                        
                        if valid_codes:
                            # 發送提示訊息
                            redeem_embed = discord.Embed(
                                title="🎁 自動兌換禮品碼",
                                description=(
                                    f"為 **{success_count + transfer_count}** 位新成員自動兌換禮品碼...\n\n"
                                    f"📦 找到 **{len(valid_codes)}** 個已驗證的禮品碼\n"
                                    f"⏳ 正在排程兌換，請稍候..."
                                ),
                                color=discord.Color.gold()
                            )
                            await interaction.followup.send(embed=redeem_embed, ephemeral=True)
                            
                            # 為每個禮品碼排程兌換
                            for giftcode in valid_codes:
                                await gift_cog.add_to_validation_queue(
                                    giftcode=giftcode,
                                    source='新增成員自動兌換',
                                    operation_type='redemption',
                                    alliance_id=self.alliance_id,
                                    interaction=None
                                )
                                await asyncio.sleep(0.5)  # 避免過快排程
                            
                            # 更新訊息
                            redeem_embed.description = (
                                f"✅ 已為 **{success_count + transfer_count}** 位新成員排程兌換\n\n"
                                f"📦 共 **{len(valid_codes)}** 個禮品碼\n"
                                f"📝 可在日誌中查看兌換進度"
                            )
                            await interaction.followup.send(embed=redeem_embed, ephemeral=True)
                        else:
                            # 沒有禮品碼
                            no_code_embed = discord.Embed(
                                title="ℹ️ 無禮品碼需兌換",
                                description="目前沒有已驗證的禮品碼",
                                color=discord.Color.blue()
                            )
                            await interaction.followup.send(embed=no_code_embed, ephemeral=True)
                except Exception as redeem_error:
                    print(f"[AddMemberModal] 自動兌換禮品碼時發生錯誤: {redeem_error}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            import traceback
            print(f"Error in AddMemberModal: {e}")
            traceback.print_exc()
            try:
                if interaction.response.is_done():
                    await interaction.edit_original_response(
                        content=f"❌ 批量新增時發生錯誤: {str(e)}"
                    )
                else:
                    await interaction.response.send_message(
                        f"❌ 批量新增時發生錯誤: {str(e)}",
                        ephemeral=True
                    )
            except:
                pass


class MemberSelectView(discord.ui.View):
    def __init__(self, members, alliance_name, alliance_id, cog, page=0, context="remove"):
        super().__init__(timeout=300)
        self.members = members
        self.alliance_name = alliance_name
        self.alliance_id = alliance_id
        self.cog = cog
        self.page = page
        self.context = context
        self.max_page = (len(members) - 1) // 25 if members else 0
        self.update_select_menu()
    
    def update_select_menu(self):
        # 移除舊的選單
        for item in self.children[:]:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
        
        start_idx = self.page * 25
        end_idx = min(start_idx + 25, len(self.members))
        current_members = self.members[start_idx:end_idx]
        
        select = discord.ui.Select(
            placeholder=f"👤 選擇成員... (第 {self.page + 1}/{self.max_page + 1} 頁)",
            options=[
                discord.SelectOption(
                    label=f"{nickname if nickname else f'玩家 {fid}'}",
                    value=str(fid),
                    description=f"FID: {fid} | Lv: {furnace_lv if furnace_lv else 'N/A'}",
                    emoji="👤"
                ) for fid, nickname, furnace_lv in current_members
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            try:
                selected_fid = int(select.values[0])
                
                if self.context == "remove":
                    await self.handle_remove(interaction, selected_fid)
                elif self.context == "transfer":
                    await self.handle_transfer(interaction, selected_fid)
                    
            except Exception as e:
                print(f"Error in member select_callback: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 處理選擇時發生錯誤",
                        ephemeral=True
                    )
        
        select.callback = select_callback
        self.add_item(select)
        
        # 更新翻頁按鈕狀態
        if hasattr(self, 'prev_button'):
            self.prev_button.disabled = self.page == 0
        if hasattr(self, 'next_button'):
            self.next_button.disabled = self.page == self.max_page
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """上一頁按鈕"""
        self.page = max(0, self.page - 1)
        self.update_select_menu()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """下一頁按鈕"""
        self.page = min(self.max_page, self.page + 1)
        self.update_select_menu()
        await interaction.response.edit_message(view=self)
    
    async def handle_remove(self, interaction, fid):
        """處理移除成員"""
        try:
            # 獲取成員資訊
            self.cog.c_users.execute(
                "SELECT nickname FROM users WHERE fid = ?",
                (fid,)
            )
            result = self.cog.c_users.fetchone()
            member_name = result[0] if result and result[0] else f"玩家 {fid}"
            
            # 創建確認介面
            embed = discord.Embed(
                title="⚠️ 確認移除",
                description=f"確定要從 **{self.alliance_name}** 移除以下成員嗎？\n\n👤 **{member_name}**\n🆔 **FID:** {fid}",
                color=discord.Color.orange()
            )
            
            view = ConfirmView(fid, self.alliance_id, self.cog, member_name, context="remove")
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in handle_remove: {e}")
            await interaction.response.send_message(
                "❌ 處理移除時發生錯誤",
                ephemeral=True
            )
    
    async def handle_transfer(self, interaction, fid):
        """處理轉移成員"""
        try:
            # 獲取成員資訊
            self.cog.c_users.execute(
                "SELECT nickname FROM users WHERE fid = ?",
                (fid,)
            )
            result = self.cog.c_users.fetchone()
            member_name = result[0] if result and result[0] else f"玩家 {fid}"
            
            # 獲取所有聯盟（排除當前聯盟）
            alliances, _, _ = await self.cog.get_admin_alliances(
                interaction.user.id,
                interaction.guild_id
            )
            
            # 過濾掉當前聯盟並添加成員數量
            target_alliances_with_counts = []
            for alliance_id, name in alliances:
                if alliance_id != self.alliance_id:
                    # 獲取成員數量
                    self.cog.c_users.execute(
                        "SELECT COUNT(*) FROM users WHERE alliance = ?",
                        (str(alliance_id),)
                    )
                    count = self.cog.c_users.fetchone()[0]
                    target_alliances_with_counts.append((alliance_id, name, count))
            
            if not target_alliances_with_counts:
                await interaction.response.send_message(
                    "❌ 沒有其他可轉移的聯盟",
                    ephemeral=True
                )
                return
            
            # 創建目標聯盟選擇介面
            embed = discord.Embed(
                title="🔄 選擇目標聯盟",
                description=f"將 **{member_name}** (FID: {fid}) 轉移到：",
                color=discord.Color.blue()
            )
            
            view = TargetAllianceSelectView(target_alliances_with_counts, fid, self.alliance_id, self.cog, member_name)
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in handle_transfer: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ 處理轉移時發生錯誤",
                    ephemeral=True
                )


class ConfirmView(discord.ui.View):
    def __init__(self, fid, alliance_id, cog, member_name, context="remove"):
        super().__init__(timeout=60)
        self.fid = fid
        self.alliance_id = alliance_id
        self.cog = cog
        self.member_name = member_name
        self.context = context
    
    @discord.ui.button(label=_("confirm", "BUTTON"), style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # 移除成員
            self.cog.c_users.execute(
                "DELETE FROM users WHERE fid = ?",
                (self.fid,)
            )
            self.cog.conn_users.commit()
            
            embed = discord.Embed(
                title=_("remove_success", "TITLE"),
                description=_("member_removed_success", "DESCRIPTION").format(name=self.member_name, fid=self.fid),
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            print(f"Error in confirm_button: {e}")
            await interaction.response.send_message(
                _("remove_failed", "ERRORS"),
                ephemeral=True
            )
    
    @discord.ui.button(label=_("cancel", "BUTTON"), style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=_("operation_cancelled", "TITLE"),
            description=_("remove_operation_cancelled", "DESCRIPTION"),
            color=discord.Color.grey()
        )
        await interaction.response.edit_message(embed=embed, view=None)


class TargetAllianceSelectView(discord.ui.View):
    def __init__(self, alliances, fid, source_alliance_id, cog, member_name, page=0):
        super().__init__(timeout=300)
        self.alliances = alliances
        self.fid = fid
        self.source_alliance_id = source_alliance_id
        self.cog = cog
        self.member_name = member_name
        self.page = page
        self.max_page = (len(alliances) - 1) // 25 if alliances else 0
        self.update_select_menu()
    
    def update_select_menu(self):
        # 移除舊的選單
        for item in self.children[:]:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
        
        start_idx = self.page * 25
        end_idx = min(start_idx + 25, len(self.alliances))
        current_alliances = self.alliances[start_idx:end_idx]
        
        select = discord.ui.Select(
            placeholder=f"🏰 選擇目標聯盟... (第 {self.page + 1}/{self.max_page + 1} 頁)",
            options=[
                discord.SelectOption(
                    label=f"{name[:50]}",
                    value=str(alliance_id),
                    description=f"ID: {alliance_id} | 成員: {count}",
                    emoji="🏰"
                ) for alliance_id, name, count in current_alliances
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            try:
                target_alliance_id = int(select.values[0])
                print(f"[DEBUG] Transferring member {self.fid} from {self.source_alliance_id} to {target_alliance_id}")
                
                # 更新成員的聯盟
                self.cog.c_users.execute(
                    "UPDATE users SET alliance = ? WHERE fid = ?",
                    (str(target_alliance_id), self.fid)
                )
                self.cog.conn_users.commit()
                print(f"[DEBUG] Database updated successfully")
                
                # 獲取目標聯盟名稱
                self.cog.c_alliance.execute(
                    "SELECT name FROM alliance_list WHERE alliance_id = ?",
                    (target_alliance_id,)
                )
                target_alliance_name = self.cog.c_alliance.fetchone()[0]
                print(f"[DEBUG] Target alliance name: {target_alliance_name}")
                
                embed = discord.Embed(
                    title="✅ 轉移成功",
                    description=f"已成功將 **{self.member_name}** (FID: {self.fid}) 轉移到 **{target_alliance_name}**",
                    color=discord.Color.green()
                )
                await interaction.response.edit_message(embed=embed, view=None)
                
            except Exception as e:
                print(f"[ERROR] Error in target alliance select: {e}")
                import traceback
                traceback.print_exc()
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            f"❌ 轉移失敗: {str(e)}",
                            ephemeral=True
                        )
                    else:
                        await interaction.followup.send(
                            f"❌ 轉移失敗: {str(e)}",
                            ephemeral=True
                        )
                except Exception as inner_e:
                    print(f"[ERROR] Failed to send error message: {inner_e}")
        
        select.callback = select_callback
        self.add_item(select)


class MemberListPaginationView(discord.ui.View):
    """成員列表分頁視圖"""
    def __init__(self, members, alliance_name, cog, page=0):
        super().__init__(timeout=300)
        self.members = members
        self.alliance_name = alliance_name
        self.cog = cog
        self.page = page
        self.items_per_page = 15
        self.max_page = (len(members) - 1) // self.items_per_page if members else 0
        self.update_buttons()
    
    def create_embed(self):
        """創建當前頁的 embed"""
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.members))
        current_members = self.members[start_idx:end_idx]
        
        # 創建成員列表
        member_list = []
        for idx, (fid, nickname, furnace_lv) in enumerate(current_members, start=start_idx + 1):
            name = nickname if nickname else f"玩家 {fid}"
            level_display = self.cog.level_mapping.get(furnace_lv, str(furnace_lv)) if furnace_lv else "N/A"
            member_list.append(f"**{idx:02d}.** 👤 {name}\n└ 🔥 `{level_display}` | 🆔 `{fid}`\n")
        
        embed = discord.Embed(
            title=f"📋 {self.alliance_name} - 成員列表",
            description="".join(member_list) if member_list else "沒有成員",
            color=discord.Color.blue()
        )
        
        if self.max_page > 0:
            embed.set_footer(text=f"第 {self.page + 1}/{self.max_page + 1} 頁 | 總共 {len(self.members)} 名成員")
        else:
            embed.set_footer(text=f"總共 {len(self.members)} 名成員")
        
        return embed
    
    def update_buttons(self):
        """更新按鈕狀態"""
        # 清除舊按鈕
        self.clear_items()
        
        # 只有當有多頁時才顯示翻頁按鈕
        if self.max_page > 0:
            prev_button = discord.ui.Button(
                label="◀️",
                style=discord.ButtonStyle.secondary,
                disabled=(self.page == 0)
            )
            prev_button.callback = self.prev_page
            self.add_item(prev_button)
            
            next_button = discord.ui.Button(
                label="▶️",
                style=discord.ButtonStyle.secondary,
                disabled=(self.page == self.max_page)
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def prev_page(self, interaction: discord.Interaction):
        """上一頁"""
        self.page = max(0, self.page - 1)
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        """下一頁"""
        self.page = min(self.max_page, self.page + 1)
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot):
    await bot.add_cog(AllianceMemberOperations(bot))

