# Annaway WOS Gift Code Bot

> **Note:** This is a customized fork of the Whiteout Survival Discord Bot for Annaway Studio.
> 
> **See [README_ANNAWAY.md](README_ANNAWAY.md) for complete setup instructions and documentation.**

## What's Different in This Fork?

This version has been significantly refactored for Annaway Studio with:

1. **Multi-Guild Support** - One bot instance can serve multiple Discord servers with complete data isolation
2. **Simplified Permissions** - Role-based system using `Annaway_Admin` and `Annaway_Manager` roles
3. **No Auto-Update** - Self-contained codebase that doesn't auto-update from remote sources
4. **Clean Structure** - Removed packaging/deployment scripts from the original project
5. **Annaway Branding** - Neutral branding without original project promotion

## Quick Start

```bash
# Install
python -m venv bot_venv
bot_venv\Scripts\activate  # Windows
# or: source bot_venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure
cp bot_config.env.example bot_config.env
# Edit bot_config.env with your Discord token

# Run
python main.py
```

**Important:** Create `Annaway_Admin` and `Annaway_Manager` roles in your Discord server before using the bot.

## Documentation

- **[Complete Setup Guide](README_ANNAWAY.md)** - Full installation and configuration
- **[Refactoring Documentation](ANNAWAY_REFACTORING.md)** - Technical details of changes
- **[Permission System](PERMISSION_SYSTEM.md)** - Role-based access control
- **[Guild Isolation](migrations/002_complete_guild_isolation.sql)** - Multi-guild architecture

## Key Features

- 🏰 Alliance management per Discord server
- 👥 Member tracking and management
- 🎁 Automatic gift code redemption
- 📊 Statistics and reporting
- 🔐 Simple role-based permissions
- 🌍 Multi-guild data isolation

## Migration from Original

If you're upgrading from the original bot:

1. Back up your database: `cp -r db/ db_backup/`
2. Run migration: `python migrations/001_add_guild_isolation.py`
3. Create required Discord roles: `Annaway_Admin`, `Annaway_Manager`
4. Verify guild isolation: Test in multiple servers

## Original Project

This fork is based on: https://github.com/105405003/annaway-wos-giftcode-bot

The original project is maintained by the Whiteout Survival community. This Annaway fork is independently maintained with significant architectural changes for multi-guild support.

## License

See [LICENSE](LICENSE) file. This project retains the original license and attribution as required by the license terms.

---

**Maintained by Annaway Studio**

For issues with this fork, please open a GitHub issue.
