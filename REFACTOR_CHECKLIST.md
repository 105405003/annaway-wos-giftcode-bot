# 🔧 完整重構檢查清單

## 執行日期：2025-11-28

---

## ✅ 已完成的重構項目

### A. 統一權限系統

**已移除的重複權限檢查：**

1. ✅ `cogs/gift_operations.py`
   - `delete_gift_code()` - 已移除 DB admin 檢查
   - `create_gift_code()` - 已移除 DB admin 檢查
   - `show_ocr_settings()` - 已移除 DB admin 檢查

2. ✅ `cogs/backup_operations.py`
   - `show_backup_menu()` - 改用 `check_permission(admin_only=True)`

3. ✅ `cogs/minister_menu.py`
   - `update_names()` - 改用 `check_permission(admin_only=False)`

4. ✅ `cogs/bear_trap.py`
   - `check_admin()` - 重寫為使用 `check_permission(admin_only=False)`

5. ✅ `cogs/id_channel.py`
   - `show_id_channel_menu()` - 改用 `check_permission(admin_only=False)`

6. ✅ `cogs/alliance.py`
   - `view_alliances()` - 移除 DB admin early return
   - `on_interaction` - 正確的權限映射已設定

**保留的業務邏輯查詢（非權限門檻）：**
- `get_admin_alliances()` 系列 - 決定使用者能看到哪些聯盟
- `get_admin_info()` - helper function
- `check_is_global_admin()` - UI 狀態判斷（按鈕 disabled）

---

### B. Interaction 流程修正

**已修正的超時問題：**

1. ✅ `cogs/alliance.py::on_interaction`
   - 在權限檢查後立即 `defer(ephemeral=True)`
   - 使用 `edit_original_response` 更新訊息

2. ✅ `cogs/alliance_member_operations.py`
   - `handle_member_operations()` - 開始時 defer
   - `_handle_alliance_selection()` - 開始時 defer，使用 followup.send

3. ✅ `cogs/gift_operations.py`
   - `show_gift_menu()` - 開始時 defer，使用 edit_original_response

4. ✅ `cogs/changes.py`
   - `show_alliance_history_menu()` - 開始時 defer，使用 edit_original_response

5. ✅ `cogs/other_features.py`
   - `show_other_features_menu()` - 開始時 defer，使用 edit_original_response

**Interaction 處理模式：**
```python
# 標準模式 1：更新現有訊息（選單類）
async def show_menu(self, interaction):
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True)
    
    # 建立 embed + view
    await interaction.edit_original_response(embed=embed, view=view)

# 標準模式 2：新訊息
async def button_callback(self, interaction):
    await interaction.response.send_message("...", ephemeral=True)
    
# 標準模式 3：後續訊息
async def after_first_response(self, interaction):
    await interaction.followup.send("...", ephemeral=True)
```

---

### C. 權限映射驗證

**cogs/alliance.py::on_interaction**
```python
admin_only_ids = {
    "add_alliance",
    "edit_alliance",
    "delete_alliance",
    "permission_management",
}

manager_ids = {
    "alliance_operations",
    "member_operations",
    "gift_code_operations",
    "alliance_history",
    "other_features",
    "check_alliance",
    "view_alliances",
    "main_menu",
}
```

**cogs/bot_operations.py::on_interaction**
```python
admin_only_ids = {
    "add_admin",
    "remove_admin",
    "transfer_old_database",
    "check_updates",
    "view_administrators",
    "view_admin_permissions",
}

manager_ids = {
    "alliance_control_messages",
    "assign_alliance",
    "bot_status",
    "bot_settings",
    "main_menu",
}
```

**cogs/logsystem.py::on_interaction**
```python
admin_only_ids = {
    "set_log_channel",
    "remove_log_channel",
}

manager_ids = {
    "log_system",
    "view_log_channels",
}
```

---

### D. 錯誤訊息統一

**統一的權限錯誤訊息（僅來自 check_permission）：**
```
"❌ You do not have permission to perform this action."
```

**中性的運行時錯誤訊息：**
```
"❌ 處理時發生錯誤"
"❌ 載入選單時發生錯誤"
"❌ An error occurred while processing this interaction."
```

---

### E. 專案清理

**已清理：**
- ✅ 37 個舊的 ZIP 檔案（本地專案資料夾）
- ✅ `.gitignore` 更新：
  - `permission_debug.log`
  - `*.zip`
  - `wos_bot*.zip`
  - `hotfix*.zip`
  - `update_files*.zip`
  - `final_fix*.zip`
  - `A1_deployment*.zip`

**提供的清理工具：**
- ✅ `cleanup_gcp_vm.sh` - 互動式 GCP VM 清理腳本

---

### F. 禮品碼更新時間文件化

**已更新的文件：**

1. ✅ `README.md`
   ```markdown
   ## ⏰ Gift Code Refresh Schedule
   
   Gift codes are refreshed **twice per day**:
   - **00:00 UTC** (08:00 Taiwan time / UTC+8)
   - **12:00 UTC** (20:00 Taiwan time / UTC+8)
   ```

2. ✅ `cogs/gift_operations.py::show_gift_menu`
   ```python
   description=(
       # ...
       f"⏰ **更新時間**\n"
       f"└ 禮品碼每日更新：00:00 與 12:00 UTC\n"
       f"└ (台灣時間 08:00 與 20:00)"
   )
   ```

3. ✅ `DEPLOYMENT.md` - 包含更新時間說明

---

## 🧪 驗證標準

### Manager 角色測試

**預期行為：**
- ✅ `/settings` 開啟主選單
- ✅ 點擊「成員操作」→ 正常開啟，無錯誤
- ✅ 點擊「禮品碼操作」→ 正常開啟，顯示更新時間
- ✅ 點擊「聯盟歷史」→ 正常開啟
- ✅ 點擊「其他功能」→ 正常開啟
- ✅ 所有操作第一次點擊就成功
- ✅ 沒有 "Unknown interaction" (10062) 錯誤
- ✅ 沒有 "You do not have permission" 錯誤（除了 Admin-only 功能）

**permission_debug.log 應顯示：**
```
custom_id: member_operations
admin_only: False
User roles (names): ['@everyone', 'Annaway_Manager']
has_manager_role: True
allowed: True
✅ ALLOWED
```

### Admin 角色測試

**預期行為：**
- ✅ 所有 Manager 功能都可用
- ✅ Admin-only 功能都可用：
  - 新增/編輯/刪除聯盟
  - 管理員管理
  - 日誌頻道設定

### 普通使用者測試

**預期行為：**
- ❌ 所有管理功能被 `check_permission` 阻擋
- ❌ 看到統一的錯誤訊息（來自 check_permission）

---

## 📊 權限系統架構

### 單一來源真理

**`utils/permissions.py::check_permission(interaction, admin_only=True/False)`**

- ✅ 檢查 Discord 角色：`Annaway_Admin`, `Annaway_Manager`
- ✅ 檢查 DB `admin` 表的 `is_initial` 欄位
- ✅ 詳細的 debug logging 到 `permission_debug.log`
- ✅ 統一的錯誤訊息

### 權限邏輯

```python
# Admin-only
if admin_only:
    allowed = has_admin_role or is_global_admin_db

# Manager-level  
else:
    allowed = has_admin_role or has_manager_role or is_global_admin_db
```

---

## 📁 修改的檔案清單

### 核心權限系統
1. `utils/permissions.py` ✅
2. `cogs/gift_operations.py` ✅
3. `cogs/backup_operations.py` ✅
4. `cogs/minister_menu.py` ✅
5. `cogs/bear_trap.py` ✅
6. `cogs/id_channel.py` ✅
7. `cogs/alliance.py` ✅
8. `cogs/alliance_member_operations.py` ✅
9. `cogs/changes.py` ✅
10. `cogs/other_features.py` ✅
11. `cogs/bot_operations.py` ✅
12. `cogs/logsystem.py` ✅

### 文件
13. `README.md` ✅
14. `DEPLOYMENT.md` ✅
15. `TESTING_GUIDE.md` ✅
16. `FINAL_AUDIT_SUMMARY.md` ✅
17. `QUICK_DEPLOY.md` ✅
18. `.gitignore` ✅

### 工具
19. `cleanup_gcp_vm.sh` ✅
20. `REFACTOR_CHECKLIST.md` ✅

---

## 🔍 剩餘的已知業務邏輯查詢

這些 DB 查詢是**業務邏輯**，不是權限門檻，因此保留：

1. **`get_admin_alliances()` 系列函式**
   - 位置：`alliance_member_operations.py`, `changes.py`, `statistics.py`, `attendance.py`
   - 用途：決定使用者能看到哪些聯盟
   - 行為：根據角色 + adminserver 表回傳聯盟列表
   - 不發送錯誤訊息

2. **`get_admin_info()` helper**
   - 位置：`gift_operations.py`
   - 用途：獲取使用者資訊
   - 不阻止執行

3. **`check_is_global_admin()` (permission_management.py)**
   - 用途：判斷 UI 元素狀態
   - 不阻止執行

4. **Alliance 按鈕 disabled 狀態**
   - 位置：`alliance.py::on_interaction`
   - 查詢 `is_initial` 僅用於設定 `disabled=not is_global_admin`
   - 不發送錯誤訊息

---

## ⚠️ 重要提醒

### 不要混淆權限檢查與業務邏輯

**權限檢查（應統一）：**
- "使用者是否有角色可以使用此功能？"
- 應該只通過 `check_permission()`

**業務邏輯（應保留）：**
- "使用者管理哪些聯盟？"
- "使用者是否是此聯盟的擁有者？"
- "使用者有權限編輯哪些資料？"

### 錯誤訊息指南

**權限相關：**
- 只能來自 `check_permission()`
- 訊息：「You do not have permission to perform this action.」

**業務邏輯相關：**
- 可以在各 cog 中自定義
- 例如：「你沒有管理任何聯盟」、「找不到該聯盟」

**運行時錯誤：**
- 使用中性訊息
- 例如：「處理時發生錯誤」、「載入選單時發生錯誤」

---

## 🎯 下一步

### 部署驗證

1. 上傳 `complete.zip` 到 GCP VM
2. 執行部署步驟（見 `QUICK_DEPLOY.md`）
3. 執行完整測試（見 `TESTING_GUIDE.md`）
4. 檢查 `permission_debug.log`
5. 使用 `cleanup_gcp_vm.sh` 清理舊檔案

### 持續監控

- 監控 `permission_debug.log` 檔案大小
- 定期備份資料庫
- 定期清理舊的 ZIP 和備份

---

## ✅ 驗收確認

- [x] 所有重複的 DB 權限檢查已移除
- [x] Interaction 流程已標準化
- [x] 權限映射已驗證
- [x] 錯誤訊息已統一
- [x] ZIP 檔案已清理
- [x] `.gitignore` 已更新
- [x] 禮品碼更新時間已文件化
- [x] 完整的測試指南已提供
- [x] 部署流程已文件化

**重構完成！** ✅

