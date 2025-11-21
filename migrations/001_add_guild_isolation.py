#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration 001: Add Guild Isolation for Alliance List
遷移腳本 001: 為聯盟清單添加 Guild 隔離機制

Purpose:
- Ensure all alliances are properly tagged with discord_server_id
- Create indexes for performance
- Handle orphaned alliances
"""

import sqlite3
import sys
from datetime import datetime

def migrate():
    """執行遷移"""
    print("=" * 80)
    print("MIGRATION 001: Guild Isolation for Alliance List")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    conn = sqlite3.connect('db/alliance.sqlite')
    c = conn.cursor()
    
    try:
        # Step 1: Ensure discord_server_id column exists
        print("[1/5] Checking discord_server_id column...")
        c.execute("PRAGMA table_info(alliance_list)")
        columns = [info[1] for info in c.fetchall()]
        
        if "discord_server_id" not in columns:
            print("  ➜ Adding discord_server_id column...")
            c.execute("ALTER TABLE alliance_list ADD COLUMN discord_server_id INTEGER")
            conn.commit()
            print("  ✓ Column added")
        else:
            print("  ✓ Column already exists")
        
        # Step 2: Check for orphaned alliances (NULL discord_server_id)
        print("\n[2/5] Checking for orphaned alliances...")
        c.execute("SELECT COUNT(*) FROM alliance_list WHERE discord_server_id IS NULL")
        orphan_count = c.fetchone()[0]
        
        if orphan_count > 0:
            print(f"  ⚠️  Found {orphan_count} orphaned alliance(s)")
            c.execute("SELECT alliance_id, name FROM alliance_list WHERE discord_server_id IS NULL")
            orphans = c.fetchall()
            
            print("\n  Orphaned Alliances:")
            for aid, name in orphans:
                print(f"    - ID: {aid}, Name: {name}")
            
            # Tag them with a special marker (-1) for admin review
            print("\n  ➜ Tagging orphaned alliances with discord_server_id = -1...")
            c.execute("UPDATE alliance_list SET discord_server_id = -1 WHERE discord_server_id IS NULL")
            conn.commit()
            print("  ✓ Orphaned alliances tagged (guild_id = -1)")
            print("  ℹ️  Admin can manually assign correct guild_id or delete these alliances")
        else:
            print("  ✓ No orphaned alliances found")
        
        # Step 3: Create indexes for performance
        print("\n[3/5] Creating performance indexes...")
        
        # Index 1: discord_server_id (for WHERE filtering)
        try:
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_alliance_guild 
                ON alliance_list(discord_server_id)
            """)
            print("  ✓ Created idx_alliance_guild")
        except Exception as e:
            print(f"  ⚠️  idx_alliance_guild: {e}")
        
        # Index 2: Composite index (discord_server_id, name) for autocomplete
        try:
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_alliance_guild_name 
                ON alliance_list(discord_server_id, name)
            """)
            print("  ✓ Created idx_alliance_guild_name")
        except Exception as e:
            print(f"  ⚠️  idx_alliance_guild_name: {e}")
        
        conn.commit()
        
        # Step 4: Verify data integrity
        print("\n[4/5] Verifying data integrity...")
        c.execute("SELECT COUNT(*) FROM alliance_list")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(DISTINCT discord_server_id) FROM alliance_list")
        unique_guilds = c.fetchone()[0]
        
        c.execute("""
            SELECT discord_server_id, COUNT(*) as cnt 
            FROM alliance_list 
            GROUP BY discord_server_id
        """)
        guild_distribution = c.fetchall()
        
        print(f"  Total alliances: {total}")
        print(f"  Unique guilds: {unique_guilds}")
        print("\n  Distribution by Guild:")
        for guild_id, count in guild_distribution:
            guild_label = "ORPHANED" if guild_id == -1 else f"Guild {guild_id}"
            print(f"    {guild_label}: {count} alliance(s)")
        
        # Step 5: Show index usage (EXPLAIN QUERY PLAN)
        print("\n[5/5] Verifying index usage...")
        c.execute("""
            EXPLAIN QUERY PLAN 
            SELECT * FROM alliance_list WHERE discord_server_id = 123456789
        """)
        explain_result = c.fetchall()
        print("  Query Plan for guild filter:")
        for row in explain_result:
            print(f"    {row}")
        
        conn.commit()
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

def rollback():
    """回滾遷移（如果需要）"""
    print("=" * 80)
    print("ROLLBACK 001: Removing Guild Isolation")
    print("=" * 80)
    
    conn = sqlite3.connect('db/alliance.sqlite')
    c = conn.cursor()
    
    try:
        # Drop indexes
        c.execute("DROP INDEX IF EXISTS idx_alliance_guild")
        c.execute("DROP INDEX IF EXISTS idx_alliance_guild_name")
        
        # Optionally remove column (not recommended, just set to NULL)
        c.execute("UPDATE alliance_list SET discord_server_id = NULL")
        
        conn.commit()
        print("✅ Rollback completed")
        return True
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()




