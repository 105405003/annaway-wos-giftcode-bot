#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annaway Embed Utilities
統一的 Discord Embed 樣式，讓 Discord 訊息更美觀
"""

import discord
from datetime import datetime
from typing import Optional


# Annaway 主題顏色
ANNAWAY_COLOR = 0x5865F2  # Discord Blurple
SUCCESS_COLOR = 0x57F287   # Green
WARNING_COLOR = 0xFEE75C   # Yellow
ERROR_COLOR = 0xED4245     # Red
INFO_COLOR = 0x5865F2      # Blue


def build_admin_log_embed(
    title: str,
    description: str,
    guild: Optional[discord.Guild] = None,
    alliance_name: Optional[str] = None,
    actor: Optional[discord.abc.User] = None,
    color: int = ANNAWAY_COLOR,
    add_timestamp: bool = True
) -> discord.Embed:
    """
    建立管理員操作日誌的 Embed
    
    Args:
        title: Embed 標題
        description: Embed 描述
        guild: Discord 伺服器物件
        alliance_name: 聯盟名稱
        actor: 執行操作的使用者
        color: Embed 顏色（預設為 Annaway 主題色）
        add_timestamp: 是否加入時間戳記
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    if guild is not None:
        embed.add_field(
            name="🏰 伺服器",
            value=f"{guild.name}\n`ID: {guild.id}`",
            inline=False
        )
    
    if alliance_name:
        embed.add_field(
            name="🛡️ 聯盟",
            value=alliance_name,
            inline=True
        )
    
    if actor is not None:
        embed.add_field(
            name="👤 操作者",
            value=actor.mention,
            inline=True
        )
    
    if add_timestamp:
        embed.timestamp = datetime.utcnow()
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_success_embed(
    title: str,
    description: str,
    add_timestamp: bool = True
) -> discord.Embed:
    """
    建立成功訊息的 Embed
    
    Args:
        title: Embed 標題
        description: Embed 描述
        add_timestamp: 是否加入時間戳記
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=SUCCESS_COLOR
    )
    
    if add_timestamp:
        embed.timestamp = datetime.utcnow()
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_error_embed(
    title: str,
    description: str,
    add_timestamp: bool = True
) -> discord.Embed:
    """
    建立錯誤訊息的 Embed
    
    Args:
        title: Embed 標題
        description: Embed 描述
        add_timestamp: 是否加入時間戳記
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=ERROR_COLOR
    )
    
    if add_timestamp:
        embed.timestamp = datetime.utcnow()
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_warning_embed(
    title: str,
    description: str,
    add_timestamp: bool = True
) -> discord.Embed:
    """
    建立警告訊息的 Embed
    
    Args:
        title: Embed 標題
        description: Embed 描述
        add_timestamp: 是否加入時間戳記
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title=f"⚠️ {title}",
        description=description,
        color=WARNING_COLOR
    )
    
    if add_timestamp:
        embed.timestamp = datetime.utcnow()
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_info_embed(
    title: str,
    description: str,
    add_timestamp: bool = True
) -> discord.Embed:
    """
    建立資訊訊息的 Embed
    
    Args:
        title: Embed 標題
        description: Embed 描述
        add_timestamp: 是否加入時間戳記
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=INFO_COLOR
    )
    
    if add_timestamp:
        embed.timestamp = datetime.utcnow()
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_member_operation_embed(
    operation: str,
    member_name: str,
    fid: int,
    alliance_name: str,
    furnace_level: Optional[int] = None,
    actor: Optional[discord.abc.User] = None,
    success: bool = True
) -> discord.Embed:
    """
    建立成員操作的 Embed
    
    Args:
        operation: 操作類型（如 "新增成員", "移除成員"）
        member_name: 成員名稱
        fid: 玩家 FID
        alliance_name: 聯盟名稱
        furnace_level: 熔爐等級
        actor: 執行操作的使用者
        success: 是否成功
    
    Returns:
        Discord Embed 物件
    """
    color = SUCCESS_COLOR if success else ERROR_COLOR
    status_emoji = "✅" if success else "❌"
    
    embed = discord.Embed(
        title=f"{status_emoji} {operation}",
        color=color,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="👤 玩家",
        value=f"{member_name}\n`FID: {fid}`",
        inline=True
    )
    
    embed.add_field(
        name="🛡️ 聯盟",
        value=alliance_name,
        inline=True
    )
    
    if furnace_level is not None:
        embed.add_field(
            name="🔥 熔爐等級",
            value=str(furnace_level),
            inline=True
        )
    
    if actor is not None:
        embed.add_field(
            name="🔧 操作者",
            value=actor.mention,
            inline=False
        )
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_gift_operation_embed(
    operation: str,
    giftcode: str,
    alliance_name: Optional[str] = None,
    total_members: Optional[int] = None,
    success_count: Optional[int] = None,
    failed_count: Optional[int] = None,
    actor: Optional[discord.abc.User] = None
) -> discord.Embed:
    """
    建立禮包碼操作的 Embed
    
    Args:
        operation: 操作類型（如 "建立禮包碼", "發送禮包碼"）
        giftcode: 禮包碼
        alliance_name: 聯盟名稱
        total_members: 總成員數
        success_count: 成功數量
        failed_count: 失敗數量
        actor: 執行操作的使用者
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title=f"🎁 {operation}",
        color=ANNAWAY_COLOR,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="禮包碼",
        value=f"`{giftcode}`",
        inline=False
    )
    
    if alliance_name:
        embed.add_field(
            name="🛡️ 聯盟",
            value=alliance_name,
            inline=True
        )
    
    if total_members is not None:
        embed.add_field(
            name="👥 總成員",
            value=str(total_members),
            inline=True
        )
    
    if success_count is not None:
        embed.add_field(
            name="✅ 成功",
            value=str(success_count),
            inline=True
        )
    
    if failed_count is not None:
        embed.add_field(
            name="❌ 失敗",
            value=str(failed_count),
            inline=True
        )
    
    if actor is not None:
        embed.add_field(
            name="🔧 操作者",
            value=actor.mention,
            inline=False
        )
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed


def build_attendance_embed(
    alliance_name: str,
    date: str,
    present_count: int,
    absent_count: int,
    total_count: int,
    actor: Optional[discord.abc.User] = None
) -> discord.Embed:
    """
    建立出席記錄的 Embed
    
    Args:
        alliance_name: 聯盟名稱
        date: 日期
        present_count: 出席人數
        absent_count: 缺席人數
        total_count: 總人數
        actor: 執行操作的使用者
    
    Returns:
        Discord Embed 物件
    """
    embed = discord.Embed(
        title="📋 出席記錄",
        color=ANNAWAY_COLOR,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="🛡️ 聯盟",
        value=alliance_name,
        inline=True
    )
    
    embed.add_field(
        name="📅 日期",
        value=date,
        inline=True
    )
    
    embed.add_field(
        name="👥 總人數",
        value=str(total_count),
        inline=True
    )
    
    embed.add_field(
        name="✅ 出席",
        value=str(present_count),
        inline=True
    )
    
    embed.add_field(
        name="❌ 缺席",
        value=str(absent_count),
        inline=True
    )
    
    attendance_rate = (present_count / total_count * 100) if total_count > 0 else 0
    embed.add_field(
        name="📊 出席率",
        value=f"{attendance_rate:.1f}%",
        inline=True
    )
    
    if actor is not None:
        embed.add_field(
            name="🔧 操作者",
            value=actor.mention,
            inline=False
        )
    
    embed.set_footer(text="Annaway WOS Giftcode Bot")
    
    return embed

