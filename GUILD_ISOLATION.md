# Guild Isolation Implementation Guide

## Overview

This document describes the multi-guild data isolation system implemented in the Annaway WOS Giftcode Bot. The system ensures that each Discord server (guild) can only see and interact with its own alliances, members, and data.

---

## Core Principle

**Every query that reads or writes alliance-related data MUST filter by `discord_server_id`.**

This applies to:
- `alliance_list` table queries
- Any JOIN operations involving alliances
- Alliance selection menus and dropdowns
- Admin/Manager permission checks that determine which alliances a user can manage

---

## Database Schema

### alliance_list Table

```sql
CREATE TABLE alliance_list (
    alliance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    discord_server_id INTEGER,  -- Guild ID for isolation (CRITICAL!)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alliance_guild ON alliance_list(discord_server_id);
CREATE INDEX idx_alliance_guild_name ON alliance_list(discord_server_id, name);
```

**Key Points:**
- `discord_server_id` stores the Discord guild ID (e.g., `1398071974692913324`)
- `discord_server_id = -1` or `NULL` indicates orphaned alliances (created before guild isolation)
- All queries MUST include `WHERE discord_server_id = ?`

###Other Guild-Sensitive Tables

These tables also store guild context (though not always with `discord_server_id` column):
- `adminserver` - Maps admins to specific alliances
- `alliancesettings` - Alliance-specific settings (channel_id, interval)
- `giftcode_channel` - Gift code channels per alliance
- Alliance members are stored in `users` table with `alliance` field (alliance_id as string)

---

## Query Patterns

### ✅ CORRECT Patterns

#### 1. Get All Alliances for Current Guild

```python
guild_id = interaction.guild.id
cursor.execute(
    "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
    (guild_id,)
)
```

#### 2. Get Alliance by ID (with Guild Validation)

```python
guild_id = interaction.guild.id
cursor.execute(
    "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?",
    (alliance_id, guild_id)
)
result = cursor.fetchone()
if not result:
    await interaction.response.send_message("❌ 找不到聯盟或您無權查看", ephemeral=True)
    return
alliance_name = result[0]
```

#### 3. Check if Alliance Name Exists (within Guild)

```python
guild_id = interaction.guild.id
cursor.execute(
    "SELECT alliance_id FROM alliance_list WHERE name = ? AND discord_server_id = ?",
    (alliance_name, guild_id)
)
```

#### 4. Get Admin's Alliances (with Guild Filter)

```python
guild_id = interaction.guild.id

# Get special alliances assigned to this admin
cursor.execute("SELECT alliances_id FROM adminserver WHERE admin = ?", (user_id,))
alliance_ids = [row[0] for row in cursor.fetchall()]

if alliance_ids:
    placeholders = ','.join('?' * len(alliance_ids))
    cursor.execute(f"""
        SELECT alliance_id, name FROM alliance_list 
        WHERE alliance_id IN ({placeholders})
        AND discord_server_id = ?
        ORDER BY name
    """, alliance_ids + [guild_id])
else:
    # No specific alliances assigned: return all in this guild
    cursor.execute("""
        SELECT alliance_id, name FROM alliance_list
        WHERE discord_server_id = ?
        ORDER BY name
    """, (guild_id,))
```

### ❌ WRONG Patterns (Security Vulnerabilities)

#### 1. Missing Guild Filter

```python
# BAD: Shows alliances from ALL guilds
cursor.execute("SELECT * FROM alliance_list")

# BAD: Only filters by name, not guild
cursor.execute("SELECT alliance_id FROM alliance_list WHERE name = ?", (name,))

# BAD: Assumes alliance_id is globally unique (it is, but guild check is missing)
cursor.execute("SELECT name FROM alliance_list WHERE alliance_id = ?", (alliance_id,))
```

#### 2. Global Admin Bypass

```python
# BAD: Global admins should still only see current guild's alliances
if is_global_admin:
    cursor.execute("SELECT * FROM alliance_list")  # Shows all guilds!
else:
    cursor.execute("SELECT * FROM alliance_list WHERE discord_server_id = ?", (guild_id,))
```

**Correct approach:**
```python
# Even global admins must be filtered by guild
guild_id = interaction.guild.id
cursor.execute("SELECT * FROM alliance_list WHERE discord_server_id = ?", (guild_id,))
```

---

## Files Fixed (2025-11-28 Refactor)

### High Priority (User-Facing Features)

1. ✅ **cogs/alliance.py**
   - Fixed: Alliance name uniqueness check now scoped to guild (lines ~958, ~1147)
   - Fixed: Delete alliance callback validates guild ownership (line ~1326)
   
2. ✅ **cogs/gift_operations.py**
   - Fixed: Global admin now filters by guild_id (line ~2535)
   - Fixed: Admin's special alliances filtered by guild (line ~2613)

3. ✅ **cogs/alliance_member_operations.py**
   - Fixed: All member list displays validate guild (lines ~569, ~625, ~681, ~737, ~1329)

4. ✅ **cogs/statistics.py**
   - Fixed: Furnace distribution validates guild (line ~402)
   - Fixed: Alliance detail report validates guild (line ~493)

5. ✅ **cogs/changes.py**
   - Fixed: All change history queries validate guild (lines ~339, ~394, ~440, ~639)

### Medium Priority (Admin Features)

6. **cogs/bot_operations.py** - Already has guild isolation
7. **cogs/permission_management.py** - Already has guild isolation
8. **cogs/logsystem.py** - Log channels are guild-specific

### Low Priority (Specialized Features)

9. **cogs/attendance.py** - Uses alliance_id but should validate guild
10. **cogs/minister_menu.py** - Ministerfeature uses alliances
11. **cogs/id_channel.py** - ID channel feature uses alliances
12. **cogs/wel.py** - Welcome messages per alliance
13. **cogs/olddb.py** - Legacy import (special case)

---

## Standard Code Pattern

For any new feature or bugfix involving alliances:

```python
async def some_alliance_operation(self, interaction: discord.Interaction, alliance_id: int = None):
    """
    Template for guild-safe alliance operations.
    """
    # Step 1: Get guild_id from interaction
    guild_id = interaction.guild.id if interaction.guild else -1
    
    # Step 2: If querying by alliance_id, validate guild ownership
    if alliance_id:
        cursor.execute(
            "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?",
            (alliance_id, guild_id)
        )
        result = cursor.fetchone()
        if not result:
            await interaction.response.send_message(
                "❌ 找不到聯盟或您無權操作",
                ephemeral=True
            )
            return
        alliance_name = result[0]
    
    # Step 3: If listing alliances, filter by guild
    else:
        cursor.execute(
            "SELECT alliance_id, name FROM alliance_list WHERE discord_server_id = ? ORDER BY name",
            (guild_id,)
        )
        alliances = cursor.fetchall()
    
    # Step 4: Proceed with operation...
```

---

## Testing Guild Isolation

### Setup

1. Create two test Discord servers:
   - **Guild A** (e.g., "Test Server Alpha")
   - **Guild B** (e.g., "Test Server Beta")

2. Invite the bot to both servers

3. Create Discord roles in both:
   - `Annaway_Admin`
   - `Annaway_Manager`

4. Assign roles to test users

### Test Cases

#### Test 1: Alliance Visibility

**In Guild A:**
```
/settings → Alliance Operations → View Alliances
Expected: Only see alliances with discord_server_id = Guild A's ID
```

**In Guild B:**
```
/settings → Alliance Operations → View Alliances
Expected: Only see alliances with discord_server_id = Guild B's ID
```

**Result:** Guild A and Guild B should have completely separate alliance lists.

#### Test 2: Alliance Creation

**In Guild A:**
```
/settings → Alliance Operations → Add Alliance
Create alliance named "Alpha Test Alliance"
```

**In Guild B:**
```
/settings → Alliance Operations → View Alliances
Expected: "Alpha Test Alliance" should NOT appear
```

#### Test 3: Member Operations

**In Guild A:**
```
/settings → Member Operations → Add Member
Add member with FID 111111 to "Alpha Test Alliance"
```

**In Guild B:**
```
/settings → Member Operations → View Members
Expected: Member 111111 should NOT appear in any list
```

#### Test 4: Gift Code Operations

**In Guild A:**
```
/settings → Gift Code Operations → Create Gift Code
Create code "TESTA123" for "Alpha Test Alliance"
```

**In Guild B:**
```
/settings → Gift Code Operations
Expected: Code "TESTA123" should NOT be visible
```

#### Test 5: Statistics

**In Guild A:**
```
/settings → Other Features → Statistics
View furnace distribution for "Alpha Test Alliance"
```

**In Guild B:**
```
/settings → Other Features → Statistics
Expected: "Alpha Test Alliance" should NOT be in the dropdown
```

#### Test 6: Cross-Guild ID Injection (Security Test)

**Setup:**
- In Guild A, create alliance with ID 1
- In Guild B, try to access alliance ID 1 via direct interaction

**Expected:**
- All operations should reject with "找不到聯盟或您無權操作"
- No data from Guild A should leak to Guild B

---

## Migration Guide

If you have existing alliances without `discord_server_id`:

1. **Identify orphaned alliances:**
   ```sql
   SELECT alliance_id, name, discord_server_id
   FROM alliance_list
   WHERE discord_server_id IS NULL OR discord_server_id = -1;
   ```

2. **Manually assign to guild:**
   ```sql
   UPDATE alliance_list
   SET discord_server_id = <your_guild_id>
   WHERE alliance_id IN (1, 2, 3, ...);
   ```

3. **Verify:**
   ```sql
   SELECT discord_server_id, COUNT(*) as count, GROUP_CONCAT(name, ', ') as names
   FROM alliance_list
   GROUP BY discord_server_id
   ORDER BY count DESC;
   ```

---

## Common Pitfalls

### Pitfall 1: Trusting alliance_id Alone

❌ **Wrong:**
```python
cursor.execute("SELECT name FROM alliance_list WHERE alliance_id = ?", (alliance_id,))
```

✅ **Correct:**
```python
guild_id = interaction.guild.id
cursor.execute(
    "SELECT name FROM alliance_list WHERE alliance_id = ? AND discord_server_id = ?",
    (alliance_id, guild_id)
)
```

**Why:** Even though `alliance_id` is globally unique, a malicious user from Guild B could try to access Guild A's alliance by crafting a custom interaction with a different `alliance_id`.

### Pitfall 2: Global Admin Privilege Escalation

❌ **Wrong:**
```python
if is_global_admin:
    return all_alliances_from_all_guilds()
```

✅ **Correct:**
```python
# Global admin still respects guild boundaries
guild_id = interaction.guild.id
return get_alliances_for_guild(guild_id)
```

**Why:** A global admin in Guild A should not see Guild B's alliances, even if they have `is_initial = 1` in the database.

### Pitfall 3: Forgetting Guild in JOINs

❌ **Wrong:**
```python
cursor.execute("""
    SELECT u.fid, u.nickname, a.name
    FROM users u
    JOIN alliance_list a ON u.alliance = a.alliance_id
""")
```

✅ **Correct:**
```python
guild_id = interaction.guild.id
cursor.execute("""
    SELECT u.fid, u.nickname, a.name
    FROM users u
    JOIN alliance_list a ON u.alliance = a.alliance_id
    WHERE a.discord_server_id = ?
""", (guild_id,))
```

---

## Performance Considerations

### Indexes

The following indexes are CRITICAL for performance:

```sql
CREATE INDEX idx_alliance_guild ON alliance_list(discord_server_id);
CREATE INDEX idx_alliance_guild_name ON alliance_list(discord_server_id, name);
CREATE INDEX idx_alliance_id_guild ON alliance_list(alliance_id, discord_server_id);
```

### Query Optimization

When checking admin's special alliances:

```python
# Use IN clause with guild filter
cursor.execute(f"""
    SELECT alliance_id, name FROM alliance_list
    WHERE alliance_id IN ({placeholders})
    AND discord_server_id = ?
""", alliance_ids + [guild_id])
```

This is much faster than checking each alliance individually.

---

## Validation Queries

### Check for Missing Guild Filters

```bash
# Search for queries without guild_id
grep -r "FROM alliance_list" cogs/ | grep -v "discord_server_id"
```

### Count Alliances per Guild

```sql
SELECT
    discord_server_id,
    COUNT(*) as alliance_count,
    GROUP_CONCAT(name, ', ') as alliance_names
FROM alliance_list
GROUP BY discord_server_id
ORDER BY alliance_count DESC;
```

### Find Orphaned Alliances

```sql
SELECT alliance_id, name, discord_server_id
FROM alliance_list
WHERE discord_server_id IS NULL OR discord_server_id = -1;
```

---

## Summary

**Guild isolation is achieved by:**

1. ✅ Adding `discord_server_id` column to `alliance_list`
2. ✅ ALWAYS filtering queries by `discord_server_id`
3. ✅ Validating guild ownership when using `alliance_id`
4. ✅ Ensuring global admins also respect guild boundaries
5. ✅ Testing with multiple guilds to verify no data leaks

**Security guarantee:**
No alliance, member, gift code, or statistics data from Guild A should ever be visible or accessible to users in Guild B, regardless of their permission level.

---

**Last Updated:** 2025-11-28  
**Status:** ✅ Core implementation complete, ongoing validation required


