# Annaway WOS Gift Code Bot - Refactoring Documentation

## Overview

This is a customized fork of the Whiteout Survival Discord Bot, refactored for Annaway Studio with:
- **Multi-guild data separation** - Each Discord server sees only its own alliances
- **Simple role-based permissions** - Only `Annaway_Admin` and `Annaway_Manager` roles can manage
- **Clean, self-contained codebase** - No auto-update system, minimal dependencies
- **Annaway branding** - Neutral branding without original project promotion

## Key Changes from Original

### 1. Multi-Guild Data Separation

**Problem:** The original bot shared alliance data across all guilds using the same bot token.

**Solution:**
- Added `discord_server_id` column to `alliance_list` table
- All alliance queries now filter by `guild_id`
- Migration script: `migrations/001_add_guild_isolation.py`
- Database indexes for performance

**Implementation:**
```python
# Before (wrong - shows all alliances)
cursor.execute("SELECT * FROM alliance_list")

# After (correct - only this guild's alliances)
guild_id = interaction.guild.id
cursor.execute("SELECT * FROM alliance_list WHERE discord_server_id = ?", (guild_id,))
```

**Files Modified:**
- `cogs/alliance.py` - Core alliance management
- `cogs/gift_operations.py` - Gift code redemption
- `cogs/statistics.py` - Statistics filtering
- `cogs/changes.py` - Change log filtering
- `cogs/alliance_member_operations.py` - Member operations
- All other cogs that query alliances

### 2. Permission System

**Old System:** Complex permission database with multiple levels, hard to understand.

**New System:** Simple role-based checks using Discord roles.

**Roles:**
- **`Annaway_Admin`** - Full management permissions (create/edit/delete alliances, manage settings)
- **`Annaway_Manager`** - Can manage members and gift codes, view statistics

**Implementation:**

New utility module: `utils/permissions.py`

```python
from utils.permissions import requires_annaway_role, check_permission

# For slash commands
@app_commands.command()
@requires_annaway_role()
async def my_command(self, interaction: discord.Interaction):
    # Only Annaway_Admin or Annaway_Manager can run this
    pass

# For admin-only commands
@app_commands.command()
@requires_annaway_role(admin_only=True)
async def admin_command(self, interaction: discord.Interaction):
    # Only Annaway_Admin can run this
    pass

# For button/select callbacks
@discord.ui.button(...)
@requires_annaway_role_button()
async def my_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    pass
```

**Permission Checks:**
- All management commands check for required roles
- DM commands are blocked (show "This command can only be used in a server")
- Ephemeral error messages for unauthorized attempts

### 3. Removed Auto-Update System

**Removed:**
- `cogs/bot_operations.py::check_for_updates()` method
- Auto-download from GitHub releases
- Update prompts in startup
- Connection to original project's update servers

**Why:** This fork is self-contained and doesn't need to auto-update from the original project.

**Status:** Already disabled in current codebase (line 439-445 in `main.py`)

### 4. Clean File Structure

**Removed/Ignored:**
- All `.zip` packaging files
- `pack_*.py` scripts (original project's deployment tools)
- `hotfix_*.py` scripts
- `fix_*.py` diagnostic scripts
- `完整診斷腳本.sh`
- Test diagnostic packages

**Added:**
- `utils/` directory for clean helper modules
  - `utils/permissions.py` - Permission checking
  - `utils/guild_helpers.py` - Guild context utilities
- `.gitignore` updated to exclude packaging scripts
- This documentation file

**Kept:**
- Runtime code (`cogs/`, `main.py`)
- Database files (gitignored, required at runtime)
- Configuration examples
- Original LICENSE (required by license terms)

### 5. Configuration

**Environment Variables** (`.env` or `bot_config.env`):
```env
# Required
DISCORD_TOKEN=your_bot_token_here

# Optional
TWOCAPTCHA_API_KEY=your_2captcha_key_here
LANGUAGE=zh_TW
DEBUG_MODE=false
```

**Per-Guild Settings** (stored in database):
- Default alliance for the guild
- Log channel ID for redemption results
- Language preferences

### 6. Safety Features

**Guild Context Checks:**
```python
from utils.permissions import check_guild_context

async def my_command(self, interaction: discord.Interaction):
    if not await check_guild_context(interaction):
        return  # Error already sent to user
```

**No Alliance Found:**
```python
alliances = cursor.execute(
    "SELECT * FROM alliance_list WHERE discord_server_id = ?",
    (interaction.guild.id,)
).fetchall()

if not alliances:
    await interaction.response.send_message(
        "No alliances configured for this server. Please create one first.",
        ephemeral=True
    )
    return
```

**All errors are ephemeral** - No public spam, only the user sees the error.

## Migration Guide

### For Existing Installations

1. **Backup your database:**
   ```bash
   cp -r db/ db_backup/
   ```

2. **Run the guild isolation migration:**
   ```bash
   python migrations/001_add_guild_isolation.py
   ```

3. **Assign orphaned alliances to guilds:**
   - Check for alliances with `discord_server_id = -1`
   - Manually update them to the correct guild ID:
   ```sql
   UPDATE alliance_list 
   SET discord_server_id = YOUR_GUILD_ID 
   WHERE alliance_id = ALLIANCE_ID;
   ```

4. **Set up Discord roles:**
   - Create `Annaway_Admin` role in your Discord server
   - Create `Annaway_Manager` role
   - Assign users to appropriate roles

5. **Update bot permissions:**
   - Enable "Server Members Intent" in Discord Developer Portal
   - This is required for role checking

### For Fresh Installations

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   python -m venv bot_venv
   source bot_venv/bin/activate  # or bot_venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Configure:**
   ```bash
   cp bot_config.env.example bot_config.env
   # Edit bot_config.env with your token
   ```

4. **Create Discord roles:**
   - `Annaway_Admin`
   - `Annaway_Manager`

5. **Run the bot:**
   ```bash
   python main.py
   ```

## Testing Multi-Guild Separation

1. **Invite bot to multiple servers**
2. **In Server A:**
   - Create alliance "Test A"
   - Add members
3. **In Server B:**
   - Create alliance "Test B"
   - Verify "Test A" is NOT visible
   - Add members
4. **Verify:**
   - Each server only sees its own alliances in dropdowns
   - Gift code redemptions only affect current server's alliances
   - Statistics only show current server's data

## Database Schema

### alliance_list Table

```sql
CREATE TABLE alliance_list (
    alliance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    discord_server_id INTEGER,  -- Guild ID for isolation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alliance_guild ON alliance_list(discord_server_id);
CREATE INDEX idx_alliance_guild_name ON alliance_list(discord_server_id, name);
```

### Orphaned Alliances

Alliances with `discord_server_id = -1` or `NULL` are considered orphaned:
- Created before the guild isolation feature
- Need manual assignment to a guild
- Won't show up in any guild's lists until fixed

## Known Issues & TODOs

- [ ] Some cogs may still have un-isolated queries (see grep output in refactoring)
- [ ] Need to add guild_id checks to ALL alliance-related queries
- [ ] Some error messages still in Chinese (need i18n review)
- [ ] Logging is very verbose (consider log levels/rotation)
- [ ] Original branding references may still exist in some cogs

## Support & Contributing

This is a private fork for Annaway Studio. 

Original project: https://github.com/105405003/annaway-wos-giftcode-bot

## License

See `LICENSE` file. This project retains the original license and attribution as required.

