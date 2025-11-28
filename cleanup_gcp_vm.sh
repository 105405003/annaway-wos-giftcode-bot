#!/bin/bash
# GCP VM Cleanup Script for WOS Giftcode Bot
# 清理臨時 ZIP 檔案和舊備份

echo "🧹 開始清理 GCP VM..."
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 計數器
ZIP_COUNT=0
BACKUP_COUNT=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 檢查臨時 ZIP 檔案..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 列出要刪除的 ZIP 檔案
ZIP_FILES=$(find ~ -maxdepth 2 -type f \( -name "wos_bot*.zip" -o -name "hotfix*.zip" -o -name "update_files*.zip" -o -name "final_fix*.zip" -o -name "A1_deployment*.zip" \) 2>/dev/null)

if [ -z "$ZIP_FILES" ]; then
    echo -e "${GREEN}✓${NC} 沒有找到臨時 ZIP 檔案"
else
    echo "找到以下 ZIP 檔案："
    echo "$ZIP_FILES" | while read file; do
        echo "  - $file"
        ((ZIP_COUNT++))
    done
    echo ""
    echo -e "${YELLOW}是否刪除這些檔案？ [y/N]${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "$ZIP_FILES" | xargs rm -f
        echo -e "${GREEN}✓${NC} 已刪除 ZIP 檔案"
    else
        echo -e "${YELLOW}⊘${NC} 跳過刪除 ZIP 檔案"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 檢查舊的資料庫備份..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 列出備份目錄
BACKUP_DIRS=$(find ~ -maxdepth 1 -type d -name "wos_bot_backup_*" 2>/dev/null | sort -r)

if [ -z "$BACKUP_DIRS" ]; then
    echo -e "${GREEN}✓${NC} 沒有找到舊備份"
else
    BACKUP_COUNT=$(echo "$BACKUP_DIRS" | wc -l)
    echo "找到 $BACKUP_COUNT 個備份目錄："
    echo "$BACKUP_DIRS" | nl
    echo ""
    
    # 保留最新的 3 個備份
    if [ $BACKUP_COUNT -gt 3 ]; then
        OLD_BACKUPS=$(echo "$BACKUP_DIRS" | tail -n +4)
        echo -e "${YELLOW}建議保留最新的 3 個備份，刪除其他 $((BACKUP_COUNT - 3)) 個舊備份${NC}"
        echo ""
        echo "要刪除的備份："
        echo "$OLD_BACKUPS" | nl
        echo ""
        echo -e "${YELLOW}是否刪除這些舊備份？ [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "$OLD_BACKUPS" | xargs rm -rf
            echo -e "${GREEN}✓${NC} 已刪除舊備份"
        else
            echo -e "${YELLOW}⊘${NC} 跳過刪除備份"
        fi
    else
        echo -e "${GREEN}✓${NC} 備份數量合理，無需清理"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 磁碟空間統計"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 顯示磁碟使用情況
df -h ~ | tail -1 | awk '{printf "使用空間: %s / %s (%s 已使用)\n", $3, $2, $5}'

# Bot 目錄大小
BOT_SIZE=$(du -sh ~/wos_bot 2>/dev/null | cut -f1)
echo "Bot 目錄大小: $BOT_SIZE"

# 備份目錄總大小
BACKUP_SIZE=$(du -sh ~/wos_bot_backup_* 2>/dev/null | awk '{sum+=$1} END {print sum"M"}')
if [ ! -z "$BACKUP_SIZE" ]; then
    echo "備份目錄總大小: $BACKUP_SIZE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ 清理完成！${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 提示："
echo "  - 建議定期清理舊檔案以節省空間"
echo "  - 保留最近 3 個備份就足夠了"
echo "  - 部署前記得先備份資料庫！"
echo ""

