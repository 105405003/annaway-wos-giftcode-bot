import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
from collections import defaultdict
import io
from i18n_manager import i18n, _
from utils.permissions import check_permission

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 連接資料庫
        self.conn_alliance = sqlite3.connect('db/alliance.sqlite')
        self.c_alliance = self.conn_alliance.cursor()
        
        self.conn_users = sqlite3.connect('db/users.sqlite')
        self.c_users = self.conn_users.cursor()
        
        self.conn_changes = sqlite3.connect('db/changes.sqlite')
        self.c_changes = self.conn_changes.cursor()
        
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
    
    async def get_admin_alliances(self, user_id: int, guild_id: int):
        """獲取用戶有權限的聯盟列表"""
        try:
            # ✨ HOTFIX: 支援 Manager 角色（Discord 身分組驅動）
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member:
                    has_manager_role = discord.utils.get(member.roles, name="Annaway_Manager") is not None
                    has_admin_role = discord.utils.get(member.roles, name="Annaway_Admin") is not None
                    
                    print(f"[statistics.get_admin_alliances] 用戶: {member.display_name}")
                    print(f"[statistics.get_admin_alliances] Manager: {has_manager_role}, Admin: {has_admin_role}")
                    
                    if has_manager_role or has_admin_role:
                        self.c_alliance.execute(
                            "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
                            (guild_id,)
                        )
                        alliances = self.c_alliance.fetchall()
                        print(f"[statistics.get_admin_alliances] 找到 {len(alliances)} 個聯盟")
                        
                        is_global = has_admin_role
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
                                    self.c_alliance.execute(
                                        f"SELECT alliance_id, name FROM alliance_list WHERE alliance_id IN ({placeholders}) AND discord_server_id = ? ORDER BY name",
                                        special_ids + [guild_id]
                                    )
                                    special_alliances = self.c_alliance.fetchall()
                        
                        if has_manager_role and not has_admin_role and special_alliances:
                            return special_alliances, special_alliances, False
                        else:
                            return alliances, special_alliances, is_global
            
            # 舊邏輯（資料庫驅動）
            with sqlite3.connect('db/settings.sqlite') as settings_db:
                cursor = settings_db.cursor()
                cursor.execute("SELECT is_initial FROM admin WHERE id = ?", (user_id,))
                admin_result = cursor.fetchone()
                
                if not admin_result:
                    print(f"[statistics.get_admin_alliances] User {user_id} 沒有在 admin 表中，也沒有 Discord 角色")
                    return [], [], False
                    
                is_initial = admin_result[0]
                
            if is_initial == 1:
                # ✨ A1 FIX: 全域管理員也只能看到當前 guild 的聯盟
                self.c_alliance.execute(
                    "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
                    (guild_id,)
                )
                alliances = self.c_alliance.fetchall()
                return alliances, [], True
            
            # 非全域管理員
            server_alliances = []
            special_alliances = []
            
            self.c_alliance.execute("""
                SELECT DISTINCT alliance_id, name 
                FROM alliance_list 
                WHERE discord_server_id = ?
                ORDER BY name
            """, (guild_id,))
            server_alliances = self.c_alliance.fetchall()
            
            with sqlite3.connect('db/settings.sqlite') as settings_db:
                cursor = settings_db.cursor()
                cursor.execute("""
                    SELECT alliances_id 
                    FROM adminserver 
                    WHERE admin = ?
                """, (user_id,))
                special_alliance_ids = cursor.fetchall()
                
            if special_alliance_ids:
                placeholders = ','.join('?' * len(special_alliance_ids))
                self.c_alliance.execute(f"""
                    SELECT DISTINCT alliance_id, name
                    FROM alliance_list
                    WHERE alliance_id IN ({placeholders})
                    ORDER BY name
                """, [aid[0] for aid in special_alliance_ids])
                special_alliances = self.c_alliance.fetchall()
            
            all_alliances = list({(aid, name) for aid, name in (server_alliances + special_alliances)})
            return all_alliances, special_alliances, False
                
        except Exception as e:
            print(f"Error getting admin alliances: {e}")
            return [], [], False
    
    async def show_statistics_menu(self, interaction: discord.Interaction):
        """顯示統計選單"""
        try:
            embed = discord.Embed(
                title="📊 統計報表",
                description=(
                    "請選擇要查看的統計報表：\n\n"
                    "**可用報表**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📈 **聯盟成員統計** - 查看各聯盟的成員數量和分佈\n"
                    "🔥 **熔爐等級分佈** - 查看聯盟成員的熔爐等級分佈\n"
                    "📊 **詳細聯盟報表** - 查看特定聯盟的詳細統計\n"
                    "📉 **變更統計** - 查看成員暱稱和等級變更統計\n"
                    "━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.blue()
            )
            
            view = StatisticsMenuView(self)
            
            # 優先嘗試編輯 original response（如果已 defer）
            try:
                await interaction.edit_original_response(embed=embed, view=view)
            except discord.NotFound:
                # 如果 original response 不存在，使用 followup
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error in show_statistics_menu: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 載入統計選單時發生錯誤",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ 載入統計選單時發生錯誤",
                        ephemeral=True
                    )
            except Exception:
                pass
    
    async def show_alliance_statistics(self, interaction: discord.Interaction):
        """顯示聯盟成員統計"""
        try:
            # 獲取所有聯盟及其成員數
            self.c_alliance.execute("""
                SELECT al.alliance_id, al.name
                FROM alliance_list al
                ORDER BY al.name
            """)
            alliances = self.c_alliance.fetchall()
            
            if not alliances:
                await interaction.response.send_message(
                    "ℹ️ 目前沒有聯盟資料",
                    ephemeral=True
                )
                return
            
            # 統計資料
            stats_lines = []
            total_members = 0
            
            for alliance_id, name in alliances:
                self.c_users.execute(
                    "SELECT COUNT(*), AVG(furnace_lv), MAX(furnace_lv) FROM users WHERE alliance = ?",
                    (str(alliance_id),)
                )
                count, avg_lv, max_lv = self.c_users.fetchone()
                
                if count > 0:
                    avg_lv = avg_lv or 0
                    max_lv = max_lv or 0
                    avg_display = self.level_mapping.get(int(avg_lv), str(int(avg_lv)))
                    max_display = self.level_mapping.get(max_lv, str(max_lv))
                    
                    stats_lines.append(
                        f"**{name}**\n"
                        f"├ 👥 成員數: `{count}`\n"
                        f"├ 📊 平均等級: `{avg_display}`\n"
                        f"└ ⚔️ 最高等級: `{max_display}`\n"
                    )
                    total_members += count
            
            if not stats_lines:
                await interaction.response.send_message(
                    "ℹ️ 所有聯盟都沒有成員",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="📈 聯盟成員統計",
                description=(
                    f"**總覽**\n"
                    f"📊 聯盟總數: `{len(alliances)}`\n"
                    f"👥 總成員數: `{total_members}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    + "\n".join(stats_lines)
                ),
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToStatsView(self))
            
        except Exception as e:
            print(f"Error in show_alliance_statistics: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 載入統計資料時發生錯誤",
                ephemeral=True
            )
    
    async def show_furnace_distribution(self, interaction: discord.Interaction):
        """顯示熔爐等級分佈統計"""
        try:
            # 選擇聯盟
            alliances, _, _ = await self.get_admin_alliances(
                interaction.user.id,
                interaction.guild_id
            )
            
            if not alliances:
                await interaction.response.send_message(
                    "❌ 沒有可用的聯盟",
                    ephemeral=True
                )
                return
            
            # 添加成員數量
            alliances_with_counts = []
            for alliance_id, name in alliances:
                self.c_users.execute(
                    "SELECT COUNT(*) FROM users WHERE alliance = ?",
                    (str(alliance_id),)
                )
                count = self.c_users.fetchone()[0]
                alliances_with_counts.append((alliance_id, name, count))
            
            view = AllianceSelectForStatsView(alliances_with_counts, self, context="furnace")
            embed = discord.Embed(
                title="🔥 熔爐等級分佈",
                description="請選擇要查看的聯盟：",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in show_furnace_distribution: {e}")
            await interaction.response.send_message(
                "❌ 載入等級分佈時發生錯誤",
                ephemeral=True
            )
    
    async def show_alliance_detail_report(self, interaction: discord.Interaction):
        """顯示詳細聯盟報表"""
        try:
            alliances, _, _ = await self.get_admin_alliances(
                interaction.user.id,
                interaction.guild_id
            )
            
            if not alliances:
                await interaction.response.send_message(
                    "❌ 沒有可用的聯盟",
                    ephemeral=True
                )
                return
            
            alliances_with_counts = []
            for alliance_id, name in alliances:
                self.c_users.execute(
                    "SELECT COUNT(*) FROM users WHERE alliance = ?",
                    (str(alliance_id),)
                )
                count = self.c_users.fetchone()[0]
                alliances_with_counts.append((alliance_id, name, count))
            
            view = AllianceSelectForStatsView(alliances_with_counts, self, context="detail")
            embed = discord.Embed(
                title="📊 詳細聯盟報表",
                description="請選擇要查看的聯盟：",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in show_alliance_detail_report: {e}")
            await interaction.response.send_message(
                "❌ 載入聯盟報表時發生錯誤",
                ephemeral=True
            )
    
    async def show_changes_statistics(self, interaction: discord.Interaction):
        """顯示變更統計"""
        try:
            # 獲取最近的變更統計
            self.c_changes.execute("""
                SELECT COUNT(*) FROM nickname_changes 
                WHERE date(change_date) >= date('now', '-30 days')
            """)
            nickname_changes = self.c_changes.fetchone()[0]
            
            self.c_changes.execute("""
                SELECT COUNT(*) FROM furnace_changes 
                WHERE date(change_date) >= date('now', '-30 days')
            """)
            furnace_changes = self.c_changes.fetchone()[0]
            
            # 獲取最活躍的成員（變更次數最多）
            # 先獲取所有變更的 fid
            self.c_changes.execute("""
                SELECT fid, COUNT(*) as changes
                FROM (
                    SELECT fid FROM nickname_changes 
                    WHERE date(change_date) >= date('now', '-30 days')
                    UNION ALL
                    SELECT fid FROM furnace_changes 
                    WHERE date(change_date) >= date('now', '-30 days')
                ) as all_changes
                GROUP BY fid
                ORDER BY changes DESC
                LIMIT 10
            """)
            fid_changes = self.c_changes.fetchall()
            
            # 然後從 users 資料庫獲取暱稱
            top_changers = []
            for fid, changes in fid_changes:
                self.c_users.execute("SELECT nickname FROM users WHERE fid = ?", (fid,))
                result = self.c_users.fetchone()
                nickname = result[0] if result else f"Unknown ({fid})"
                top_changers.append((nickname, fid, changes))
            
            top_list = "\n".join([
                f"{idx}. **{name}** (FID: `{fid}`) - {count} 次變更"
                for idx, (name, fid, count) in enumerate(top_changers, 1)
            ]) if top_changers else "無資料"
            
            embed = discord.Embed(
                title="📉 變更統計（最近30天）",
                description=(
                    f"**統計總覽**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 暱稱變更次數: `{nickname_changes}`\n"
                    f"🔥 熔爐等級變更次數: `{furnace_changes}`\n"
                    f"📊 總變更次數: `{nickname_changes + furnace_changes}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"**最活躍成員（變更次數）**\n"
                    f"{top_list}"
                ),
                color=discord.Color.purple()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToStatsView(self))
            
        except Exception as e:
            print(f"Error in show_changes_statistics: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 載入變更統計時發生錯誤",
                ephemeral=True
            )
    
    async def generate_furnace_distribution_for_alliance(self, interaction, alliance_id):
        """生成特定聯盟的熔爐等級分佈"""
        try:
            # 獲取聯盟名稱（驗證 guild）
            guild_id = interaction.guild.id if interaction.guild else -1
            self.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?",
                (alliance_id, guild_id)
            )
            result = self.c_alliance.fetchone()
            if not result:
                await interaction.response.send_message("❌ 找不到聯盟或您無權查看", ephemeral=True)
                return
            alliance_name = result[0]
            
            # 獲取成員等級分佈
            self.c_users.execute("""
                SELECT furnace_lv, COUNT(*) as count
                FROM users 
                WHERE alliance = ? AND furnace_lv IS NOT NULL
                GROUP BY furnace_lv
                ORDER BY furnace_lv DESC
            """, (str(alliance_id),))
            distribution = self.c_users.fetchall()
            
            if not distribution:
                await interaction.response.send_message(
                    f"ℹ️ **{alliance_name}** 沒有成員資料",
                    ephemeral=True
                )
                return
            
            # 按等級範圍分組
            level_groups = {
                "FC 10": (80, 84),
                "FC 9": (75, 79),
                "FC 8": (70, 74),
                "FC 7": (65, 69),
                "FC 6": (60, 64),
                "FC 5": (55, 59),
                "FC 4": (50, 54),
                "FC 3": (45, 49),
                "FC 2": (40, 44),
                "FC 1": (35, 39),
                "30": (30, 34),
                "< 30": (0, 29)
            }
            
            group_counts = defaultdict(int)
            total_members = 0
            
            for level, count in distribution:
                total_members += count
                for group_name, (min_lv, max_lv) in level_groups.items():
                    if min_lv <= level <= max_lv:
                        group_counts[group_name] += count
                        break
            
            # 生成圖表文字
            stats_text = []
            for group_name in level_groups.keys():
                count = group_counts.get(group_name, 0)
                if count > 0:
                    percentage = (count / total_members) * 100
                    bar_length = int(percentage / 2)  # 每2%一個方塊
                    bar = "█" * bar_length
                    stats_text.append(
                        f"**{group_name:6}** │ {bar} `{count:3}` ({percentage:5.1f}%)"
                    )
            
            embed = discord.Embed(
                title=f"🔥 {alliance_name} - 熔爐等級分佈",
                description=(
                    f"**總成員數:** `{total_members}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    + "\n".join(stats_text)
                ),
                color=discord.Color.orange()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToStatsView(self))
            
        except Exception as e:
            print(f"Error generating furnace distribution: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 生成等級分佈時發生錯誤",
                ephemeral=True
            )
    
    async def generate_alliance_detail_report(self, interaction, alliance_id):
        """生成詳細聯盟報表"""
        try:
            # 獲取聯盟名稱（驗證 guild）
            guild_id = interaction.guild.id if interaction.guild else -1
            self.c_alliance.execute(
                "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?",
                (alliance_id, guild_id)
            )
            result = self.c_alliance.fetchone()
            if not result:
                await interaction.response.send_message("❌ 找不到聯盟或您無權查看", ephemeral=True)
                return
            alliance_name = result[0]
            
            # 獲取成員統計
            self.c_users.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(furnace_lv) as avg_lv,
                    MAX(furnace_lv) as max_lv,
                    MIN(furnace_lv) as min_lv
                FROM users 
                WHERE alliance = ? AND furnace_lv IS NOT NULL
            """, (str(alliance_id),))
            stats = self.c_users.fetchone()
            total, avg_lv, max_lv, min_lv = stats
            
            if total == 0:
                await interaction.response.send_message(
                    f"ℹ️ **{alliance_name}** 沒有成員資料",
                    ephemeral=True
                )
                return
            
            avg_display = self.level_mapping.get(int(avg_lv), str(int(avg_lv)))
            max_display = self.level_mapping.get(max_lv, str(max_lv))
            min_display = self.level_mapping.get(min_lv, str(min_lv))
            
            # 獲取該聯盟的所有成員 fid
            self.c_users.execute("""
                SELECT fid FROM users WHERE alliance = ?
            """, (str(alliance_id),))
            member_fids = [row[0] for row in self.c_users.fetchall()]
            
            # 獲取最近變更統計
            recent_nickname_changes = 0
            recent_furnace_changes = 0
            
            if member_fids:
                placeholders = ','.join('?' * len(member_fids))
                
                self.c_changes.execute(f"""
                    SELECT COUNT(*) FROM nickname_changes
                    WHERE fid IN ({placeholders}) AND date(change_date) >= date('now', '-30 days')
                """, member_fids)
                recent_nickname_changes = self.c_changes.fetchone()[0]
                
                self.c_changes.execute(f"""
                    SELECT COUNT(*) FROM furnace_changes
                    WHERE fid IN ({placeholders}) AND date(change_date) >= date('now', '-30 days')
                """, member_fids)
                recent_furnace_changes = self.c_changes.fetchone()[0]
            
            # 獲取頂尖玩家
            self.c_users.execute("""
                SELECT nickname, fid, furnace_lv
                FROM users
                WHERE alliance = ? AND furnace_lv IS NOT NULL
                ORDER BY furnace_lv DESC
                LIMIT 5
            """, (str(alliance_id),))
            top_players = self.c_users.fetchall()
            
            top_list = "\n".join([
                f"{idx}. **{name}** - `{self.level_mapping.get(lv, str(lv))}`"
                for idx, (name, fid, lv) in enumerate(top_players, 1)
            ])
            
            embed = discord.Embed(
                title=f"📊 {alliance_name} - 詳細報表",
                description=(
                    f"**基本統計**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👥 總成員數: `{total}`\n"
                    f"📊 平均等級: `{avg_display}`\n"
                    f"⚔️ 最高等級: `{max_display}`\n"
                    f"🔻 最低等級: `{min_display}`\n\n"
                    f"**最近活動（30天）**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 暱稱變更: `{recent_nickname_changes}` 次\n"
                    f"🔥 等級變更: `{recent_furnace_changes}` 次\n\n"
                    f"**頂尖玩家 Top 5**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{top_list}"
                ),
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(embed=embed, view=BackToStatsView(self))
            
        except Exception as e:
            print(f"Error generating alliance detail report: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ 生成報表時發生錯誤",
                ephemeral=True
            )


class StatisticsMenuView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @discord.ui.button(label="聯盟成員統計", emoji="📈", style=discord.ButtonStyle.primary, row=0)
    async def alliance_stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 權限檢查：Manager 級別
        if not await check_permission(interaction, admin_only=False):
            return
        await self.cog.show_alliance_statistics(interaction)
    
    @discord.ui.button(label="熔爐等級分佈", emoji="🔥", style=discord.ButtonStyle.primary, row=0)
    async def furnace_dist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 權限檢查：Manager 級別
        if not await check_permission(interaction, admin_only=False):
            return
        await self.cog.show_furnace_distribution(interaction)
    
    @discord.ui.button(label="詳細聯盟報表", emoji="📊", style=discord.ButtonStyle.primary, row=1)
    async def detail_report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 權限檢查：Manager 級別
        if not await check_permission(interaction, admin_only=False):
            return
        await self.cog.show_alliance_detail_report(interaction)
    
    @discord.ui.button(label="變更統計", emoji="📉", style=discord.ButtonStyle.primary, row=1)
    async def changes_stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 權限檢查：Manager 級別
        if not await check_permission(interaction, admin_only=False):
            return
        await self.cog.show_changes_statistics(interaction)
    
    @discord.ui.button(label="主選單", emoji="🏠", style=discord.ButtonStyle.secondary, row=2)
    async def main_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 權限檢查：Manager 級別
        if not await check_permission(interaction, admin_only=False):
            return
        try:
            alliance_cog = self.cog.bot.get_cog("Alliance")
            if alliance_cog:
                await alliance_cog._show_settings_menu(interaction, from_button=True)
        except Exception as e:
            if not any(error_code in str(e) for error_code in ["10062", "40060", "InteractionResponded"]):
                print(f"Error in main_menu_button: {e}")
            pass


class AllianceSelectForStatsView(discord.ui.View):
    def __init__(self, alliances_with_counts, cog, page=0, context="furnace"):
        super().__init__(timeout=300)
        self.alliances = alliances_with_counts
        self.cog = cog
        self.page = page
        self.context = context
        self.max_page = (len(alliances_with_counts) - 1) // 25 if alliances_with_counts else 0
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
                    description=f"ID: {alliance_id} | 成員: {count}",
                    emoji="🏰"
                ) for alliance_id, name, count in current_alliances
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            try:
                alliance_id = int(select.values[0])
                
                if self.context == "furnace":
                    await self.cog.generate_furnace_distribution_for_alliance(interaction, alliance_id)
                elif self.context == "detail":
                    await self.cog.generate_alliance_detail_report(interaction, alliance_id)
                    
            except Exception as e:
                print(f"Error in select_callback: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ 處理選擇時發生錯誤",
                        ephemeral=True
                    )
        
        select.callback = select_callback
        self.add_item(select)


class BackToStatsView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @discord.ui.button(label="返回統計選單", emoji="📊", style=discord.ButtonStyle.primary, row=0)
    async def back_to_stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.show_statistics_menu(interaction)
    
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
    await bot.add_cog(Statistics(bot))

