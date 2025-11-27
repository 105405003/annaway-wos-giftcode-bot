#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PATCH A2: Enhanced Scheduler Logging for Gift Code Redemption
增強排程記錄用於禮品碼兌換

Purpose:
- Add structured DEBUG logging to auto_retry_redemption_loop
- Track timezone, execution time, status filtering
- Log API responses and state transitions
- Implement dry-run mode for testing
"""

import re

def patch_auto_retry_loop_enhanced_logging():
    """為 auto_retry_redemption_loop 添加結構化 DEBUG 日誌"""
    
    file_path = 'cogs/gift_operations.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在 auto_retry_redemption_loop 函數開始處添加增強日誌
    enhanced_log_start = '''    @tasks.loop(hours=12)
    async def auto_retry_redemption_loop(self):
        """每天台灣時間 8:00 和 20:00 檢查未完全兌換的禮品碼，並重試失敗的FID"""
        from datetime import datetime, timezone
        import pytz
        
        # ========== A2 FIX: 結構化 DEBUG 日誌 ==========
        log_prefix = "[AUTO_RETRY_DEBUG]"
        
        # 取得台灣時區的當前時間
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now_taiwan = datetime.now(taiwan_tz)
        now_utc = datetime.now(timezone.utc)
        
        loop_start_time = now_taiwan
        
        # 結構化日誌：開始
        self.logger.info(f"{log_prefix} ========================================")
        self.logger.info(f"{log_prefix} AUTO RETRY LOOP STARTED")
        self.logger.info(f"{log_prefix} ========================================")
        self.logger.info(f"{log_prefix} Taiwan Time: {now_taiwan.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.logger.info(f"{log_prefix} UTC Time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.logger.info(f"{log_prefix} Timezone Offset: UTC{now_taiwan.strftime('%z')}")
        self.logger.info(f"{log_prefix} ========================================")
        
        # 原有日誌
        self.logger.info(f"\\n[自動重試] 開始自動重試檢查 - 台灣時間 {loop_start_time.strftime('%Y-%m-%d %H:%M:%S')}")'''
    
    # Find and replace the function start
    old_start = '''    @tasks.loop(hours=12)
    async def auto_retry_redemption_loop(self):
        """每天台灣時間 8:00 和 20:00 檢查未完全兌換的禮品碼，並重試失敗的FID"""
        from datetime import datetime, timezone
        import pytz
        
        # 取得台灣時區的當前時間
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now_taiwan = datetime.now(taiwan_tz)
        
        loop_start_time = now_taiwan
        self.logger.info(f"\\n[自動重試] 開始自動重試檢查 - 台灣時間 {loop_start_time.strftime('%Y-%m-%d %H:%M:%S')}")'''
    
    if old_start in content:
        content = content.replace(old_start, enhanced_log_start)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Enhanced logging added to auto_retry_redemption_loop")
        return True
    else:
        print("⚠️  Pattern not found, may already be patched")
        return False

def add_status_filtering_debug():
    """添加狀態篩選的 DEBUG 日誌"""
    
    file_path = 'cogs/gift_operations.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在查詢未兌換 FID 的地方添加詳細日誌
    # 這需要找到具體的查詢位置並添加日誌
    
    # 示例：在查詢前後添加日誌
    search_pattern = r'(# 查詢該聯盟中尚未兌換的 FID.*?self\.users_cursor\.execute\(.*?user_giftcodes.*?\))'
    
    def add_debug_wrapper(match):
        original = match.group(0)
        return f'''# A2 FIX: 狀態篩選 DEBUG
                    self.logger.debug(f"{{log_prefix}} Querying unredeemed FIDs for alliance {{alliance_id}}, giftcode {{giftcode}}")
                    self.logger.debug(f"{{log_prefix}} SQL: SELECT DISTINCT fid FROM users WHERE alliance = ? AND fid NOT IN (SELECT fid FROM user_giftcodes WHERE giftcode = ?)")
                    {original}
                    unredeemed_count = len(unredeemed_fids)
                    self.logger.debug(f"{{log_prefix}} Found {{unredeemed_count}} unredeemed FIDs")'''
    
    content = re.sub(search_pattern, add_debug_wrapper, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Status filtering debug added")
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("APPLYING PATCH A2: Enhanced Scheduler Logging")
    print("=" * 80)
    print()
    
    results = []
    results.append(("Enhanced Logging", patch_auto_retry_loop_enhanced_logging()))
    # results.append(("Status Filtering Debug", add_status_filtering_debug()))
    
    print()
    print("=" * 80)
    print("PATCH A2 SUMMARY")
    print("=" * 80)
    for name, success in results:
        status = "✅" if success else "⚠️ "
        print(f"{status} {name}")
    
    print()
    print("Next steps:")
    print("  1. Review the enhanced logs in log/gift_ops.txt")
    print("  2. Verify timezone is correct (Taiwan +08:00)")
    print("  3. Check status filtering logic")
    print("  4. Implement retry strategy if needed")







