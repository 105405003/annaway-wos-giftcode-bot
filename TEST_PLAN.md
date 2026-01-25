# Testing Plan for Annaway WOS Giftcode Bot

**Date:** 2025-11-28  
**Version:** Post-Refactor (Guild Isolation + Permission System + Interaction Fixes)

---

## Test Environment Setup

### Prerequisites

1. **Two Discord Servers (Guilds)**
   - Guild A: "Test Server Alpha" (or any name)
   - Guild B: "Test Server Beta" (or any name)

2. **Bot Deployment**
   - Bot must be invited to BOTH guilds
   - Bot must have necessary permissions:
     - Read Messages
     - Send Messages
     - Use Application Commands
     - Manage Messages (for editing)
     - Embed Links

3. **Discord Roles (in BOTH guilds)**
   - `Annaway_Admin` - Full admin access
   - `Annaway_Manager` - Manager-level access

4. **Test Users**
   - **Admin User:** Has `Annaway_Admin` role in both guilds
   - **Manager User:** Has `Annaway_Manager` role in both guilds
   - **Normal User:** No special roles

---

## Test Categories

- [A] Guild Isolation Tests
- [B] Permission System Tests
- [C] Interaction Handling Tests
- [D] Manager First-Click Tests
- [E] Permission Management Tests

---

## [A] Guild Isolation Tests

**Goal:** Verify that each guild only sees its own data.

### A1: Alliance Visibility

**In Guild A:**
1. Login as Admin or Manager
2. Run `/settings`
3. Click "Alliance Operations" (聯盟操作)
4. Click "View Alliances" (查看聯盟)

**Expected:**
- Only alliances with `discord_server_id = <Guild A's ID>` are shown
- No alliances from Guild B appear

**In Guild B:**
1. Repeat the same steps

**Expected:**
- Only alliances with `discord_server_id = <Guild B's ID>` are shown
- No alliances from Guild A appear

**Status:** [ ] PASS [ ] FAIL

---

### A2: Alliance Creation Isolation

**In Guild A:**
1. Run `/settings` → "Alliance Operations" → "Add Alliance"
2. Create alliance named "Alpha Alliance" with interval 60

**Expected:**
- Alliance is created with `discord_server_id = <Guild A's ID>`
- Success message appears

**In Guild B:**
1. Run `/settings` → "Alliance Operations" → "View Alliances"

**Expected:**
- "Alpha Alliance" does NOT appear in the list

**Status:** [ ] PASS [ ] FAIL

---

### A3: Member Operations Isolation

**In Guild A:**
1. Run `/settings` → "Member Operations" (成員操作)
2. Click "Add Member" (新增成員)
3. Select "Alpha Alliance"
4. Add member with FID: 111111, Nickname: "TestMemberA"

**Expected:**
- Member is added successfully

**In Guild B:**
1. Run `/settings` → "Member Operations" → "View Members"
2. Try to select any alliance

**Expected:**
- Member 111111 (TestMemberA) does NOT appear in any alliance in Guild B

**Status:** [ ] PASS [ ] FAIL

---

### A4: Gift Code Operations Isolation

**In Guild A:**
1. Run `/settings` → "Gift Code Operations" (禮品碼操作)
2. Click "Create Gift Code" (新增禮品碼)
3. Enter code: "TESTCODEA"
4. Select "Alpha Alliance" to redeem for

**Expected:**
- Gift code is created and associated with Guild A

**In Guild B:**
1. Run `/settings` → "Gift Code Operations"
2. View gift code list

**Expected:**
- "TESTCODEA" does NOT appear in Guild B's gift code list

**Status:** [ ] PASS [ ] FAIL

---

### A5: Statistics Isolation

**In Guild A:**
1. Run `/settings` → "Other Features" (其他功能) → "Statistics" (統計)
2. Generate furnace distribution for "Alpha Alliance"

**Expected:**
- Shows statistics for members in Alpha Alliance

**In Guild B:**
1. Run `/settings` → "Other Features" → "Statistics"
2. Try to select an alliance

**Expected:**
- "Alpha Alliance" does NOT appear in the dropdown

**Status:** [ ] PASS [ ] FAIL

---

### A6: Alliance History Isolation

**In Guild A:**
1. Run `/settings` → "Alliance History" (聯盟歷史)
2. Select "Alpha Alliance"
3. View furnace level changes

**Expected:**
- Shows change history for Alpha Alliance

**In Guild B:**
1. Run `/settings` → "Alliance History"

**Expected:**
- "Alpha Alliance" does NOT appear in the selection menu

**Status:** [ ] PASS [ ] FAIL

---

## [B] Permission System Tests

**Goal:** Verify that `Annaway_Admin` and `Annaway_Manager` roles work correctly.

### B1: Manager Can Access Manager-Level Features

**Test User:** Manager (has `Annaway_Manager` role)

**In Guild A:**
1. Run `/settings`
2. Click each of the following buttons:
   - "Member Operations" (成員操作)
   - "Gift Code Operations" (禮品碼操作)
   - "Alliance History" (聯盟歷史)
   - "Other Features" (其他功能)

**Expected for EACH click:**
- ✅ Menu opens successfully on FIRST click
- ✅ No error message: "You do not have permission to perform this action."
- ✅ No "Unknown interaction" error
- ✅ `permission_debug.log` shows `✅ ALLOWED` with `has_manager_role: True`

**Status:** [ ] PASS [ ] FAIL

---

### B2: Manager CANNOT Access Admin-Only Features

**Test User:** Manager (has `Annaway_Manager` role)

**In Guild A:**
1. Run `/settings` → "Alliance Operations" (聯盟操作)
2. Try to click:
   - "Add Alliance" (新增聯盟)
   - "Edit Alliance" (編輯聯盟)
   - "Delete Alliance" (刪除聯盟)
3. Try to click "Permission Management" (權限管理)

**Expected:**
- ❌ Error message: "You do not have permission to perform this action."
- ❌ Permission denied by `check_permission(interaction, admin_only=True)`
- ✅ `permission_debug.log` shows `❌ DENIED` with `admin_only: True`

**Status:** [ ] PASS [ ] FAIL

---

### B3: Admin Can Access All Features

**Test User:** Admin (has `Annaway_Admin` role)

**In Guild A:**
1. Run `/settings`
2. Test ALL buttons:
   - Member Operations ✅
   - Gift Code Operations ✅
   - Alliance History ✅
   - Other Features ✅
   - Alliance Operations ✅
     - Add Alliance ✅
     - Edit Alliance ✅
     - Delete Alliance ✅
   - Permission Management ✅

**Expected:**
- ✅ ALL features work
- ✅ No permission errors
- ✅ First click always succeeds

**Status:** [ ] PASS [ ] FAIL

---

### B4: Normal User CANNOT Access Management Features

**Test User:** Normal user (NO `Annaway_Admin` or `Annaway_Manager` role)

**In Guild A:**
1. Run `/settings`

**Expected:**
- ❌ Error message: "You do not have permission to perform this action."
- ❌ Main settings menu does not open
- ✅ `permission_debug.log` shows `❌ DENIED`

**Status:** [ ] PASS [ ] FAIL

---

## [C] Interaction Handling Tests

**Goal:** Verify that all interactions respond correctly without timeouts or double-response errors.

### C1: No "Unknown Interaction" Errors

**Test User:** Manager or Admin

**Test All Menu Flows:**
1. `/settings` → "Member Operations"
2. `/settings` → "Gift Code Operations"
3. `/settings` → "Alliance History"
4. `/settings` → "Other Features"
5. `/settings` → "Alliance Operations" → "View Alliances"

**Expected for EACH flow:**
- ✅ Menu opens within 3 seconds
- ✅ NO error: "This interaction failed" or "Unknown interaction (10062)"
- ✅ NO error: "Interaction has already been acknowledged"

**Check Logs:**
```bash
tail -f ~/wos_bot/log/gift_ops.txt
sudo journalctl -u wos-bot -f
```

**Expected:**
- No `discord.errors.NotFound: 404 Not Found (error code: 10062)`
- No `InteractionResponded` errors

**Status:** [ ] PASS [ ] FAIL

---

### C2: Proper Defer + Edit Pattern

**Test:** Open any menu that takes time to load

**In Code Review:**
- Check that menu functions use:
  ```python
  if not interaction.response.is_done():
      await interaction.response.defer(ephemeral=True)
  
  # ... build embed and view ...
  
  await interaction.edit_original_response(embed=embed, view=view)
  ```

**Expected:**
- ✅ Menus load smoothly
- ✅ No race conditions
- ✅ No double responses

**Status:** [ ] PASS [ ] FAIL

---

## [D] Manager First-Click Tests

**Goal:** Verify that the four main buttons work on the FIRST click for Managers.

**Test User:** Manager (has `Annaway_Manager` role)

### D1: Member Operations - First Click

**In Guild A:**
1. Run `/settings`
2. Click "Member Operations" (成員操作) **ONCE**
3. Wait for response

**Expected:**
- ✅ Menu opens successfully on FIRST click
- ✅ Shows alliance selection or member operation options
- ❌ NO error: "You do not have permission to perform this action."
- ✅ `permission_debug.log` shows `✅ ALLOWED` for `custom_id: member_operations`

**Status:** [ ] PASS [ ] FAIL

---

### D2: Gift Code Operations - First Click

**In Guild A:**
1. Run `/settings`
2. Click "Gift Code Operations" (禮品碼操作) **ONCE**
3. Wait for response

**Expected:**
- ✅ Gift code menu opens on FIRST click
- ✅ Shows gift code options (create, view, settings, etc.)
- ✅ Shows gift code refresh schedule: "禮品碼每日更新：00:00 與 12:00 UTC (台灣時間 08:00 與 20:00)"
- ❌ NO error messages
- ✅ `permission_debug.log` shows `✅ ALLOWED` for `custom_id: gift_code_operations`

**Status:** [ ] PASS [ ] FAIL

---

### D3: Alliance History - First Click

**In Guild A:**
1. Run `/settings`
2. Click "Alliance History" (聯盟歷史) **ONCE**
3. Wait for response

**Expected:**
- ✅ Alliance history menu opens on FIRST click
- ✅ Shows options: furnace changes, nickname changes, member list
- ❌ NO error messages
- ✅ `permission_debug.log` shows `✅ ALLOWED` for `custom_id: alliance_history`

**Status:** [ ] PASS [ ] FAIL

---

### D4: Other Features - First Click

**In Guild A:**
1. Run `/settings`
2. Click "Other Features" (其他功能) **ONCE**
3. Wait for response

**Expected:**
- ✅ Other features menu opens on FIRST click
- ✅ Shows options: statistics, minister menu, ID channel, etc.
- ❌ NO error messages
- ✅ `permission_debug.log` shows `✅ ALLOWED` for `custom_id: other_features`

**Status:** [ ] PASS [ ] FAIL

---

## [E] Permission Management Tests

**Goal:** Verify that Permission Management menu works reliably without hanging.

**Test User:** Admin (has `Annaway_Admin` role)

### E1: Assign Manager - No Hanging

**In Guild A:**
1. Run `/settings` → "Permission Management" (權限管理)
2. Click "Assign Manager" (分配管理員)
3. Select a user from the dropdown
4. Wait for confirmation

**Expected:**
- ✅ User is assigned Manager role or alliance access
- ✅ Confirmation message appears
- ❌ NO hanging after selecting user
- ❌ NO error: "An error occurred while loading Permission Management menu."

**Status:** [ ] PASS [ ] FAIL

---

### E2: Remove Manager - Works Reliably

**In Guild A:**
1. Run `/settings` → "Permission Management"
2. Click "Remove Manager" (移除管理員)
3. Select a user who is currently a manager
4. Confirm removal

**Expected:**
- ✅ Manager is removed successfully
- ✅ Confirmation message appears
- ❌ NO errors

**Status:** [ ] PASS [ ] FAIL

---

### E3: Re-Open Permission Management

**In Guild A:**
1. Assign a manager (test E1)
2. Close the menu
3. Run `/settings` → "Permission Management" **again**
4. View the list of managers

**Expected:**
- ✅ Menu opens successfully on second use
- ✅ Shows updated list of managers
- ❌ NO error: "An error occurred while loading Permission Management menu."

**Status:** [ ] PASS [ ] FAIL

---

## [F] Gift Code Refresh Schedule

**Goal:** Verify that the refresh schedule is correctly displayed.

### F1: Gift Code Menu Shows Refresh Times

**In Guild A:**
1. Run `/settings` → "Gift Code Operations"

**Expected:**
- ✅ Menu embed includes:
  ```
  ⏰ 更新時間
  └ 禮品碼每日更新：00:00 與 12:00 UTC
  └ (台灣時間 08:00 與 20:00)
  ```

**Status:** [ ] PASS [ ] FAIL

---

### F2: README Documents Refresh Times

**Check `README.md`:**
- ✅ Contains a section titled "Gift Code Refresh Schedule" or similar
- ✅ States refresh times: "00:00 and 12:00 UTC (08:00 and 20:00 Taiwan time)"

**Status:** [ ] PASS [ ] FAIL

---

## Debug Log Verification

### Check permission_debug.log

**After each test, verify:**

```bash
cat ~/wos_bot/permission_debug.log | tail -100
```

**Expected format:**
```
========================================
custom_id: member_operations
admin_only: False
user.id: 1398088670300475573
user.name: test_manager
guild.id: 1398071974692913324
guild.name: Test Server Alpha
User roles (names): ['@everyone', 'Annaway_Manager']
has_admin_role: False
has_manager_role: True
is_global_admin (DB is_initial): False
allowed: True
✅ ALLOWED
========================================
```

**For denied requests:**
```
allowed: False
❌ DENIED - insufficient permission
```

---

## Performance Checks

### P1: Response Time

**For all menu operations:**
- ✅ First response (defer) within 1 second
- ✅ Menu fully loaded within 3 seconds
- ❌ NO timeout errors

**Status:** [ ] PASS [ ] FAIL

---

### P2: Database Query Efficiency

**Check bot logs for slow queries:**
```bash
grep -i "slow\|timeout\|deadlock" ~/wos_bot/log/gift_ops.txt
```

**Expected:**
- ❌ NO slow query warnings
- ❌ NO database locks

**Status:** [ ] PASS [ ] FAIL

---

## Summary Checklist

After completing all tests, verify:

- [ ] **Guild Isolation:** No cross-guild data leaks (tests A1-A6 all PASS)
- [ ] **Manager Permissions:** Manager can use all 4 main buttons on first click (tests B1, D1-D4 all PASS)
- [ ] **Admin Permissions:** Admin can access all features (test B3 PASS)
- [ ] **Normal User Blocked:** Non-privileged users cannot access management features (test B4 PASS)
- [ ] **No Interaction Errors:** No "Unknown interaction" or timeout errors (test C1 PASS)
- [ ] **Permission Management:** Assign/remove managers works without hanging (tests E1-E3 all PASS)
- [ ] **Gift Code Schedule:** Refresh times correctly displayed (tests F1-F2 PASS)
- [ ] **Debug Logging:** `permission_debug.log` shows correct ALLOWED/DENIED decisions
- [ ] **Performance:** All operations complete within 3 seconds (test P1 PASS)

---

## Regression Tests (Future)

When making changes, always re-run:
1. Guild Isolation Tests (A1-A6)
2. Manager First-Click Tests (D1-D4)
3. Permission Management Tests (E1-E3)

---

## Troubleshooting

### If Tests Fail

**Guild Isolation Failure (tests A1-A6):**
- Check `alliance_list` table: `SELECT * FROM alliance_list LIMIT 10;`
- Verify `discord_server_id` column exists and is populated
- Check code: search for `FROM alliance_list` without `WHERE discord_server_id`

**Manager First-Click Failure (tests D1-D4):**
- Check `permission_debug.log` for DENIED messages
- Verify `Annaway_Manager` role exists (exact spelling, case-sensitive!)
- Check for duplicate permission checks in code (grep for "SELECT.*FROM admin WHERE")

**Permission Management Hanging (tests E1-E3):**
- Check for double `interaction.response` calls
- Verify `defer(ephemeral=True)` is called early
- Check for missing `await` keywords

**Interaction Timeout (test C1):**
- Increase logging in the affected function
- Check if defer is called within 3 seconds
- Verify no blocking operations (large DB queries, API calls)

---

**Test Plan Version:** 1.0  
**Last Updated:** 2025-11-28  
**Next Review:** After major feature changes or reported bugs


