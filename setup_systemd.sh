#!/bin/bash
# WOS Discord Bot - Systemd 自動設定腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=========================================="
echo "  設定 Systemd 自動啟動"
echo "=========================================="
echo -e "${NC}"
echo ""

# 取得當前用戶和路徑
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)
SERVICE_FILE="${CURRENT_DIR}/wos-bot.service"

echo -e "${YELLOW}當前用戶: ${NC}${CURRENT_USER}"
echo -e "${YELLOW}專案路徑: ${NC}${CURRENT_DIR}"
echo ""

# 檢查是否在正確的目錄
if [ ! -f "main.py" ]; then
    echo -e "${RED}錯誤: 找不到 main.py${NC}"
    echo "請在專案根目錄執行此腳本"
    exit 1
fi

# 檢查虛擬環境
if [ ! -d "bot_venv" ]; then
    echo -e "${RED}錯誤: 找不到 bot_venv${NC}"
    echo "請先執行 quick_deploy.sh"
    exit 1
fi

# 建立 log 目錄
mkdir -p log

# 創建 service 檔案
echo -e "${YELLOW}建立 systemd service 檔案...${NC}"
cat > wos-bot.service << EOF
[Unit]
Description=WOS Gift Code Redemption Bot
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${CURRENT_DIR}
Environment="PATH=${CURRENT_DIR}/bot_venv/bin"
ExecStart=${CURRENT_DIR}/bot_venv/bin/python main.py
Restart=always
RestartSec=10

# Logging
StandardOutput=append:${CURRENT_DIR}/log/bot.log
StandardError=append:${CURRENT_DIR}/log/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service 檔案已建立${NC}"
echo ""

# 顯示檔案內容
echo -e "${YELLOW}Service 檔案內容:${NC}"
echo "---"
cat wos-bot.service
echo "---"
echo ""

# 詢問是否繼續
read -p "是否要安裝此 service？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消安裝${NC}"
    exit 0
fi

# 安裝 service
echo -e "${YELLOW}安裝 systemd service...${NC}"
sudo cp wos-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Service 已安裝${NC}"
echo ""

# 啟用服務
echo -e "${YELLOW}啟用開機自動啟動...${NC}"
sudo systemctl enable wos-bot
echo -e "${GREEN}✓ 已啟用開機自動啟動${NC}"
echo ""

# 啟動服務
echo -e "${YELLOW}啟動機器人...${NC}"
sudo systemctl start wos-bot
sleep 2
echo -e "${GREEN}✓ 機器人已啟動${NC}"
echo ""

# 檢查狀態
echo -e "${YELLOW}服務狀態:${NC}"
sudo systemctl status wos-bot --no-pager
echo ""

# 完成
echo -e "${GREEN}"
echo "=========================================="
echo "  設定完成！"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "常用命令："
echo ""
echo -e "${YELLOW}查看狀態:${NC}"
echo "  sudo systemctl status wos-bot"
echo ""
echo -e "${YELLOW}重啟機器人:${NC}"
echo "  sudo systemctl restart wos-bot"
echo ""
echo -e "${YELLOW}停止機器人:${NC}"
echo "  sudo systemctl stop wos-bot"
echo ""
echo -e "${YELLOW}查看即時日誌:${NC}"
echo "  sudo journalctl -u wos-bot -f"
echo ""
echo -e "${YELLOW}查看最近 50 行日誌:${NC}"
echo "  sudo journalctl -u wos-bot -n 50"
echo ""
echo -e "${YELLOW}查看 bot 日誌檔案:${NC}"
echo "  tail -f log/bot.log"
echo "  tail -f log/bot_error.log"
echo ""




