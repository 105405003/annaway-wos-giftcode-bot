# Discord 機器人權限設定指南

## ✅ 重要：機器人不需要管理員權限

這個機器人使用**基於角色的權限系統**，不需要 Discord 的管理員或管理伺服器權限。

---

## 🔧 必要設定

### 1. Discord 開發者門戶設定

前往 [Discord Developer Portal](https://discord.com/developers/applications)：

1. 選擇您的應用程式
2. 進入 **Bot** 頁面
3. 在 **Privileged Gateway Intents** 區塊啟用：
   - ✅ **Server Members Intent** （必須！用於讀取成員角色）
   - ✅ **Message Content Intent** （必須！）

### 2. 機器人邀請權限

生成邀請連結時，只需要勾選以下權限：

#### 基本權限（必須）
- ✅ 查看頻道 (View Channels)
- ✅ 發送訊息 (Send Messages)
- ✅ 嵌入連結 (Embed Links)
- ✅ 附加檔案 (Attach Files)
- ✅ 讀取訊息歷史 (Read Message History)
- ✅ 使用應用程式命令 (Use Application Commands)

#### 不需要的權限
- ❌ 管理員 (Administrator)
- ❌ 管理伺服器 (Manage Server)
- ❌ 管理頻道 (Manage Channels)
- ❌ 管理角色 (Manage Roles)
- ❌ 踢除成員 (Kick Members)
- ❌ 封鎖成員 (Ban Members)

**權限整數值：** `277025508416`

**邀請連結範例：**
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=277025508416&scope=bot%20applications.commands
```

### 3. 在伺服器中創建角色

在您的 Discord 伺服器設定中：

1. 進入 **伺服器設定** → **角色**
2. 創建兩個新角色（名稱必須完全一致，區分大小寫）：
   - `Annaway_Admin` - 完整管理權限
   - `Annaway_Manager` - 操作管理權限
3. 將這些角色分配給需要使用管理功能的使用者

**重要：** 這兩個角色不需要賦予任何 Discord 權限，只是標記身份用的普通角色即可。

---

## 🎯 權限運作方式

### 機器人如何檢查權限

1. **讀取使用者的角色**
   - 機器人讀取執行指令的使用者有哪些角色
   - 檢查是否包含 `Annaway_Admin` 或 `Annaway_Manager`

2. **根據角色決定權限**
   - `Annaway_Admin`: 可以創建/刪除聯盟、管理所有設定
   - `Annaway_Manager`: 可以管理成員、兌換禮品碼、查看統計
   - 一般使用者: 只能使用 `/add` 指令新增成員

3. **機器人本身只需要基本權限**
   - 發送訊息和嵌入內容
   - 讀取訊息歷史
   - 執行斜線命令

### 為什麼不需要管理權限？

機器人只是：
- 📊 記錄和顯示資料
- 🎁 協助兌換禮品碼
- 👥 追蹤成員資訊
- 📈 產生統計報表

機器人**不會**：
- ❌ 創建或刪除頻道
- ❌ 修改伺服器設定
- ❌ 管理其他機器人或成員的角色
- ❌ 踢除或封鎖成員

---

## 🐛 常見問題排除

### 問題：收到「機器人需要管理伺服器權限」錯誤

**原因：** 程式碼中有一個錯誤的權限檢查（已在 v1.2.1 修復）

**解決方案：**
1. 確認您使用的是最新版本的程式碼
2. 檢查 `cogs/alliance.py` 第 152-163 行是否已移除 `manage_guild` 檢查
3. 重新啟動機器人

**修復內容：**
```python
# 舊版（錯誤）：
if perm_check and not perm_check.guild_permissions.manage_guild:
    await interaction.response.send_message(
        _("bot_needs_admin_permission", "ERRORS"), 
        ephemeral=True
    )
    return

# 新版（正確）：
# 機器人不需要 manage_guild 權限，只需要基本的發送訊息權限
# 權限控制已透過 Annaway_Admin/Manager 角色實現
```

### 問題：指令無回應

**檢查清單：**
- ✅ 確認 Server Members Intent 已啟用
- ✅ 確認機器人在線
- ✅ 確認機器人有「查看頻道」和「發送訊息」權限
- ✅ 確認在伺服器頻道中使用（不是私訊）

### 問題：顯示「權限不足」

**檢查清單：**
- ✅ 確認角色名稱完全正確：`Annaway_Admin` 或 `Annaway_Manager`
- ✅ 確認使用者已被分配這些角色
- ✅ 確認角色在機器人角色之上（Discord 角色階層）

### 問題：無法讀取成員角色

**原因：** Server Members Intent 未啟用

**解決方案：**
1. 前往 Discord Developer Portal
2. Bot → Privileged Gateway Intents
3. 啟用 Server Members Intent
4. 重新啟動機器人

---

## 📝 告訴伺服器管理員

如果您不是伺服器管理員，可以將以下內容傳給管理員：

---

### 給伺服器管理員的設定說明

感謝您協助設定 WOS 禮品碼機器人！設定很簡單：

#### 步驟 1：創建兩個角色

在伺服器設定中創建這兩個角色（名稱必須完全一致）：
- `Annaway_Admin` - 給完全管理權限的人員
- `Annaway_Manager` - 給日常操作人員

這兩個角色**不需要**賦予任何特殊的 Discord 權限，只是標記身份的普通角色即可。

#### 步驟 2：確認機器人權限

機器人只需要這些基本權限（邀請時應該已經設定好）：
- 查看頻道
- 發送訊息
- 嵌入連結
- 附加檔案
- 讀取訊息歷史
- 使用應用程式命令

**不需要**給機器人「管理員」或「管理伺服器」權限！

#### 步驟 3：分配角色給使用者

將 `Annaway_Admin` 或 `Annaway_Manager` 角色分配給需要使用機器人管理功能的人員。

#### 驗證設定

- 沒有角色的人執行 `/settings` → 應該看到「權限不足」
- 有 Manager 角色的人執行 `/settings` → 應該可以成功
- 所有人都可以使用 `/add` 指令

---

## 🔒 安全性說明

### 最小權限原則

這個機器人遵循「最小權限原則」：
- 只要求完成功能所需的最低權限
- 不要求任何伺服器管理權限
- 權限控制透過自訂角色實現

### 為什麼這樣設計更安全？

1. **降低風險**
   - 即使機器人帳號被入侵，攻擊者也無法修改伺服器設定
   - 無法刪除頻道或踢除成員

2. **透明控制**
   - 伺服器管理員可以清楚看到誰有管理權限（透過角色）
   - 隨時可以移除某人的管理權限（移除角色）

3. **多伺服器支援**
   - 每個伺服器都可以獨立控制誰有管理權限
   - 不同伺服器的資料完全隔離

---

## 📊 權限對照表

| 功能 | 需要的 Discord 權限 | 需要的角色 |
|------|-------------------|-----------|
| 檢視頻道內容 | View Channels | - |
| 發送訊息和嵌入 | Send Messages, Embed Links | - |
| 執行 `/add` 指令 | Use Application Commands | 無（所有人） |
| 執行 `/settings` 指令 | Use Application Commands | Annaway_Admin 或 Annaway_Manager |
| 創建/刪除聯盟 | Use Application Commands | Annaway_Admin |
| 管理成員 | Use Application Commands | Annaway_Admin 或 Annaway_Manager |
| 兌換禮品碼 | Use Application Commands | Annaway_Admin 或 Annaway_Manager |

---

## 🎓 技術說明

### 權限檢查實作

機器人使用 `utils/permissions.py` 中的函式檢查權限：

```python
def has_annaway_role(member: discord.Member) -> bool:
    """檢查成員是否有 Annaway_Admin 或 Annaway_Manager 角色"""
    role_names = {role.name for role in member.roles}
    return ADMIN_ROLE_NAME in role_names or MANAGER_ROLE_NAME in role_names
```

### 為什麼需要 Server Members Intent？

Server Members Intent 允許機器人：
- 讀取成員的角色列表
- 檢查成員是否有特定角色
- 在成員資訊更新時收到通知

**不會**讓機器人：
- 修改成員的角色
- 踢除或封鎖成員
- 存取成員的私人訊息

---

## ✅ 設定檢查清單

完成以下檢查清單以確保正確設定：

### Discord 開發者門戶
- [ ] Server Members Intent 已啟用
- [ ] Message Content Intent 已啟用

### Discord 伺服器
- [ ] 已創建 `Annaway_Admin` 角色（名稱完全正確）
- [ ] 已創建 `Annaway_Manager` 角色（名稱完全正確）
- [ ] 至少有一位使用者有 Admin 角色
- [ ] 機器人有基本權限（發送訊息、嵌入連結等）
- [ ] 機器人**沒有**被給予不必要的管理權限

### 功能測試
- [ ] 有角色的使用者可以執行 `/settings`
- [ ] 沒有角色的使用者會看到「權限不足」
- [ ] 所有人都可以使用 `/add` 指令
- [ ] 機器人可以正常發送訊息和嵌入內容

---

## 📞 需要協助？

如果遇到問題：

1. 檢查本文件的「常見問題排除」章節
2. 確認使用最新版本的程式碼
3. 查看終端機的錯誤訊息
4. 檢查 `log/` 資料夾中的日誌檔案
5. 在 GitHub 上開啟 issue

---

**更新日期：** 2026-01-25  
**版本：** v1.2.1  
**狀態：** 已修復 manage_guild 權限檢查問題
