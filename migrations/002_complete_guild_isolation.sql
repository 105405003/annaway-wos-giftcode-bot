-- Migration 002: Complete Guild Isolation
-- This SQL script documents all queries that need guild_id filtering
-- For manual reference when updating cogs

-- =============================================================================
-- PATTERN TO FIX:
-- =============================================================================
-- 
-- WRONG (shows all alliances):
--   SELECT * FROM alliance_list
--   SELECT * FROM alliance_list WHERE name = ?
--
-- CORRECT (only current guild):
--   SELECT * FROM alliance_list WHERE discord_server_id = ?
--   SELECT * FROM alliance_list WHERE discord_server_id = ? AND name = ?
--
-- =============================================================================

-- =============================================================================
-- CHECKLIST: Files that need complete review
-- =============================================================================

-- HIGH PRIORITY (user-facing features):
-- - cogs/gift_operations.py - Gift code redemption
-- - cogs/alliance.py - Alliance management (mostly done)
-- - cogs/alliance_member_operations.py - Member operations (mostly done)
-- - cogs/statistics.py - Statistics (mostly done)
-- - cogs/changes.py - Change logs (mostly done)

-- MEDIUM PRIORITY (admin features):
-- - cogs/bot_operations.py - Bot settings
-- - cogs/permission_management.py - Permissions (mostly done)
-- - cogs/wel.py - Welcome messages
-- - cogs/w.py - User info lookup
-- - cogs/olddb.py - Legacy DB operations

-- LOW PRIORITY (specialized features):
-- - cogs/minister_menu.py - Minister feature
-- - cogs/minister_schedule.py - Minister scheduling
-- - cogs/id_channel.py - ID channel feature
-- - cogs/attendance.py - Attendance tracking
-- - cogs/attendance_report.py - Attendance reports
-- - cogs/logsystem.py - Logging system
-- - cogs/control.py - Control panel

-- =============================================================================
-- QUERIES TO FIX BY FILE
-- =============================================================================

-- cogs/gift_operations.py
-- Line ~314, 1704, 1989, 4098: SELECT name FROM alliance_list WHERE alliance_id = ?
--   These are OK if alliance_id is already validated to belong to current guild
--   Should add: AND discord_server_id = ?

-- Line ~2534, 2545: SELECT name FROM alliance_list
--   MUST add: WHERE discord_server_id = ?

-- Line ~2562, 2581: SELECT alliance_id, name FROM alliance_list
--   MUST add: WHERE discord_server_id = ?

-- cogs/alliance_member_operations.py
-- Line ~61: SELECT alliance_id, name FROM alliance_list WHERE name LIKE ? OR alliance_id = ?
--   MUST add: AND discord_server_id = ?

-- cogs/olddb.py
-- Line ~53: SELECT alliance_id, name FROM alliance_list
--   MUST add: WHERE discord_server_id = ?
--   OR consider if this legacy import should assign a guild

-- cogs/wel.py
-- Line ~82: SELECT alliance_id, name FROM alliance_list
--   MUST add: WHERE discord_server_id = ?

-- cogs/id_channel.py
-- Line ~637: SELECT alliance_id, name FROM alliance_list
--   MUST add: WHERE discord_server_id = ?

-- cogs/attendance.py
-- Line ~1754, 1825: SELECT alliance_id, name FROM alliance_list ORDER BY alliance_id
--   MUST add: WHERE discord_server_id = ?

-- =============================================================================
-- VALIDATION QUERIES
-- =============================================================================

-- Check for orphaned alliances (need manual guild assignment)
SELECT alliance_id, name, discord_server_id 
FROM alliance_list 
WHERE discord_server_id IS NULL OR discord_server_id = -1;

-- Count alliances per guild
SELECT 
    discord_server_id,
    COUNT(*) as alliance_count,
    GROUP_CONCAT(name, ', ') as alliance_names
FROM alliance_list
GROUP BY discord_server_id
ORDER BY alliance_count DESC;

-- Find potential cross-guild data leaks (members in alliances from other guilds)
-- This would require joining with the members table and checking user contexts

-- =============================================================================
-- RECOMMENDED TESTING PROCEDURE
-- =============================================================================
-- 
-- 1. Set up two test Discord servers (A and B)
-- 2. Invite the bot to both
-- 3. In Server A:
--    - Create alliance "Alpha"
--    - Add test member with UID 111111
-- 4. In Server B:
--    - Create alliance "Beta"
--    - Add test member with UID 222222
-- 5. Verify:
--    - Server A cannot see "Beta" in any dropdown
--    - Server B cannot see "Alpha" in any dropdown
--    - /add command in A only shows "Alpha"
--    - /add command in B only shows "Beta"
--    - Gift code redemption in A only affects "Alpha"
--    - Statistics in A only show "Alpha" data
-- 6. Test error cases:
--    - Try to use commands in DM (should be blocked)
--    - Try to use commands without Annaway roles (should be blocked)
--    - Try to access empty guild (no alliances) - should show friendly message
--
-- =============================================================================

