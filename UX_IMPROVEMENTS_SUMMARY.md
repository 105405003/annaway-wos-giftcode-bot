# UX Improvements Summary

本文件記錄了所有使用者體驗（UX）改善項目的實作細節。

## 📅 實作日期

**2025-11-27**

## 🎯 改善目標

1. 統一日誌格式，使其更易閱讀與除錯
2. 在啟動時顯示 Annaway 品牌 ASCII Logo
3. 明確標示專案授權與 fork 來源
4. 統一使用者面向的錯誤訊息
5. 美化 Discord 內的 Embed 訊息

## 📁 新增檔案

### 1. `utils/log_format.py`

**用途：** 統一的日誌格式化工具

**主要功能：**

- `format_admin_log()` - 格式化管理員操作日誌
  ```
  [Annaway WOS][GUILD:1458][ALLIANCE:DVL][USER:@Anna] Added 3 members (ids=123, 456, 789)
  ```

- `format_error_log()` - 格式化錯誤日誌
  ```
  [Annaway WOS][ERROR][gift_operations.py] Failed to redeem code: API timeout
  ```

- `format_gift_log()` - 格式化禮包碼相關日誌
- `format_member_log()` - 格式化成員管理日誌
- `format_attendance_log()` - 格式化出席記錄日誌
- `log_to_file()` - 統一的檔案寫入函數
- `get_timestamp()` - 取得 ISO 格式時間戳記

**使用範例：**

```python
from utils.log_format import format_admin_log, log_to_file

# 格式化日誌
log_msg = format_admin_log(
    action="Added member",
    guild=interaction.guild,
    alliance_name="DVL",
    user=interaction.user,
    extra={"fid": 123456, "nickname": "TestPlayer"}
)

# 寫入檔案
log_to_file("log/member_operations.txt", log_msg)
```

### 2. `utils/embeds.py`

**用途：** 統一的 Discord Embed 樣式

**主要功能：**

- `build_admin_log_embed()` - 管理員操作日誌 Embed
- `build_success_embed()` - 成功訊息 Embed（綠色）
- `build_error_embed()` - 錯誤訊息 Embed（紅色）
- `build_warning_embed()` - 警告訊息 Embed（黃色）
- `build_info_embed()` - 資訊訊息 Embed（藍色）
- `build_member_operation_embed()` - 成員操作 Embed
- `build_gift_operation_embed()` - 禮包碼操作 Embed
- `build_attendance_embed()` - 出席記錄 Embed

**預設顏色主題：**

- Annaway 主題色：`#5865F2` (Discord Blurple)
- 成功：`#57F287` (綠色)
- 警告：`#FEE75C` (黃色)
- 錯誤：`#ED4245` (紅色)
- 資訊：`#5865F2` (藍色)

**所有 Embed 都包含：**

- 統一的 footer："Annaway WOS Giftcode Bot"
- 可選的時間戳記
- 一致的 emoji 使用

**使用範例：**

```python
from utils.embeds import build_success_embed, build_member_operation_embed

# 簡單成功訊息
embed = build_success_embed(
    title="操作成功",
    description="成員已成功加入聯盟"
)
await interaction.response.send_message(embed=embed)

# 詳細的成員操作訊息
embed = build_member_operation_embed(
    operation="新增成員",
    member_name="TestPlayer",
    fid=123456,
    alliance_name="DVL",
    furnace_level=25,
    actor=interaction.user,
    success=True
)
await log_channel.send(embed=embed)
```

### 3. `utils/messages.py`

**用途：** 統一的使用者訊息模板

**主要功能：**

- `no_permission_message_admin_only()` - Admin 專用權限錯誤
- `no_permission_message_manager_or_admin()` - Manager/Admin 權限錯誤
- `no_guild_context_message()` - DM 使用錯誤
- `no_alliance_configured_message()` - 未設定聯盟提示
- `alliance_not_found_message()` - 找不到聯盟錯誤
- `invalid_fid_message()` - 無效 FID 格式錯誤
- `api_error_message()` - API 連線錯誤
- `captcha_error_message()` - 驗證碼處理錯誤
- `database_error_message()` - 資料庫錯誤
- `operation_success_message()` - 一般性成功訊息
- `operation_in_progress_message()` - 處理中訊息
- `batch_operation_summary()` - 批次操作摘要
- `help_message()` - 一般性幫助訊息
- `feature_not_configured_message()` - 功能未設定提示

**特色：**

- 所有訊息都包含 emoji 和清晰的標題
- 提供「下一步」或「可能原因」指引
- 一致的格式和語氣
- 易於維護和修改

**使用範例：**

```python
from utils.messages import no_alliance_configured_message, operation_success_message

# 錯誤訊息
if not alliances:
    await interaction.response.send_message(
        no_alliance_configured_message(),
        ephemeral=True
    )
    return

# 成功訊息
await interaction.response.send_message(
    operation_success_message(
        operation="新增成員",
        details=f"成功將 {nickname} (FID: {fid}) 加入 {alliance_name}"
    ),
    ephemeral=True
)
```

### 4. `utils/banner.py`

**用途：** 啟動時的 ASCII Banner 和版本資訊

**主要功能：**

- `print_startup_banner()` - 顯示啟動橫幅
- `print_shutdown_banner()` - 顯示關閉橫幅
- `__version__` - 版本號常數

**Banner 內容：**

```
============================================================
    ___                                           
   /   |  ____  ____  ____ __      ______ ___  __
  / /| | / __ \/ __ \/ __ `/ | /| / / __ `/ / / /
 / ___ |/ / / / / / / /_/ /| |/ |/ / /_/ / /_/ / 
/_/  |_/_/ /_/_/ /_/\__,_/ |__/|__/\__,_/\__, /  
                                        /____/   
    WOS Giftcode Redemption Bot
============================================================
  [Annaway WOS Giftcode Bot] v1.0.0-annaway - Started at 2025-11-27T12:00:00Z
============================================================

📋 Bot Information:
  • Original Project: Reloisback/Whiteout-Survival-Discord-Bot
  • Customized by: Annaway Studio
  • Features: Multi-Guild Support + Role-Based Permissions

🔐 Required Roles:
  • Annaway_Admin  - Full administrative access
  • Annaway_Manager - Standard management access

============================================================
```

**使用方式：**

在 `main.py` 中已自動整合：

```python
from utils.banner import print_startup_banner, __version__
print_startup_banner(__version__)
```

**修改版本號：**

編輯 `utils/banner.py` 中的 `__version__` 常數：

```python
__version__ = "1.0.0-annaway"
```

### 5. `ANNAWAY_NOTICE.md`

**用途：** Fork 版本說明和授權資訊

**內容包含：**

1. **關於此專案** - 說明這是 Reloisback 原專案的 fork
2. **原始專案授權** - 強調 LICENSE 檔案不得修改
3. **Annaway 的修改** - 列出所有增強功能
   - 多伺服器隔離
   - 角色權限系統
   - 繁體中文化
   - UX 改善
   - 部署優化
   - 文件完善
4. **授權條款** - 詳細說明使用限制
5. **商業使用** - 如何聯絡原作者
6. **致謝** - 感謝原作者和 Annaway 貢獻
7. **支援和貢獻** - 如何獲得協助
8. **重要提醒** - 使用須知

## 🔄 修改的檔案

### 1. `main.py`

**修改內容：**

- 在啟動序列中加入 Banner 顯示

**修改位置：**

```python
if __name__ == "__main__":
    import requests
    
    # 顯示啟動 Banner
    from utils.banner import print_startup_banner, __version__
    print_startup_banner(__version__)
    
    # ... 其餘啟動代碼
```

**影響：**

- 啟動時會顯示美觀的 ASCII Banner
- 清楚顯示版本號和基本資訊
- 不影響任何功能

### 2. `utils/permissions.py`

**修改內容：**

- 加入內部訊息函數 `_get_permission_error_message()`
- 加入內部訊息函數 `_get_no_guild_message()`
- 更新所有錯誤訊息使用新格式

**修改位置：**

- `check_guild_context()` - 使用統一的 DM 錯誤訊息
- `check_permission()` - 使用統一的權限錯誤訊息
- `requires_annaway_role_button()` - 使用統一的錯誤訊息

**為何使用內部函數而非 messages.py：**

為避免循環引入問題（`permissions.py` 可能被 `messages.py` 引用），我們在 `permissions.py` 內部定義了訊息函數，但保持與 `messages.py` 相同的格式和內容。

**影響：**

- 所有權限錯誤訊息現在更清晰、更一致
- 包含「如何獲得權限」的指引
- 使用 emoji 和格式化標題
- 不影響權限檢查邏輯

### 3. `README_ANNAWAY.md`

**修改內容：**

- 擴充「License」章節為「Credits & License」
- 加入原作者致謝
- 明確說明 fork 的修改內容
- 列出授權重點
- 提供聯絡原作者的資訊
- 引用 ANNAWAY_NOTICE.md

**影響：**

- 使用者能清楚了解專案來源
- 尊重原作者的貢獻
- 符合授權要求

## 🎨 改善的使用者體驗要素

### 1. 錯誤訊息改善

**改善前：**

```
❌ You don't have permission to use this command.
Only members with the Annaway_Admin role can use this.
```

**改善後：**

```
❌ **權限不足**

此功能僅限 `Annaway_Admin` 身分組使用。

📌 **如何獲得權限？**
請聯絡伺服器管理員，或參考 Annaway 文件中的權限說明。
```

**改善點：**

- ✅ 清楚的標題和結構
- ✅ 使用 emoji 提高可讀性
- ✅ 提供下一步指引
- ✅ 使用繁體中文（符合目標使用者）

### 2. 日誌格式改善

**改善前：**

```
Added member 123456 to DVL
```

**改善後：**

```
[Annaway WOS][GUILD:1458][ALLIANCE:DVL][USER:@Anna] Added member (fid=123456, nickname=TestPlayer)
```

**改善點：**

- ✅ 包含 Guild ID（多伺服器識別）
- ✅ 包含執行者資訊
- ✅ 結構化的額外資訊
- ✅ 易於搜尋和過濾

### 3. Discord Embed 改善

**改善前：**

簡單的文字訊息或基本 Embed

**改善後：**

結構化的 Embed，包含：

- ✅ 統一的顏色主題
- ✅ 清晰的欄位分隔
- ✅ 時間戳記
- ✅ Footer 品牌標識
- ✅ 適當的 emoji

## 🛠️ 如何使用新工具

### 在 Cogs 中使用日誌格式化

```python
from utils.log_format import format_member_log, log_to_file

async def add_member(self, interaction, fid, alliance_name):
    # ... 業務邏輯 ...
    
    # 格式化日誌
    log_msg = format_member_log(
        operation="Added",
        fid=fid,
        nickname=nickname,
        alliance_name=alliance_name,
        furnace_level=furnace_level,
        extra={"actor": interaction.user.name}
    )
    
    # 寫入檔案
    log_to_file("log/member_operations.txt", log_msg)
```

### 在 Cogs 中使用 Embed

```python
from utils.embeds import build_member_operation_embed

async def add_member(self, interaction, fid, alliance_name):
    # ... 業務邏輯 ...
    
    # 建立 Embed
    embed = build_member_operation_embed(
        operation="新增成員",
        member_name=nickname,
        fid=fid,
        alliance_name=alliance_name,
        furnace_level=furnace_level,
        actor=interaction.user,
        success=True
    )
    
    # 發送到日誌頻道
    if log_channel:
        await log_channel.send(embed=embed)
```

### 在 Cogs 中使用訊息模板

```python
from utils.messages import no_alliance_configured_message, operation_success_message

async def my_command(self, interaction):
    # 檢查聯盟
    alliances = get_alliances(interaction.guild.id)
    if not alliances:
        await interaction.response.send_message(
            no_alliance_configured_message(),
            ephemeral=True
        )
        return
    
    # 執行操作
    # ...
    
    # 成功訊息
    await interaction.response.send_message(
        operation_success_message(
            operation="操作名稱",
            details="詳細資訊"
        ),
        ephemeral=True
    )
```

## 📊 統計

**新增檔案：** 5 個

- `utils/log_format.py` (約 240 行)
- `utils/embeds.py` (約 390 行)
- `utils/messages.py` (約 240 行)
- `utils/banner.py` (約 70 行)
- `ANNAWAY_NOTICE.md` (約 180 行)

**修改檔案：** 3 個

- `main.py` (新增 3 行)
- `utils/permissions.py` (新增約 30 行，修改約 20 行)
- `README_ANNAWAY.md` (新增約 20 行)

**總計新增：** 約 1,170 行程式碼和文件

## ✅ 完成的任務

- ✅ **TASK 3** - Log 美化（建立 `utils/log_format.py`）
- ✅ **TASK 4** - ASCII Logo（建立 `utils/banner.py` 並整合到 `main.py`）
- ✅ **TASK 5** - LICENSE / Branding（建立 `ANNAWAY_NOTICE.md` 並更新 README）
- ✅ **TASK 6** - 使用者體驗（建立 `utils/messages.py`）
- ✅ **TASK 7** - Log Channel & UX（建立 `utils/embeds.py`）
- ✅ 更新 `utils/permissions.py` 使用統一訊息

## 🔮 未來建議

### 逐步整合新工具

建議在未來修改或新增功能時，逐步整合新的工具：

1. **新增指令時**：使用 `utils/messages.py` 中的訊息模板
2. **寫入日誌時**：使用 `utils/log_format.py` 中的格式化函數
3. **發送 Embed 時**：使用 `utils/embeds.py` 中的 Embed 建構器

### 可選的進一步改善

這些不在本次任務範圍內，但可考慮在未來實作：

1. **日誌等級系統**
   - 加入 DEBUG, INFO, WARNING, ERROR 等級
   - 可設定過濾等級

2. **日誌輪轉**
   - 自動分割大型日誌檔案
   - 定期清理舊日誌

3. **Embed 模板系統**
   - 建立更多專用的 Embed 模板
   - 支援自訂顏色主題

4. **多語言訊息**
   - 整合 i18n 系統
   - 支援動態語言切換

5. **日誌查詢工具**
   - 建立管理員指令來查詢日誌
   - 過濾和搜尋功能

## 🎯 關鍵原則

在所有改善中，我們遵循了以下原則：

1. **不破壞現有功能** - 所有修改都是加法式的
2. **保持向後兼容** - 舊代碼仍然可以正常運作
3. **尊重原授權** - 不修改 LICENSE，明確標示 fork
4. **提高可維護性** - 統一格式使未來維護更容易
5. **改善使用者體驗** - 清晰的訊息和美觀的介面

## 📞 聯絡資訊

如有任何關於這些改善的問題或建議，請：

- 查看 `DOCUMENTATION_INDEX.md` 了解完整文件
- 參考各個模組的 docstring
- 聯絡 Annaway Studio 技術支援

---

**文件建立日期：** 2025-11-27  
**最後更新：** 2025-11-27  
**維護者：** Annaway Studio

