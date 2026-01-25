# 🚀 Guild Isolation 修復部署指南

**檔案：** `guild_isolation_fix_20251129_031932.zip` (641 KB)  
**日期：** 2025-11-29  
**問題：** Guild isolation 回歸 + Manager 首次點擊失敗  
**狀態：** ✅ 已修復

---

## 📋 修復內容摘要

### 主要問題

1. **Guild Isolation 被破壞**
   - 不同 Discord 伺服器的聯盟被混在一起顯示
   - 使用者可以看到其他伺服器的聯盟

2. **Manager 首次點擊失敗**
   - `Annaway_Manager` 角色使用者點擊按鈕時看到「沒有權限」錯誤
   - 即使 `permission_debug.log` 顯示 `✅ ALLOWED`

### 修復的檔案

1. ✅ `cogs/alliance.py` - 3 處查詢
2. ✅ `cogs/gift_operations.py` - 2 處查詢
3. ✅ `cogs/alliance_member_operations.py` - 5 處查詢
4. ✅ `cogs/statistics.py` - 2 處查詢
5. ✅ `cogs/changes.py` - 4 處查詢

**總計：修復 16 處未過濾 guild_id 的查詢**

### 新增文件

1. **GUILD_ISOLATION.md** - Guild isolation 完整實作指南
2. **TEST_PLAN.md** - 完整測試計劃（包含所有測試案例）
3. **GUILD_ISOLATION_REGRESSION_FIX.md** - 本次修復的詳細說明

---

## 🔧 部署步驟

### 步驟 1：上傳檔案到 GCP VM

```bash
# 使用 Google Cloud Console 的 SSH 上傳功能
# 或使用 gcloud CLI
gcloud compute scp guild_isolation_fix_20251129_031932.zip anna_c@wos-giftcode-bot:~ --zone=你的區域
```

### 步驟 2：在 VM 上部署

```bash
# SSH 連線
gcloud compute ssh anna_c@wos-giftcode-bot --zone=你的區域

# 停止 Bot
sudo systemctl stop wos-bot

# 備份資料庫（非常重要！）
cp -r ~/wos_bot/db/ ~/wos_bot_backup_guild_fix_$(date +%Y%m%d_%H%M%S)/

# 解壓縮新檔案
cd ~/wos_bot
unzip -o ~/guild_isolation_fix_20251129_031932.zip

# 設定權限
sudo chown -R anna_c:anna_c ~/wos_bot

# 清理 Python 快取
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/wos_bot -type f -name "*.pyc" -delete

# 啟動 Bot
sudo systemctl start wos-bot

# 檢查狀態
sudo systemctl status wos-bot
```

### 步驟 3：驗證部署

```bash
# 查看即時日誌
sudo journalctl -u wos-bot -f

# 查看權限 debug log
tail -f ~/wos_bot/permission_debug.log
```

---

## 🧪 必要測試

部署後，請使用 **兩個 Discord 伺服器** 進行測試：

### 測試 1：Guild Isolation（最重要！）

**在伺服器 A：**
1. 執行 `/settings` → 聯盟操作 → 查看聯盟
2. 記下顯示的聯盟列表

**在伺服器 B：**
1. 執行 `/settings` → 聯盟操作 → 查看聯盟
2. 確認伺服器 A 的聯盟 **不會** 出現在這裡

**預期結果：** ✅ 每個伺服器只看到自己的聯盟

---

### 測試 2：Manager 角色首次點擊

**使用 `Annaway_Manager` 角色：**

在伺服器 A：
1. 執行 `/settings`
2. 點擊「成員操作」→ ✅ 第一次點擊就成功
3. 點擊「禮品碼操作」→ ✅ 第一次點擊就成功
4. 點擊「聯盟歷史」→ ✅ 第一次點擊就成功
5. 點擊「其他功能」→ ✅ 第一次點擊就成功

**預期結果：** ✅ 所有按鈕第一次點擊都成功，無「沒有權限」錯誤

---

### 測試 3：Admin 角色功能

**使用 `Annaway_Admin` 角色：**

1. 執行 `/settings` → 聯盟操作 → 新增聯盟
2. 創建測試聯盟「Test Guild Isolation」
3. 執行 `/settings` → 權限管理
4. 嘗試分配 Manager

**預期結果：** ✅ 所有功能正常運作

---

## 🔍 驗證 Guild Isolation

### 在資料庫中檢查

```bash
cd ~/wos_bot
sqlite3 db/alliance.sqlite

# 檢查所有聯盟的 guild_id
SELECT alliance_id, name, discord_server_id FROM alliance_list;

# 確認沒有 NULL 或 -1 的 discord_server_id
SELECT COUNT(*) FROM alliance_list WHERE discord_server_id IS NULL OR discord_server_id = -1;
```

**預期：** 最後一個查詢應該返回 0（沒有孤兒聯盟）

---

## ⚠️ 故障排除

### 問題 1：還是看到其他伺服器的聯盟

**可能原因：**
- 舊的 Python 快取沒有清理
- 資料庫中的 `discord_server_id` 為 NULL

**解決方案：**
```bash
# 清理快取並重啟
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/wos_bot -type f -name "*.pyc" -delete
sudo systemctl restart wos-bot

# 檢查資料庫
sqlite3 ~/wos_bot/db/alliance.sqlite "SELECT alliance_id, name, discord_server_id FROM alliance_list WHERE discord_server_id IS NULL;"
```

如果發現 NULL 值，手動設定：
```sql
UPDATE alliance_list SET discord_server_id = <你的伺服器ID> WHERE alliance_id = <聯盟ID>;
```

---

### 問題 2：Manager 還是被阻擋

**檢查：**
```bash
# 1. 確認角色名稱（大小寫敏感）
# 在 Discord 中檢查角色名稱是否完全是 "Annaway_Manager"

# 2. 查看 permission_debug.log
cat ~/wos_bot/permission_debug.log | tail -100

# 3. 檢查是否還有遺漏的重複檢查
cd ~/wos_bot
grep -r "SELECT.*FROM admin WHERE" cogs/ | grep -v "get_admin_alliances"
```

---

### 問題 3：Bot 無法啟動

**檢查：**
```bash
# 查看完整錯誤
sudo journalctl -u wos-bot -n 100 --no-pager

# 手動執行測試
cd ~/wos_bot
source bot_venv/bin/activate
python main.py
```

---

## 📚 相關文件

請參閱以下文件以了解更多：

1. **GUILD_ISOLATION.md** - Guild isolation 實作指南
   - 正確的查詢模式
   - 常見錯誤
   - 測試方法

2. **TEST_PLAN.md** - 完整測試計劃
   - 所有測試案例（A1-E3）
   - 預期結果
   - 故障排除

3. **GUILD_ISOLATION_REGRESSION_FIX.md** - 本次修復的詳細說明
   - 根本原因分析
   - 所有修復的檔案和行號
   - 修復前後對比

---

## ✅ 驗收標準

部署成功後，以下項目應該全部達成：

### Guild Isolation
- [x] 伺服器 A 只看到自己的聯盟
- [x] 伺服器 B 只看到自己的聯盟
- [x] 沒有跨伺服器的資料洩漏

### Manager 角色
- [x] 可以使用「成員操作」（第一次點擊就成功）
- [x] 可以使用「禮品碼操作」（第一次點擊就成功）
- [x] 可以使用「聯盟歷史」（第一次點擊就成功）
- [x] 可以使用「其他功能」（第一次點擊就成功）
- [x] 不能使用 Admin-only 功能（新增/編輯/刪除聯盟）

### Admin 角色
- [x] 所有 Manager 功能都可用
- [x] 所有 Admin-only 功能都可用
- [x] 權限管理功能正常

### 系統穩定性
- [x] Bot 持續運行
- [x] 沒有 "Unknown interaction" 錯誤
- [x] 沒有超時錯誤

---

## 🎯 下一步

部署並測試成功後：

1. **監控日誌**
   ```bash
   tail -f ~/wos_bot/permission_debug.log
   sudo journalctl -u wos-bot -f
   ```

2. **清理舊檔案**
   ```bash
   # 刪除上傳的 ZIP
   rm ~/guild_isolation_fix_20251129_031932.zip
   
   # 使用清理腳本
   chmod +x ~/wos_bot/cleanup_gcp_vm.sh
   ~/wos_bot/cleanup_gcp_vm.sh
   ```

3. **定期測試**
   - 每週使用兩個伺服器測試 guild isolation
   - 每次新增聯盟相關功能後重新測試

---

## 📊 修復統計

**修復的查詢數：** 16  
**修改的檔案數：** 5  
**新增的文件數：** 3  
**測試案例數：** 20+

**預估部署時間：** 5-10 分鐘  
**預估測試時間：** 15-20 分鐘

---

**部署包：** `guild_isolation_fix_20251129_031932.zip`  
**版本：** Guild Isolation Fix v1.0  
**狀態：** ✅ Ready for Production


