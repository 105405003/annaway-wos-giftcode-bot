# 🚀 開始部署 WOS 禮品碼機器人

歡迎！這裡是部署指南的入口。

---

## 📖 我應該閱讀哪個文件？

### 🆕 第一次部署？從頭開始？

**➡️ 閱讀：[`GCP_部署完整指南.md`](GCP_部署完整指南.md)**

這份指南包含：
- ✅ Discord Developer Portal 詳細設定步驟（含截圖說明）
- ✅ Discord 伺服器角色設定教學
- ✅ GCP VM 創建完整流程
- ✅ 本地檔案準備
- ✅ 上傳和部署步驟
- ✅ 驗證和測試
- ✅ 常見問題詳細排除

**預計時間：** 1-2 小時

---

### ⚡ 已經部署過，只是更新？

**➡️ 閱讀：[`部署快速參考.md`](部署快速參考.md)**

快速更新流程：
```bash
# 1. 本地打包
# 2. 上傳到 GCP
# 3. 在 VM 上執行：
sudo systemctl stop wos-bot
cp -r ~/wos_bot/db/ ~/wos_bot_backup_$(date +%Y%m%d_%H%M%S)/
cd ~/wos_bot && unzip -o ~/wos_bot_deploy_*.zip
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
sudo systemctl start wos-bot
```

**預計時間：** 10-15 分鐘

---

### 🔐 需要了解權限系統？

**➡️ 閱讀：[`BOT_PERMISSIONS_GUIDE.md`](BOT_PERMISSIONS_GUIDE.md)**

這份指南解釋：
- ✅ 機器人需要什麼 Discord 權限
- ✅ 為什麼不需要管理員權限
- ✅ 如何設定 Annaway_Admin 和 Annaway_Manager 角色
- ✅ 權限系統如何運作
- ✅ 如何告訴伺服器管理員

---

### 🐛 遇到「機器人需要管理伺服器權限」錯誤？

**➡️ 這是已知問題，已經修復！**

請參考：[`BOT_PERMISSIONS_GUIDE.md`](BOT_PERMISSIONS_GUIDE.md) 的「常見問題排除」章節

**快速解決：**
1. 確認使用最新版程式碼（已修復 `cogs/alliance.py`）
2. 重新部署
3. 重啟機器人：`sudo systemctl restart wos-bot`

---

## 📚 所有部署相關文件

### 中文文件（推薦）

| 文件名稱 | 適用對象 | 內容 |
|---------|---------|------|
| **GCP_部署完整指南.md** | 🆕 新手 | 一步一步完整教學 |
| **部署快速參考.md** | ⚡ 進階 | 快速指令參考 |
| **BOT_PERMISSIONS_GUIDE.md** | 🔐 所有人 | Discord 權限詳解 |
| **README_DEPLOY_TW.md** | 📝 所有人 | 部署說明（繁中） |
| **部署指令.txt** | ⚡ 進階 | 快速複製貼上指令 |

### 英文文件

| 文件名稱 | 內容 |
|---------|------|
| **DEPLOYMENT.md** | 英文部署指南 |
| **QUICK_START.md** | 快速開始指南 |
| **README_ANNAWAY.md** | 完整專案說明 |

---

## 🎯 部署流程總覽

### 階段 1：Discord 設定（30 分鐘）

1. Discord Developer Portal 創建應用程式和機器人
2. 啟用 Privileged Gateway Intents
3. 複製 Bot Token
4. 生成邀請連結
5. 邀請機器人到伺服器
6. 創建 `Annaway_Admin` 和 `Annaway_Manager` 角色

### 階段 2：GCP 準備（20 分鐘）

1. 創建 GCP 專案
2. 創建 VM 實例（Ubuntu 22.04）
3. 設定 SSH 連線

### 階段 3：本地準備（10 分鐘）

1. 確認程式碼是最新版
2. 打包部署檔案
3. 準備 Bot Token

### 階段 4：上傳和部署（30 分鐘）

1. 上傳壓縮檔到 GCP
2. 安裝 Python 和相關套件
3. 設定虛擬環境
4. 設定 bot_config.env
5. 設定 systemd 服務

### 階段 5：啟動和驗證（10 分鐘）

1. 啟動機器人服務
2. 檢查日誌
3. 在 Discord 測試指令
4. 驗證權限系統

---

## ⚠️ 開始之前，請確認

### Discord 方面

- [ ] 您有 Discord 開發者帳號
- [ ] 您有一個測試用的 Discord 伺服器（或可以創建角色的權限）
- [ ] 您知道什麼是「Bot Token」

### GCP 方面

- [ ] 您有 Google Cloud Platform 帳號
- [ ] 您的 GCP 帳號有創建 VM 的權限
- [ ] 您知道如何使用 SSH 連線（或願意學習）

### 本地環境

- [ ] Windows、macOS 或 Linux 系統
- [ ] 已安裝 PowerShell（Windows）或 Terminal（Mac/Linux）
- [ ] 有程式碼的最新版本

---

## 🆘 需要幫助？

### 查看日誌

```bash
# 在 GCP VM 上
sudo journalctl -u wos-bot -f
```

### 檢查權限除錯

```bash
# 在 GCP VM 上
tail -50 ~/wos_bot/permission_debug.log
```

### 查看服務狀態

```bash
# 在 GCP VM 上
sudo systemctl status wos-bot
```

### 常見錯誤

| 錯誤訊息 | 解決方案 |
|---------|---------|
| Token 無效 | 檢查 `bot_config.env` 中的 BOT_TOKEN |
| 無法讀取成員 | 檢查 Server Members Intent 是否啟用 |
| 權限不足 | 檢查 Discord 角色名稱是否完全正確 |
| 機器人需要管理伺服器權限 | 部署最新版程式碼（已修復） |

---

## 💡 建議

### 第一次部署？

1. **預留充足時間：** 建議週末或非工作時間進行
2. **準備測試伺服器：** 不要直接在正式伺服器測試
3. **仔細閱讀每個步驟：** 不要跳過任何步驟
4. **保存所有重要資訊：** 特別是 Bot Token

### 已經熟悉流程？

1. **使用快速參考：** 查閱 `部署快速參考.md`
2. **備份資料庫：** 每次更新前務必備份
3. **查看變更日誌：** 了解新版本的改動
4. **測試再部署：** 在測試伺服器先測試

---

## 🎉 準備好了嗎？

### 🆕 新手？

**➡️ 前往：[`GCP_部署完整指南.md`](GCP_部署完整指南.md)**

跟著一步一步的教學，您一定可以成功部署！

### ⚡ 進階使用者？

**➡️ 前往：[`部署快速參考.md`](部署快速參考.md)**

快速複製指令，立即開始部署！

---

**祝您部署順利！** 🚀

如有任何問題，請參考相關文件的「常見問題排除」章節。
