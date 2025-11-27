# WOS Discord Bot - 打包腳本（Windows PowerShell）
# 用於準備上傳到 GCP 的壓縮檔

Write-Host "=========================================="  -ForegroundColor Blue
Write-Host "  WOS Discord Bot - 部署打包工具"  -ForegroundColor Blue
Write-Host "=========================================="  -ForegroundColor Blue
Write-Host ""

# 檢查是否在正確的目錄
if (-not (Test-Path "main.py")) {
    Write-Host "錯誤: 找不到 main.py" -ForegroundColor Red
    Write-Host "請在專案根目錄執行此腳本" -ForegroundColor Red
    exit 1
}

# 輸出檔名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "wos_bot_deploy_$timestamp.zip"

Write-Host "準備打包專案..." -ForegroundColor Yellow
Write-Host ""

# 要包含的項目
$includeItems = @(
    "main.py",
    "requirements.txt",
    "bot_config.env",
    "bot_config.env.example",
    "i18n_manager.py",
    "i18n_config.py",
    "permission_manager.py",
    "start_bot.bat",
    "deploy_check.sh",
    "quick_deploy.sh",
    "setup_systemd.sh",
    "wos-bot.service.example",
    "GCP_DEPLOYMENT_GUIDE.md",
    ".gcloudignore",
    "README.md",
    "PERMISSION_SYSTEM.md",
    "FEATURE_STATUS.md",
    "cogs",
    "i18n",
    "models",
    "fonts",
    "db"
)

# 檢查必要檔案
Write-Host "檢查檔案..." -ForegroundColor Yellow
$missingFiles = @()
foreach ($item in $includeItems) {
    if (Test-Path $item) {
        Write-Host "  ✓ $item" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $item (不存在)" -ForegroundColor Red
        $missingFiles += $item
    }
}
Write-Host ""

# 如果有缺少的重要檔案，詢問是否繼續
if ($missingFiles.Count -gt 0) {
    $important = @("main.py", "requirements.txt", "cogs", "i18n", "models")
    $missingImportant = $missingFiles | Where-Object { $important -contains $_ }
    
    if ($missingImportant.Count -gt 0) {
        Write-Host "缺少重要檔案: $($missingImportant -join ', ')" -ForegroundColor Red
        Write-Host "無法繼續打包" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "缺少部分非必要檔案，繼續打包..." -ForegroundColor Yellow
        Write-Host ""
    }
}

# 檢查 bot_config.env
if (Test-Path "bot_config.env") {
    $content = Get-Content "bot_config.env" -Raw
    if ($content -match "your_discord_token_here" -or $content -notmatch "DISCORD_TOKEN=\w+") {
        Write-Host "警告: bot_config.env 看起來還沒設定 DISCORD_TOKEN" -ForegroundColor Yellow
        Write-Host "請確保在 VM 上設定正確的 Token" -ForegroundColor Yellow
        Write-Host ""
    }
}

# 建立臨時目錄
$tempDir = "temp_deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# 複製檔案
Write-Host "複製檔案到臨時目錄..." -ForegroundColor Yellow
foreach ($item in $includeItems) {
    if (Test-Path $item) {
        if (Test-Path $item -PathType Container) {
            # 是目錄
            Copy-Item $item -Destination $tempDir -Recurse -Force
            
            # 清理目錄中的不需要的檔案
            if ($item -eq "db") {
                # 可選：是否包含資料庫
                $includeDb = Read-Host "是否包含資料庫檔案？(y/n，建議 n，在 VM 上重新建立)"
                if ($includeDb -ne "y") {
                    Remove-Item "$tempDir\db\*" -Force -ErrorAction SilentlyContinue
                    Write-Host "  已排除資料庫檔案" -ForegroundColor Yellow
                }
            }
        } else {
            # 是檔案
            Copy-Item $item -Destination $tempDir -Force
        }
    }
}

# 清理 Python cache
if (Test-Path "$tempDir\cogs\__pycache__") {
    Remove-Item "$tempDir\cogs\__pycache__" -Recurse -Force
}
if (Test-Path "$tempDir\i18n\__pycache__") {
    Remove-Item "$tempDir\i18n\__pycache__" -Recurse -Force
}
if (Test-Path "$tempDir\__pycache__") {
    Remove-Item "$tempDir\__pycache__" -Recurse -Force
}

Write-Host "  ✓ 檔案複製完成" -ForegroundColor Green
Write-Host ""

# 壓縮
Write-Host "壓縮檔案..." -ForegroundColor Yellow
if (Test-Path $outputFile) {
    Remove-Item $outputFile -Force
}
Compress-Archive -Path "$tempDir\*" -DestinationPath $outputFile -CompressionLevel Optimal
Write-Host "  ✓ 壓縮完成" -ForegroundColor Green
Write-Host ""

# 清理臨時目錄
Remove-Item $tempDir -Recurse -Force

# 顯示結果
$fileSize = (Get-Item $outputFile).Length / 1MB
Write-Host "=========================================="  -ForegroundColor Green
Write-Host "  打包完成！"  -ForegroundColor Green
Write-Host "=========================================="  -ForegroundColor Green
Write-Host ""
Write-Host "輸出檔案: $outputFile" -ForegroundColor Cyan
Write-Host "檔案大小: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步驟:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 上傳到 GCP VM:" -ForegroundColor White
Write-Host "   gcloud compute scp $outputFile wos-discord-bot:~/ --zone=asia-east1-b" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 在 VM 上解壓縮:" -ForegroundColor White
Write-Host "   unzip $outputFile -d ~/wos_bot" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 執行快速部署:" -ForegroundColor White
Write-Host "   cd ~/wos_bot" -ForegroundColor Gray
Write-Host "   chmod +x quick_deploy.sh" -ForegroundColor Gray
Write-Host "   ./quick_deploy.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "詳細步驟請參考: GCP_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""







