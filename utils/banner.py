#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annaway Startup Banner
在機器人啟動時顯示 ASCII Logo 和版本資訊
"""

from datetime import datetime
from typing import Optional


ANNAWAY_BANNER = r"""
    ___                                           
   /   |  ____  ____  ____ __      ______ ___  __
  / /| | / __ \/ __ \/ __ `/ | /| / / __ `/ / / /
 / ___ |/ / / / / / / /_/ /| |/ |/ / /_/ / /_/ / 
/_/  |_/_/ /_/_/ /_/\__,_/ |__/|__/\__,_/\__, /  
                                        /____/   
    WOS Giftcode Redemption Bot
"""


def print_startup_banner(version: Optional[str] = None):
    """
    顯示啟動橫幅，包含 ASCII logo 和版本資訊
    
    Args:
        version: 版本號（例如 "1.0.0-annaway"）
    """
    print("\n" + "=" * 60)
    print(ANNAWAY_BANNER)
    print("=" * 60)
    
    # 建立資訊行
    info_line = "  [Annaway WOS Giftcode Bot]"
    
    if version:
        info_line += f" v{version}"
    
    # 加入啟動時間
    startup_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    info_line += f" - Started at {startup_time}"
    
    print(info_line)
    print("=" * 60)
    
    # 顯示關鍵資訊
    print("\n📋 Bot Information:")
    print("  • Original Project: Reloisback/Whiteout-Survival-Discord-Bot")
    print("  • Customized by: Annaway Studio")
    print("  • Features: Multi-Guild Support + Role-Based Permissions")
    print("\n🔐 Required Roles:")
    print("  • Annaway_Admin  - Full administrative access")
    print("  • Annaway_Manager - Standard management access")
    print("\n" + "=" * 60 + "\n")


def print_shutdown_banner():
    """
    顯示關閉橫幅
    """
    print("\n" + "=" * 60)
    print("  [Annaway WOS Giftcode Bot] Shutting down...")
    shutdown_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    print(f"  Stopped at {shutdown_time}")
    print("=" * 60 + "\n")


# 版本號常數（可在此處更新版本）
__version__ = "1.0.0-annaway"

