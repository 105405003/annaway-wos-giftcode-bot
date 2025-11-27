import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from i18n_manager import i18n, _
from utils.permissions import requires_annaway_role, check_permission, check_guild_context

class PermissionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 連接資料庫
        self.conn_settings = sqlite3.connect('db/settings.sqlite')
        self.c_settings = self.conn_settings.cursor()
        
        self.conn_alliance = sqlite3.connect('db/alliance.sqlite')
        self.c_alliance = self.conn_alliance.cursor()
        
        self._ensure_tables()
    
    def _ensure_tables(self):
        """確保資料庫表存在"""
        try:
            self.c_settings.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY,
                    is_initial INTEGER DEFAULT 0
                )
            """)
            
            self.c_settings.execute("""
                CREATE TABLE IF NOT EXISTS adminserver (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin INTEGER NOT NULL,
                    alliances_id INTEGER NOT NULL,
                    FOREIGN KEY (admin) REFERENCES admin(id),
                    UNIQUE(admin, alliances_id)
                )
            """)
            
            self.conn_settings.commit()
        except Exception as e:
            print(f"Error ensuring tables: {e}")
    
    async def check_is_global_admin(self, user_id: int) -> bool:
        """檢查用戶是否為全域管理員"""
        try:
            self.c_settings.execute(
                "SELECT is_initial FROM admin WHERE id = ?",
                (user_id,)
            )
            result = self.c_settings.fetchone()
            return result and result[0] == 1
        except Exception as e:
            print(f"Error checking global admin: {e}")
            return False
    
    async def show_permission_management_menu(self, interaction: discord.Interaction):
        """顯示權限管理選單"""
        try:
            # 檢查是否為全域管理員
            if not await self.check_is_global_admin(interaction.user.id):
                await interaction.response.send_message(
                    "❌ 只有全域管理員可以使用權限管理功能",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="⚙️ 權限管理",
                description=(
                    "管理 Manager 的聯盟操作權限\n\n"
                    "**可用操作**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "👤 **指定 Manager 權限** - 設定 Manager 可以操作哪些聯盟\n"
                    "📋 **查看權限列表** - 查看所有 Manager 的聯盟權限\n"
                    "🗑️ **移除權限** - 移除 Manager 的特定聯盟權限\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "**說明：**\n"
                    "• Manager 預設可以操作其所在伺服器的所有聯盟\n"
                    "• 透過此功能可以讓 Manager 操作其他伺服器的特定聯盟\n"
                    "• 全域管理員（Admin）不受限制"
                ),
                color=discord.Color.gold()
            )
            
            view = PermissionManagementView(self)
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in show_permission_management_menu: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 載入權限管理選單時發生錯誤",
                ephemeral=True
            )
    
    async def show_assign_permission_menu(self, interaction: discord.Interaction):
        """顯示指定權限選單"""
        try:
            # ✨ HOTFIX: 直接從 Discord 讀取 Annaway_Manager 身分組成員
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message(
                    "❌ 此命令只能在伺服器中使用",
                    ephemeral=True
                )
                return
            
            # 查找 Annaway_Manager 身分組
            manager_role = discord.utils.get(guild.roles, name="Annaway_Manager")
            if not manager_role or not manager_role.members:
                await interaction.response.send_message(
                    "ℹ️ 伺服器中沒有 Annaway_Manager 身分組的成員",
                    ephemeral=True
                )
                return
            
            # 將 Discord members 轉換為 (id, name) 元組列表
            managers = [(member.id, member.display_name) for member in manager_role.members]
            
            print(f"[權限管理] 找到 {len(managers)} 位 Manager")
            for manager_id, manager_name in managers:
                print(f"[權限管理] - {manager_name} (ID: {manager_id})")
            
            # 創建用戶選擇選單
            view = ManagerSelectView(managers, self, context="assign")
            embed = discord.Embed(
                title="👤 選擇 Manager",
                description="請選擇要設定權限的 Manager：",
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in show_assign_permission_menu: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 載入選單時發生錯誤",
                ephemeral=True
            )
    
    async def show_view_permissions_list(self, interaction: discord.Interaction):
        """顯示權限列表"""
        try:
            # 獲取所有權限設定
            self.c_settings.execute("""
                SELECT DISTINCT admin FROM adminserver
            """)
            admins_with_permissions = self.c_settings.fetchall()
            
            if not admins_with_permissions:
                await interaction.response.send_message(
                    "ℹ️ 目前沒有設定任何特殊權限",
                    ephemeral=True
                )
                return
            
            # 構建權限列表
            permissions_text = []
            
            for (admin_id,) in admins_with_permissions:
                try:
                    user = await self.bot.fetch_user(admin_id)
                    user_name = f"{user.name}"
                except:
                    user_name = f"用戶 {admin_id}"
                
                # 獲取該用戶的聯盟權限
                self.c_settings.execute("""
                    SELECT alliances_id FROM adminserver WHERE admin = ?
                """, (admin_id,))
                alliance_ids = [row[0] for row in self.c_settings.fetchall()]
                
                if alliance_ids:
                    # 獲取聯盟名稱
                    alliance_names = []
                    for aid in alliance_ids:
                        self.c_alliance.execute(
                            "SELECT name FROM alliance_list WHERE alliance_id = ?",
                            (aid,)
                        )
                        result = self.c_alliance.fetchone()
                        if result:
                            alliance_names.append(f"{result[0]} (ID: {aid})")
                    
                    permissions_text.append(
                        f"**{user_name}** (`{admin_id}`)\n"
                        f"└ 可操作聯盟: {len(alliance_names)}\n"
                        f"   {', '.join(alliance_names[:3])}"
                        f"{' ...' if len(alliance_names) > 3 else ''}\n"
                    )
            
            embed = discord.Embed(
                title="📋 Manager 聯盟權限列表",
                description="\n".join(permissions_text) if permissions_text else "無權限設定",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToPermissionView(self))
            
        except Exception as e:
            print(f"Error in show_view_permissions_list: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 載入權限列表時發生錯誤",
                ephemeral=True
            )
    
    async def show_remove_permission_menu(self, interaction: discord.Interaction):
        """顯示移除權限選單"""
        try:
            # 獲取有權限設定的管理員
            self.c_settings.execute("""
                SELECT DISTINCT admin FROM adminserver
            """)
            managers = [(row[0], 0) for row in self.c_settings.fetchall()]
            
            if not managers:
                await interaction.response.send_message(
                    "ℹ️ 目前沒有設定任何特殊權限",
                    ephemeral=True
                )
                return
            
            view = ManagerSelectView(managers, self, context="remove")
            embed = discord.Embed(
                title="🗑️ 選擇 Manager",
                description="請選擇要移除權限的 Manager：",
                color=discord.Color.red()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in show_remove_permission_menu: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 載入選單時發生錯誤",
                ephemeral=True
            )
    
    async def assign_alliance_to_manager(self, interaction, manager_id, alliance_id):
        """指定聯盟給 Manager"""
        try:
            # 檢查是否已存在
            self.c_settings.execute("""
                SELECT id FROM adminserver WHERE admin = ? AND alliances_id = ?
            """, (manager_id, alliance_id))
            
            if self.c_settings.fetchone():
                await interaction.response.send_message(
                    "ℹ️ 該 Manager 已經擁有此聯盟的權限",
                    ephemeral=True
                )
                return
            
            # 添加權限
            self.c_settings.execute("""
                INSERT INTO adminserver (admin, alliances_id) VALUES (?, ?)
            """, (manager_id, alliance_id))
            self.conn_settings.commit()
            
            # 獲取聯盟名稱
            self.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ?",
                (alliance_id,)
            )
            alliance_name = self.c_alliance.fetchone()[0]
            
            # 獲取用戶名稱
            try:
                user = await self.bot.fetch_user(manager_id)
                user_name = user.name
            except:
                user_name = f"用戶 {manager_id}"
            
            embed = discord.Embed(
                title="✅ 權限設定成功",
                description=(
                    f"**Manager:** {user_name} (`{manager_id}`)\n"
                    f"**聯盟:** {alliance_name} (ID: {alliance_id})\n\n"
                    f"該 Manager 現在可以操作此聯盟的成員和禮品碼功能。"
                ),
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToPermissionView(self))
            
        except Exception as e:
            print(f"Error assigning alliance: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 設定權限時發生錯誤",
                ephemeral=True
            )
    
    async def remove_alliance_from_manager(self, interaction, manager_id, alliance_id):
        """移除 Manager 的聯盟權限"""
        try:
            # 移除權限
            self.c_settings.execute("""
                DELETE FROM adminserver WHERE admin = ? AND alliances_id = ?
            """, (manager_id, alliance_id))
            self.conn_settings.commit()
            
            if self.c_settings.rowcount == 0:
                await interaction.response.send_message(
                    "ℹ️ 該權限不存在或已被移除",
                    ephemeral=True
                )
                return
            
            # 獲取聯盟名稱 (guild-aware)
            guild_id = interaction.guild.id if interaction.guild else None
            if guild_id:
                self.c_alliance.execute(
                    "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?",
                    (alliance_id, guild_id)
                )
            else:
                self.c_alliance.execute(
                    "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = -1",
                    (alliance_id,)
                )
            result = self.c_alliance.fetchone()
            alliance_name = result[0] if result else f"聯盟 {alliance_id}"
            
            # 獲取用戶名稱
            try:
                user = await self.bot.fetch_user(manager_id)
                user_name = user.name
            except:
                user_name = f"用戶 {manager_id}"
            
            embed = discord.Embed(
                title="✅ 權限已移除",
                description=(
                    f"**Manager:** {user_name} (`{manager_id}`)\n"
                    f"**聯盟:** {alliance_name} (ID: {alliance_id})\n\n"
                    f"該 Manager 已無法操作此聯盟。"
                ),
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToPermissionView(self))
            
        except Exception as e:
            print(f"Error removing alliance: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 移除權限時發生錯誤",
                ephemeral=True
            )


class PermissionManagementView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @discord.ui.button(label="指定 Manager 權限", emoji="👤", style=discord.ButtonStyle.success, row=0)
    async def assign_permission_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_permission(interaction, admin_only=True):
            return
        await self.cog.show_assign_permission_menu(interaction)
    
    @discord.ui.button(label="查看權限列表", emoji="📋", style=discord.ButtonStyle.primary, row=0)
    async def view_permissions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_permission(interaction, admin_only=True):
            return
        await self.cog.show_view_permissions_list(interaction)
    
    @discord.ui.button(label="移除權限", emoji="🗑️", style=discord.ButtonStyle.danger, row=1)
    async def remove_permission_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_permission(interaction, admin_only=True):
            return
        await self.cog.show_remove_permission_menu(interaction)
    
    @discord.ui.button(label="主選單", emoji="🏠", style=discord.ButtonStyle.secondary, row=1)
    async def main_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            alliance_cog = self.cog.bot.get_cog("Alliance")
            if alliance_cog:
                await alliance_cog._show_settings_menu(interaction, from_button=True)
        except Exception as e:
            if not any(error_code in str(e) for error_code in ["10062", "40060", "InteractionResponded"]):
                print(f"Error in main_menu_button: {e}")
            pass


class ManagerSelectView(discord.ui.View):
    def __init__(self, managers, cog, page=0, context="assign"):
        super().__init__(timeout=300)
        self.managers = managers
        self.cog = cog
        self.page = page
        self.context = context
        self.max_page = (len(managers) - 1) // 25 if managers else 0
        self.update_select_menu()
    
    def update_select_menu(self):
        for item in self.children[:]:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
        
        start_idx = self.page * 25
        end_idx = min(start_idx + 25, len(self.managers))
        current_managers = self.managers[start_idx:end_idx]
        
        options = []
        for manager_id, _ in current_managers:
            try:
                # 同步獲取用戶資訊（在 View 初始化時）
                options.append(
                    discord.SelectOption(
                        label=f"Manager ID: {manager_id}",
                        value=str(manager_id),
                        description=f"用戶 ID: {manager_id}",
                        emoji="👤"
                    )
                )
            except:
                options.append(
                    discord.SelectOption(
                        label=f"Manager ID: {manager_id}",
                        value=str(manager_id),
                        description=f"用戶 ID: {manager_id}",
                        emoji="👤"
                    )
                )
        
        select = discord.ui.Select(
            placeholder=f"👤 選擇 Manager... (第 {self.page + 1}/{self.max_page + 1} 頁)",
            options=options
        )
        
        async def select_callback(interaction: discord.Interaction):
            # Admin-only permission check
            if not await check_permission(interaction, admin_only=True):
                return
            
            try:
                manager_id = int(select.values[0])
                
                if self.context == "assign":
                    await self.show_alliance_selection(interaction, manager_id)
                elif self.context == "remove":
                    await self.show_alliance_removal_selection(interaction, manager_id)
                    
            except Exception as e:
                print(f"Error in select_callback: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 處理選擇時發生錯誤",
                        ephemeral=True
                    )
        
        select.callback = select_callback
        self.add_item(select)
    
    async def show_alliance_selection(self, interaction, manager_id):
        """顯示聯盟選擇（用於指定權限）"""
        try:
            # ✨ A1 FIX: 只顯示當前 guild 的聯盟
            guild_id = interaction.guild.id if interaction.guild else None
            if guild_id:
                self.cog.c_alliance.execute(
                    "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
                    (guild_id,)
                )
            else:
                self.cog.c_alliance.execute("SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = -1 ORDER BY name")
            alliances = self.cog.c_alliance.fetchall()
            
            if not alliances:
                await interaction.response.send_message(
                    "ℹ️ 目前沒有聯盟",
                    ephemeral=True
                )
                return
            
            view = AllianceSelectForPermissionView(alliances, self.cog, manager_id, context="assign")
            embed = discord.Embed(
                title="🏰 選擇聯盟",
                description=f"請選擇要授權給 Manager (`{manager_id}`) 的聯盟：",
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error showing alliance selection: {e}")
            await interaction.response.send_message(
                "❌ 載入聯盟列表時發生錯誤",
                ephemeral=True
            )
    
    async def show_alliance_removal_selection(self, interaction, manager_id):
        """顯示聯盟選擇（用於移除權限）"""
        try:
            # 獲取該 Manager 有權限的聯盟
            self.cog.c_settings.execute("""
                SELECT alliances_id FROM adminserver WHERE admin = ?
            """, (manager_id,))
            alliance_ids = [row[0] for row in self.cog.c_settings.fetchall()]
            
            if not alliance_ids:
                await interaction.response.send_message(
                    "ℹ️ 該 Manager 沒有任何特殊權限設定",
                    ephemeral=True
                )
                return
            
            # 獲取聯盟名稱
            alliances = []
            for aid in alliance_ids:
                self.cog.c_alliance.execute(
                    "SELECT alliance_id, name FROM alliance_list WHERE alliance_id = ?",
                    (aid,)
                )
                result = self.cog.c_alliance.fetchone()
                if result:
                    alliances.append(result)
            
            view = AllianceSelectForPermissionView(alliances, self.cog, manager_id, context="remove")
            embed = discord.Embed(
                title="🗑️ 選擇要移除的聯盟",
                description=f"請選擇要從 Manager (`{manager_id}`) 移除的聯盟權限：",
                color=discord.Color.red()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error showing alliance removal selection: {e}")
            await interaction.response.send_message(
                "❌ 載入聯盟列表時發生錯誤",
                ephemeral=True
            )


class AllianceSelectForPermissionView(discord.ui.View):
    def __init__(self, alliances, cog, manager_id, page=0, context="assign"):
        super().__init__(timeout=300)
        self.alliances = alliances
        self.cog = cog
        self.manager_id = manager_id
        self.page = page
        self.context = context
        self.max_page = (len(alliances) - 1) // 25 if alliances else 0
        self.update_select_menu()
    
    def update_select_menu(self):
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
                    description=f"ID: {alliance_id}",
                    emoji="🏰"
                ) for alliance_id, name in current_alliances
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            # Admin-only permission check
            if not await check_permission(interaction, admin_only=True):
                return
            
            try:
                alliance_id = int(select.values[0])
                
                if self.context == "assign":
                    await self.cog.assign_alliance_to_manager(interaction, self.manager_id, alliance_id)
                elif self.context == "remove":
                    await self.cog.remove_alliance_from_manager(interaction, self.manager_id, alliance_id)
                    
            except Exception as e:
                print(f"Error in select_callback: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 處理選擇時發生錯誤",
                        ephemeral=True
                    )
        
        select.callback = select_callback
        self.add_item(select)


class BackToPermissionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @discord.ui.button(label="返回權限管理", emoji="⚙️", style=discord.ButtonStyle.primary, row=0)
    async def back_to_permission_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_permission(interaction, admin_only=True):
            return
        await self.cog.show_permission_management_menu(interaction)
    
    @discord.ui.button(label="主選單", emoji="🏠", style=discord.ButtonStyle.secondary, row=0)
    async def main_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            alliance_cog = self.cog.bot.get_cog("Alliance")
            if alliance_cog:
                await alliance_cog._show_settings_menu(interaction, from_button=True)
        except Exception as e:
            if not any(error_code in str(e) for error_code in ["10062", "40060", "InteractionResponded"]):
                print(f"Error in main_menu_button: {e}")
            pass


async def setup(bot):
    await bot.add_cog(PermissionManagement(bot))

