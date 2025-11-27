import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from i18n_manager import i18n, _

class GNCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('db/settings.sqlite')
        self.c = self.conn.cursor()

    def cog_unload(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            with sqlite3.connect('db/settings.sqlite') as settings_db:
                cursor = settings_db.cursor()
                cursor.execute("SELECT id FROM admin WHERE is_initial = 1 LIMIT 1")
                result = cursor.fetchone()
            
            if result:
                admin_id = result[0]
                admin_user = await self.bot.fetch_user(admin_id)
                
                if admin_user:
                    cursor.execute("SELECT value FROM auto LIMIT 1")
                    auto_result = cursor.fetchone()
                    auto_value = auto_result[0] if auto_result else 1
                    
                    # Check OCR initialization status
                    ocr_status = "❌"
                    ocr_details = _('not_initialized', 'BOT_STATUS')
                    try:
                        gift_operations_cog = self.bot.get_cog('GiftOperations')
                        if gift_operations_cog and hasattr(gift_operations_cog, 'captcha_solver'):
                            if gift_operations_cog.captcha_solver and gift_operations_cog.captcha_solver.is_initialized:
                                ocr_status = "✅"
                                ocr_details = _('ocr_ready', 'BOT_STATUS')
                            else:
                                ocr_details = _('solver_not_initialized', 'BOT_STATUS')
                        else:
                            ocr_details = _('gift_operations_cog_not_found', 'BOT_STATUS')
                    except Exception as e:
                        ocr_details = f"{_('error_checking_ocr', 'BOT_STATUS')}: {str(e)[:30]}..."
                    
                    status_embed = discord.Embed(
                        title=_('bot_successfully_activated', 'BOT_STATUS'),
                        description=(
                            f"{_('status_separator', 'BOT_STATUS')}\n"
                            f"**{_('system_status', 'BOT_STATUS')}**\n"
                            f"✅ {_('bot_online_operational', 'BOT_STATUS')}\n"
                            f"✅ {_('database_connections_established', 'BOT_STATUS')}\n"
                            f"✅ {_('command_systems_initialized', 'BOT_STATUS')}\n"
                            f"{'✅' if auto_value == 1 else '❌'} {_('alliance_control_messages', 'BOT_STATUS')}\n"
                            f"{ocr_status} {ocr_details}\n"
                            f"{_('status_separator', 'BOT_STATUS')}\n"
                        ),
                        color=discord.Color.green()
                    )

                    status_embed.add_field(
                        name="Annaway WOS Bot",
                        value=(
                            f"**Bot Version:** Annaway Custom Fork\n"
                            f"**Maintained by:** Annaway Studio\n"
                            f"**Multi-Guild Support:** Enabled\n"
                            f"{_('status_separator', 'BOT_STATUS')}"
                        ),
                        inline=False
                    )

                    status_embed.set_footer(text=_('thanks_for_using_bot', 'BOT_STATUS'))

                    await admin_user.send(embed=status_embed)

                    with sqlite3.connect('db/alliance.sqlite') as alliance_db:
                        cursor = alliance_db.cursor()
                        cursor.execute("SELECT alliance_id, name FROM alliance_list")
                        alliances = cursor.fetchall()

                    if alliances:
                        ALLIANCES_PER_PAGE = 5
                        alliance_info = []
                        
                        for alliance_id, name in alliances:
                            info_parts = []
                            
                            with sqlite3.connect('db/users.sqlite') as users_db:
                                cursor = users_db.cursor()
                                cursor.execute("SELECT COUNT(*) FROM users WHERE alliance = ?", (alliance_id,))
                                user_count = cursor.fetchone()[0]
                                info_parts.append(f"👥 {_('members', 'BOT_STATUS')}: {user_count}")
                            
                            with sqlite3.connect('db/alliance.sqlite') as alliance_db:
                                cursor = alliance_db.cursor()
                                cursor.execute("SELECT discord_server_id FROM alliance_list WHERE alliance_id = ?", (alliance_id,))
                                discord_server = cursor.fetchone()
                                if discord_server and discord_server[0]:
                                    info_parts.append(f"🌐 {_('server_id', 'BOT_STATUS')}: {discord_server[0]}")
                            
                                cursor.execute("SELECT channel_id, interval FROM alliancesettings WHERE alliance_id = ?", (alliance_id,))
                                settings = cursor.fetchone()
                                if settings:
                                    if settings[0]:
                                        info_parts.append(f"📢 {_('channel', 'BOT_STATUS')}: <#{settings[0]}>")
                                    interval_text = f"⏱️ {_('auto_check', 'BOT_STATUS')}: {settings[1]} {_('minutes', 'BOT_STATUS')}" if settings[1] > 0 else f"⏱️ {_('no_auto_check', 'BOT_STATUS')}"
                                    info_parts.append(interval_text)
                            
                            with sqlite3.connect('db/giftcode.sqlite') as gift_db:
                                cursor = gift_db.cursor()
                                cursor.execute("SELECT status FROM giftcodecontrol WHERE alliance_id = ?", (alliance_id,))
                                gift_status = cursor.fetchone()
                                gift_text = f"🎁 {_('gift_system', 'BOT_STATUS')}: {_('active', 'BOT_STATUS')}" if gift_status and gift_status[0] == 1 else f"🎁 {_('gift_system', 'BOT_STATUS')}: {_('inactive', 'BOT_STATUS')}"
                                info_parts.append(gift_text)
                                
                                cursor.execute("SELECT channel_id FROM giftcode_channel WHERE alliance_id = ?", (alliance_id,))
                                gift_channel = cursor.fetchone()
                                if gift_channel and gift_channel[0]:
                                    info_parts.append(f"🎉 {_('gift_channel', 'BOT_STATUS')}: <#{gift_channel[0]}>")
                            
                            alliance_info.append(
                                f"**{name}**\n" + 
                                "\n".join(f"> {part}" for part in info_parts) +
                                "\n━━━━━━━━━━━━━━━━━━━━━━"
                            )

                        pages = [alliance_info[i:i + ALLIANCES_PER_PAGE] 
                                for i in range(0, len(alliance_info), ALLIANCES_PER_PAGE)]

                        for page_num, page in enumerate(pages, 1):
                            alliance_embed = discord.Embed(
                                title=_('alliance_information_page', 'BOT_STATUS').format(page=page_num, total=len(pages)),
                                color=discord.Color.blue()
                            )
                            alliance_embed.description = "\n".join(page)
                            await admin_user.send(embed=alliance_embed)

                    else:
                        alliance_embed = discord.Embed(
                            title=_('alliance_information', 'BOT_STATUS'),
                            description=_('no_alliances_registered', 'BOT_STATUS'),
                            color=discord.Color.blue()
                        )
                        await admin_user.send(embed=alliance_embed)

                    print("Activation messages sent to admin user.")
                else:
                    print(f"User with Admin ID {admin_id} not found.")
            else:
                print("No record found in the admin table.")
        except Exception as e:
            print(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(GNCommands(bot))