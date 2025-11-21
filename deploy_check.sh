#!/bin/bash
# Google Cloud VM 部署前檢查腳本

echo "=========================================="
echo "  WOS Gift Code Bot - 部署前檢查"
echo "=========================================="
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查函數
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 ${RED}(MISSING)${NC}"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ ${RED}(MISSING)${NC}"
        return 1
    fi
}

# 檢查必要文件
echo "檢查必要文件..."
check_file "main.py"
check_file "requirements.txt"
check_file "bot_config.env.example"
check_file "i18n_manager.py"
check_file "permission_manager.py"
echo ""

# 檢查配置文件
echo "檢查配置..."
if [ -f "bot_config.env" ]; then
    echo -e "${GREEN}✓${NC} bot_config.env ${YELLOW}(記得設定 DISCORD_TOKEN)${NC}"
else
    echo -e "${YELLOW}!${NC} bot_config.env ${YELLOW}(需要從 bot_config.env.example 複製並設定)${NC}"
fi
echo ""

# 檢查目錄
echo "檢查目錄結構..."
check_dir "cogs"
check_dir "i18n"
check_dir "db"
check_dir "models"
check_dir "fonts"
echo ""

# 檢查關鍵文件
echo "檢查關鍵資源..."
check_file "models/captcha_model.onnx"
check_file "fonts/unifont-16.0.04.otf"
echo ""

# Python 語法檢查
echo "Python 語法檢查..."
if command -v python3 &> /dev/null; then
    python3 -m py_compile main.py 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} main.py 語法正確"
    else
        echo -e "${RED}✗${NC} main.py 語法錯誤"
    fi
    
    python3 -m compileall cogs i18n -q 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} 所有 cogs 和 i18n 模組語法正確"
    else
        echo -e "${RED}✗${NC} 部分模組有語法錯誤"
    fi
else
    echo -e "${YELLOW}!${NC} Python3 未安裝，跳過語法檢查"
fi
echo ""

# 檢查 requirements.txt
echo "檢查依賴套件..."
if [ -f "requirements.txt" ]; then
    PKG_COUNT=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l)
    echo -e "${GREEN}✓${NC} requirements.txt 包含 $PKG_COUNT 個套件"
else
    echo -e "${RED}✗${NC} requirements.txt 不存在"
fi
echo ""

# 部署建議
echo "=========================================="
echo "  部署建議"
echo "=========================================="
echo ""
echo "1. 上傳前確保已設定 bot_config.env"
echo "2. 使用以下命令安裝依賴:"
echo "   python3 -m venv bot_venv"
echo "   source bot_venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "3. 啟動機器人:"
echo "   python3 main.py"
echo ""
echo "4. 使用 systemd 或 screen 讓機器人在背景運行"
echo ""
echo "=========================================="
echo "  檢查完成！"
echo "=========================================="




