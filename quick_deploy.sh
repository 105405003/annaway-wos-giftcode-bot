#!/bin/bash
# WOS Discord Bot - 快速部署腳本
# 用於 Ubuntu 22.04 LTS

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標題
echo -e "${BLUE}"
echo "=========================================="
echo "  WOS Discord Bot - 快速部署腳本"
echo "=========================================="
echo -e "${NC}"
echo ""

# 檢查是否為 root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}請不要使用 root 用戶執行此腳本${NC}"
    exit 1
fi

# 步驟 1: 更新系統
echo -e "${YELLOW}[1/8] 更新系統套件...${NC}"
sudo apt update
sudo apt upgrade -y
echo -e "${GREEN}✓ 系統更新完成${NC}"
echo ""

# 步驟 2: 安裝必要工具
echo -e "${YELLOW}[2/8] 安裝 Python 和必要工具...${NC}"
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential unzip git curl htop
echo -e "${GREEN}✓ 工具安裝完成${NC}"
echo ""

# 步驟 3: 檢查專案目錄
echo -e "${YELLOW}[3/8] 檢查專案目錄...${NC}"
if [ ! -f "main.py" ]; then
    echo -e "${RED}錯誤: 找不到 main.py${NC}"
    echo "請確保在專案根目錄執行此腳本"
    exit 1
fi
echo -e "${GREEN}✓ 專案目錄確認${NC}"
echo ""

# 步驟 4: 建立虛擬環境
echo -e "${YELLOW}[4/8] 建立 Python 虛擬環境...${NC}"
if [ ! -d "bot_venv" ]; then
    python3 -m venv bot_venv
    echo -e "${GREEN}✓ 虛擬環境建立完成${NC}"
else
    echo -e "${YELLOW}! 虛擬環境已存在，跳過${NC}"
fi
echo ""

# 步驟 5: 安裝依賴套件
echo -e "${YELLOW}[5/8] 安裝 Python 依賴套件...${NC}"
source bot_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ 依賴套件安裝完成${NC}"
echo ""

# 步驟 6: 設定配置文件
echo -e "${YELLOW}[6/8] 檢查配置文件...${NC}"
if [ ! -f "bot_config.env" ]; then
    if [ -f "bot_config.env.example" ]; then
        echo -e "${YELLOW}! bot_config.env 不存在，從範例複製...${NC}"
        cp bot_config.env.example bot_config.env
        echo -e "${RED}重要: 請編輯 bot_config.env 並設定 DISCORD_TOKEN${NC}"
        echo "執行: nano bot_config.env"
    else
        echo -e "${RED}錯誤: 找不到 bot_config.env.example${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ bot_config.env 已存在${NC}"
fi
echo ""

# 步驟 7: 建立必要目錄
echo -e "${YELLOW}[7/8] 建立必要目錄...${NC}"
mkdir -p db log backups captcha_images
echo -e "${GREEN}✓ 目錄建立完成${NC}"
echo ""

# 步驟 8: 測試運行
echo -e "${YELLOW}[8/8] 執行部署檢查...${NC}"
if [ -f "deploy_check.sh" ]; then
    chmod +x deploy_check.sh
    ./deploy_check.sh
else
    echo -e "${YELLOW}! deploy_check.sh 不存在，跳過${NC}"
fi
echo ""

# 完成
echo -e "${GREEN}"
echo "=========================================="
echo "  基本部署完成！"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "接下來的步驟："
echo ""
echo -e "${YELLOW}1. 設定 bot_config.env:${NC}"
echo "   nano bot_config.env"
echo ""
echo -e "${YELLOW}2. 測試啟動機器人:${NC}"
echo "   source bot_venv/bin/activate"
echo "   python3 main.py"
echo ""
echo -e "${YELLOW}3. 設定 systemd 自動啟動:${NC}"
echo "   ./setup_systemd.sh"
echo ""
echo -e "${GREEN}如需更多幫助，請查看 GCP_DEPLOYMENT_GUIDE.md${NC}"
echo ""







