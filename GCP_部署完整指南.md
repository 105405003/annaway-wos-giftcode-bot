# 🚀 GCP 部署完整指南（一步一步教學）

**更新日期：** 2026-01-25  
**適用對象：** 第一次部署或需要完整步驟的使用者

---

## 📋 目錄

1. [準備工作](#準備工作)
2. [步驟 1：Discord Developer Portal 設定](#步驟-1discord-developer-portal-設定)
3. [步驟 2：Discord 伺服器設定](#步驟-2discord-伺服器設定)
4. [步驟 3：本地準備檔案](#步驟-3本地準備檔案)
5. [步驟 4：創建 GCP VM（首次部署）](#步驟-4創建-gcp-vm首次部署)
6. [步驟 5：上傳檔案到 GCP](#步驟-5上傳檔案到-gcp)
7. [步驟 6：在 GCP 上設定環境](#步驟-6在-gcp-上設定環境)
8. [步驟 7：啟動機器人](#步驟-7啟動機器人)
9. [步驟 8：驗證和測試](#步驟-8驗證和測試)
10. [常見問題排除](#常見問題排除)

---

## 準備工作

### 需要的資訊和帳號

在開始之前，請確保您有：

- [ ] Discord 開發者帳號
- [ ] Google Cloud Platform (GCP) 帳號
- [ ] 一個 Discord 測試伺服器
- [ ] 本機已安裝 Git（用於下載或更新程式碼）

### 預計所需時間

- **首次完整部署：** 約 1-2 小時
- **更新部署：** 約 10-15 分鐘

---

## 步驟 1：Discord Developer Portal 設定

### 1.1 創建 Discord 應用程式

1. **前往 Discord Developer Portal**
   - 網址：https://discord.com/developers/applications
   - 使用您的 Discord 帳號登入

2. **創建新應用程式**
   - 點擊右上角的「**New Application**」按鈕
   - 輸入應用程式名稱，例如：`WOS 禮品碼機器人`
   - 點擊「**Create**」

3. **記錄 Application ID**
   - 在「**General Information**」頁面
   - 找到「**Application ID**」
   - 複製並保存（稍後會用到）

### 1.2 創建機器人

1. **進入 Bot 頁面**
   - 左側選單點擊「**Bot**」
   - 點擊「**Add Bot**」
   - 確認「**Yes, do it!**」

2. **設定機器人**
   - **機器人名稱：** 可以設定您想要的名稱
   - **圖示：** 可以上傳機器人的頭像（可選）

3. **取得 Bot Token（重要！）**
   - 在「**TOKEN**」區塊，點擊「**Reset Token**」
   - 點擊「**Copy**」複製 Token
   - **⚠️ 重要：** 立即保存到安全的地方，這個 Token 只會顯示一次！
   - **不要分享給任何人！**

### 1.3 啟用 Privileged Gateway Intents

這是必要步驟，否則機器人無法讀取成員角色！

1. **在 Bot 頁面向下滾動**
   - 找到「**Privileged Gateway Intents**」區塊

2. **啟用以下兩項（必須！）**
   - ✅ **Server Members Intent** ← 勾選這個
   - ✅ **Message Content Intent** ← 勾選這個

3. **儲存變更**
   - 點擊底部的「**Save Changes**」

### 1.4 生成邀請連結

1. **進入 OAuth2 頁面**
   - 左側選單點擊「**OAuth2**」
   - 選擇「**URL Generator**」

2. **選擇 Scopes**
   - ✅ **bot** ← 勾選這個
   - ✅ **applications.commands** ← 勾選這個

3. **選擇 Bot Permissions**
   
   勾選以下權限（只需要這些，不要勾選管理員）：
   
   **General Permissions:**
   - ✅ View Channels（查看頻道）
   
   **Text Permissions:**
   - ✅ Send Messages（發送訊息）
   - ✅ Send Messages in Threads（在討論串發送訊息）
   - ✅ Embed Links（嵌入連結）
   - ✅ Attach Files（附加檔案）
   - ✅ Read Message History（讀取訊息歷史）
   - ✅ Add Reactions（加入反應）
   - ✅ Use Slash Commands（使用斜線命令）

   **⚠️ 不要勾選：**
   - ❌ Administrator（管理員）
   - ❌ Manage Server（管理伺服器）
   - ❌ Manage Channels（管理頻道）
   - ❌ Manage Roles（管理角色）

4. **複製生成的 URL**
   - 在頁面底部會看到生成的 URL
   - 複製這個 URL（稍後用來邀請機器人）

### 1.5 邀請機器人到測試伺服器

1. **開啟瀏覽器新分頁**
   - 貼上剛才複製的邀請 URL
   - 按 Enter

2. **選擇伺服器**
   - 從下拉選單選擇您的測試伺服器
   - 點擊「**Continue**」

3. **確認權限**
   - 檢查權限列表（應該只有基本權限）
   - 點擊「**Authorize**」

4. **完成驗證**
   - 完成 reCAPTCHA 驗證
   - 機器人應該會出現在您的伺服器中

---

## 步驟 2：Discord 伺服器設定

### 2.1 創建機器人需要的角色

1. **進入伺服器設定**
   - 在您的 Discord 伺服器，點擊伺服器名稱
   - 選擇「**伺服器設定**」

2. **進入角色設定**
   - 左側選單選擇「**角色**」

3. **創建 Annaway_Admin 角色**
   - 點擊「**創建角色**」
   - **角色名稱：** 輸入 `Annaway_Admin`（必須完全一致，區分大小寫）
   - **角色顏色：** 可以選擇一個顏色（例如紅色）
   - **權限：** 不需要勾選任何特殊權限（保持預設）
   - 點擊「**儲存變更**」

4. **創建 Annaway_Manager 角色**
   - 再次點擊「**創建角色**」
   - **角色名稱：** 輸入 `Annaway_Manager`（必須完全一致，區分大小寫）
   - **角色顏色：** 可以選擇一個顏色（例如藍色）
   - **權限：** 不需要勾選任何特殊權限（保持預設）
   - 點擊「**儲存變更**」

### 2.2 分配角色給自己

1. **回到伺服器主畫面**
   - 按 ESC 或點擊左上角的 X 關閉設定

2. **在成員列表找到自己**
   - 右鍵點擊自己的名字
   - 選擇「**角色**」
   - 勾選 `Annaway_Admin`

3. **驗證角色**
   - 您的名字旁邊應該會顯示角色顏色

---

## 步驟 3：本地準備檔案

### 3.1 準備程式碼

1. **開啟 PowerShell**
   - 按 `Win + X`
   - 選擇「**Windows PowerShell**」或「**終端機**」

2. **進入專案目錄**
   ```powershell
   cd F:\AnnawayProjects\wos_giftcode_redemption_bot
   ```

3. **確認最新的程式碼**
   ```powershell
   # 查看當前狀態
   git status
   
   # 如果有未提交的變更，先提交
   git add .
   git commit -m "修復權限檢查問題"
   ```

### 3.2 創建部署壓縮檔

1. **執行打包指令**
   ```powershell
   # 設定時間戳記
   $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
   
   # 要包含的檔案和資料夾
   $files = @(
       "main.py",
       "cogs\*",
       "utils\*",
       "i18n\*",
       "migrations\*",
       "models\*",
       "fonts\*",
       "permission_manager.py",
       "i18n_manager.py",
       "i18n_config.py",
       "requirements.txt",
       "README.md",
       "README_ANNAWAY.md",
       "BOT_PERMISSIONS_GUIDE.md",
       "QUICK_START.md",
       "bot_config.env.example",
       "setup_systemd.sh",
       "wos-bot.service.example",
       "cleanup_gcp_vm.sh",
       ".gitignore"
   )
   
   # 創建壓縮檔
   $zipName = "wos_bot_deploy_$timestamp.zip"
   
   # 先刪除舊的臨時資料夾（如果存在）
   if (Test-Path "temp_deploy") {
       Remove-Item -Path "temp_deploy" -Recurse -Force
   }
   
   # 創建臨時資料夾
   New-Item -ItemType Directory -Path "temp_deploy" | Out-Null
   
   # 複製檔案到臨時資料夾
   foreach ($file in $files) {
       if (Test-Path $file) {
           $destination = "temp_deploy\$(Split-Path $file -Leaf)"
           Copy-Item -Path $file -Destination "temp_deploy" -Recurse -Force
       }
   }
   
   # 創建壓縮檔
   Compress-Archive -Path "temp_deploy\*" -DestinationPath $zipName -Force
   
   # 清理臨時資料夾
   Remove-Item -Path "temp_deploy" -Recurse -Force
   
   # 顯示結果
   Write-Host "`n✅ 打包完成！" -ForegroundColor Green
   Write-Host "檔案名稱: $zipName" -ForegroundColor Cyan
   Write-Host "檔案大小: $((Get-Item $zipName).Length / 1KB) KB" -ForegroundColor Cyan
   Write-Host "檔案位置: $(Get-Location)\$zipName`n" -ForegroundColor Cyan
   ```

2. **確認壓縮檔已創建**
   ```powershell
   # 列出壓縮檔
   Get-ChildItem -Filter "wos_bot_deploy_*.zip" | Select-Object Name, Length, LastWriteTime
   ```

### 3.3 準備設定檔內容

1. **記錄您的 Discord Bot Token**
   - 從步驟 1.2 複製的 Token
   - 格式為三區段以 `.` 分隔的隨機字串；請僅在 Discord Developer Portal 複製，**切勿**將真實 Token 寫進版本庫或文件範例

2. **（可選）準備 2Captcha API Key**
   - 如果您有 2Captcha 帳號並想使用自動驗證碼功能
   - 前往：https://2captcha.com/
   - 在帳號設定中取得 API Key

---

## 步驟 4：創建 GCP VM（首次部署）

**⚠️ 注意：** 如果您已經有 VM 且只是更新程式碼，請跳到[步驟 5](#步驟-5上傳檔案到-gcp)

### 4.1 登入 Google Cloud Console

1. **開啟瀏覽器**
   - 前往：https://console.cloud.google.com/

2. **選擇或創建專案**
   - 在頂部選擇現有專案，或創建新專案
   - 專案名稱例如：`wos-bot-project`

### 4.2 創建 VM 實例

1. **進入 Compute Engine**
   - 左側選單：「**Compute Engine**」→「**VM 執行個體**」
   - 如果是首次使用，需要啟用 API（點擊「啟用」）

2. **創建執行個體**
   - 點擊「**建立執行個體**」

3. **基本設定**
   - **名稱：** `wos-giftcode-bot`
   - **區域：** 選擇離您最近的區域（例如：`asia-east1` 台灣）
   - **機器類型：** `e2-micro` 或 `e2-small`（免費方案或低成本）

4. **開機磁碟**
   - 點擊「**變更**」
   - **作業系統：** Ubuntu
   - **版本：** Ubuntu 22.04 LTS
   - **磁碟大小：** 10 GB（足夠使用）
   - 點擊「**選取**」

5. **防火牆**
   - ✅ 勾選「**允許 HTTP 流量**」（可選）
   - ✅ 勾選「**允許 HTTPS 流量**」（可選）

6. **其他設定保持預設**
   - 點擊底部的「**建立**」

7. **等待 VM 啟動**
   - 需要 1-2 分鐘
   - 狀態顯示綠色勾勾表示啟動完成

### 4.3 設定 SSH 金鑰（建議）

1. **在 VM 執行個體頁面**
   - 找到您剛建立的 VM
   - 點擊 VM 名稱

2. **編輯 VM**
   - 點擊頂部的「**編輯**」

3. **SSH 金鑰**
   - 滾動到「**SSH 金鑰**」區塊
   - 這裡可以新增您的 SSH 公鑰（可選，使用 gcloud CLI 會更方便）

4. **儲存**
   - 點擊底部的「**儲存**」

---

## 步驟 5：上傳檔案到 GCP

### 方法 A：使用 Google Cloud Console（推薦，最簡單）

1. **在 VM 執行個體頁面**
   - 找到您的 VM：`wos-giftcode-bot`
   - 點擊「**SSH**」按鈕旁的下拉箭頭
   - 選擇「**在瀏覽器視窗中開啟**」

2. **等待 SSH 連線建立**
   - 會開啟一個新的瀏覽器視窗
   - 顯示終端機介面

3. **上傳壓縮檔**
   - 在 SSH 視窗，點擊右上角的「**齒輪圖示**」⚙️
   - 選擇「**Upload file**」
   - 選擇您剛才打包的 `wos_bot_deploy_*.zip`
   - 等待上傳完成（會顯示在視窗中）

4. **確認檔案已上傳**
   ```bash
   ls -lh ~/wos_bot_deploy_*.zip
   ```

### 方法 B：使用 gcloud CLI（進階）

1. **在本地 PowerShell 執行**
   ```powershell
   # 設定您的專案 ID
   $projectId = "your-project-id"  # 替換成您的專案 ID
   
   # 上傳檔案
   gcloud compute scp wos_bot_deploy_*.zip wos-giftcode-bot:~ --zone=asia-east1-b --project=$projectId
   ```

---

## 步驟 6：在 GCP 上設定環境

### 6.1 連線到 VM

1. **如果還沒連線**
   - 在 GCP Console 的 VM 執行個體頁面
   - 點擊「**SSH**」按鈕
   - 選擇「**在瀏覽器視窗中開啟**」

### 6.2 首次設定（只需要執行一次）

1. **更新系統**
   ```bash
   # 更新套件清單
   sudo apt update
   
   # 升級已安裝的套件（可選）
   sudo apt upgrade -y
   ```

2. **安裝 Python 和相關工具**
   ```bash
   # 安裝 Python 3 和 pip
   sudo apt install -y python3 python3-pip python3-venv
   
   # 安裝 unzip
   sudo apt install -y unzip
   ```

3. **創建專案目錄**
   ```bash
   # 創建目錄
   mkdir -p ~/wos_bot
   
   # 進入目錄
   cd ~/wos_bot
   ```

4. **解壓縮上傳的檔案**
   ```bash
   # 解壓縮
   unzip -o ~/wos_bot_deploy_*.zip -d ~/wos_bot
   
   # 確認檔案
   ls -la ~/wos_bot
   ```
   
   應該看到：
   ```
   cogs/
   utils/
   i18n/
   main.py
   requirements.txt
   ...等檔案
   ```

5. **創建虛擬環境**
   ```bash
   # 創建虛擬環境
   python3 -m venv ~/wos_bot/bot_venv
   
   # 啟動虛擬環境
   source ~/wos_bot/bot_venv/bin/activate
   
   # 升級 pip
   pip install --upgrade pip
   ```

6. **安裝 Python 套件**
   ```bash
   # 確認在虛擬環境中
   which python
   # 應該顯示：/home/你的使用者名稱/wos_bot/bot_venv/bin/python
   
   # 安裝套件
   pip install -r ~/wos_bot/requirements.txt
   
   # 等待安裝完成（需要幾分鐘）
   ```

7. **創建資料庫目錄**
   ```bash
   # 創建 db 資料夾
   mkdir -p ~/wos_bot/db
   
   # 設定權限
   chmod 755 ~/wos_bot/db
   ```

### 6.3 設定機器人 Token

1. **創建設定檔**
   ```bash
   # 複製範例設定檔
   cp ~/wos_bot/bot_config.env.example ~/wos_bot/bot_config.env
   
   # 編輯設定檔
   nano ~/wos_bot/bot_config.env
   ```

2. **編輯內容**
   
   將檔案內容修改為：
   ```env
   # Discord Bot Token（必填）
   BOT_TOKEN=你的機器人Token在這裡
   
   # 2Captcha API Key（可選，用於自動驗證碼）
   TWOCAPTCHA_API_KEY=你的2Captcha_Key在這裡
   
   # 語言設定
   LANGUAGE=zh_TW
   ```

3. **儲存檔案**
   - 按 `Ctrl + O` 儲存
   - 按 `Enter` 確認檔名
   - 按 `Ctrl + X` 離開

4. **驗證設定檔**
   ```bash
   # 確認檔案內容（不會顯示敏感資訊）
   cat ~/wos_bot/bot_config.env | grep -E "^(BOT_TOKEN|LANGUAGE)=" | sed 's/=.*/=***/'
   ```

### 6.4 設定 systemd 服務

1. **使用設定腳本**
   ```bash
   # 給腳本執行權限
   chmod +x ~/wos_bot/setup_systemd.sh
   
   # 執行設定腳本
   cd ~/wos_bot
   ./setup_systemd.sh
   ```

2. **如果腳本不存在，手動設定**
   ```bash
   # 創建 service 檔案
   sudo nano /etc/systemd/system/wos-bot.service
   ```
   
   內容：
   ```ini
   [Unit]
   Description=WOS Gift Code Bot
   After=network.target
   
   [Service]
   Type=simple
   User=你的使用者名稱
   WorkingDirectory=/home/你的使用者名稱/wos_bot
   Environment="PATH=/home/你的使用者名稱/wos_bot/bot_venv/bin"
   ExecStart=/home/你的使用者名稱/wos_bot/bot_venv/bin/python main.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   **⚠️ 記得替換：** `你的使用者名稱` 為您實際的使用者名稱（執行 `whoami` 查看）

3. **儲存並啟用服務**
   ```bash
   # 重新載入 systemd
   sudo systemctl daemon-reload
   
   # 啟用服務（開機自動啟動）
   sudo systemctl enable wos-bot
   ```

---

## 步驟 7：啟動機器人

### 7.1 啟動服務

```bash
# 啟動機器人
sudo systemctl start wos-bot

# 查看狀態
sudo systemctl status wos-bot
```

**期望結果：**
```
● wos-bot.service - WOS Gift Code Bot
     Loaded: loaded (/etc/systemd/system/wos-bot.service; enabled)
     Active: active (running) since ...
```

如果看到 `Active: active (running)` 和綠色的點，表示啟動成功！

### 7.2 查看啟動日誌

```bash
# 查看即時日誌
sudo journalctl -u wos-bot -f
```

**應該看到：**
```
✅ 自動更新功能已停用，專案不會被意外覆蓋
Logged in as 你的機器人名稱#1234
Commands synced: XX
Synced commands:
  - /settings: "設定選單"
  - /add: "新增成員"
  ...
```

如果看到 `Logged in as`，表示機器人已成功連線到 Discord！

### 7.3 檢查 Discord

1. **開啟您的 Discord 伺服器**
2. **查看成員列表**
3. **機器人應該顯示為線上**（綠色圓點）

---

## 步驟 8：驗證和測試

### 8.1 測試斜線命令

1. **在 Discord 頻道輸入**
   ```
   /settings
   ```

2. **期望結果**
   - 機器人回應一個選單
   - 有多個按鈕：成員操作、禮品碼操作、聯盟歷史、其他功能

3. **如果沒有回應**
   - 等待 1-2 分鐘（Discord 需要同步命令）
   - 檢查機器人是否在線
   - 檢查日誌：`sudo journalctl -u wos-bot -n 50`

### 8.2 測試權限系統

1. **以 Admin 身份測試**
   - 執行 `/settings`
   - 點擊所有按鈕，應該都能使用

2. **建立聯盟**
   - `/settings` → 點擊「成員操作」或直接在選單中選擇
   - 第一次使用需要先創建聯盟
   - 聯盟管理功能應該只有 `Annaway_Admin` 可以使用

3. **測試 `/add` 指令**
   ```
   /add
   ```
   - 這個指令所有人都可以使用

### 8.3 檢查權限日誌

```bash
# 查看權限檢查日誌
tail -50 ~/wos_bot/permission_debug.log
```

**應該看到類似：**
```
========================================
custom_id: member_operations
admin_only: False
user.id: 123456789
user.name: YourName
guild.id: 987654321
User roles (names): ['@everyone', 'Annaway_Admin']
has_admin_role: True
has_manager_role: False
is_global_admin (DB is_initial): False
allowed: True
✅ ALLOWED
========================================
```

---

## 常見問題排除

### 問題 1：機器人無法啟動

**檢查日誌：**
```bash
sudo journalctl -u wos-bot -n 100 --no-pager
```

**常見原因：**

1. **Token 錯誤**
   ```bash
   # 檢查 token 是否正確設定
   grep "BOT_TOKEN" ~/wos_bot/bot_config.env
   
   # 重新編輯
   nano ~/wos_bot/bot_config.env
   ```

2. **缺少 Python 套件**
   ```bash
   source ~/wos_bot/bot_venv/bin/activate
   pip install -r ~/wos_bot/requirements.txt
   ```

3. **權限問題**
   ```bash
   # 確保所有檔案權限正確
   sudo chown -R $USER:$USER ~/wos_bot
   chmod +x ~/wos_bot/main.py
   ```

### 問題 2：收到「機器人需要管理伺服器權限」錯誤

**這是已知問題，已在最新版修復。**

**解決方案：**
1. 確認您部署的是修復後的版本
2. 檢查 `cogs/alliance.py` 是否包含修復：
   ```bash
   grep -A 5 "_show_settings_menu" ~/wos_bot/cogs/alliance.py | head -10
   ```
   應該看到註解：「機器人不需要 manage_guild 權限」

3. 重新啟動機器人：
   ```bash
   sudo systemctl restart wos-bot
   ```

### 問題 3：斜線命令不顯示

**原因：** Discord 需要時間同步命令

**解決方案：**
1. 等待 5-10 分鐘
2. 嘗試在不同的頻道
3. 重新啟動 Discord 應用程式
4. 檢查機器人是否有「使用應用程式命令」權限

### 問題 4：權限檢查失敗

**檢查角色名稱：**
```bash
# 在 Discord 中確認：
# 1. 角色名稱完全是 Annaway_Admin 或 Annaway_Manager
# 2. 大小寫完全一致
# 3. 沒有多餘的空格
```

**查看日誌：**
```bash
tail -50 ~/wos_bot/permission_debug.log
```

### 問題 5：「Unknown interaction」錯誤

**原因：** Python 快取檔案未清理

**解決方案：**
```bash
# 停止機器人
sudo systemctl stop wos-bot

# 清理快取
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/wos_bot -type f -name "*.pyc" -delete

# 重新啟動
sudo systemctl start wos-bot
```

### 問題 6：VM 連線不穩定

**解決方案：**
```bash
# 使用 tmux 或 screen 保持連線
sudo apt install -y tmux

# 創建新的 tmux session
tmux new -s bot

# 查看日誌
sudo journalctl -u wos-bot -f

# 離開 tmux（不會中斷）
# 按 Ctrl+B 然後按 D

# 重新連接
tmux attach -t bot
```

---

## 🔄 更新部署流程

當您需要更新程式碼時：

### 1. 本地打包新版本

```powershell
# 在本地執行
cd F:\AnnawayProjects\wos_giftcode_redemption_bot
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
# ... 打包指令（同步驟 3.2）
```

### 2. 上傳到 GCP

```bash
# 使用 Google Cloud Console 的 SSH 上傳功能
# 或使用 gcloud CLI
```

### 3. 在 VM 上執行更新

```bash
# 停止機器人
sudo systemctl stop wos-bot

# 備份資料庫（重要！）
cp -r ~/wos_bot/db/ ~/wos_bot_backup_$(date +%Y%m%d_%H%M%S)/

# 解壓縮新檔案
cd ~/wos_bot
unzip -o ~/wos_bot_deploy_*.zip

# 清理快取
find ~/wos_bot -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/wos_bot -type f -name "*.pyc" -delete

# 啟動機器人
sudo systemctl start wos-bot

# 查看狀態
sudo systemctl status wos-bot
```

### 4. 清理舊檔案

```bash
# 清理上傳的 ZIP
find ~ -maxdepth 1 -type f -name "wos_bot_deploy_*.zip" -mtime +7 -delete

# 保留最新 3 個備份，刪除舊的
ls -t ~/wos_bot_backup_* | tail -n +4 | xargs rm -rf
```

---

## 🛠️ 實用指令

### 服務管理

```bash
# 啟動
sudo systemctl start wos-bot

# 停止
sudo systemctl stop wos-bot

# 重新啟動
sudo systemctl restart wos-bot

# 查看狀態
sudo systemctl status wos-bot

# 查看日誌
sudo journalctl -u wos-bot -f

# 查看最近 100 行日誌
sudo journalctl -u wos-bot -n 100 --no-pager
```

### 檔案管理

```bash
# 查看專案結構
tree ~/wos_bot -L 2

# 查看磁碟使用
du -sh ~/wos_bot

# 查看資料庫大小
du -sh ~/wos_bot/db/*

# 列出備份
ls -lh ~/wos_bot_backup_*
```

### 系統資源

```bash
# 查看記憶體使用
free -h

# 查看磁碟空間
df -h

# 查看 CPU 使用
top

# 查看機器人進程
ps aux | grep python | grep main.py
```

---

## 📚 相關文件

- **`BOT_PERMISSIONS_GUIDE.md`** - Discord 權限詳細說明
- **`README_DEPLOY_TW.md`** - 繁體中文部署說明
- **`DEPLOYMENT.md`** - 英文部署指南
- **`QUICK_START.md`** - 快速開始指南
- **`README_ANNAWAY.md`** - 完整專案說明

---

## ✅ 檢查清單

完成部署後，確認以下項目：

### Discord Developer Portal
- [ ] Bot Token 已複製並保存
- [ ] Server Members Intent 已啟用
- [ ] Message Content Intent 已啟用
- [ ] 機器人已邀請到伺服器
- [ ] 機器人有正確的權限

### Discord 伺服器
- [ ] 已創建 `Annaway_Admin` 角色
- [ ] 已創建 `Annaway_Manager` 角色
- [ ] 至少一位使用者有 Admin 角色
- [ ] 機器人顯示為線上

### GCP VM
- [ ] VM 已創建並運行
- [ ] Python 和套件已安裝
- [ ] 專案檔案已上傳
- [ ] bot_config.env 已設定
- [ ] systemd 服務已設定

### 功能測試
- [ ] `/settings` 指令可以使用
- [ ] 所有按鈕可以點擊
- [ ] 權限系統正常運作
- [ ] 沒有錯誤訊息

---

## 🎉 完成！

恭喜您成功部署機器人到 GCP！

**下一步：**
1. 創建您的第一個聯盟
2. 新增成員
3. 測試禮品碼兌換功能
4. 定期備份資料庫

**需要協助？**
- 查看日誌：`sudo journalctl -u wos-bot -f`
- 檢查權限：`tail -f ~/wos_bot/permission_debug.log`
- 閱讀相關文件

祝您使用愉快！🚀
