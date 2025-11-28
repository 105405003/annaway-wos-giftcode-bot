# 🧪 完整測試指南

## 部署後驗證步驟

### 第一步：檢查 Bot 狀態

```bash
# SSH 到 GCP VM
gcloud compute ssh anna_c@wos-giftcode-bot --zone=your-zone

# 檢查服務狀態
sudo systemctl status wos-bot

# 應該看到：Active: active (running)
```

### 第二步：查看啟動日誌

```bash
# 即時查看日誌
sudo journalctl -u wos-bot -f

# 或查看最近 100 行
sudo journalctl -u wos-bot -n 100 --no-pager

# 確認沒有錯誤訊息，應該看到 Bot 成功登入
```

### 第三步：查看權限 Debug Log

```bash
cd ~/wos_bot
cat permission_debug.log

# 或即時監控
tail -f permission_debug.log
```

---

## Discord 完整測試流程

### 測試帳號準備

1. **測試帳號 A** - 擁有 `Annaway_Manager` 角色
2. **測試帳號 B** - 擁有 `Annaway_Admin` 角色  
3. **測試帳號 C** - 無任何特殊角色（普通使用者）

---

## 📋 測試清單 - Annaway_Manager

### 1. 主選單測試

```
步驟：
1. 在 Discord 中執行 /settings
2. 應該看到主選單，包含以下按鈕：
   ✅ 聯盟操作
   ✅ 成員操作
   ✅ 禮品碼操作
   ✅ 聯盟歷史
   ✅ 其他功能
   ✅ 主選單

預期結果：
- 所有按鈕都可以點擊
- 不會看到 "You do not have permission" 錯誤
```

### 2. 成員操作測試

```
步驟：
1. 點擊「成員操作」按鈕
2. 應該看到成員操作選單，包含：
   ➕ 新增成員
   ➖ 移除成員
   🔄 轉移成員
   📋 查看成員
   🔄 更新成員資訊
   🏠 主選單

測試 2.1 - 新增成員：
1. 點擊「新增成員」
2. 應該看到聯盟選擇選單
3. 選擇一個聯盟
4. 應該彈出 Modal 輸入框
5. 輸入 FID 測試（例如：123456）

預期結果：
- ✅ 正常彈出 Modal
- ✅ 可以輸入並提交
- ✅ 看到處理結果訊息
- ❌ 不會看到 "Unknown interaction" 錯誤
- ❌ 不會看到 "You do not have permission" 錯誤

測試 2.2 - 查看成員：
1. 點擊「查看成員」
2. 選擇一個聯盟
3. 應該看到成員列表

預期結果：
- ✅ 正常顯示成員列表
- ✅ 可以翻頁（如果成員多於一頁）

測試 2.3 - 返回主選單：
1. 點擊「主選單」按鈕
2. 應該回到主選單

預期結果：
- ✅ 正常回到主選單
- ❌ 不會卡住或無反應
```

### 3. 禮品碼操作測試

```
步驟：
1. 在主選單點擊「禮品碼操作」
2. 應該看到禮品碼操作選單

預期看到的資訊：
- 📋 操作選項
- ⏰ 更新時間說明：
  "禮品碼每日更新：00:00 與 12:00 UTC"
  "(台灣時間 08:00 與 20:00)"

測試 3.1 - 新增禮品碼（如果設定為 Manager 可用）：
1. 點擊「新增禮品碼」
2. 應該彈出 Modal
3. 輸入測試禮品碼（例如：TEST2024）

預期結果：
- ✅ 正常彈出 Modal
- ✅ 可以提交
- ✅ 看到成功或錯誤訊息
- ❌ 不會看到 "not_authorized" 錯誤

測試 3.2 - 查看禮品碼設定：
1. 點擊「禮品碼設定」按鈕（如果有）

預期結果：
- 如果是 Manager-level → ✅ 可以查看
- 如果是 Admin-only → ❌ 被 check_permission 擋下
```

### 4. 聯盟歷史測試

```
步驟：
1. 在主選單點擊「聯盟歷史」
2. 應該看到歷史記錄選單

測試 4.1 - 查看熔爐變更：
1. 點擊「熔爐變更」按鈕
2. 選擇聯盟
3. 應該看到變更記錄

預期結果：
- ✅ 正常顯示記錄
- ❌ 不會出現 "Unknown interaction" (10062)
- ❌ 不會卡住

測試 4.2 - 查看暱稱變更：
1. 點擊「暱稱變更」按鈕
2. 應該看到暱稱變更記錄

預期結果：
- ✅ 正常顯示記錄
```

### 5. 其他功能測試

```
步驟：
1. 在主選單點擊「其他功能」
2. 應該看到其他功能選單

測試各個子功能：
- 📊 統計報表
- 其他 Manager-level 功能

預期結果：
- ✅ Manager-level 功能都可以正常使用
- ❌ Admin-only 功能應該被擋下（由 check_permission 統一處理）
- ❌ 不會出現 "Unknown interaction"
```

---

## 📋 測試清單 - Annaway_Admin

### 1. 所有 Manager 功能測試

```
預期結果：
- ✅ Admin 可以使用所有 Manager 的功能
- ✅ 沒有任何限制
```

### 2. Admin-Only 功能測試

```
測試 2.1 - 聯盟操作（Admin-only）：
1. 在主選單點擊「聯盟操作」
2. 應該看到：
   ➕ 新增聯盟
   ✏️ 編輯聯盟
   🗑️ 刪除聯盟
   👀 查看聯盟
   🔍 檢查聯盟

3. 測試新增聯盟：
   - 點擊「新增聯盟」
   - 應該彈出 Modal
   - 可以成功新增

預期結果：
- ✅ 所有操作都可以正常執行
- ❌ 不會被錯誤擋下

測試 2.2 - Bot 操作（部分 Admin-only）：
1. 點擊「Bot 操作」（如果有）
2. 測試：
   - 新增管理員 (Admin-only)
   - 移除管理員 (Admin-only)
   - 查看管理員 (Admin-only)
   - Bot 狀態 (Manager/Admin)

預期結果：
- ✅ Admin-only 功能可以使用
- ✅ Manager-level 功能也可以使用

測試 2.3 - 日誌系統：
1. 點擊「日誌系統」
2. 測試：
   - 設定日誌頻道 (Admin-only)
   - 移除日誌頻道 (Admin-only)
   - 查看日誌頻道 (Manager/Admin)

預期結果：
- ✅ 所有功能都可以正常使用
```

---

## 📋 測試清單 - 普通使用者

### 1. 嘗試使用管理功能

```
步驟：
1. 執行 /settings（如果指令有權限限制，應該直接被阻擋）
2. 或嘗試點擊任何管理相關的按鈕

預期結果：
- ❌ 應該看到統一的錯誤訊息：
  "❌ You do not have permission to perform this action."
- ❌ 不應該看到多種不同的錯誤訊息
- ❌ 不應該看到任何 DB 相關的錯誤
```

---

## 🔍 檢查 Permission Debug Log

測試完成後，在 GCP VM 上執行：

```bash
cat ~/wos_bot/permission_debug.log
```

### 對於 Manager 使用者，應該看到：

```
========================================
custom_id: member_operations
admin_only: False
user.id: [使用者 ID]
user.name: [使用者名稱]
guild.id: [伺服器 ID]
guild.name: [伺服器名稱]
User roles (names): ['@everyone', 'Annaway_Manager']
has_admin_role: False
has_manager_role: True
is_global_admin (DB is_initial): False
allowed: True
✅ ALLOWED
========================================
```

### 如果看到 `❌ DENIED`，檢查：

1. **角色名稱是否正確**：
   - 必須完全是 `Annaway_Manager`（大小寫敏感）
   - 不能是 `Manager` 或 `annaway_manager`

2. **使用者是否真的有這個角色**：
   - 在 Discord 伺服器設定中確認
   - 確認角色有正確分配給測試使用者

3. **Bot 是否有權限讀取角色**：
   - Bot 需要 `View Server Members` 權限
   - Bot 的角色位置要高於 Manager/Admin 角色

---

## 常見問題排查

### 問題 1：看到 "Unknown interaction" (10062)

**可能原因：**
- Interaction 超過 3 秒沒回應
- 同一個 interaction 被回應多次

**檢查：**
```bash
# 查看日誌中的 traceback
sudo journalctl -u wos-bot -n 200 --no-pager | grep -A 10 "10062"
```

**解決方案：**
- 確認所有 menu 函式都在最開始 `defer()`
- 確認使用 `edit_original_response` 而不是 `send_message`

### 問題 2：Manager 被擋住，但 log 顯示 ALLOWED

**可能原因：**
- 函式內部還有第二層 DB 權限檢查

**檢查：**
```bash
# 搜尋是否還有遺漏的 DB 檢查
cd ~/wos_bot
grep -r "SELECT.*FROM admin WHERE" cogs/
grep -r "not_authorized" cogs/
grep -r "You do not have permission" cogs/
```

**解決方案：**
- 移除所有內部的 DB 權限檢查
- 只保留 `check_permission` 的判斷

### 問題 3：Bot 無法啟動

**檢查：**
```bash
# 查看完整錯誤
sudo journalctl -u wos-bot -n 100 --no-pager

# 手動執行查看錯誤
cd ~/wos_bot
source bot_venv/bin/activate
python main.py
```

**常見原因：**
- 缺少 Python 套件
- `bot_config.env` 設定錯誤
- 資料庫檔案損壞

---

## ✅ 驗收標準

完成所有測試後，應該滿足：

### Manager 角色：
- ✅ 四個主要按鈕（成員操作/禮品碼/歷史/其他）全部可用
- ✅ 所有子功能正常運作
- ✅ 沒有 "Unknown interaction" 錯誤
- ✅ 沒有 "You do not have permission" 錯誤（除了 Admin-only 功能）
- ✅ permission_debug.log 顯示 `✅ ALLOWED`

### Admin 角色：
- ✅ 所有功能都可以使用
- ✅ Admin-only 功能正常運作
- ✅ 沒有任何錯誤訊息

### 普通使用者：
- ✅ 所有管理功能被統一阻擋
- ✅ 只看到一種錯誤訊息（來自 check_permission）

### 系統層面：
- ✅ Bot 穩定運行，沒有 crash
- ✅ 日誌乾淨，沒有重複的錯誤
- ✅ Interaction 響應時間 < 3 秒
- ✅ 禮品碼更新時間正確顯示（UTC 0/12，台灣 8/20）

---

## 📊 測試報告模板

```markdown
# Bot 測試報告

**測試日期：** [日期]
**測試者：** [姓名]
**Bot 版本：** [版本號/部署時間]

## Manager 測試結果

| 功能 | 狀態 | 備註 |
|------|------|------|
| 主選單 | ✅/❌ | |
| 成員操作 | ✅/❌ | |
| 禮品碼操作 | ✅/❌ | |
| 聯盟歷史 | ✅/❌ | |
| 其他功能 | ✅/❌ | |

## Admin 測試結果

| 功能 | 狀態 | 備註 |
|------|------|------|
| 聯盟操作 | ✅/❌ | |
| Admin 管理 | ✅/❌ | |
| 日誌系統 | ✅/❌ | |

## 發現的問題

1. [問題描述]
   - 重現步驟：
   - 預期結果：
   - 實際結果：
   - 錯誤訊息：

## 總結

- 通過測試：[數量]
- 失敗測試：[數量]
- 整體評價：✅ 通過 / ❌ 需要修正
```

---

## 🔧 快速故障排除指令

```bash
# 重啟 Bot
sudo systemctl restart wos-bot

# 查看最新日誌
sudo journalctl -u wos-bot -n 50 --no-pager

# 查看權限 debug
tail -n 100 ~/wos_bot/permission_debug.log

# 檢查 Bot 進程
ps aux | grep python | grep main.py

# 檢查資料庫
ls -lh ~/wos_bot/db/

# 清理舊的 debug log
> ~/wos_bot/permission_debug.log

# 手動測試 Python 環境
cd ~/wos_bot
source bot_venv/bin/activate
python -c "import discord; print(discord.__version__)"
```

