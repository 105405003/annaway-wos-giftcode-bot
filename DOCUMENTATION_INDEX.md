# Documentation Index - Annaway WOS Gift Code Bot

**Quick Navigation:** Find the right documentation for your needs.

---

## 🚀 Getting Started

### For First-Time Setup
👉 **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- Install dependencies
- Configure bot token
- Create Discord roles
- Run the bot

### For Complete Setup & Usage
👉 **[README_ANNAWAY.md](README_ANNAWAY.md)** - Full documentation
- Detailed installation steps
- Permission system explanation
- Command reference
- Troubleshooting guide
- Multi-guild testing

---

## 📖 Understanding the Refactoring

### High-Level Overview
👉 **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Executive summary
- What was changed and why
- Key architectural decisions
- Testing checklist
- Migration path for existing users

### Technical Deep-Dive
👉 **[ANNAWAY_REFACTORING.md](ANNAWAY_REFACTORING.md)** - Technical documentation
- Multi-guild data separation explained
- Permission system implementation
- Removed features (auto-update)
- Database schema
- Code examples and patterns

### Current Status
👉 **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - What's done vs pending
- Completed tasks ✅
- In-progress tasks 🔧
- Pending tasks ⏳
- Priority order
- File-by-file breakdown

---

## 🛠️ For Developers

### Permission System
👉 **[PERMISSION_SYSTEM.md](PERMISSION_SYSTEM.md)** - Original permission docs
- Role descriptions
- Permission levels
- Usage examples

👉 **[utils/permissions.py](utils/permissions.py)** - New permission utilities
- `@requires_annaway_role()` decorator
- `check_permission()` helper
- `has_annaway_role()` function

### Multi-Guild Architecture
👉 **[migrations/002_complete_guild_isolation.sql](migrations/002_complete_guild_isolation.sql)** - SQL reference
- Query patterns to fix
- Validation queries
- Testing procedures

👉 **[migrations/apply_guild_isolation_fixes.py](migrations/apply_guild_isolation_fixes.py)** - Scanner tool
```bash
python migrations/apply_guild_isolation_fixes.py --scan
```

### Database Migrations
👉 **[migrations/001_add_guild_isolation.py](migrations/001_add_guild_isolation.py)** - Guild isolation migration
```bash
python migrations/001_add_guild_isolation.py
```

---

## 🧹 Maintenance & Tools

### Cleanup Tool
👉 **[cleanup_packaging_files.py](cleanup_packaging_files.py)** - Remove unnecessary files
```bash
# Preview what would be deleted (safe)
python cleanup_packaging_files.py

# Actually delete files
python cleanup_packaging_files.py --live
```

### Configuration
👉 **[bot_config.env.example](bot_config.env.example)** - Configuration template
- Copy to `bot_config.env`
- Add your Discord token
- Optional: 2CAPTCHA API key

---

## 📊 Quick Reference Charts

### Documentation by Purpose

| I want to... | Read this... |
|--------------|--------------|
| Get bot running quickly | [QUICK_START.md](QUICK_START.md) |
| Understand all features | [README_ANNAWAY.md](README_ANNAWAY.md) |
| Know what changed | [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) |
| See technical details | [ANNAWAY_REFACTORING.md](ANNAWAY_REFACTORING.md) |
| Check progress | [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) |
| Learn permissions | [PERMISSION_SYSTEM.md](PERMISSION_SYSTEM.md) |
| Fix guild queries | [migrations/002_complete_guild_isolation.sql](migrations/002_complete_guild_isolation.sql) |

### Documentation by Role

| If you are... | Start here... |
|---------------|---------------|
| **Server Admin** | [QUICK_START.md](QUICK_START.md) → [README_ANNAWAY.md](README_ANNAWAY.md) |
| **Bot User** | [README_ANNAWAY.md](README_ANNAWAY.md) (Commands section) |
| **Developer** | [ANNAWAY_REFACTORING.md](ANNAWAY_REFACTORING.md) → [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) |
| **Maintainer** | [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) → All technical docs |

---

## 🔗 External Resources

- **Discord Developer Portal:** https://discord.com/developers/applications
- **Discord Bot Permissions:** https://discord.com/developers/docs/topics/permissions
- **Original Project:** https://github.com/105405003/annaway-wos-giftcode-bot
- **2CAPTCHA (optional):** https://2captcha.com/

---

## 📂 File Structure Overview

```
annaway-wos-giftcode-bot/
│
├── 📘 QUICK_START.md           # ← Start here!
├── 📘 README_ANNAWAY.md        # Complete guide
├── 📘 REFACTORING_SUMMARY.md   # What changed
├── 📘 ANNAWAY_REFACTORING.md   # Technical details
├── 📘 IMPLEMENTATION_STATUS.md # Current status
├── 📘 DOCUMENTATION_INDEX.md   # This file
│
├── cogs/                       # Bot features
│   ├── alliance.py             # Alliance management
│   ├── gift_operations.py      # Gift code redemption
│   └── ...
│
├── utils/                      # Helper utilities
│   ├── permissions.py          # Permission checking
│   └── guild_helpers.py        # Guild context helpers
│
├── migrations/                 # Database migrations
│   ├── 001_add_guild_isolation.py
│   ├── 002_complete_guild_isolation.sql
│   └── apply_guild_isolation_fixes.py
│
├── db/                         # SQLite databases (gitignored)
├── log/                        # Log files (gitignored)
│
├── main.py                     # Bot entry point
├── bot_config.env.example      # Config template
├── requirements.txt            # Python dependencies
├── cleanup_packaging_files.py  # Cleanup tool
│
└── LICENSE                     # License and attribution
```

---

## 🎯 Common Tasks

### Initial Setup
1. Read: [QUICK_START.md](QUICK_START.md)
2. Follow steps to install and configure
3. Create Discord roles
4. Run bot

### Troubleshooting
1. Check: [README_ANNAWAY.md](README_ANNAWAY.md) Troubleshooting section
2. Review: `log/` directory for detailed logs
3. Verify: Discord roles and permissions set correctly

### Development
1. Read: [ANNAWAY_REFACTORING.md](ANNAWAY_REFACTORING.md)
2. Check: [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for pending tasks
3. Use: Scanner tools before modifying queries
4. Test: In multiple Discord servers

### Migration from Original
1. Backup: `cp -r db/ db_backup/`
2. Run: `python migrations/001_add_guild_isolation.py`
3. Fix: Orphaned alliances (see [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md))
4. Create: Discord roles
5. Test: Multi-guild separation

---

## 📝 Documentation Standards

When updating docs:
- ✅ Keep examples clear and tested
- ✅ Include code snippets with context
- ✅ Update IMPLEMENTATION_STATUS.md with changes
- ✅ Cross-reference related documents
- ✅ Use clear headings and formatting

---

## 🆘 Getting Help

1. **Check logs:**
   - Console output
   - Files in `log/` directory

2. **Review documentation:**
   - This index → find relevant doc
   - Read troubleshooting sections

3. **Search codebase:**
   ```bash
   # Find alliance queries
   python migrations/apply_guild_isolation_fixes.py --scan
   
   # Search for specific patterns
   grep -r "pattern" cogs/
   ```

4. **Open GitHub issue:**
   - Include error messages
   - Steps to reproduce
   - Relevant log excerpts
   - What you've already tried

---

## 🎓 Learning Path

### Beginner (Just want to use the bot)
1. [QUICK_START.md](QUICK_START.md)
2. [README_ANNAWAY.md](README_ANNAWAY.md) - Commands section
3. Test in your Discord server

### Intermediate (Want to understand how it works)
1. [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
2. [ANNAWAY_REFACTORING.md](ANNAWAY_REFACTORING.md)
3. [PERMISSION_SYSTEM.md](PERMISSION_SYSTEM.md)
4. Browse `cogs/` code

### Advanced (Want to modify or maintain)
1. All above documents
2. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
3. [migrations/002_complete_guild_isolation.sql](migrations/002_complete_guild_isolation.sql)
4. Use scanner tools
5. Read source code with documentation

---

**Last Updated:** November 27, 2024

**Maintained by:** Annaway Studio

**Questions?** Open a GitHub issue or check the troubleshooting sections in the main documentation.

