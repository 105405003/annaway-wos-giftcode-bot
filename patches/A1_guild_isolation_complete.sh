#!/bin/bash
# PATCH A1: Guild Isolation - Complete All Files
# 完整修補所有需要 guild 隔離的文件

echo "========================================================================"
echo "PATCH A1: Guild Isolation - Comprehensive Fix"
echo "========================================================================"
echo ""

# 備份
echo "[1/4] Creating backups..."
mkdir -p backups/A1_guild_isolation_$(date +%Y%m%d_%H%M%S)
cp cogs/statistics.py backups/A1_guild_isolation_$(date +%Y%m%d_%H%M%S)/
cp cogs/changes.py backups/A1_guild_isolation_$(date +%Y%m%d_%H%M%S)/
cp cogs/permission_management.py backups/A1_guild_isolation_$(date +%Y%m%d_%H%M%S)/
cp cogs/gift_operations.py backups/A1_guild_isolation_$(date +%Y%m%d_%H%M%S)/
echo "✓ Backups created"

# 執行遷移
echo ""
echo "[2/4] Running migration script..."
python migrations/001_add_guild_isolation.py
if [ $? -eq 0 ]; then
    echo "✓ Migration completed"
else
    echo "✗ Migration failed"
    exit 1
fi

# 驗證索引
echo ""
echo "[3/4] Verifying indexes..."
sqlite3 db/alliance.sqlite "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='alliance_list';"
echo "✓ Index verification complete"

# 顯示統計
echo ""
echo "[4/4] Alliance distribution by guild..."
sqlite3 db/alliance.sqlite << EOF
SELECT 
    CASE 
        WHEN discord_server_id = -1 THEN 'ORPHANED'
        WHEN discord_server_id IS NULL THEN 'NULL (ERROR)'
        ELSE 'Guild ' || discord_server_id
    END as guild_label,
    COUNT(*) as alliance_count
FROM alliance_list
GROUP BY discord_server_id
ORDER BY discord_server_id;
EOF

echo ""
echo "========================================================================"
echo "✅ PATCH A1 COMPLETED"
echo "========================================================================"
echo ""
echo "Next Steps:"
echo "  1. Restart bot: pkill -f 'python.*main.py' && nohup python main.py > bot.log 2>&1 &"
echo "  2. Test in multiple Discord servers"
echo "  3. Verify alliance isolation with /settings > View Alliances"
echo ""







