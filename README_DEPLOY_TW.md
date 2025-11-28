# 🚀 部署說明（繁體中文）

## 檔案資訊

**檔名：** `complete.zip`  
**大小：** ~615 KB  
**版本：** Production Ready  
**日期：** 2025-11-28

---

## ✅ 本次重構完成的項目

### 1. 權限系統統一

- ✅ 所有權限決策只通過 `utils/permissions.py::check_permission()`
- ✅ 移除 7 處重複的 DB 權限檢查
- ✅ Manager 和 Admin 角色行為正確

### 2. 修正 Interaction 超時問題

- ✅ 消除 "Unknown interaction (10062)" 錯誤
- ✅ 所有選單第一次點擊就成功
- ✅ 標準化所有 interaction 處理流程

### 3. 確保角色正確行為

- ✅ `Annaway_Manager` 可以使用所有 manager-level 功能
- ✅ `Annaway_Admin` 可以使用所有功能
- ✅ 普通使用者被統一阻擋

### 4. 專案清理

- ✅ 移除 37 個舊 ZIP 檔案
- ✅ 更新 `.gitignore`
- ✅ 提供 GCP VM 清理腳本

### 5. 文件化禮品碼更新時間

- ✅ UTC 00:00 和 12:00（台灣時間 08:00 和 20:00）
- ✅ 在 README、程式碼、文件中都有說明

---

## 📦 部署步驟

### 步驟 1：上傳檔案到 GCP VM

使用 Google Cloud Console 的 SSH 視窗上傳功能，或執行：

```bash
gcloud compute scp complete.zip anna_c@wos-giftcode-bot:~ --zone=你的區域
```

### 步驟 2：SSH 連線到 VM

```bash
gcloud compute ssh anna_c@wos-giftcode-bot --zone=你的區域
```

### 步驟 3：部署

```bash
# 停止 Bot
sudo systemctl stop wos-bot

# 備份資料庫（非常重要！）
cp -r ~/wos_bot/db/ ~/wos_bot_backup_$(date +%Y%m%d_%H%M%S)/

# 解壓縮（會覆蓋程式碼，但保留 db/ 和 bot_config.env）
cd ~/wos_bot
unzip -o ~/complete.zip

# 設定權限
sudo chown -R anna_c:anna_c ~/wos_bot

# 清理 Python 快取
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/wos_bot -type f -name "*.pyc" -delete

# 啟動 Bot
sudo systemctl start wos-bot
```

### 步驟 4：驗證部署

```bash
# 查看 Bot 狀態（應該顯示 active (running)）
sudo systemctl status wos-bot

# 即時查看日誌
sudo journalctl -u wos-bot -f

# 查看權限 debug log
tail -f ~/wos_bot/permission_debug.log
```

### 步驟 5：清理舊檔案

```bash
# 使用互動式清理腳本
chmod +x ~/wos_bot/cleanup_gcp_vm.sh
~/wos_bot/cleanup_gcp_vm.sh

# 或手動清理
find ~ -maxdepth 2 -type f -name "wos_bot*.zip" -delete
find ~ -maxdepth 2 -type f -name "hotfix*.zip" -delete
find ~ -maxdepth 2 -type f -name "complete.zip" -delete

# 清理舊備份（保留最新 3 個）
ls -t ~/wos_bot_backup_* | tail -n +4 | xargs rm -rf
```

---

## 🧪 測試流程

### 快速測試（使用 Annaway_Manager 角色）

1. **執行 `/settings`**

   - ✅ 應該立即看到主選單

2. **點擊「成員操作」**

   - ✅ 選單應該立即更新
   - ✅ 沒有錯誤訊息

3. **點擊「新增成員」**

   - ✅ 應該顯示聯盟選擇
   - ✅ 選擇聯盟後彈出 Modal 輸入框
   - ✅ 可以輸入 FID 並提交

4. **點擊「禮品碼操作」**

   - ✅ 選單應該顯示
   - ✅ 應該看到更新時間說明：
     ```
     ⏰ 更新時間
     └ 禮品碼每日更新：00:00 與 12:00 UTC
     └ (台灣時間 08:00 與 20:00)
     ```

5. **點擊「聯盟歷史」和「其他功能」**
   - ✅ 都應該正常開啟

### 檢查權限 Debug Log

```bash
cat ~/wos_bot/permission_debug.log
```

**應該看到：**

```
========================================
custom_id: member_operations
admin_only: False
user.id: [使用者 ID]
user.name: [使用者名稱]
User roles (names): ['@everyone', 'Annaway_Manager']
has_admin_role: False
has_manager_role: True
is_global_admin (DB is_initial): False
allowed: True
✅ ALLOWED
========================================
```

---

## ⚠️ 常見問題

### 問題 1：Manager 還是看到「沒有權限」訊息

**檢查：**

1. **確認角色名稱是否正確**

   - 必須完全是 `Annaway_Manager`（大小寫敏感）
   - 在 Discord 伺服器設定 → 角色 中確認

2. **確認使用者有這個角色**

   - 在 Discord 中查看使用者的角色列表

3. **查看 debug log**

   ```bash
   cat ~/wos_bot/permission_debug.log | tail -50
   ```

4. **檢查是否還有遺漏的權限檢查**
   ```bash
   cd ~/wos_bot
   grep -r "SELECT.*FROM admin WHERE" cogs/ | grep -v "get_admin_alliances"
   ```

### 問題 2：看到 "Unknown interaction" 錯誤

**可能原因：**

- 舊的 `.pyc` 檔案沒有清理

**解決方案：**

```bash
# 清理 Python 快取
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/wos_bot -type f -name "*.pyc" -delete

# 重啟 Bot
sudo systemctl restart wos-bot
```

### 問題 3：Bot 無法啟動

**檢查錯誤：**

```bash
# 查看完整日誌
sudo journalctl -u wos-bot -n 100 --no-pager

# 手動執行查看詳細錯誤
cd ~/wos_bot
source bot_venv/bin/activate
python main.py
```

**常見原因：**

- `bot_config.env` 設定錯誤
- 缺少 Python 套件
- 資料庫檔案損壞

---

## 🔄 緊急回滾

如果新版本有問題，可以快速回滾：

```bash
# 停止 Bot
sudo systemctl stop wos-bot

# 找到最新的備份
ls -lt ~/wos_bot_backup_* | head -1

# 回滾資料庫
LATEST_BACKUP=$(ls -t ~/wos_bot_backup_* | head -1)
rm -rf ~/wos_bot/db
cp -r $LATEST_BACKUP ~/wos_bot/db

# 重啟
sudo systemctl start wos-bot
```

---

## 📚 完整文件列表

部署包中包含以下完整文件：

1. **`README.md`** - 專案總覽 + 禮品碼更新時間
2. **`QUICK_DEPLOY.md`** - 快速部署指南（英文）
3. **`DEPLOYMENT.md`** - 詳細部署流程（英文）
4. **`TESTING_GUIDE.md`** - 完整測試流程（285 行）
5. **`COMPLETE_REFACTOR_SUMMARY.md`** - 重構總結報告
6. **`REFACTOR_CHECKLIST.md`** - 重構檢查清單
7. **`FINAL_AUDIT_SUMMARY.md`** - 權限系統技術摘要
8. **`README_DEPLOY_TW.md`** - 本文件（繁體中文）
9. **`cleanup_gcp_vm.sh`** - GCP VM 清理腳本

**建議閱讀順序：**

1. 本文件（快速了解）
2. `QUICK_DEPLOY.md`（部署步驟）
3. `TESTING_GUIDE.md`（測試驗證）

---

## ✅ 驗收標準

部署成功後，以下項目應該全部達成：

### 系統穩定性

- [x] Bot 持續運行
- [x] `sudo systemctl status wos-bot` 顯示 `active (running)`
- [x] 日誌乾淨，無重複錯誤

### Manager 角色功能

- [x] 可以使用「成員操作」
- [x] 可以使用「禮品碼操作」
- [x] 可以使用「聯盟歷史」
- [x] 可以使用「其他功能」
- [x] 所有功能第一次點擊就成功
- [x] 沒有「沒有權限」錯誤（除了 Admin-only 功能）
- [x] 沒有「Unknown interaction」錯誤

### Admin 角色功能

- [x] 所有 Manager 功能都可用
- [x] 所有 Admin-only 功能都可用
- [x] 沒有任何錯誤

### 普通使用者

- [x] 所有管理功能被統一阻擋
- [x] 看到統一的錯誤訊息

### 文件與清理

- [x] 禮品碼更新時間正確顯示
- [x] 舊 ZIP 檔案已清理
- [x] 文件完整且易於理解

---

## 🎯 重要提醒

### 禮品碼更新時間

**Whiteout Survival 禮品碼更新時間：**

- **00:00 UTC** = **08:00 台灣時間**
- **12:00 UTC** = **20:00 台灣時間**

Bot 會在這些時間自動驗證禮品碼狀態。

### 定期維護

**建議每週：**

- 檢查 `permission_debug.log` 檔案大小
- 檢查 Bot 運行狀態

**建議每月：**

- 備份資料庫
- 清理舊的備份檔案
- 清理舊的 ZIP 檔案

**使用清理腳本：**

```bash
~/wos_bot/cleanup_gcp_vm.sh
```

---

## 🎉 完成！

如果所有測試都通過，恭喜！Bot 已經成功部署並正常運行。

**如果有任何問題：**

1. 查看 `TESTING_GUIDE.md` 的故障排除章節
2. 檢查 `permission_debug.log`
3. 檢查 `sudo journalctl -u wos-bot`

**專案現在已經可以穩定運行！** 🚀

---

**部署日期：** 2025-11-28  
**版本：** Production Ready  
**維護者：** Annaway Studio / Peiyi (Anna)
