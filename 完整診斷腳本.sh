#!/bin/bash
# 完整診斷 Manager 權限問題

echo "========================================"
echo "1. 檢查檔案修改時間"
echo "========================================"
ls -lh ~/wos_bot/cogs/alliance_member_operations.py
ls -lh ~/wos_bot/cogs/changes.py
ls -lh ~/wos_bot/cogs/statistics.py
echo ""

echo "========================================"
echo "2. 檢查檔案是否包含 HOTFIX"
echo "========================================"
echo "alliance_member_operations.py:"
grep -c "HOTFIX: 支援 Manager 角色" ~/wos_bot/cogs/alliance_member_operations.py || echo "未找到 HOTFIX"
echo "changes.py:"
grep -c "HOTFIX: 支援 Manager 角色" ~/wos_bot/cogs/changes.py || echo "未找到 HOTFIX"
echo "statistics.py:"
grep -c "HOTFIX: 支援 Manager 角色" ~/wos_bot/cogs/statistics.py || echo "未找到 HOTFIX"
echo ""

echo "========================================"
echo "3. 檢查 bot 進程"
echo "========================================"
ps aux | grep "python.*main.py" | grep -v grep
echo ""

echo "========================================"
echo "4. 檢查最近的 bot 日誌"
echo "========================================"
tail -50 ~/wos_bot/bot.log
echo ""

echo "========================================"
echo "5. 現在請在 Discord 用 Manager 帳號執行 /settings"
echo "   然後點擊「成員操作」按鈕"
echo "   等待 3 秒後按 Enter 繼續..."
echo "========================================"
read -p "按 Enter 繼續..."

echo ""
echo "========================================"
echo "6. 查看點擊後的日誌"
echo "========================================"
tail -100 ~/wos_bot/bot.log | grep -A 5 -B 5 "get_admin_alliances\|Manager\|沒有可用\|沒有權限\|no permission"
echo ""

echo "========================================"
echo "7. 檢查解壓後的檔案（如果步驟2沒有 HOTFIX）"
echo "========================================"
if [ -f ~/hotfix4_all_cogs_manager_*.zip ]; then
    echo "找到 zip 檔案"
    cd ~
    unzip -l hotfix4_all_cogs_manager_*.zip
else
    echo "未找到 hotfix4 zip 檔案"
fi
echo ""

echo "========================================"
echo "完成診斷！請把所有輸出貼給我"
echo "========================================"




