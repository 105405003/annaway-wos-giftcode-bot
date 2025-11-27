# Quick Start Guide - Annaway WOS Gift Code Bot

This is the **fastest path** to get your Annaway fork running. For complete documentation, see `README_ANNAWAY.md`.

---

## 🚀 5-Minute Setup

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv bot_venv

# Activate it
# Windows:
bot_venv\Scripts\activate

# Linux/Mac:
source bot_venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Bot Token

```bash
# Copy example config
cp bot_config.env.example bot_config.env

# Edit bot_config.env and add your Discord token
# Get token from: https://discord.com/developers/applications
```

Edit `bot_config.env`:

```env
DISCORD_TOKEN=your_actual_bot_token_here
```

### 3. Create Discord Roles

In your Discord server:

1. Go to **Server Settings** → **Roles**
2. Create a new role named exactly: **`Annaway_Admin`**
3. Create another role named exactly: **`Annaway_Manager`**
4. Assign yourself the `Annaway_Admin` role

**⚠️ Role names must match exactly (case-sensitive)!**

### 4. Enable Bot Permissions

In Discord Developer Portal:

1. Go to your application
2. **Bot** section → **Privileged Gateway Intents**
3. Enable: **Server Members Intent** ✅
4. Enable: **Message Content Intent** ✅

### 5. Run the Bot

```bash
python main.py
```

Wait for: `Logged in as YourBotName#1234`

---

## ✅ First Steps After Bot Starts

### Create Your First Alliance

1. In Discord, use command: `/settings`
2. Click **"🏰 Alliance Management"**
3. Click **"Add Alliance"**
4. Enter alliance name (e.g., "MyAlliance")
5. Click Submit

### Add Members

Anyone in your server can use:

```
/add MyAlliance 12345678
```

Where `12345678` is the player's UID.

### Test Multi-Guild (Optional)

If using bot in multiple servers:

1. Invite bot to second server
2. Create roles there too
3. Create different alliance
4. Verify alliances don't mix between servers

---

## 🔧 Troubleshooting

### Bot doesn't respond

- ✅ Check console for errors
- ✅ Verify bot has "Send Messages" permission in Discord
- ✅ Make sure "Server Members Intent" is enabled

### Permission errors

- ✅ Role names MUST be exact: `Annaway_Admin` and `Annaway_Manager`
- ✅ Verify you assigned yourself the role
- ✅ Try `/check_permission` to see your current role

### Commands don't show up

- Wait 1-2 minutes for Discord to sync commands
- Try using commands in server (not DMs)
- Restart the bot if needed

### "Can only be used in a server"

- This bot requires guild context
- Commands won't work in DMs (by design)

---

## 📚 Next Steps

- **Full Documentation:** `README_ANNAWAY.md`
- **Technical Details:** `ANNAWAY_REFACTORING.md`
- **Implementation Status:** `IMPLEMENTATION_STATUS.md`
- **Quick Summary:** `REFACTORING_SUMMARY.md`

---

## 🎯 Key Commands

| Command                 | Who Can Use     | Description                 |
| ----------------------- | --------------- | --------------------------- |
| `/settings`             | Admins/Managers | Open settings menu          |
| `/add <alliance> <uid>` | Everyone        | Add member to alliance      |
| `/update_members`       | Admins/Managers | Refresh member data         |
| `/check_permission`     | Everyone        | Check your permission level |

---

## 🔐 Permission Roles

| Role                | Can Do                                               |
| ------------------- | ---------------------------------------------------- |
| **Annaway_Admin**   | Everything (create alliances, manage settings, etc.) |
| **Annaway_Manager** | Manage members, redeem gift codes, view stats        |
| **Everyone**        | Add members with `/add` command                      |

---

## ⚠️ Important Notes

1. **Multi-Guild:** Each Discord server has isolated data. Alliances in Server A won't appear in Server B.
2. **Backups:** Database files are in `db/` directory. Back them up regularly!
3. **Migrations:** If upgrading from original bot, run: `python migrations/001_add_guild_isolation.py`
4. **Security:** Never commit `bot_config.env` or `bot_token.txt` to Git!

---

## 🆘 Need Help?

1. Check console logs in terminal
2. Check `log/` directory for detailed logs
3. Review troubleshooting in `README_ANNAWAY.md`
4. Open GitHub issue with error details

---

**That's it! You're ready to use the bot. 🎉**

For advanced features and configuration, see the full documentation files.
