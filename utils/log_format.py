#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annaway Log Formatting Utilities
統一的日誌格式化工具，讓日誌更容易閱讀和除錯
"""

import discord
from datetime import datetime
from typing import Optional, Dict, Any


def format_admin_log(
    action: str,
    guild: Optional[discord.Guild] = None,
    alliance_name: Optional[str] = None,
    user: Optional[discord.User] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """
    格式化管理員操作日誌為統一的單行格式
    
    Args:
        action: 操作動作描述
        guild: Discord 伺服器物件
        alliance_name: 聯盟名稱
        user: 執行操作的使用者
        extra: 額外的資訊字典
    
    Returns:
        格式化的日誌字串
        
    Example:
        "[Annaway WOS][GUILD:1458][ALLIANCE:DVL][USER:@Anna] Added 3 members (ids=123, 456, 789)"
    """
    parts = ["[Annaway WOS]"]
    
    # 加入 Guild 資訊
    if guild:
        parts.append(f"[GUILD:{guild.id}]")
    
    # 加入聯盟資訊
    if alliance_name:
        parts.append(f"[ALLIANCE:{alliance_name}]")
    
    # 加入使用者資訊
    if user:
        parts.append(f"[USER:@{user.name}]")
    
    # 加入操作動作
    parts.append(action)
    
    # 加入額外資訊
    if extra:
        extra_str = ", ".join([f"{k}={v}" for k, v in extra.items()])
        parts[-1] += f" ({extra_str})"
    
    return " ".join(parts)


def format_error_log(
    location: str,
    error: Exception | str,
    guild: Optional[discord.Guild] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """
    格式化錯誤日誌
    
    Args:
        location: 錯誤發生位置（如 cog 名稱或函數名稱）
        error: 錯誤物件或錯誤訊息
        guild: Discord 伺服器物件
        extra: 額外的資訊字典
    
    Returns:
        格式化的錯誤日誌字串
        
    Example:
        "[Annaway WOS][ERROR][gift_operations.py] Failed to redeem code: API timeout"
    """
    parts = ["[Annaway WOS][ERROR]"]
    
    # 加入 Guild 資訊
    if guild:
        parts.append(f"[GUILD:{guild.id}]")
    
    # 加入位置
    parts.append(f"[{location}]")
    
    # 加入錯誤訊息
    if isinstance(error, Exception):
        error_msg = f"{type(error).__name__}: {str(error)}"
    else:
        error_msg = str(error)
    
    parts.append(error_msg)
    
    # 加入額外資訊
    if extra:
        extra_str = ", ".join([f"{k}={v}" for k, v in extra.items()])
        parts.append(f"({extra_str})")
    
    return " ".join(parts)


def format_gift_log(
    operation: str,
    giftcode: Optional[str] = None,
    fid: Optional[int] = None,
    status: Optional[str] = None,
    alliance_name: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """
    格式化禮包碼相關日誌
    
    Args:
        operation: 操作類型（如 "Created", "Redeemed", "Failed"）
        giftcode: 禮包碼
        fid: 玩家 FID
        status: 狀態
        alliance_name: 聯盟名稱
        extra: 額外資訊
    
    Returns:
        格式化的日誌字串
    """
    parts = ["[Annaway WOS][GIFT]"]
    
    if alliance_name:
        parts.append(f"[ALLIANCE:{alliance_name}]")
    
    parts.append(operation)
    
    details = []
    if giftcode:
        details.append(f"code={giftcode}")
    if fid:
        details.append(f"fid={fid}")
    if status:
        details.append(f"status={status}")
    
    if extra:
        details.extend([f"{k}={v}" for k, v in extra.items()])
    
    if details:
        parts.append(f"({', '.join(details)})")
    
    return " ".join(parts)


def format_member_log(
    operation: str,
    fid: int,
    nickname: Optional[str] = None,
    alliance_name: Optional[str] = None,
    furnace_level: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """
    格式化成員管理相關日誌
    
    Args:
        operation: 操作類型（如 "Added", "Removed", "Updated"）
        fid: 玩家 FID
        nickname: 玩家暱稱
        alliance_name: 聯盟名稱
        furnace_level: 熔爐等級
        extra: 額外資訊
    
    Returns:
        格式化的日誌字串
    """
    parts = ["[Annaway WOS][MEMBER]"]
    
    if alliance_name:
        parts.append(f"[ALLIANCE:{alliance_name}]")
    
    parts.append(operation)
    
    details = [f"fid={fid}"]
    if nickname:
        details.append(f"nickname={nickname}")
    if furnace_level is not None:
        details.append(f"furnace={furnace_level}")
    
    if extra:
        details.extend([f"{k}={v}" for k, v in extra.items()])
    
    parts.append(f"({', '.join(details)})")
    
    return " ".join(parts)


def format_attendance_log(
    operation: str,
    alliance_name: str,
    date: Optional[str] = None,
    member_count: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """
    格式化出席記錄相關日誌
    
    Args:
        operation: 操作類型（如 "Recorded", "Updated", "Exported"）
        alliance_name: 聯盟名稱
        date: 日期
        member_count: 成員數量
        extra: 額外資訊
    
    Returns:
        格式化的日誌字串
    """
    parts = ["[Annaway WOS][ATTENDANCE]", f"[ALLIANCE:{alliance_name}]", operation]
    
    details = []
    if date:
        details.append(f"date={date}")
    if member_count is not None:
        details.append(f"members={member_count}")
    
    if extra:
        details.extend([f"{k}={v}" for k, v in extra.items()])
    
    if details:
        parts.append(f"({', '.join(details)})")
    
    return " ".join(parts)


def get_timestamp() -> str:
    """
    獲取統一格式的時間戳記
    
    Returns:
        ISO 格式的時間戳記字串
    """
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'


def log_to_file(filepath: str, message: str, include_timestamp: bool = True):
    """
    寫入日誌到檔案
    
    Args:
        filepath: 日誌檔案路徑
        message: 日誌訊息
        include_timestamp: 是否包含時間戳記
    """
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            if include_timestamp:
                f.write(f"[{get_timestamp()}] {message}\n")
            else:
                f.write(f"{message}\n")
    except Exception as e:
        print(f"[WARNING] Failed to write to log file {filepath}: {e}")

