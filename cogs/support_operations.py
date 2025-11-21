import discord
from discord.ext import commands
from i18n_manager import i18n, _

class SupportOperations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def show_support_menu(self, interaction: discord.Interaction):
        support_menu_embed = discord.Embed(
            title=_("support_operations", "MENU"),
            description=(
                f"{_('please_select_operation', 'SUPPORT_OPS')}\n\n"
                f"**{_('available_operations', 'SUPPORT_OPS')}**\n"
                f"{_('separator', 'SUPPORT_OPS')}\n"
                f"📝 **{_('request_support', 'SUPPORT_OPS')}**\n"
                f"└ {_('get_help_support', 'SUPPORT_OPS')}\n\n"
                f"ℹ️ **{_('about_project', 'SUPPORT_OPS')}**\n"
                f"└ {_('project_information', 'SUPPORT_OPS')}\n"
                f"{_('separator', 'SUPPORT_OPS')}"
            ),
            color=discord.Color.blue()
        )

        view = SupportView(self)
        
        try:
            await interaction.response.edit_message(embed=support_menu_embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.message.edit(embed=support_menu_embed, view=view)

    async def show_support_info(self, interaction: discord.Interaction):
        support_embed = discord.Embed(
            title=f"🤖 {_('bot_support_information', 'SUPPORT_OPS')}",
            description=(
                f"{_('support_description', 'SUPPORT_OPS')} [Discord](https://discord.gg/apYByj6K2m)\n\n"
                f"**{_('additional_resources', 'SUPPORT_OPS')}**\n"
                f"**{_('github_repository', 'SUPPORT_OPS')}** [Whiteout Project](https://github.com/whiteout-project/bot)\n"
                f"**{_('issues_bug_reports', 'SUPPORT_OPS')}** [GitHub Issues](https://github.com/whiteout-project/bot/issues)\n\n"
                f"{_('bot_description', 'SUPPORT_OPS')}\n\n"
                f"{_('technical_support', 'SUPPORT_OPS')}"
            ),
            color=discord.Color.blue()
        )
        
        try:
            await interaction.response.send_message(embed=support_embed, ephemeral=True)
            try:
                await interaction.user.send(embed=support_embed)
            except discord.Forbidden:
                await interaction.followup.send(
                    _("could_not_send_dm", "ERRORS"),
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error sending support info: {e}")

class SupportView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.button(
        label=_("request_support", "SUPPORT_OPS"),
        emoji="📝",
        style=discord.ButtonStyle.primary,
        custom_id="request_support"
    )
    async def support_request_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.show_support_info(interaction)

    @discord.ui.button(
        label=_("about_project", "SUPPORT_OPS"),
        emoji="ℹ️",
        style=discord.ButtonStyle.primary,
        custom_id="about_project"
    )
    async def about_project_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        about_embed = discord.Embed(
            title=f"ℹ️ {_('about_whiteout_project', 'SUPPORT_OPS')}",
            description=(
                f"**{_('open_source_bot', 'SUPPORT_OPS')}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{_('open_source_description', 'SUPPORT_OPS')}\n"
                f"{_('separator', 'SUPPORT_OPS')}\n\n"
                f"**{_('features', 'SUPPORT_OPS')}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{_('feature_list', 'SUPPORT_OPS')}\n\n"
                f"**{_('contributing', 'SUPPORT_OPS')}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{_('contributing_description', 'SUPPORT_OPS')}"
            ),
            color=discord.Color.green()
        )

        about_embed.set_footer(text=f"{_('made_with_love', 'SUPPORT_OPS')}")
        
        try:
            await interaction.response.send_message(embed=about_embed, ephemeral=True)
            try:
                await interaction.user.send(embed=about_embed)
            except discord.Forbidden:
                await interaction.followup.send(
                    _("could_not_send_dm", "ERRORS"),
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error sending project info: {e}")

    @discord.ui.button(
        label=_("main_menu", "GENERAL"),
        emoji="🏠",
        style=discord.ButtonStyle.secondary,
        custom_id="main_menu"
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
            print(f"Error in support main_menu_button: {e}")
            embed = discord.Embed(
                title="🏠 Warner of Sins - 主選單",
                description="請使用 `/settings` 指令進入主選單",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SupportOperations(bot))