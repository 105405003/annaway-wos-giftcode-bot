# WOS 禮品碼兌換機器人 - 權限管理系統

## 🔐 權限等級說明

本機器人採用基於 Discord 身分組的權限管理系統，根據使用者的身分組分配不同的權限等級。

### 📋 權限等級

#### 1. **Annaway_Admin（最高管理員）**

- **身分組名稱：** `Annaway_Admin`
- **權限等級：** 3 (最高)
- **可用功能：**
  - ✅ 聯盟管理（新增、編輯、刪除、查看）
  - ✅ 權限管理（設定用戶權限等級、管理所有用戶權限）
  - ✅ 成員管理（新增、移除、查看、轉移、更新成員資訊）
  - ✅ 禮品碼管理（測試、新增禮品碼）
  - ✅ 統計查看（查看各種統計資料）
  - ✅ 設定存取（完整設定選單）

#### 2. **Annaway_Manager（管理員）**

- **身分組名稱：** `Annaway_Manager`
- **權限等級：** 2 (中等)
- **可用功能：**
  - ❌ 聯盟管理
  - ❌ 權限管理
  - ✅ 成員管理（新增、移除、查看、轉移、更新成員資訊）
  - ✅ 禮品碼管理（測試、新增禮品碼）
  - ✅ 統計查看（查看各種統計資料）
  - ✅ 設定存取（部分設定選單）

#### 3. **User（基本使用者）**

- **身分組名稱：** 其他所有使用者
- **權限等級：** 1 (基本)
- **可用功能：**
  - ❌ 聯盟管理
  - ❌ 權限管理
  - ❌ 成員管理
  - ❌ 禮品碼管理
  - ❌ 統計查看
  - ❌ 設定存取
  - ✅ 新增成員（僅限 `/add` 命令）

## 🎯 命令使用說明

### Annaway_Admin 專用命令

#### `/settings`

- **功能：** 開啟完整設定選單
- **可用選項：**
  - 🏰 聯盟管理
  - 👥 成員管理
  - 🎁 禮品碼管理
  - 📊 統計查看
  - ⚙️ 權限管理

#### `/permission <user> <level>`

- **功能：** 管理使用者權限等級
- **參數：**
  - `user`: 要管理權限的使用者
  - `level`: 權限等級 (admin/manager/user)
- **範例：** `/permission @使用者 manager`

#### `/check_permission [user]`

- **功能：** 檢查使用者權限等級
- **參數：**
  - `user`: 要檢查的使用者（可選，預設為自己）

### Annaway_Manager 專用命令

#### `/settings`

- **功能：** 開啟部分設定選單
- **可用選項：**
  - 👥 成員管理
  - 🎁 禮品碼管理
  - 📊 統計查看

### User 專用命令

#### `/add <oper1> <oper2>`

- **功能：** 新增成員到聯盟（所有人都可以使用）
- **參數：**
  - `oper1`: 聯盟簡稱（聯盟名稱）
  - `oper2`: UID（玩家 ID）
- **範例：** `/add ABC 12345`
- **說明：**
  - 任何人都可以使用此命令來添加玩家 ID 到聯盟
  - 支援模糊匹配聯盟名稱（如輸入「AB」可以找到「ABC」聯盟）
  - 會自動檢查 UID 是否已存在於該聯盟
  - 使用 Discord 身分組權限系統進行額外控制

## 🔧 技術實現

### 權限檢查機制

```python
from permission_manager import permission_manager, PermissionLevel

# 檢查使用者權限等級
user_level = permission_manager.get_user_permission_level(member)

# 檢查特定功能權限
has_permission = permission_manager.has_permission(member, "alliance_management")

# 權限等級枚舉
PermissionLevel.ADMIN    # 3 - 最高管理員
PermissionLevel.MANAGER  # 2 - 管理員
PermissionLevel.USER     # 1 - 基本使用者
```

### 資料庫結構

#### `role_permissions` 表

```sql
CREATE TABLE role_permissions (
    role_name TEXT PRIMARY KEY,
    permission_level INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### `user_permissions` 表

```sql
CREATE TABLE user_permissions (
    user_id INTEGER PRIMARY KEY,
    permission_level INTEGER,
    granted_by INTEGER,
    granted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (granted_by) REFERENCES admin(id)
);
```

## 🚀 設定步驟

### 1. 建立 Discord 身分組

在您的 Discord 伺服器中建立以下身分組：

- `Annaway_Admin`
- `Annaway_Manager`

### 2. 分配身分組

將適當的使用者分配到對應的身分組：

- 將最高管理員設為 `Annaway_Admin`
- 將一般管理員設為 `Annaway_Manager`
- 其他使用者保持預設（User 等級）

### 3. 測試權限

使用以下命令測試權限系統：

- `/check_permission` - 檢查自己的權限
- `/settings` - 測試設定選單存取
- `/add ABC 12345` - 測試新增成員功能

## 📝 使用範例

### Annaway_Admin 操作範例

```
/settings
→ 顯示完整設定選單，包含所有功能

/permission @使用者 manager
→ 將指定使用者設為管理員等級

/check_permission @使用者
→ 檢查指定使用者的權限等級
```

### Annaway_Manager 操作範例

```
/settings
→ 顯示部分設定選單，僅包含成員管理、禮品碼管理、統計查看

/add ABC 12345
→ 新增 UID 12345 到聯盟 ABC
```

### User 操作範例

```
/add ABC 12345
→ 新增 UID 12345 到聯盟 ABC

/settings
→ 顯示權限不足訊息
```

## ⚠️ 注意事項

1. **身分組名稱必須完全匹配**：`Annaway_Admin` 和 `Annaway_Manager` 必須與 Discord 身分組名稱完全一致
2. **權限繼承**：較高權限等級包含較低權限等級的所有功能
3. **首次設定**：只有 `Annaway_Admin` 可以進行機器人的首次設定
4. **權限管理**：只有 `Annaway_Admin` 可以修改其他使用者的權限等級

## 🔄 更新和維護

### 添加新的權限等級

1. 在 `permission_manager.py` 中的 `PermissionLevel` 枚舉添加新等級
2. 在 `role_permissions` 字典中添加身分組對應
3. 在 `permission_functions` 中定義新等級的功能權限

### 修改功能權限

1. 在 `permission_manager.py` 中的 `permission_functions` 修改對應功能
2. 重新啟動機器人以載入新設定

---

**重要提醒**：請確保正確設定 Discord 身分組，並將適當的使用者分配到對應的身分組中，以確保權限系統正常運作。
