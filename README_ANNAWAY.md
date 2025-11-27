# Annaway WOS Gift Code Bot

A customized fork of the Whiteout Survival Discord Bot for Annaway Studio, featuring multi-guild support and simple role-based permissions.

## ✨ Key Features

- **Multi-Guild Isolation**: Each Discord server sees only its own alliances and data
- **Simple Permissions**: Role-based access control (`Annaway_Admin`, `Annaway_Manager`)
- **Gift Code Automation**: Automatic redemption with scheduling
- **Member Management**: Track and manage alliance members
- **Self-Contained**: No auto-update system, runs entirely from local code

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- A Discord server where you have permission to manage roles

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/105405003/annaway-wos-giftcode-bot.git
   cd annaway-wos-giftcode-bot
   ```

2. **Install dependencies:**
   ```bash
   python -m venv bot_venv
   
   # On Windows:
   bot_venv\Scripts\activate
   
   # On Linux/Mac:
   source bot_venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   ```bash
   cp bot_config.env.example bot_config.env
   ```
   
   Edit `bot_config.env` and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   TWOCAPTCHA_API_KEY=your_2captcha_key_here  # Optional
   ```

4. **Set up Discord roles:**
   
   In your Discord server, create these roles (exact names required):
   - `Annaway_Admin` - Full management permissions
   - `Annaway_Manager` - Can manage members and gift codes

5. **Run the bot:**
   ```bash
   python main.py
   ```

### First-Time Setup

After the bot starts:

1. **Create your first alliance:**
   - Use the `/settings` command (requires `Annaway_Admin` role)
   - Navigate to Alliance Management
   - Create a new alliance

2. **Add members:**
   - Anyone can use `/add <alliance> <uid>` to add members
   - Admins can use the advanced member management features

3. **Configure gift code redemption:**
   - Set up automatic redemption schedules
   - Configure redemption channels
   - Test with a gift code

## 🔐 Permission System

### Roles

| Role | Permissions |
|------|-------------|
| **Annaway_Admin** | • Create/edit/delete alliances<br>• Manage all settings<br>• Manage members<br>• Configure gift code automation<br>• View statistics |
| **Annaway_Manager** | • Manage members<br>• Manually redeem gift codes<br>• View statistics |
| **Everyone** | • Add members with `/add` command |

### Role Setup

1. Go to Server Settings → Roles
2. Create new roles named exactly:
   - `Annaway_Admin`
   - `Annaway_Manager`
3. Assign roles to users
4. The bot automatically detects these roles

**Important:** Role names are case-sensitive and must match exactly.

## 🗄️ Multi-Guild Support

This bot can be invited to multiple Discord servers. Each server maintains completely separate data:

- ✅ Each guild has its own alliances
- ✅ Members are isolated per guild
- ✅ Statistics are guild-specific
- ✅ Gift code redemption only affects current guild's alliances

### Testing Multi-Guild Separation

1. Invite the bot to two different servers
2. Create different alliances in each server
3. Verify that alliances from Server A don't appear in Server B's menus
4. Confirm that `/add` and other commands only show the current guild's data

## 📚 Commands

### Admin Commands (Annaway_Admin only)

- `/settings` - Open full settings menu (alliance management, permissions, etc.)

### Manager Commands (Annaway_Admin or Annaway_Manager)

- `/update_members` - Manually update member information
- `/settings` - Open settings menu (limited access)

### Everyone

- `/add <alliance> <uid>` - Add a member to an alliance

## 🔄 Automatic Features

### Gift Code Redemption Schedule

The bot automatically redeems gift codes:
1. **Immediately on startup** - Processes any pending codes
2. **Daily at 8:00 and 20:00 Taiwan Time** - Scheduled redemption
3. **When new codes are detected** - Instant redemption

### Configuration

Edit schedule in `cogs/gift_operations.py` if needed (for advanced users).

## 📁 Project Structure

```
annaway-wos-giftcode-bot/
├── cogs/               # Bot features (commands, event handlers)
├── db/                 # SQLite databases (gitignored)
├── migrations/         # Database migration scripts
├── utils/              # Helper utilities
│   ├── permissions.py  # Permission checking
│   └── guild_helpers.py # Guild isolation helpers
├── i18n/               # Internationalization
├── models/             # AI models for CAPTCHA solving
├── fonts/              # Font files
├── log/                # Log files (gitignored)
├── main.py             # Bot entry point
├── requirements.txt    # Python dependencies
└── bot_config.env      # Configuration (gitignored)
```

## 🛠️ Development

### Running Migrations

If you're upgrading from an older version:

```bash
# Add guild isolation to existing database
python migrations/001_add_guild_isolation.py

# Scan for queries that need fixing
python migrations/apply_guild_isolation_fixes.py --scan
```

### Adding New Features

1. Permission checks for commands:
   ```python
   from utils.permissions import requires_annaway_role
   
   @app_commands.command()
   @requires_annaway_role()  # Requires Annaway_Admin or Annaway_Manager
   async def my_command(self, interaction: discord.Interaction):
       pass
   ```

2. Guild isolation for database queries:
   ```python
   guild_id = interaction.guild.id
   cursor.execute(
       "SELECT * FROM alliance_list WHERE discord_server_id = ?",
       (guild_id,)
   )
   ```

3. Guild context checks:
   ```python
   from utils.permissions import check_guild_context
   
   async def my_command(self, interaction: discord.Interaction):
       if not await check_guild_context(interaction):
           return  # Error already sent to user
   ```

## 🐛 Troubleshooting

### Bot doesn't respond to commands

- Check that the bot has proper permissions in your Discord server
- Verify "Server Members Intent" is enabled in Discord Developer Portal
- Ensure the bot is online (check console for errors)

### Permission errors

- Verify role names are exactly `Annaway_Admin` and `Annaway_Manager`
- Check that users have been assigned the roles
- Confirm "Server Members Intent" is enabled

### Alliances not showing up

- Make sure you're using commands in a server (not DMs)
- Check that alliances were created in the current server
- Run the migration script if upgrading from old version

### Database errors

- Back up your `db/` folder before making changes
- Check file permissions on the `db/` directory
- Review `log/` files for detailed error messages

## 📝 Configuration Options

### Environment Variables (bot_config.env)

```env
# Required
DISCORD_TOKEN=your_token_here

# Optional
TWOCAPTCHA_API_KEY=your_key_here
LANGUAGE=zh_TW
DEBUG_MODE=false
```

### Database Files

Located in `db/` directory:
- `alliance.sqlite` - Alliance and member data
- `giftcode.sqlite` - Gift code history
- `settings.sqlite` - Bot settings
- `users.sqlite` - User profiles

**Important:** Back up these files regularly!

## 🔒 Security

- Never commit `bot_config.env` or `bot_token.txt` to Git
- Keep your Discord bot token secret
- Regularly review users with `Annaway_Admin` role
- Back up database files before updates

## 📄 Credits & License

### Original Project

This bot is based on [Reloisback/Whiteout-Survival-Discord-Bot](https://github.com/Reloisback/Whiteout-Survival-Discord-Bot).

**Original Author:** Reloisback  
**Original Repository:** https://github.com/Reloisback/Whiteout-Survival-Discord-Bot

We thank Reloisback for creating the foundation of this bot and making it available to the community.

### Annaway Fork

This is an unofficial **Annaway Studio** fork that adds:
- Multi-guild isolation by `discord_server_id`
- Role-based permissions (`Annaway_Admin`, `Annaway_Manager`)
- Traditional Chinese localization
- Enhanced UX and documentation
- Deployment optimizations

### License Terms

**The original license terms in [LICENSE](LICENSE) continue to apply to this fork.**

Key points:
- ✅ Allowed: Personal use, educational purposes, modifications
- ❌ Restricted: Commercial use requires written permission from original author
- ❌ Prohibited: Selling to specific Discord server members
- 📝 Required: Attribution to original author in derivative works

For detailed licensing information, see:
- [LICENSE](LICENSE) - Original license terms
- [ANNAWAY_NOTICE.md](ANNAWAY_NOTICE.md) - Fork-specific information

**For commercial use inquiries, contact the original author:**
- Email: usabsz@gmail.com
- GitHub: https://github.com/Reloisback

## 🤝 Support

For issues or questions about this Annaway fork, please open an issue on GitHub.

Original project: https://github.com/105405003/annaway-wos-giftcode-bot

---

**Note:** This is a private fork maintained for Annaway Studio. It has been significantly modified from the original project to support multiple guilds and simplified permissions.

