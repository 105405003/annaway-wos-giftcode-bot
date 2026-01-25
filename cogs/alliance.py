import discord
from discord import app_commands
from discord.ext import commands
import sqlite3  
import asyncio
from datetime import datetime
from i18n_manager import i18n, _
from permission_manager import permission_manager, PermissionLevel
from utils.permissions import (
    requires_annaway_role,
    requires_annaway_role_button,
    check_permission,
    check_guild_context,
)

class AllianceModal(discord.ui.Modal):
    def __init__(self, title: str, default_name: str = "", default_interval: str = "0"):
        super().__init__(title=title)
        
        self.name = discord.ui.TextInput(
            label=_("alliance_name", "LABEL"),
            placeholder=_("enter_alliance_name", "PLACEHOLDER"),
            default=default_name,
            required=True
        )
        self.add_item(self.name)
        
        self.interval = discord.ui.TextInput(
            label=_("control_interval_minutes", "LABEL"),
            placeholder=_("enter_interval_or_zero", "PLACEHOLDER"),
            default=default_interval,
            required=True
        )
        self.add_item(self.interval)

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        
    async def wait(self):
        # Compatibility method for older code
        pass

class Alliance(commands.Cog):
    def __init__(self, bot, conn):
        self.bot = bot
        self.conn = conn
        self.c = self.conn.cursor()
        
        self.conn_users = sqlite3.connect('db/users.sqlite')
        self.c_users = self.conn_users.cursor()
        
        self.conn_settings = sqlite3.connect('db/settings.sqlite')
        self.c_settings = self.conn_settings.cursor()
        
        self.conn_giftcode = sqlite3.connect('db/giftcode.sqlite')
        self.c_giftcode = self.conn_giftcode.cursor()

        self._create_table()
        self._check_and_add_column()

    def _create_table(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS alliance_list (
                alliance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                discord_server_id INTEGER
            )
        """)
        self.conn.commit()

    def _check_and_add_column(self):
        self.c.execute("PRAGMA table_info(alliance_list)")
        columns = [info[1] for info in self.c.fetchall()]
        if "discord_server_id" not in columns:
            self.c.execute("ALTER TABLE alliance_list ADD COLUMN discord_server_id INTEGER")
            self.conn.commit()

    @requires_annaway_role()
    async def view_alliances(self, interaction: discord.Interaction):
        
        if interaction.guild is None:
            await interaction.response.send_message(_("command_server_only", "ERRORS"), ephemeral=True)
            return

        # Permission already checked by @requires_annaway_role decorator
        user_id = interaction.user.id
        self.c_settings.execute("SELECT id, is_initial FROM admin WHERE id = ?", (user_id,))
        admin = self.c_settings.fetchone()
        is_initial = admin[1] if admin else 0
        guild_id = interaction.guild.id

        try:
            # ✨ A1 FIX: 所有用戶（包括 global admin）都只能看到當前 guild 的聯盟
            query = """
                SELECT a.alliance_id, a.name, COALESCE(s.interval, 0) as interval
                FROM alliance_list a
                LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
                WHERE a.discord_server_id = ?
                ORDER BY a.alliance_id ASC
            """
            self.c.execute(query, (guild_id,))

            alliances = self.c.fetchall()

            alliance_list = ""
            for alliance_id, name, interval in alliances:
                
                self.c_users.execute("SELECT COUNT(*) FROM users WHERE alliance = ?", (alliance_id,))
                member_count = self.c_users.fetchone()[0]
                
                interval_text = f"{interval} minutes" if interval > 0 else "No automatic control"
                alliance_list += f"🛡️ **{alliance_id}: {name}**\n👥 Members: {member_count}\n⏱️ Control Interval: {interval_text}\n\n"

            if not alliance_list:
                alliance_list = "No alliances found."

            embed = discord.Embed(
                title="Existing Alliances",
                description=alliance_list,
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while fetching alliances.", 
                ephemeral=True
            )

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str):
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
        ][:25]

    @app_commands.command(name="settings", description=_("open_settings_menu", "SETTINGS"))
    @requires_annaway_role()
    async def settings(self, interaction: discord.Interaction):
        """Slash command entry point for settings"""
        await self._show_settings_menu(interaction, from_button=False)
    
    async def _show_settings_menu(self, interaction: discord.Interaction, from_button: bool = False):
        """Internal method to show settings menu - handles both slash command and button interactions"""
        try:
            # 機器人不需要 manage_guild 權限，只需要基本的發送訊息權限
            # 權限控制已透過 Annaway_Admin/Manager 角色實現
            
            # 確保 interaction.user 是 Member 類型（在伺服器中）
            member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(interaction.user.id) if interaction.guild else interaction.user
            
            # 調試輸出
            print(f"[權限調試] 用戶: {member.display_name if hasattr(member, 'display_name') else member.name}")
            print(f"[權限調試] 類型: {type(member)}")
            if isinstance(member, discord.Member):
                print(f"[權限調試] 身分組: {[role.name for role in member.roles]}")
            
            # 檢查用戶權限等級
            user_permission_level = permission_manager.get_user_permission_level(member)
            
            # 根據權限等級顯示相應的功能
            available_functions = permission_manager.get_available_functions(member)
            
            # 權限等級名稱
            level_name = permission_manager.get_permission_level_name(user_permission_level)
            
            print(f"[權限調試] 權限等級: {level_name}")
            print(f"[權限調試] settings_access: {permission_manager.has_permission(member, 'settings_access')}")
            
            # 檢查用戶是否有 settings_access 權限
            if not permission_manager.has_permission(member, "settings_access"):
                await interaction.response.send_message(
                    f"{_('no_permission_command', 'ERRORS')}\n"
                    f"{_('your_permission_level', 'LABEL').format(level=level_name)}\n"
                    f"{_('available_commands', 'LABEL')}",
                    ephemeral=True
                )
                return

            # 根據權限等級構建描述
            description_parts = [
                f"{_('please_select_category', 'MENU')}\n",
                f"**您的權限等級:** {level_name}\n",
                f"**{_('menu_categories', 'SETTINGS')}**\n",
                f"{_('separator', 'MENU')}\n"
            ]
            
            # 根據權限添加功能說明
            if permission_manager.has_permission(member, "alliance_management"):
                description_parts.append(
                    f"🏰 **{_('alliance_operations', 'MENU')}**\n"
                    f"└ {_('manage_alliances_settings', 'MENU')}\n\n"
                )
            
            if permission_manager.has_permission(member, "member_management"):
                description_parts.append(
                    f"👥 **{_('alliance_member_operations', 'MENU')}**\n"
                    f"└ {_('add_remove_view_members', 'MENU')}\n\n"
                )
            
            
            if permission_manager.has_permission(member, "gift_code_management"):
                description_parts.append(
                    f"🎁 **{_('gift_code_operations', 'MENU')}**\n"
                    f"└ {_('manage_gift_codes_rewards', 'MENU')}\n\n"
                )
            
            description_parts.append(
                f"📜 **{_('alliance_history', 'MENU')}**\n"
                f"└ {_('view_alliance_changes_history', 'MENU')}\n\n"
            )
            
            if permission_manager.has_permission(member, "statistics_view"):
                description_parts.append(
                    f"🔧 **{_('other_features', 'MENU')}**\n"
                    f"└ {_('access_other_features', 'MENU')}\n\n"
                )
            
            # 全域管理員才能看到權限管理
            if permission_manager.has_permission(member, "permission_management"):
                description_parts.append(
                    f"⚙️ **權限管理**\n"
                    f"└ 設定 Manager 的聯盟操作權限\n"
                )
            
            description_parts.append(f"{_('separator', 'MENU')}")

            embed = discord.Embed(
                title=f"⚙️ {_('settings_menu', 'SETTINGS')}",
                description="".join(description_parts),
                color=discord.Color.blue()
            )
            
            view = discord.ui.View(timeout=None)  # 設置為持久化 View
            button_count = 0  # 用於調試
            
            # 收集所有要添加的按鈕
            buttons_to_add = []
            
            if permission_manager.has_permission(member, "alliance_management"):
                buttons_to_add.append({
                    "label": _("alliance_operations", "BUTTON"),
                    "emoji": "🏰",
                    "style": discord.ButtonStyle.primary,
                    "custom_id": "alliance_operations"
                })
            
            if permission_manager.has_permission(member, "member_management"):
                buttons_to_add.append({
                    "label": _("member_operations", "BUTTON"),
                    "emoji": "👥",
                    "style": discord.ButtonStyle.primary,
                    "custom_id": "member_operations"
                })
            
            if permission_manager.has_permission(member, "gift_code_management"):
                buttons_to_add.append({
                    "label": _("gift_code_operations", "BUTTON"),
                    "emoji": "🎁",
                    "style": discord.ButtonStyle.primary,
                    "custom_id": "gift_code_operations"
                })
            
            # 聯盟歷史對所有管理員開放
            buttons_to_add.append({
                "label": _("alliance_history", "BUTTON"),
                "emoji": "📜",
                "style": discord.ButtonStyle.primary,
                "custom_id": "alliance_history"
            })
            
            if permission_manager.has_permission(member, "statistics_view"):
                buttons_to_add.append({
                    "label": _("other_features", "BUTTON"),
                    "emoji": "🔧",
                    "style": discord.ButtonStyle.primary,
                    "custom_id": "other_features"
                })
            
            # 權限管理按鈕（僅全域管理員）
            if permission_manager.has_permission(member, "permission_management"):
                buttons_to_add.append({
                    "label": _("permission_management", "BUTTON"),
                    "emoji": "⚙️",
                    "style": discord.ButtonStyle.danger,
                    "custom_id": "permission_management"
                })
            
            # 添加按鈕到 view（每行最多 5 個，分配到不同行）
            for idx, btn_data in enumerate(buttons_to_add):
                row = idx // 5  # 每 5 個按鈕換一行
                view.add_item(discord.ui.Button(
                    label=btn_data["label"],
                    emoji=btn_data["emoji"],
                    style=btn_data["style"],
                    custom_id=btn_data["custom_id"],
                    row=row
                ))
                button_count += 1
                print(f"[DEBUG] 按鈕 {button_count}: {btn_data['label']}, row={row}")
            
            print(f"[DEBUG] 主選單按鈕數量: {button_count}, from_button: {from_button}")
            
            # 調試：檢查 View 中的實際按鈕
            print(f"[DEBUG] View 中的組件數量: {len(view.children)}")
            for idx, child in enumerate(view.children):
                if isinstance(child, discord.ui.Button):
                    print(f"[DEBUG] 組件 {idx}: label='{child.label}', custom_id='{child.custom_id}', row={child.row}")

            # 使用 try-except 來處理所有可能的響應方式
            try:
                if from_button:
                    # 來自按鈕 - 優先嘗試 edit_message
                    print(f"[DEBUG] 嘗試 edit_message...")
                    await interaction.response.edit_message(embed=embed, view=view)
                    print(f"[DEBUG] edit_message 成功")
                else:
                    # 來自 slash command - 使用 send_message
                    print(f"[DEBUG] 嘗試 send_message...")
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                    print(f"[DEBUG] send_message 成功")
            except (discord.errors.InteractionResponded, discord.errors.HTTPException) as e:
                print(f"[DEBUG] 第一次嘗試失敗: {e}")
                # 如果響應失敗，嘗試使用 edit_original_response
                try:
                    print(f"[DEBUG] 嘗試 edit_original_response...")
                    await interaction.edit_original_response(embed=embed, view=view)
                    print(f"[DEBUG] edit_original_response 成功")
                except Exception as e2:
                    print(f"[DEBUG] edit_original_response 失敗: {e2}")
                    # 如果還是失敗，使用 followup
                    try:
                        print(f"[DEBUG] 嘗試 followup.send...")
                        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                        print(f"[DEBUG] followup.send 成功")
                    except Exception as e3:
                        print(f"[DEBUG] followup.send 失敗: {e3}")
                        pass  # 實在沒辦法了，放棄

        except Exception as e:
            # 只記錄非預期的錯誤
            if not any(error_code in str(e) for error_code in ["10062", "40060", "InteractionResponded"]):
                import traceback
                print(f"Settings command error: {e}")
                traceback.print_exc()
            # 嘗試發送錯誤訊息
            error_message = "An error occurred while processing your request."
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(error_message, ephemeral=True)
                else:
                    await interaction.followup.send(error_message, ephemeral=True)
            except:
                pass  # 靜默失敗

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """監聽頻道中的禮品碼訊息"""
        try:
            # 忽略機器人自己發送的訊息
            if message.author.bot:
                return
            
            # 檢查是否設定在全域禮品碼頻道
            self.c_settings.execute("SELECT global_gift_code_channel FROM botsettings WHERE id = 1")
            result = self.c_settings.fetchone()
            
            if not result or not result[0]:
                return  # 沒有設定全域禮品碼頻道
            
            global_channel_id = result[0]
            
            # 檢查是否在指定的全域頻道中
            if message.channel.id != global_channel_id:
                return
            
            # 檢查訊息是否包含 "Code: " 格式
            content = message.content.strip()
            if not content.startswith("Code:"):
                return
            
            # 提取禮品碼
            code = content[5:].strip()  # 移除 "Code:" 並去除空白
            if not code:
                return
            
            print(f"[全域監聽器] 檢測到禮品碼: {code} 在頻道 {message.channel.name}")
            
            # 使用 gift_operations 的驗證佇列
            gift_cog = self.bot.get_cog('GiftOperations')
            if not gift_cog:
                print("[全域監聽器] GiftOperations cog 未找到")
                return
            
            # 將禮品碼加入驗證佇列
            # 使用 'global' 作為來源標記
            await gift_cog.add_to_validation_queue(
                giftcode=code,
                source='global_channel',
                message=message,
                channel=message.channel,
                operation_type='automatic',
                alliance_id=None,  # 全域禮品碼適用於所有聯盟
                interaction=None
            )
            
            print(f"[全域監聽器] 禮品碼 {code} 已加入驗證佇列")
            
            # 發送確認訊息
            embed = discord.Embed(
                title="🎁 全域禮品碼檢測",
                description=(
                    f"檢測到禮品碼: **{code}**\n\n"
                    f"🔍 **狀態**: 已加入驗證佇列\n"
                    f"⏰ **檢測時間**: <t:{int(discord.utils.utcnow().timestamp())}:R>\n\n"
                    f"📋 **流程**:\n"
                    f"1️⃣ 驗證禮品碼有效性\n"
                    f"2️⃣ 為所有已啟用的聯盟兌換\n"
                    f"3️⃣ 回報兌換結果\n\n"
                    f"⌛ 請稍候，處理中..."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"來源: {message.author.display_name} | 全域禮品碼頻道")
            
            try:
                await message.reply(embed=embed)
            except Exception as e:
                print(f"[全域監聽器] Error sending confirmation: {e}")
            
        except Exception as e:
            print(f"Error in on_message: {e}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")
            
            # 計算 is_global_admin（僅用於按鈕 disabled 狀態）
            user_id = interaction.user.id
            self.c_settings.execute("SELECT id, is_initial FROM admin WHERE id = ?", (user_id,))
            admin_row = self.c_settings.fetchone()
            is_global_admin = bool(admin_row and admin_row[1] == 1)
            
            # 定義權限等級映射
            admin_only_ids = {
                "add_alliance",
                "edit_alliance", 
                "delete_alliance",
                "permission_management",
            }
            
            manager_ids = {
                "alliance_operations",
                "member_operations",
                "gift_code_operations",
                "alliance_history",
                "other_features",
                "check_alliance",
                "view_alliances",
                "main_menu",
            }
            
            # 統一權限檢查
            if custom_id in admin_only_ids:
                if not await check_permission(interaction, admin_only=True):
                    return
            elif custom_id in manager_ids:
                if not await check_permission(interaction, admin_only=False):
                    return
            
            # Defer immediately after permission check to prevent timeout
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            
            try:
                if custom_id == "alliance_operations":
                    embed = discord.Embed(
                        title=_("alliance_operations", "MENU"),
                        description=(
                            f"{_('please_select_operation', 'ALLIANCE')}\n\n"
                            f"**{_('available_operations', 'ALLIANCE')}**\n"
                            f"{_('separator', 'ALLIANCE')}\n"
                            f"➕ **{_('add_alliance', 'ALLIANCE')}**\n"
                            f"└ {_('create_new_alliance', 'ALLIANCE')}\n\n"
                            f"✏️ **{_('edit_alliance', 'ALLIANCE')}**\n"
                            f"└ {_('modify_alliance_settings', 'ALLIANCE')}\n\n"
                            f"🗑️ **{_('delete_alliance', 'ALLIANCE')}**\n"
                            f"└ {_('remove_existing_alliance', 'ALLIANCE')}\n\n"
                            f"👀 **{_('view_alliances', 'ALLIANCE')}**\n"
                            f"└ {_('list_available_alliances', 'ALLIANCE')}\n"
                            f"{_('separator', 'ALLIANCE')}"
                        ),
                        color=discord.Color.blue()
                    )
                    
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(
                        label=_("add_alliance", "BUTTON"), 
                        emoji="➕",
                        style=discord.ButtonStyle.success, 
                        custom_id="add_alliance", 
                        disabled=not is_global_admin   # 只讓全域 Admin 點
                    ))
                    view.add_item(discord.ui.Button(
                        label=_("edit_alliance", "BUTTON"), 
                        emoji="✏️",
                        style=discord.ButtonStyle.primary, 
                        custom_id="edit_alliance", 
                        disabled=not is_global_admin   # 只讓全域 Admin 點
                    ))
                    view.add_item(discord.ui.Button(
                        label=_("delete_alliance", "BUTTON"), 
                        emoji="🗑️",
                        style=discord.ButtonStyle.danger, 
                        custom_id="delete_alliance", 
                        disabled=not is_global_admin   # 只讓全域 Admin 點
                    ))
                    view.add_item(discord.ui.Button(
                        label=_("view_alliances", "BUTTON"), 
                        emoji="👀",
                        style=discord.ButtonStyle.primary, 
                        custom_id="view_alliances"
                    ))
                    view.add_item(discord.ui.Button(
                        label=_("check_alliance", "BUTTON"), 
                        emoji="🔍",
                        style=discord.ButtonStyle.primary, 
                        custom_id="check_alliance"
                    ))
                    view.add_item(discord.ui.Button(
                        label=_("main_menu", "BUTTON"), 
                        emoji="🏠",
                        style=discord.ButtonStyle.secondary, 
                        custom_id="main_menu"
                    ))

                    # Use edit_original_response since we deferred
                    await interaction.edit_original_response(embed=embed, view=view)

                elif custom_id == "edit_alliance":
                    # 權限已在上面檢查過（admin_only=True）
                    await self.edit_alliance(interaction)

                elif custom_id == "check_alliance":
                    self.c.execute("""
                        SELECT a.alliance_id, a.name, COALESCE(s.interval, 0) as interval
                        FROM alliance_list a
                        LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
                        ORDER BY a.name
                    """)
                    alliances = self.c.fetchall()

                    if not alliances:
                        await interaction.response.send_message("No alliances found to check.", ephemeral=True)
                        return

                    options = [
                        discord.SelectOption(
                            label="Check All Alliances",
                            value="all",
                            description="Start control process for all alliances",
                            emoji="🔄"
                        )
                    ]
                    
                    options.extend([
                        discord.SelectOption(
                            label=f"{name[:40]}",
                            value=str(alliance_id),
                            description=f"Control Interval: {interval} minutes"
                        ) for alliance_id, name, interval in alliances
                    ])

                    select = discord.ui.Select(
                        placeholder="Select an alliance to check",
                        options=options,
                        custom_id="alliance_check_select"
                    )

                    async def alliance_check_callback(select_interaction: discord.Interaction):
                        try:
                            selected_value = select_interaction.data["values"][0]
                            control_cog = self.bot.get_cog('Control')
                            
                            if not control_cog:
                                await select_interaction.response.send_message("Control module not found.", ephemeral=True)
                                return
                            
                            # Ensure the centralized queue processor is running
                            await control_cog.login_handler.start_queue_processor()
                            
                            if selected_value == "all":
                                progress_embed = discord.Embed(
                                    title="🔄 Alliance Control Queue",
                                    description=(
                                        "**Control Queue Information**\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"📊 **Total Alliances:** `{len(alliances)}`\n"
                                        "🔄 **Status:** `Adding alliances to control queue...`\n"
                                        "⏰ **Queue Start:** `Now`\n"
                                        "⚠️ **Note:** `Each alliance will be processed in sequence`\n"
                                        "⏱️ **Wait Time:** `1 minute between each alliance control`\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                        "⌛ Please wait while alliances are being processed..."
                                    ),
                                    color=discord.Color.blue()
                                )
                                await select_interaction.response.send_message(embed=progress_embed)
                                msg = await select_interaction.original_response()
                                message_id = msg.id

                                # Queue all alliance operations at once
                                queued_alliances = []
                                for index, (alliance_id, name, _) in enumerate(alliances):
                                    try:
                                        self.c.execute("""
                                            SELECT channel_id FROM alliancesettings WHERE alliance_id = ?
                                        """, (alliance_id,))
                                        channel_data = self.c.fetchone()
                                        channel = self.bot.get_channel(channel_data[0]) if channel_data else select_interaction.channel
                                        
                                        await control_cog.login_handler.queue_operation({
                                            'type': 'alliance_control',
                                            'callback': lambda ch=channel, aid=alliance_id, inter=select_interaction: control_cog.check_agslist(ch, aid, interaction=inter),
                                            'description': f'Manual control check for alliance {name}',
                                            'alliance_id': alliance_id,
                                            'interaction': select_interaction
                                        })
                                        queued_alliances.append((alliance_id, name))
                                    
                                    except Exception as e:
                                        print(f"Error queuing alliance {name}: {e}")
                                        continue
                                
                                # Update status to show all alliances have been queued
                                queue_status_embed = discord.Embed(
                                    title="🔄 Alliance Control Queue",
                                    description=(
                                        "**Control Queue Information**\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"📊 **Total Alliances Queued:** `{len(queued_alliances)}`\n"
                                        f"⏰ **Queue Start:** <t:{int(datetime.now().timestamp())}:R>\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                        "⌛ All alliance controls have been queued and will process in order..."
                                    ),
                                    color=discord.Color.blue()
                                )
                                channel = select_interaction.channel
                                msg = await channel.fetch_message(message_id)
                                await msg.edit(embed=queue_status_embed)
                                
                                # Monitor queue completion with timeout
                                start_time = datetime.now()
                                log_timeout = 300  # 5 minutes timeout
                                check_interval = 5  # Check every 5 seconds
                                
                                while (datetime.now() - start_time).total_seconds() < log_timeout:
                                    queue_info = control_cog.login_handler.get_queue_info()
                                    
                                    # Check if all our operations are done
                                    if queue_info['queue_size'] == 0 and queue_info['current_operation'] is None:
                                        # Double-check by waiting a moment
                                        await asyncio.sleep(2)
                                        queue_info = control_cog.login_handler.get_queue_info()
                                        if queue_info['queue_size'] == 0 and queue_info['current_operation'] is None:
                                            break
                                    
                                    # Update status periodically
                                    if queue_info['current_operation'] and queue_info['current_operation'].get('type') == 'alliance_control':
                                        current_alliance_id = queue_info['current_operation'].get('alliance_id')
                                        current_name = next((name for aid, name in queued_alliances if aid == current_alliance_id), "Unknown")
                                        
                                        update_embed = discord.Embed(
                                            title="🔄 Alliance Control Queue",
                                            description=(
                                                "**Control Queue Information**\n"
                                                "━━━━━━━━━━━━━━━━━━━━━━\n"
                                                f"📊 **Total Alliances:** `{len(queued_alliances)}`\n"
                                                f"🔄 **Currently Processing:** `{current_name}`\n"
                                                f"📈 **Queue Remaining:** `{queue_info['queue_size']}`\n"
                                                f"⏰ **Started:** <t:{int(start_time.timestamp())}:R>\n"
                                                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                                "⌛ Processing controls..."
                                            ),
                                            color=discord.Color.blue()
                                        )
                                        try:
                                            await msg.edit(embed=update_embed)
                                        except Exception as e:
                                            print(f"Error updating queue status: {e}")
                                            break  # Exit if we can't update the message
                                    
                                    await asyncio.sleep(check_interval)
                                
                                # Check if we timed out or completed normally
                                if (datetime.now() - start_time).total_seconds() >= log_timeout:
                                    print(f"Queue monitoring timed out after {log_timeout} seconds")
                                    timeout_embed = discord.Embed(
                                        title="⏰ Queue Monitoring Timeout",
                                        description=(
                                            "**Monitoring Status**\n"
                                            "━━━━━━━━━━━━━━━━━━━━━━\n"
                                            f"📊 **Alliances Queued:** `{len(queued_alliances)}`\n"
                                            f"⏰ **Monitoring Duration:** `{int((datetime.now() - start_time).total_seconds())} seconds`\n"
                                            f"⚠️ **Status:** `Monitoring stopped due to timeout`\n"
                                            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                            "📝 Note: Controls may still be processing in background"
                                        ),
                                        color=discord.Color.orange()
                                    )
                                    try:
                                        await msg.edit(embed=timeout_embed)
                                    except Exception as e:
                                        print(f"Error sending timeout message: {e}")
                                    return  # Exit early due to timeout
                                
                                # All operations complete
                                queue_complete_embed = discord.Embed(
                                    title="✅ Alliance Control Queue Complete",
                                    description=(
                                        "**Queue Status Information**\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"📊 **Total Alliances Processed:** `{len(queued_alliances)}`\n"
                                        "🔄 **Status:** `All controls completed`\n"
                                        f"⏰ **Completion Time:** <t:{int(datetime.now().timestamp())}:R>\n"
                                        f"⏱️ **Total Duration:** `{int((datetime.now() - start_time).total_seconds())} seconds`\n"
                                        "📝 **Note:** `Control results have been shared in respective channels`\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━"
                                    ),
                                    color=discord.Color.green()
                                )
                                await msg.edit(embed=queue_complete_embed)
                                
                            else:
                                alliance_id = int(selected_value)
                                self.c.execute("""
                                    SELECT a.name, s.channel_id 
                                    FROM alliance_list a
                                    LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
                                    WHERE a.alliance_id = ?
                                """, (alliance_id,))
                                alliance_data = self.c.fetchone()

                                if not alliance_data:
                                    await select_interaction.response.send_message("Alliance not found.", ephemeral=True)
                                    return

                                alliance_name, channel_id = alliance_data
                                channel = self.bot.get_channel(channel_id) if channel_id else select_interaction.channel
                                
                                status_embed = discord.Embed(
                                    title="🔍 Alliance Control",
                                    description=(
                                        "**Control Information**\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"📊 **Alliance:** `{alliance_name}`\n"
                                        f"🔄 **Status:** `Queued`\n"
                                        f"⏰ **Queue Time:** `Now`\n"
                                        f"📢 **Results Channel:** `{channel.name if channel else 'Designated channel'}`\n"
                                        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                        "⏳ Alliance control will begin shortly..."
                                    ),
                                    color=discord.Color.blue()
                                )
                                await select_interaction.response.send_message(embed=status_embed)
                                
                                await control_cog.login_handler.queue_operation({
                                    'type': 'alliance_control',
                                    'callback': lambda ch=channel, aid=alliance_id: control_cog.check_agslist(ch, aid),
                                    'description': f'Manual control check for alliance {alliance_name}',
                                    'alliance_id': alliance_id
                                })

                        except Exception as e:
                            print(f"Alliance check error: {e}")
                            await select_interaction.response.send_message(
                                "An error occurred during the control process.", 
                                ephemeral=True
                            )

                    select.callback = alliance_check_callback
                    view = discord.ui.View()
                    view.add_item(select)

                    embed = discord.Embed(
                        title="🔍 Alliance Control",
                        description=(
                            "Please select an alliance to check:\n\n"
                            "**Information**\n"
                            "━━━━━━━━━━━━━━━━━━━━━━\n"
                            "• Select 'Check All Alliances' to process all alliances\n"
                            "• Control process may take a few minutes\n"
                            "• Results will be shared in the designated channel\n"
                            "• Other controls will be queued during the process\n"
                            "━━━━━━━━━━━━━━━━━━━━━━"
                        ),
                        color=discord.Color.blue()
                    )
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

                elif custom_id == "member_operations":
                    await self.bot.get_cog("AllianceMemberOperations").handle_member_operations(interaction)

                elif custom_id == "gift_code_operations":
                    try:
                        gift_ops_cog = interaction.client.get_cog("GiftOperations")
                        if gift_ops_cog:
                            await gift_ops_cog.show_gift_menu(interaction)
                        else:
                            await interaction.response.send_message(
                                "❌ Gift Operations module not found.",
                                ephemeral=True
                            )
                    except Exception as e:
                        print(f"Gift operations error: {e}")
                        if not interaction.response.is_done():
                            await interaction.response.send_message(
                                "An error occurred while loading Gift Operations.",
                                ephemeral=True
                            )
                        else:
                            await interaction.followup.send(
                                "An error occurred while loading Gift Operations.",
                                ephemeral=True
                            )

                elif custom_id == "add_alliance":
                    # 權限已在上面檢查過（admin_only=True）
                    await self.add_alliance(interaction)

                elif custom_id == "delete_alliance":
                    # 暫時放寬權限檢查 - 所有管理員都可以刪除聯盟
                    await self.delete_alliance(interaction)

                elif custom_id == "view_alliances":
                    await self.view_alliances(interaction)

                elif custom_id == "main_menu":
                    await self._show_settings_menu(interaction, from_button=True)


                elif custom_id == "alliance_history":
                    try:
                        changes_cog = interaction.client.get_cog("Changes")
                        if changes_cog:
                            await changes_cog.show_alliance_history_menu(interaction)
                        else:
                            await interaction.response.send_message(
                                "❌ Alliance History module not found.",
                                ephemeral=True
                            )
                    except Exception as e:
                        print(f"Alliance history error: {e}")
                        if not interaction.response.is_done():
                            await interaction.response.send_message(
                                "An error occurred while loading Alliance History.",
                                ephemeral=True
                            )
                        else:
                            await interaction.followup.send(
                                "An error occurred while loading Alliance History.",
                                ephemeral=True
                            )

                elif custom_id == "other_features":
                    try:
                        other_features_cog = interaction.client.get_cog("OtherFeatures")
                        if other_features_cog:
                            await other_features_cog.show_other_features_menu(interaction)
                        else:
                            await interaction.response.send_message(
                                "❌ Other Features module not found.",
                                ephemeral=True
                            )
                    except Exception as e:
                        if not any(error_code in str(e) for error_code in ["10062", "40060"]):
                            print(f"Other features error: {e}")
                        if not interaction.response.is_done():
                            await interaction.response.send_message(
                                "An error occurred while loading Other Features menu.",
                                ephemeral=True
                            )
                        else:
                            await interaction.followup.send(
                                "An error occurred while loading Other Features menu.",
                                ephemeral=True
                            )
                
                elif custom_id == "permission_management":
                    try:
                        permission_cog = interaction.client.get_cog("PermissionManagement")
                        if permission_cog:
                            await permission_cog.show_permission_management_menu(interaction)
                        else:
                            await interaction.response.send_message(
                                "❌ Permission Management module not found.",
                                ephemeral=True
                            )
                    except Exception as e:
                        if not any(error_code in str(e) for error_code in ["10062", "40060"]):
                            print(f"Permission management error: {e}")
                        if not interaction.response.is_done():
                            await interaction.response.send_message(
                                "An error occurred while loading Permission Management menu.",
                                ephemeral=True
                            )
                        else:
                            await interaction.followup.send(
                                "An error occurred while loading Permission Management menu.",
                                ephemeral=True
                            )

            except Exception as e:
                if not any(error_code in str(e) for error_code in ["10062", "40060"]):
                    print(f"Error processing interaction with custom_id '{custom_id}': {e}")
                    await interaction.response.send_message(
                        "An error occurred while processing your request. Please try again.",
                        ephemeral=True
                    )

    @requires_annaway_role(admin_only=True)
    async def add_alliance(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(_("command_server_only", "ERRORS"), ephemeral=True)
            return

        modal = AllianceModal(title=_("add_alliance", "BUTTON"))
        await interaction.response.send_modal(modal)
        
        # 等待 modal 提交
        modal_interaction = None
        while not hasattr(modal, 'interaction') or modal.interaction is None:
            await asyncio.sleep(0.1)
        modal_interaction = modal.interaction

        try:
            alliance_name = modal.name.value.strip()
            interval = int(modal.interval.value.strip())

            # 檢查聯盟名稱是否已存在（同 guild 內）
            guild_id = interaction.guild.id if interaction.guild else -1
            self.c.execute("SELECT alliance_id FROM alliance_list WHERE name = ? AND discord_server_id = ?", (alliance_name, guild_id))
            existing_alliance = self.c.fetchone()
            
            if existing_alliance:
                error_embed = discord.Embed(
                        title=_("error", "TITLE"),
                        description=_("alliance_name_exists", "ERRORS"),
                    color=discord.Color.red()
                )
                await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

            # 直接創建聯盟，不再選擇頻道
            self.c.execute("""INSERT INTO alliance_list (name, discord_server_id)
                VALUES (?, ?)
            """, (alliance_name, interaction.guild.id))
            alliance_id = self.c.lastrowid
            self.conn.commit()

            # 創建聯盟設定，使用全域禮品碼頻道
            self.c_settings.execute("SELECT global_gift_code_channel FROM botsettings WHERE id = 1")
            global_gift_channel = self.c_settings.fetchone()
            channel_id = global_gift_channel[0] if global_gift_channel and global_gift_channel[0] else None

            self.c.execute("""INSERT INTO alliancesettings (alliance_id, channel_id, interval)
                    VALUES (?, ?, ?)
            """, (alliance_id, channel_id, interval))
            self.conn.commit()

            # 啟用禮品碼控制
            self.c_giftcode.execute("""INSERT INTO giftcodecontrol (alliance_id, status)
                VALUES (?, 1)
            """, (alliance_id,))
            self.conn_giftcode.commit()

            success_embed = discord.Embed(
                        title=_("alliance_created_success", "TITLE"),
                        description=_("alliance_created_success_desc", "DESCRIPTION").format(
                            name=alliance_name,
                            id=alliance_id,
                            interval=interval
                        ),
                        color=discord.Color.green()
                    )
            success_embed.set_footer(text=_("alliance_created_complete", "FOOTER"))
            success_embed.timestamp = discord.utils.utcnow()
                    
            await modal_interaction.response.send_message(embed=success_embed, ephemeral=True)
                    
        except Exception as e:
            print(f"Error in add_alliance: {e}")
            error_embed = discord.Embed(
                title=_("error", "TITLE"),
                description=_("error_creating_alliance", "DESCRIPTION"),
                color=discord.Color.red()
            )
            await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)

    @requires_annaway_role(admin_only=True)
    async def edit_alliance(self, interaction: discord.Interaction):
        try:
            self.c.execute("""
                SELECT a.alliance_id, a.name, COALESCE(s.interval, 0) as interval, COALESCE(s.channel_id, 0) as channel_id 
                FROM alliance_list a 
                LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
                ORDER BY a.alliance_id ASC
            """)
            alliances = self.c.fetchall()
            
            if not alliances:
                no_alliance_embed = discord.Embed(
                    title=_("error", "TITLE"),
                    description=_("no_alliances", "DESCRIPTION"),
                    color=discord.Color.red()
                )
                no_alliance_embed.set_footer(text=_("please_create_alliance_first", "FOOTER"))
                return await interaction.response.send_message(embed=no_alliance_embed, ephemeral=True)

            alliance_options = [
                discord.SelectOption(
                    label=f"{name} (ID: {alliance_id})",
                    value=f"{alliance_id})",
                    description=_("interval_minutes", "OPTION_DESC").format(interval=interval)
                ) for alliance_id, name, interval, _ in alliances
            ]
            
            items_per_page = 25
            option_pages = [alliance_options[i:i + items_per_page] for i in range(0, len(alliance_options), items_per_page)]
            total_pages = len(option_pages)

            class PaginatedAllianceEditView(discord.ui.View):
                def __init__(self, pages, original_callback):
                    super().__init__(timeout=7200)
                    self.current_page = 0
                    self.pages = pages
                    self.original_callback = original_callback
                    self.total_pages = len(pages)
                    self.update_view()

                def update_view(self):
                    self.clear_items()
                    
                    select = discord.ui.Select(
                        placeholder=f"選擇要編輯的聯盟 ({self.current_page + 1}/{self.total_pages})",
                        options=self.pages[self.current_page]
                    )
                    select.callback = self.original_callback
                    self.add_item(select)
                    
                    previous_button = discord.ui.Button(
                        label="◀️",
                        style=discord.ButtonStyle.grey,
                        custom_id="previous",
                        disabled=(self.current_page == 0)
                    )
                    previous_button.callback = self.previous_callback
                    self.add_item(previous_button)

                    next_button = discord.ui.Button(
                        label="▶️",
                        style=discord.ButtonStyle.grey,
                        custom_id="next",
                        disabled=(self.current_page == len(self.pages) - 1)
                    )
                    next_button.callback = self.next_callback
                    self.add_item(next_button)

                async def previous_callback(self, interaction: discord.Interaction):
                    self.current_page = (self.current_page - 1) % len(self.pages)
                    self.update_view()
                    
                    embed = interaction.message.embeds[0]
                    embed.description = (
                        "**說明：**\n"
                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                        "1️⃣ 從下拉選單選擇要編輯的聯盟\n"
                        "2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n"
                        f"**目前頁面：** {self.current_page + 1}/{self.total_pages}\n"
                        f"**總聯盟數：** {sum(len(page) for page in self.pages)}\n"
                        "━━━━━━━━━━━━━━━━━━━━━━"
                    )
                    await interaction.response.edit_message(embed=embed, view=self)

                async def next_callback(self, interaction: discord.Interaction):
                    self.current_page = (self.current_page + 1) % len(self.pages)
                    self.update_view()
                    
                    embed = interaction.message.embeds[0]
                    embed.description = (
                        "**說明：**\n"
                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                        "1️⃣ 從下拉選單選擇要編輯的聯盟\n"
                        "2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n"
                        f"**目前頁面：** {self.current_page + 1}/{self.total_pages}\n"
                        f"**總聯盟數：** {sum(len(page) for page in self.pages)}\n"
                        "━━━━━━━━━━━━━━━━━━━━━━"
                    )
                    await interaction.response.edit_message(embed=embed, view=self)

            async def select_callback(select_interaction: discord.Interaction):
                try:
                    alliance_id = int(select_interaction.data["values"][0])
                    alliance_data = next(a for a in alliances if a[0] == alliance_id)
                    
                    self.c.execute("""
                        SELECT interval, channel_id 
                        FROM alliancesettings 
                        WHERE alliance_id = ?
                    """, (alliance_id,))
                    settings_data = self.c.fetchone()
                    
                    modal = AllianceModal(
                        title=_("edit_alliance", "BUTTON"),
                        default_name=alliance_data[1],
                        default_interval=str(settings_data[0] if settings_data else 0)
                    )
                    await select_interaction.response.send_modal(modal)
                    
                    # 等待 modal 提交
                    modal_interaction = None
                    while not hasattr(modal, 'interaction') or modal.interaction is None:
                        await asyncio.sleep(0.1)
                    modal_interaction = modal.interaction

                    try:
                        alliance_name = modal.name.value.strip()
                        interval = int(modal.interval.value.strip())

                        # 檢查聯盟名稱是否已存在且不是當前聯盟（同 guild 內）
                        guild_id = interaction.guild.id if interaction.guild else -1
                        self.c.execute("SELECT alliance_id FROM alliance_list WHERE name = ? AND alliance_id != ? AND discord_server_id = ?", (alliance_name, alliance_id, guild_id))
                        existing_alliance = self.c.fetchone()
                        
                        if existing_alliance:
                            error_embed = discord.Embed(
                                title=_("error", "TITLE"),
                                description=_("alliance_name_exists", "ERRORS"),
                                color=discord.Color.red()
                            )
                            await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)
                            return

                        # 使用全域禮品碼頻道設定
                        self.c_settings.execute("SELECT global_gift_code_channel FROM botsettings WHERE id = 1")
                        global_gift_channel = self.c_settings.fetchone()
                        channel_id = global_gift_channel[0] if global_gift_channel and global_gift_channel[0] else None

                        # 更新聯盟名稱
                        self.c.execute("UPDATE alliance_list SET name = ? WHERE alliance_id = ?", (alliance_name, alliance_id))
                        self.conn.commit()
                        
                        # 更新或創建聯盟設定
                        if settings_data:
                            self.c.execute("""
                                UPDATE alliancesettings 
                                SET channel_id = ?, interval = ? 
                                WHERE alliance_id = ?
                            """, (channel_id, interval, alliance_id))
                        else:
                            self.c.execute("""
                                INSERT INTO alliancesettings (alliance_id, channel_id, interval)
                                VALUES (?, ?, ?)
                            """, (alliance_id, channel_id, interval))
                        
                        self.conn.commit()

                        result_embed = discord.Embed(
                            title="✅ 聯盟更新成功",
                            description="聯盟詳情已更新如下：",
                            color=discord.Color.green()
                        )
                        
                        info_section = (
                            f"**🛡️ 聯盟名稱**\n{alliance_name}\n\n"
                            f"**🔢 聯盟ID**\n{alliance_id}\n\n"
                            f"**📢 使用頻道**\n{'全域禮品碼頻道' if channel_id else '未設定'}\n\n"
                            f"**⏱️ 控制間隔**\n{interval} 分鐘"
                        )
                        result_embed.add_field(name="聯盟詳情", value=info_section, inline=False)
                        
                        result_embed.set_footer(text="聯盟設定已成功儲存")
                        result_embed.timestamp = discord.utils.utcnow()
                        
                        await modal_interaction.response.send_message(embed=result_embed, ephemeral=True)

                    except ValueError:
                        error_embed = discord.Embed(
                            title="錯誤",
                            description="無效的間隔值，請輸入數字",
                            color=discord.Color.red()
                        )
                        await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)
                    except Exception as e:
                        error_embed = discord.Embed(
                            title="錯誤",
                            description=f"更新聯盟時發生錯誤: {str(e)}",
                            color=discord.Color.red()
                        )
                        await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)

                except Exception as e:
                    print(f"Error in alliance edit callback: {e}")
                    await select_interaction.response.send_message(
                        "編輯聯盟時發生錯誤，請重試",
                        ephemeral=True
                    )

            embed = discord.Embed(
                title="✏️ 編輯聯盟",
                description=(
                    "**說明：**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "1️⃣ 從下拉選單選擇要編輯的聯盟\n"
                    "2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n"
                    f"**目前頁面：** 1/{total_pages}\n"
                    f"**總聯盟數：** {len(alliances)}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="選擇聯盟後可以修改名稱和控制間隔")
            embed.timestamp = discord.utils.utcnow()

            view = PaginatedAllianceEditView(option_pages, select_callback)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            print(f"Error in edit_alliance: {e}")
            error_embed = discord.Embed(
                title="❌ 錯誤",
                description="載入編輯選單時發生錯誤",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @requires_annaway_role(admin_only=True)
    async def delete_alliance(self, interaction: discord.Interaction):
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
            alliances = self.c.fetchall()
            
            if not alliances:
                no_alliance_embed = discord.Embed(
                    title="❌ No Alliances Found",
                    description="沒有可刪除的聯盟",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=no_alliance_embed, ephemeral=True)
                return

            alliance_members = {}
            for alliance_id, _ in alliances:
                self.c_users.execute("SELECT COUNT(*) FROM users WHERE alliance = ?", (alliance_id,))
                member_count = self.c_users.fetchone()[0]
                alliance_members[alliance_id] = member_count

            items_per_page = 25
            all_options = [
                discord.SelectOption(
                    label=f"{name[:40]} (ID: {alliance_id})",
                    value=f"{alliance_id}",
                    description=f"部落成員: {alliance_members[alliance_id]} | 點擊刪除",
                    emoji="🗑️"
                ) for alliance_id, name in alliances
            ]
            
            option_pages = [all_options[i:i + items_per_page] for i in range(0, len(all_options), items_per_page)]
            
            embed = discord.Embed(
                title=f"🗑️ 刪除聯盟",
                description=(
                    f"**警告：刪除聯盟將移除所有相關數據**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"1️⃣ 從下拉選單選擇要刪除的聯盟\n"
                    f"2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n"
                    f"**目前頁面：** 1/{len(option_pages)}\n"
                    f"**總聯盟數：** {len(alliances)}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="警告：刪除聯盟將移除所有相關數據")
            embed.timestamp = discord.utils.utcnow()

            view = PaginatedDeleteView(option_pages, self.alliance_delete_callback)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            print(f"Error in delete_alliance: {e}")
            error_embed = discord.Embed(
                title="❌ 錯誤",
                description="載入刪除選單時發生錯誤",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    async def alliance_delete_callback(self, interaction: discord.Interaction):
        try:
            alliance_id = int(interaction.data["values"][0])
            guild_id = interaction.guild.id if interaction.guild else -1
            
            # 確保聯盟屬於當前 guild
            self.c.execute("SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?", (alliance_id, guild_id))
            alliance_data = self.c.fetchone()
            
            if not alliance_data:
                await interaction.response.send_message("找不到聯盟或您無權刪除此聯盟", ephemeral=True)
                return
            
            alliance_name = alliance_data[0]

            self.c.execute("SELECT COUNT(*) FROM alliancesettings WHERE alliance_id = ?", (alliance_id,))
            settings_count = self.c.fetchone()[0]

            self.c_users.execute("SELECT COUNT(*) FROM users WHERE alliance = ?", (alliance_id,))
            users_count = self.c_users.fetchone()[0]

            self.c_settings.execute("SELECT COUNT(*) FROM adminserver WHERE alliances_id = ?", (alliance_id,))
            admin_server_count = self.c_settings.fetchone()[0]

            self.c_giftcode.execute("SELECT COUNT(*) FROM giftcode_channel WHERE alliance_id = ?", (alliance_id,))
            gift_channels_count = self.c_giftcode.fetchone()[0]

            self.c_giftcode.execute("SELECT COUNT(*) FROM giftcodecontrol WHERE alliance_id = ?", (alliance_id,))
            gift_code_control_count = self.c_giftcode.fetchone()[0]

            confirm_embed = discord.Embed(
                title=f"⚠️ {_('confirm_alliance_deletion', 'ALLIANCE')}",
                description=(
                    f"{_('confirm_delete_alliance', 'ALLIANCE')}\n\n"
                    f"**{_('alliance_details', 'ALLIANCE')}:**\n"
                    f"🛡️ **{_('alliance_name', 'ALLIANCE')}:** {alliance_name}\n"
                    f"🔢 **{_('alliance_id', 'ALLIANCE')}:** {alliance_id}\n"
                    f"👥 **{_('members', 'ALLIANCE')}:** {users_count}\n\n"
                    f"**{_('data_to_be_deleted', 'ALLIANCE')}:**\n"
                    f"⚙️ {_('alliance_settings', 'ALLIANCE')}: {settings_count}\n"
                    f"👥 {_('user_records', 'ALLIANCE')}: {users_count}\n"
                    f"🏰 {_('admin_server_records', 'ALLIANCE')}: {admin_server_count}\n"
                    f"📢 {_('gift_channels', 'ALLIANCE')}: {gift_channels_count}\n"
                    f"📊 {_('gift_code_controls', 'ALLIANCE')}: {gift_code_control_count}\n\n"
                    f"**⚠️ {_('warning_action_cannot_be_undone', 'ALLIANCE')}**"
                ),
                color=discord.Color.red()
            )
            
            confirm_view = discord.ui.View(timeout=60)
            
            async def confirm_callback(button_interaction: discord.Interaction):
                try:
                    self.c.execute("DELETE FROM alliance_list WHERE alliance_id = ?", (alliance_id,))
                    alliance_count = self.c.rowcount
                    
                    self.c.execute("DELETE FROM alliancesettings WHERE alliance_id = ?", (alliance_id,))
                    admin_settings_count = self.c.rowcount
                    
                    self.conn.commit()

                    self.c_users.execute("DELETE FROM users WHERE alliance = ?", (alliance_id,))
                    users_count_deleted = self.c_users.rowcount
                    self.conn_users.commit()

                    self.c_settings.execute("DELETE FROM adminserver WHERE alliances_id = ?", (alliance_id,))
                    admin_server_count = self.c_settings.rowcount
                    self.conn_settings.commit()

                    self.c_giftcode.execute("DELETE FROM giftcode_channel WHERE alliance_id = ?", (alliance_id,))
                    gift_channels_count = self.c_giftcode.rowcount

                    self.c_giftcode.execute("DELETE FROM giftcodecontrol WHERE alliance_id = ?", (alliance_id,))
                    gift_code_control_count = self.c_giftcode.rowcount
                    
                    self.conn_giftcode.commit()

                    cleanup_embed = discord.Embed(
                        title=f"✅ {_('alliance_deleted', 'ALLIANCE', alliance_name=alliance_name)}",
                        description=(
                            f"{_('alliance_successfully_deleted', 'ALLIANCE')}\n\n"
                            f"**{_('cleaned_up_data', 'ALLIANCE')}:**\n"
                            f"🛡️ {_('alliance_records', 'ALLIANCE')}: {alliance_count}\n"
                            f"👥 {_('users_removed', 'ALLIANCE')}: {users_count_deleted}\n"
                            f"⚙️ {_('alliance_settings', 'ALLIANCE')}: {admin_settings_count}\n"
                            f"🏰 {_('admin_server_records', 'ALLIANCE')}: {admin_server_count}\n"
                            f"📢 {_('gift_channels', 'ALLIANCE')}: {gift_channels_count}\n"
                            f"📊 {_('gift_code_controls', 'ALLIANCE')}: {gift_code_control_count}"
                        ),
                        color=discord.Color.green()
                    )
                    cleanup_embed.set_footer(text="所有相關數據已成功移除")
                    cleanup_embed.timestamp = discord.utils.utcnow()
                    
                    await button_interaction.response.edit_message(embed=cleanup_embed, view=None)
                    
                except Exception as e:
                    error_embed = discord.Embed(
                        title="❌ 錯誤",
                        description=f"刪除聯盟時發生錯誤：{str(e)}",
                        color=discord.Color.red()
                    )
                    await button_interaction.response.edit_message(embed=error_embed, view=None)

            async def cancel_callback(button_interaction: discord.Interaction):
                cancel_embed = discord.Embed(
                    title=f"❌ 刪除已取消",
                    description="聯盟刪除已取消",
                    color=discord.Color.grey()
                )
                await button_interaction.response.edit_message(embed=cancel_embed, view=None)

            confirm_button = discord.ui.Button(
                label="確認", 
                style=discord.ButtonStyle.danger
            )
            cancel_button = discord.ui.Button(
                label="取消", 
                style=discord.ButtonStyle.grey
            )
            confirm_button.callback = confirm_callback
            cancel_button.callback = cancel_callback
            confirm_view.add_item(confirm_button)
            confirm_view.add_item(cancel_button)

            await interaction.response.edit_message(embed=confirm_embed, view=confirm_view)

        except Exception as e:
            print(f"Error in alliance_delete_callback: {e}")
            error_embed = discord.Embed(
                title="❌ 錯誤",
                description="處理刪除時發生錯誤",
                color=discord.Color.red()
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=error_embed, ephemeral=True)

    async def show_main_menu(self, interaction: discord.Interaction):
        """顯示主選單 - 基於原始備份的正確實現"""
        try:
            embed = discord.Embed(
                title="⚙️ 設定選單",
                description=(
                    "請選擇一個類別：\n\n"
                    "**選單類別**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🏰 **聯盟操作**\n"
                    "└ 管理聯盟和設定\n\n"
                    "👥 **成員操作**\n"
                    "└ 新增、移除和查看成員\n\n"
                    "🤖 **機器人操作**\n"
                    "└ 設定機器人選項\n\n"
                    "🎁 **禮品碼操作**\n"
                    "└ 管理禮品碼和獎勵\n\n"
                    "📜 **聯盟歷史**\n"
                    "└ 查看聯盟變更和歷史\n\n"
                    "🔧 **其他功能**\n"
                    "└ 訪問其他特色功能\n"
                    "━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.blue()
            )
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="聯盟操作",
                emoji="🏰",
                style=discord.ButtonStyle.primary,
                custom_id="alliance_operations",
                row=0
            ))
            view.add_item(discord.ui.Button(
                label="成員操作",
                emoji="👥",
                style=discord.ButtonStyle.primary,
                custom_id="member_operations",
                row=0
            ))
            view.add_item(discord.ui.Button(
                label="機器人操作",
                emoji="🤖",
                style=discord.ButtonStyle.primary,
                custom_id="bot_operations",
                row=1
            ))
            view.add_item(discord.ui.Button(
                label="禮品碼操作",
                emoji="🎁",
                style=discord.ButtonStyle.primary,
                custom_id="gift_code_operations",
                row=1
            ))
            view.add_item(discord.ui.Button(
                label="聯盟歷史",
                emoji="📜",
                style=discord.ButtonStyle.primary,
                custom_id="alliance_history",
                row=2
            ))
            view.add_item(discord.ui.Button(
                label="其他功能",
                emoji="🔧",
                style=discord.ButtonStyle.primary,
                custom_id="other_features",
                row=2
            ))

            try:
                await interaction.response.edit_message(embed=embed, view=view)
            except discord.InteractionResponded:
                pass
                
        except Exception as _:
            pass

    async def set_global_gift_channel(self, interaction: discord.Interaction):
        """設定全域禮品碼頻道 - 所有聯盟共用同一個頻道"""
        try:
            # 先查詢當前設定
            self.c_settings.execute("SELECT global_gift_code_channel FROM botsettings WHERE id = 1")
            result = self.c_settings.fetchone()
            current_channel_id = result[0] if result and result[0] else None
            
            # 顯示當前設定
            if current_channel_id:
                try:
                    current_channel = self.bot.get_channel(int(current_channel_id))
                    channel_info = f"<#{current_channel_id}>" if current_channel else f"ID: {current_channel_id} (頻道已刪除)"
                except:
                    channel_info = f"ID: {current_channel_id}"
            else:
                channel_info = "未設定"
            
            embed = discord.Embed(
                title="🎁 設定全域禮品碼頻道",
                description=(
                    f"**目前設定：** {channel_info}\n\n"
                    f"**功能說明：**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• 所有聯盟共用同一個禮品碼頻道\n"
                    f"• 機器人會自動監聽該頻道的禮品碼\n"
                    f"• 自動為所有已啟用的聯盟兌換\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"**設定方式：**\n"
                    f"1️⃣ 點擊下方「設定頻道」按鈕\n"
                    f"2️⃣ 在下一則訊息中提及 (#頻道)\n"
                    f"3️⃣ 機器人會自動開始監聽\n\n"
                    f"💡 提示：也可以點擊「清除設定」來取消全域監聽"
                ),
                color=discord.Color.blue()
            )
            
            # 建立按鈕
            view = discord.ui.View(timeout=300)
            
            set_button = discord.ui.Button(
                label="設定頻道",
                emoji="✅",
                style=discord.ButtonStyle.success,
                custom_id="set_global_channel"
            )
            
            clear_button = discord.ui.Button(
                label="清除設定",
                emoji="🗑️",
                style=discord.ButtonStyle.danger,
                custom_id="clear_global_channel",
                disabled=(current_channel_id is None)
            )
            
            back_button = discord.ui.Button(
                label="返回",
                emoji="🔙",
                style=discord.ButtonStyle.secondary,
                custom_id="back_to_other_features"
            )
            
            async def set_callback(button_interaction: discord.Interaction):
                await button_interaction.response.send_message(
                    "請在接下來的訊息中 **提及要監聽的頻道** (例如：#禮品碼頻道)\n\n"
                    "⏱️ 60 秒內有效",
                    ephemeral=True
                )
                
                def check(m):
                    return (m.author.id == button_interaction.user.id and 
                           m.channel.id == button_interaction.channel.id and
                           len(m.channel_mentions) > 0)
                
                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                    channel = msg.channel_mentions[0]
                    
                    # 更新資料庫
                    self.c_settings.execute(
                        "UPDATE botsettings SET global_gift_code_channel = ? WHERE id = 1",
                        (str(channel.id),)
                    )
                    self.conn_settings.commit()
                    
                    success_embed = discord.Embed(
                        title="✅ 設定成功",
                        description=(
                            f"**全域禮品碼頻道已設定為：** {channel.mention}\n\n"
                            f"🤖 機器人現在會監聽此頻道\n"
                            f"🎁 自動為所有啟用的聯盟兌換禮品碼"
                        ),
                        color=discord.Color.green()
                    )
                    
                    await button_interaction.followup.send(embed=success_embed, ephemeral=True)
                    
                    # 刪除用戶的提及訊息
                    try:
                        await msg.delete()
                    except:
                        pass
                    
                    # 重新顯示設定頁面
                    await self.set_global_gift_channel(interaction)
                    
                except TimeoutError:
                    await button_interaction.followup.send("⏰ 操作超時，請重新設定。", ephemeral=True)
                except Exception as e:
                    print(f"Error in set_callback: {e}")
                    await button_interaction.followup.send(f"❌ 設定失敗：{str(e)}", ephemeral=True)
            
            async def clear_callback(button_interaction: discord.Interaction):
                # 清除設定
                self.c_settings.execute(
                    "UPDATE botsettings SET global_gift_code_channel = NULL WHERE id = 1"
                )
                self.conn_settings.commit()
                
                success_embed = discord.Embed(
                    title="✅ 已清除設定",
                    description="全域禮品碼頻道監聽已停用",
                    color=discord.Color.green()
                )
                
                await button_interaction.response.send_message(embed=success_embed, ephemeral=True)
                
                # 重新顯示設定頁面
                await self.set_global_gift_channel(interaction)
            
            async def back_callback(button_interaction: discord.Interaction):
                other_features_cog = self.bot.get_cog("OtherFeatures")
                if other_features_cog:
                    await other_features_cog.show_other_features_menu(button_interaction)
                else:
                    await button_interaction.response.send_message("❌ 無法返回其他功能選單", ephemeral=True)
            
            set_button.callback = set_callback
            clear_button.callback = clear_callback
            back_button.callback = back_callback
            
            view.add_item(set_button)
            view.add_item(clear_button)
            view.add_item(back_button)
            
            try:
                await interaction.response.edit_message(embed=embed, view=view)
            except discord.InteractionResponded:
                await interaction.edit_original_response(embed=embed, view=view)
            except Exception as e:
                print(f"Error in set_global_gift_channel: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 顯示設定頁面時發生錯誤",
                        ephemeral=True
                    )
        except Exception as e:
            print(f"Error in set_global_gift_channel: {e}")
            import traceback
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ 設定全域禮品碼頻道時發生錯誤：{str(e)}",
                    ephemeral=True
                )

class PaginatedDeleteView(discord.ui.View):
    def __init__(self, pages, original_callback):
        super().__init__(timeout=7200)
        self.current_page = 0
        self.pages = pages
        self.original_callback = original_callback
        self.total_pages = len(pages)
        self.update_view()

    def update_view(self):
        self.clear_items()
        
        select = discord.ui.Select(
            placeholder=f"Select alliance to delete ({self.current_page + 1}/{self.total_pages})",
            options=self.pages[self.current_page]
        )
        select.callback = self.original_callback
        self.add_item(select)
        
        previous_button = discord.ui.Button(
            label="◀️",
            style=discord.ButtonStyle.grey,
            custom_id="previous",
            disabled=(self.current_page == 0)
        )
        previous_button.callback = self.previous_callback
        self.add_item(previous_button)

        next_button = discord.ui.Button(
            label="▶️",
            style=discord.ButtonStyle.grey,
            custom_id="next",
            disabled=(self.current_page == len(self.pages) - 1)
        )
        next_button.callback = self.next_callback
        self.add_item(next_button)

    async def previous_callback(self, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % len(self.pages)
        self.update_view()
        
        embed = discord.Embed(
            title=f"🗑️ 刪除聯盟",
            description=(
                f"**警告：刪除聯盟將移除所有相關數據**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"1️⃣ 從下拉選單選擇要刪除的聯盟\n"
                f"2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n"
                f"**目前頁面：** {self.current_page + 1}/{self.total_pages}\n"
                f"**總聯盟數：** {sum(len(page) for page in self.pages)}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text=_("warning_deleting_alliance_remove_data", "ALLIANCE"))
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_callback(self, interaction: discord.Interaction):
        self.current_page = (self.current_page + 1) % len(self.pages)
        self.update_view()
        
        embed = discord.Embed(
            title=f"🗑️ 刪除聯盟",
            description=(
                f"**警告：刪除聯盟將移除所有相關數據**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"1️⃣ 從下拉選單選擇要刪除的聯盟\n"
                f"2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n"
                f"**目前頁面：** {self.current_page + 1}/{self.total_pages}\n"
                f"**總聯盟數：** {sum(len(page) for page in self.pages)}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text=_("warning_deleting_alliance_remove_data", "ALLIANCE"))
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    """設定 Alliance cog"""
    import sqlite3
    conn = sqlite3.connect('db/alliance.sqlite')
    await bot.add_cog(Alliance(bot, conn))

# 為了其他 cog 的兼容性，添加缺失的 PaginatedChannelView
class PaginatedChannelView(discord.ui.View):
    """
    兼容性類 - 用於其他 cog 的依存關係
    實際功能已被簡化，不再需要複雜的頻道選擇
    """
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=300)
        # 簡單實現以保持兼容性
        pass
