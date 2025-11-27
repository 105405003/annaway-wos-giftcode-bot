import discord
from discord.ext import commands
import sqlite3
from i18n_manager import i18n, _

class OtherFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def show_other_features_menu(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title=_('other_features', 'SETTINGS'),
                description=(
                    f"{_('created_by_user_request', 'OTHER_FEATURES')}\n\n"
                    f"**{_('available_operations', 'OTHER_FEATURES')}**\n"
                    f"{_('separator', 'OTHER_FEATURES')}\n"
                    f"📊 **統計報表**\n"
                    f"└ 查看聯盟成員統計\n"
                    f"└ 熔爐等級分佈\n"
                    f"└ 詳細報表和變更統計\n\n"
                    f"🎁 **設定全域禮品碼頻道**\n"
                    f"└ 所有聯盟共用同一個禮品碼頻道\n"
                    f"└ 自動監聽並兌換禮品碼\n\n"
                    f"💾 **{_('backup_system', 'OTHER_FEATURES')}**\n"
                    f"└ {_('automatic_backup', 'OTHER_FEATURES')}\n"
                    f"└ {_('send_backup_to_dm', 'OTHER_FEATURES')}\n"
                    f"└ {_('global_admin_only', 'OTHER_FEATURES')}\n"
                    f"{_('separator', 'OTHER_FEATURES')}"
                ),
                color=discord.Color.blue()
            )
            
            view = OtherFeaturesView(self)
            
            try:
                await interaction.response.edit_message(embed=embed, view=view)
            except discord.InteractionResponded:
                pass
                
        except Exception as e:
            print(f"Error in show_other_features_menu: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    _('error_occurred_try_again', 'ERRORS'),
                    ephemeral=True
                )

class OtherFeaturesView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label=_("statistics_report", "BUTTON"),
        emoji="📊",
        style=discord.ButtonStyle.primary,
        custom_id="statistics",
        row=0
    )
    async def statistics_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            statistics_cog = self.cog.bot.get_cog("Statistics")
            if statistics_cog:
                await statistics_cog.show_statistics_menu(interaction)
            else:
                await interaction.response.send_message(
                    "❌ 統計模組未載入",
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error loading Statistics menu: {e}")
            await interaction.response.send_message(
                "❌ 載入統計選單時發生錯誤",
                ephemeral=True
            )

    @discord.ui.button(
        label=_("set_global_gift_channel", "BUTTON"),
        emoji="🎁",
        style=discord.ButtonStyle.primary,
        custom_id="set_global_gift_channel",
        row=0
    )
    async def set_global_gift_channel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            alliance_cog = self.cog.bot.get_cog("Alliance")
            if alliance_cog:
                await alliance_cog.set_global_gift_channel(interaction)
            else:
                await interaction.response.send_message(
                    "❌ Alliance 模組未載入",
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error loading set_global_gift_channel: {e}")
            await interaction.response.send_message(
                "❌ 設定全域禮品碼頻道時發生錯誤",
                ephemeral=True
            )

    @discord.ui.button(
        label=_('backup_system', 'OTHER_FEATURES'),
        emoji="💾",
        style=discord.ButtonStyle.primary,
        custom_id="backup_system",
        row=1
    )
    async def backup_system_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            backup_cog = self.cog.bot.get_cog("BackupOperations")
            if backup_cog:
                await backup_cog.show_backup_menu(interaction)
            else:
                await interaction.response.send_message(
                    _('backup_system_module_not_found', 'OTHER_FEATURES'),
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error loading Backup System menu: {e}")
            await interaction.response.send_message(
                _('error_loading_backup_system_menu', 'OTHER_FEATURES'),
                ephemeral=True
            )

    @discord.ui.button(
        label=_('main_menu', 'GENERAL'),
        emoji="🏠",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def main_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            alliance_cog = self.cog.bot.get_cog("Alliance")
            if alliance_cog:
                # 正確的寫法：調用內部方法並標記來自按鈕
                await alliance_cog._show_settings_menu(interaction, from_button=True)
            else:
                embed = discord.Embed(
                    title="🏠 Warner of Sins - 主選單",
                    description="請使用 `/settings` 指令進入主選單",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            # 忽略已知的交互已確認錯誤
            if not any(error_code in str(e) for error_code in ["10062", "40060"]):
                print(f"Error returning to main menu: {e}")
            # 不要嘗試再次回應，因為交互可能已經被處理了
            pass

async def setup(bot):
    await bot.add_cog(OtherFeatures(bot))