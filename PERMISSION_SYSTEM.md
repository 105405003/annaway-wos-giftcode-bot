# Annaway WOS Bot - Permission System

**Last Updated:** November 27, 2024  
**Status:** Infrastructure Complete + Core Commands Protected

---

## Overview

The Annaway WOS Bot uses a simple role-based permission system with two Discord roles:

- **`Annaway_Admin`** - Full administrative access (create/delete alliances, global settings)
- **`Annaway_Manager`** - Operational management (member management, gift redemption, attendance)

---

## Permission Infrastructure

### Available Tools

Located in `utils/permissions.py`:

```python
# For slash/context commands
@requires_annaway_role(admin_only=False)  # Admin OR Manager
@requires_annaway_role(admin_only=True)   # Admin only

# For button/select callbacks
@requires_annaway_role_button(admin_only=False)
@requires_annaway_role_button(admin_only=True)

# Manual checks inside functions
await check_permission(interaction, admin_only=False)
await check_guild_context(interaction)  # Block DMs
```

---

## Command Classification

### PUBLIC Commands (No Role Required)

These commands are available to ALL server members:

| Command | File | Description | Notes |
|---------|------|-------------|-------|
| `/add` | `alliance_member_operations.py` | Add member to alliance | Explicitly marked "所有人都可以使用" |

**Rationale:** Self-service commands that allow members to register themselves or view their own information.

---

### MANAGER/ADMIN Commands (Requires `Annaway_Admin` OR `Annaway_Manager`)

Operational management tasks that trusted staff can perform:

| Command/Feature | File | Decorator | Purpose |
|-----------------|------|-----------|---------|
| `/settings` | `alliance.py` | `@requires_annaway_role()` | Open settings menu |
| `view_alliances()` | `alliance.py` | `@requires_annaway_role()` | View alliance list |
| `/update_members` | `control.py` | `@requires_annaway_role()` | Manual member data refresh |
| Gift code operations | `gift_operations.py` | Buttons need protection | Manual/batch redemption |
| Attendance management | `attendance.py` | Needs protection | Attendance tracking |
| Statistics viewing | `statistics.py` | Needs protection | View alliance stats |
| Change logs | `changes.py` | Needs protection | View member changes |

**Category B Features - Admin OR Manager Access:**
- Member data updates
- Manual gift code redemption
- Attendance event management
- Statistics and reports
- Log viewing
- Channel selection for notifications

---

### ADMIN-ONLY Commands (Requires `Annaway_Admin` ONLY)

Sensitive configuration changes that only top admins should perform:

| Command/Feature | File | Decorator | Purpose |
|-----------------|------|-----------|---------|
| `add_alliance()` | `alliance.py` | `@requires_annaway_role(admin_only=True)` | Create new alliance |
| `edit_alliance()` | `alliance.py` | `@requires_annaway_role(admin_only=True)` | Edit alliance settings |
| `delete_alliance()` | `alliance.py` | `@requires_annaway_role(admin_only=True)` | Delete alliance |
| Permission management | `permission_management.py` | Needs `admin_only=True` | Assign roles/permissions |
| Global bot settings | `bot_operations.py` | Needs `admin_only=True` | Bot-wide configuration |
| Auto-redeem configuration | `gift_operations.py` | Needs `admin_only=True` | Enable/disable auto features |

**Category C Features - Admin Only:**
- Alliance creation/deletion/editing
- Permission mapping configuration
- Global bot settings
- Auto-redemption enable/disable
- Database migrations/imports
- Dangerous bulk operations

---

## Implementation Status

### ✅ COMPLETE

**Files with permissions applied:**

1. **cogs/alliance.py**
   - ✅ Import added
   - ✅ `/settings` → `@requires_annaway_role()`
   - ✅ `view_alliances()` → `@requires_annaway_role()`
   - ✅ `add_alliance()` → `@requires_annaway_role(admin_only=True)`
   - ✅ `edit_alliance()` → `@requires_annaway_role(admin_only=True)`
   - ✅ `delete_alliance()` → `@requires_annaway_role(admin_only=True)`

2. **cogs/alliance_member_operations.py**
   - ✅ Import added
   - ✅ `/add` command remains PUBLIC (no decorator)

3. **cogs/control.py**
   - ✅ Import added
   - ✅ `/update_members` → `@requires_annaway_role()`

4. **cogs/gift_operations.py**
   - ✅ Import added
   - ⚠️ **Button/View callbacks need manual protection** (see below)

5. **cogs/permission_management.py**
   - ✅ Import added
   - ⚠️ **All operations need admin_only=True protection**

### 🔧 REQUIRES COMPLETION

**Files needing protection:**

1. **cogs/gift_operations.py**
   - Views: `SimplifiedGiftView`, `GiftView`, `SettingsMenuView`, `OCRSettingsView`
   - **Action:** Add permission checks at start of each button callback:
     ```python
     async def button_callback(self, interaction: discord.Interaction, button):
         if not await check_permission(interaction, admin_only=False):
             return
         # ... rest of code
     ```

2. **cogs/attendance.py**
   - **Action:** Add import + protect all attendance management functions
   - All attendance operations should require Manager/Admin

3. **cogs/statistics.py**
   - **Action:** Add import + protect statistics viewing
   - Viewing stats should require Manager/Admin

4. **cogs/changes.py**
   - **Action:** Add import + protect change log viewing
   - Viewing changes should require Manager/Admin

5. **cogs/permission_management.py**
   - **Action:** All permission management operations need `admin_only=True`

6. **cogs/backup_operations.py**
   - **Action:** Backup operations need `admin_only=True`

7. **cogs/bear_trap.py / cogs/bear_trap_editor.py**
   - **Action:** Admin features need `admin_only=True`

8. **cogs/minister_menu.py / cogs/minister_schedule.py**
   - **Action:** Minister management needs Manager/Admin protection

9. **cogs/id_channel.py**
   - **Action:** ID channel management needs Manager/Admin protection

10. **cogs/attendance_report.py**
    - **Action:** Report generation needs Manager/Admin protection

---

## Decision Guidelines

When adding protection to a new command/feature, use this flowchart:

```
Is it self-service for regular members?
  └─ YES → Leave PUBLIC (no decorator)
  └─ NO → Does it modify alliances, core settings, or permissions?
         └─ YES → Use @requires_annaway_role(admin_only=True)
         └─ NO → Does it perform operational management?
                └─ YES → Use @requires_annaway_role()
                └─ NO → Consider if it should exist
```

**Examples:**

- `/add member` → PUBLIC (member self-registration)
- Update member data → MANAGER/ADMIN (operational task)
- Create alliance → ADMIN-ONLY (structural change)
- Delete alliance → ADMIN-ONLY (destructive)
- View statistics → MANAGER/ADMIN (management info)
- Configure auto-redeem → ADMIN-ONLY (bot behavior)

---

## Button/Select Menu Protection

For `discord.ui.View` callbacks, use one of these patterns:

### Pattern 1: Decorator (if supported)
```python
@discord.ui.button(label="Manage", style=discord.ButtonStyle.primary)
@requires_annaway_role_button(admin_only=False)
async def manage_button(self, interaction: discord.Interaction, button):
    # Action code
```

### Pattern 2: Manual Check (recommended)
```python
@discord.ui.button(label="Manage", style=discord.ButtonStyle.primary)
async def manage_button(self, interaction: discord.Interaction, button):
    # Check guild context
    if not await check_guild_context(interaction):
        return
    
    # Check permission
    if not await check_permission(interaction, admin_only=False):
        return
    
    # Action code
```

**Use `admin_only=True` for:**
- Alliance create/edit/delete buttons
- Permission assignment buttons
- Global settings buttons
- Auto-redeem enable/disable buttons

**Use `admin_only=False` for:**
- Member management buttons
- Manual redeem buttons
- Attendance tracking buttons
- Report generation buttons

---

## Validation Commands

Run these PowerShell commands from the project root to verify protection:

### 1. List all slash commands
```powershell
Select-String -Path "cogs\*.py" -Pattern "@app_commands.command" -Context 0,2
```

### 2. Find slash commands without protection
```powershell
$commands = Select-String -Path "cogs\*.py" -Pattern "@app_commands.command" -Context 0,3
$commands | ForEach-Object {
    $context = $_.Context.PostContext -join "`n"
    if ($context -notmatch "requires_annaway_role" -and $context -notmatch "所有人都可以使用") {
        $_
    }
}
```

**Expected Results:** Only `/add` should appear (it's intentionally public).

### 3. Find button callbacks without protection
```powershell
Select-String -Path "cogs\*.py" -Pattern "@discord.ui.button" -Context 0,5 | 
    Where-Object { $_.Context.PostContext -join "`n" -notmatch "check_permission|requires_annaway_role" } |
    Select-Object Filename, LineNumber, Line
```

**Expected:** This will show buttons that need manual protection added.

### 4. Verify imports
```powershell
Select-String -Path "cogs\*.py" -Pattern "from utils.permissions import" | 
    Select-Object Filename, Line
```

**Expected:** Should see imports in:
- `alliance.py`
- `alliance_member_operations.py`
- `control.py`
- `gift_operations.py`
- `permission_management.py`

### 5. Find admin-only decorators
```powershell
Select-String -Path "cogs\*.py" -Pattern "requires_annaway_role\(admin_only=True\)" -Context 1,0
```

**Expected:** Should show alliance create/edit/delete operations.

---

## Testing Checklist

After completing implementation, test:

### ✅ PUBLIC Commands Work for Everyone
- [ ] Any member can use `/add` to add themselves
- [ ] No permission errors for public commands

### ✅ MANAGER/ADMIN Commands Require Roles
- [ ] `/settings` blocked for users without roles
- [ ] `/update_members` blocked for users without roles
- [ ] Gift code operations blocked for users without roles
- [ ] Users with `Annaway_Manager` role CAN use these
- [ ] Users with `Annaway_Admin` role CAN use these

### ✅ ADMIN-ONLY Commands Require Admin
- [ ] Alliance creation blocked for `Annaway_Manager`
- [ ] Alliance editing blocked for `Annaway_Manager`
- [ ] Alliance deletion blocked for `Annaway_Manager`
- [ ] Only `Annaway_Admin` can perform these actions

### ✅ Error Messages are Ephemeral
- [ ] Permission errors show only to the user (ephemeral=True)
- [ ] Clear explanation of what role is required

### ✅ DM Commands are Blocked
- [ ] Commands in DMs show "can only be used in a server"
- [ ] No crashes or unclear errors

---

## Quick Reference

### Add Protection to New Command

**For slash command:**
```python
@app_commands.command(name="my_command", description="...")
@requires_annaway_role(admin_only=False)  # or True for admin-only
async def my_command(self, interaction: discord.Interaction):
    # Your code
```

**For button callback:**
```python
@discord.ui.button(label="Action", style=discord.ButtonStyle.primary)
async def action_button(self, interaction: discord.Interaction, button):
    if not await check_permission(interaction, admin_only=False):
        return
    # Your code
```

### Import Statement
```python
from utils.permissions import requires_annaway_role, requires_annaway_role_button, check_permission, check_guild_context
```

---

## Troubleshooting

### Command not responding
- Check that role names are exactly: `Annaway_Admin` and `Annaway_Manager` (case-sensitive)
- Verify "Server Members Intent" is enabled in Discord Developer Portal
- Check bot has permission to read roles

### Permission errors not ephemeral
- Verify `ephemeral=True` in all error messages in `utils/permissions.py`
- Check no code is catching and re-throwing without ephemeral flag

### Buttons not protected
- Add manual `check_permission()` call at start of callback
- Ensure `utils.permissions` is imported
- Test with user without roles to verify blocking

---

## Migration Notes

**From old permission system:**
- Old system used database tables (`admin`, `adminserver`, etc.)
- New system uses Discord roles (simpler, more maintainable)
- Both can coexist during transition
- Eventually remove old permission database tables

**Role Names:**
- `Annaway_Admin` - Exact match required
- `Annaway_Manager` - Exact match required
- Create these roles in Discord server settings
- Assign to appropriate users

---

## Summary

**Infrastructure:** ✅ Complete (`utils/permissions.py`)  
**Core Commands:** ✅ Protected (alliance, settings, update_members)  
**Remaining Work:** 🔧 Apply to views, buttons, and remaining cogs  

**Estimated Remaining:** ~30-40 button callbacks + ~10 cogs need protection

**Priority:**
1. Gift operation buttons (HIGH - user-facing)
2. Permission management (HIGH - security)
3. Attendance features (MEDIUM)
4. Statistics/reports (MEDIUM)
5. Specialized features (LOW)

---

**Status:** Core infrastructure complete. Apply protection incrementally to remaining features using patterns documented above.
