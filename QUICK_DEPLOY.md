# 🚀 快速部署指南

## 檔案資訊

**檔名**: `complete.zip` 或 `wos_bot_complete.zip`  
**大小**: ~600 KB  
**版本**: Production Ready (2025-11-28)

---

## 部署到 GCP VM

### 步驟 1: 上傳檔案

使用 Google Cloud Console 的 SSH 視窗上傳功能，或：

```bash
gcloud compute scp complete.zip anna_c@wos-giftcode-bot:~ --zone=your-zone
```

### 步驟 2: 在 VM 上部署

```bash
# SSH 到 VM
gcloud compute ssh anna_c@wos-giftcode-bot --zone=your-zone

# 停止 Bot
sudo systemctl stop wos-bot

# 備份資料庫（重要！）
cp -r ~/wos_bot/db/ ~/wos_bot_backup_$(date +%Y%m%d_%H%M%S)/

# 解壓縮（會覆蓋程式碼，保留 db/ 和 bot_config.env）
cd ~/wos_bot
unzip -o ~/complete.zip

# 設定權限
sudo chown -R anna_c:anna_c ~/wos_bot

# 啟動 Bot
sudo systemctl start wos-bot

# 查看狀態
sudo systemctl status wos-bot
```

### 步驟 3: 驗證部署

```bash
# 即時查看日誌
sudo journalctl -u wos-bot -f

# 查看權限 debug log
tail -f ~/wos_bot/permission_debug.log

# 應該看到 Bot 成功啟動，沒有錯誤
```

---

## Discord 測試流程

### 測試 1: Manager 角色

**使用擁有 `Annaway_Manager` 角色的帳號：**

1. **執行 `/settings`**
   - ✅ 應該看到主選單
   
2. **點擊「成員操作」**
   - ✅ 應該開啟成員操作選單
   - ✅ 點擊「新增成員」→ 選擇聯盟 → 應該彈出 Modal
   - ✅ 可以正常輸入並提交
   
3. **點擊「禮品碼操作」**
   - ✅ 應該看到主選單，包含更新時間說明
   - ✅ 顯示：「禮品碼每日更新：00:00 與 12:00 UTC (台灣時間 08:00 與 20:00)」
   
4. **點擊「聯盟歷史」**
   - ✅ 應該正常開啟
   
5. **點擊「其他功能」**
   - ✅ 應該正常開啟

**預期：所有功能都可以正常使用，沒有錯誤訊息**

### 測試 2: Admin 角色

**使用擁有 `Annaway_Admin` 角色的帳號：**

1. **測試所有 Manager 功能**
   - ✅ 全部可用
   
2. **測試 Admin-only 功能**
   - ✅ 聯盟操作 → 新增/編輯/刪除聯盟
   - ✅ Bot 操作 → 新增/移除管理員
   - ✅ 日誌系統 → 設定/移除日誌頻道

**預期：所有功能都可以正常使用**

### 測試 3: 普通使用者

**使用沒有特殊角色的帳號：**

1. **執行 `/settings`（如果指令有限制）**
   - ❌ 應該被阻擋
   - ❌ 看到：「You do not have permission to perform this action.」

**預期：所有管理功能都被統一阻擋**

---

## 檢查 Permission Debug Log

```bash
cat ~/wos_bot/permission_debug.log
```

### 對於 Manager，應該看到：

```
========================================
custom_id: member_operations
admin_only: False
user.id: [ID]
user.name: [名稱]
User roles (names): ['@everyone', 'Annaway_Manager']
has_admin_role: False
has_manager_role: True
allowed: True
✅ ALLOWED
========================================
```

### 如果看到 `❌ DENIED`：

檢查角色設定：
```bash
# 在 Discord 中：
# 1. 伺服器設定 → 角色
# 2. 確認 Annaway_Manager 和 Annaway_Admin 角色存在
# 3. 確認角色名稱完全正確（大小寫敏感）
# 4. 確認測試使用者有正確的角色
```

---

## 清理舊檔案

### 使用清理腳本：

```bash
cd ~/wos_bot
chmod +x cleanup_gcp_vm.sh
./cleanup_gcp_vm.sh
```

### 或手動清理：

```bash
# 清理 ZIP 檔案
find ~ -maxdepth 2 -type f -name "wos_bot*.zip" -delete
find ~ -maxdepth 2 -type f -name "hotfix*.zip" -delete
find ~ -maxdepth 2 -type f -name "complete.zip" -delete

# 清理舊備份（保留最新 3 個）
ls -t ~/wos_bot_backup_* | tail -n +4 | xargs rm -rf

# 查看磁碟使用
df -h ~
du -sh ~/wos_bot
```

---

## 常見問題

### Q: Bot 無法啟動

```bash
# 查看詳細錯誤
sudo journalctl -u wos-bot -n 100 --no-pager

# 手動執行查看錯誤
cd ~/wos_bot
source bot_venv/bin/activate
python main.py
```

### Q: 看到 "Unknown interaction" 錯誤

**可能原因：**
- 舊的 `.pyc` 檔案沒有更新

**解決方案：**
```bash
# 清理 Python 快取
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} +
find ~/wos_bot -type f -name "*.pyc" -delete

# 重啟 Bot
sudo systemctl restart wos-bot
```

### Q: Manager 還是被擋住

**檢查：**
```bash
# 1. 確認角色名稱
# 在 Discord 中檢查角色是否完全是 "Annaway_Manager"

# 2. 查看 permission_debug.log
cat ~/wos_bot/permission_debug.log | grep -A 15 "DENIED"

# 3. 確認沒有殘留的 DB 權限檢查
cd ~/wos_bot
grep -r "SELECT.*FROM admin WHERE" cogs/ | grep -v "get_admin_alliances"
grep -r "not_authorized" cogs/
```

---

## 緊急回滾

如果新版本有問題：

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

## 完整文件列表

部署包中包含以下文件：

- **`README.md`**: 專案總覽 + 禮品碼更新時間
- **`DEPLOYMENT.md`**: 詳細部署流程
- **`TESTING_GUIDE.md`**: 完整測試流程
- **`FINAL_AUDIT_SUMMARY.md`**: 權限系統審查摘要
- **`cleanup_gcp_vm.sh`**: GCP VM 清理腳本

---

## ✅ 驗收標準

部署成功後應該滿足：

- ✅ Bot 穩定運行，`systemctl status wos-bot` 顯示 active (running)
- ✅ Manager 可以使用所有四個主要功能
- ✅ Admin 可以使用所有功能
- ✅ 普通使用者被統一阻擋
- ✅ 沒有 "Unknown interaction" 錯誤
- ✅ `permission_debug.log` 顯示正確的權限判斷
- ✅ 禮品碼選單顯示更新時間（UTC 0/12，台灣 8/20）

---

## 🎉 完成！

如果所有測試都通過，恭喜！Bot 已經成功部署並運行正常。

**建議：**
- 定期備份資料庫（每週一次）
- 定期清理舊的 ZIP 和備份檔案（每月一次）
- 監控 `permission_debug.log` 檔案大小
- 關注 Discord API 的變更

**問題回報：**
- 如果發現任何問題，請查看 `TESTING_GUIDE.md` 中的故障排除章節
- 保留 `permission_debug.log` 和 `journalctl` 日誌以便分析

