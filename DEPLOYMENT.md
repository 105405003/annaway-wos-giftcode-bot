# 🚀 部署指南

## 部署到 Google Cloud VM

### 1. 打包本地檔案

在 Windows 本地執行：

```powershell
cd F:\AnnawayProjects\wos_giftcode_redemption_bot

# 打包部署檔案
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
Compress-Archive -Path @(
    "main.py",
    "cogs",
    "utils",
    "permission_manager.py",
    "i18n_manager.py",
    "requirements.txt",
    "README.md"
) -DestinationPath "wos_bot_deploy_$timestamp.zip" -Force

Write-Host "✅ 打包完成：wos_bot_deploy_$timestamp.zip" -ForegroundColor Green
```

### 2. 上傳到 VM

使用 Google Cloud Console 的 SSH 上傳功能，或使用 `gcloud` 指令：

```bash
gcloud compute scp wos_bot_deploy_*.zip anna_c@wos-giftcode-bot:~ --zone=your-zone
```

### 3. 在 VM 上部署

```bash
# 停止 Bot
sudo systemctl stop wos-bot

# 備份資料庫（重要！）
cp -r ~/wos_bot/db/ ~/wos_bot_backup_$(date +%Y%m%d_%H%M%S)/

# 解壓縮新檔案（會覆蓋程式碼，但保留 db/ 和 bot_config.env）
cd ~/wos_bot
unzip -o ~/wos_bot_deploy_*.zip

# 確保權限正確
sudo chown -R anna_c:anna_c ~/wos_bot

# 啟動 Bot
sudo systemctl start wos-bot

# 查看啟動狀態
sudo systemctl status wos-bot

# 查看即時日誌
sudo journalctl -u wos-bot -f
```

### 4. 驗證部署

檢查以下項目：

- ✅ Bot 成功啟動（`systemctl status wos-bot` 顯示 `active (running)`）
- ✅ 沒有錯誤訊息在 `journalctl` 中
- ✅ Discord 中 Bot 顯示為在線
- ✅ 測試 `/main` 指令正常運作
- ✅ 權限系統正確（`Annaway_Manager` 可以使用 manager 功能）

### 5. 清理舊檔案（可選）

```bash
# 清理上傳的 ZIP 檔案
find ~ -maxdepth 2 -type f -name "wos_bot*.zip" -mtime +7 -delete

# 清理舊的備份（保留最近 3 個）
ls -t ~/wos_bot_backup_* | tail -n +4 | xargs rm -rf
```

## 緊急回滾

如果新版本有問題，可以快速回滾到備份：

```bash
# 停止 Bot
sudo systemctl stop wos-bot

# 回滾到最新備份
LATEST_BACKUP=$(ls -t ~/wos_bot_backup_* | head -1)
rm -rf ~/wos_bot/db
cp -r $LATEST_BACKUP ~/wos_bot/db

# 重新啟動
sudo systemctl start wos-bot
```

## 常見問題排查

### Bot 無法啟動

```bash
# 查看詳細錯誤
sudo journalctl -u wos-bot -n 100 --no-pager

# 手動執行查看錯誤
cd ~/wos_bot
source bot_venv/bin/activate
python main.py
```

### 權限問題

```bash
# 確保所有檔案歸 anna_c 所有
sudo chown -R anna_c:anna_c ~/wos_bot

# 確保執行權限
chmod +x ~/wos_bot/main.py
```

### 資料庫問題

```bash
# 檢查資料庫檔案
ls -lh ~/wos_bot/db/

# 如果資料庫損壞，從備份恢復
cp ~/wos_bot_backup_*/alliance.sqlite ~/wos_bot/db/
cp ~/wos_bot_backup_*/settings.sqlite ~/wos_bot/db/
cp ~/wos_bot_backup_*/giftcode.sqlite ~/wos_bot/db/
```

## 權限系統驗證

部署後，驗證權限系統：

1. **使用 `Annaway_Manager` 角色測試：**
   - ✅ 可以點擊「成員管理」
   - ✅ 可以點擊「禮品碼操作」
   - ✅ 可以點擊「聯盟歷史」
   - ✅ 可以點擊「其他功能」
   - ❌ 不能新增/編輯/刪除聯盟

2. **使用 `Annaway_Admin` 角色測試：**
   - ✅ 所有功能都可以使用
   - ✅ 可以新增/編輯/刪除聯盟
   - ✅ 可以管理管理員

3. **查看權限除錯日誌：**
   ```bash
   cat ~/wos_bot/permission_debug.log
   ```

   應該看到類似：
   ```
   custom_id: member_operations
   admin_only: False
   User roles (names): ['@everyone', 'Annaway_Manager']
   has_manager_role: True
   allowed: True
   ✅ ALLOWED
   ```

## 禮品碼更新時間

Bot 會在以下時間自動驗證和更新禮品碼：

- **00:00 UTC** (08:00 台灣時間)
- **12:00 UTC** (20:00 台灣時間)

## systemd 服務管理

```bash
# 查看服務狀態
sudo systemctl status wos-bot

# 啟動服務
sudo systemctl start wos-bot

# 停止服務
sudo systemctl stop wos-bot

# 重新啟動服務
sudo systemctl restart wos-bot

# 查看服務日誌
sudo journalctl -u wos-bot -f

# 查看最近 100 行日誌
sudo journalctl -u wos-bot -n 100 --no-pager
```

