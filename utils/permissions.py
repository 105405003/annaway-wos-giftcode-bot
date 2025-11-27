#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annaway Permission System
Simple role-based permissions for multi-guild bot

Only users with Annaway_Admin or Annaway_Manager roles can perform management actions.
"""

import discord
from functools import wraps
from typing import Optional, Callable
import logging
import os

logger = logging.getLogger('permissions')

# Define required role names from environment variables
ADMIN_ROLE_NAME = os.getenv("ANNAWAY_ADMIN_ROLE", "Annaway_Admin")
MANAGER_ROLE_NAME = os.getenv("ANNAWAY_MANAGER_ROLE", "Annaway_Manager")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0")) if os.getenv("BOT_OWNER_ID") else None


def _get_permission_error_message(admin_only: bool = False) -> str:
    """
    取得權限錯誤訊息（內部使用，避免循環引入）
    
    Args:
        admin_only: 是否僅限 Admin
    
    Returns:
        格式化的錯誤訊息
    """
    if admin_only:
        return (
            "❌ **權限不足**\n\n"
            f"此功能僅限 `{ADMIN_ROLE_NAME}` 身分組使用。\n\n"
            "📌 **如何獲得權限？**\n"
            "請聯絡伺服器管理員，或參考 Annaway 文件中的權限說明。"
        )
    else:
        return (
            "❌ **權限不足**\n\n"
            f"此功能需要 `{ADMIN_ROLE_NAME}` 或 `{MANAGER_ROLE_NAME}` 身分組。\n\n"
            "📌 **如何獲得權限？**\n"
            "請聯絡伺服器管理員，或參考 Annaway 文件中的權限說明。"
        )


def _get_no_guild_message() -> str:
    """
    取得非伺服器環境錯誤訊息（內部使用）
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **無法在私訊中使用**\n\n"
        "這個指令只能在伺服器頻道使用，不能在私訊中使用。\n\n"
        "📌 **如何使用？**\n"
        "請回到你的伺服器頻道再試一次。"
    )


def has_annaway_role(member: discord.Member) -> bool:
    """
    Check if member has either Annaway_Admin or Annaway_Manager role.
    
    Args:
        member: Discord member object
        
    Returns:
        True if member has at least one of the required roles
    """
    if not isinstance(member, discord.Member):
        return False
    
    role_names = {role.name for role in member.roles}
    return ADMIN_ROLE_NAME in role_names or MANAGER_ROLE_NAME in role_names


def has_admin_role(member: discord.Member) -> bool:
    """
    Check if member has Annaway_Admin role (highest permission level).
    
    Args:
        member: Discord member object
        
    Returns:
        True if member has Annaway_Admin role
    """
    if not isinstance(member, discord.Member):
        return False
    
    role_names = {role.name for role in member.roles}
    return ADMIN_ROLE_NAME in role_names


def is_guild_context(interaction: discord.Interaction) -> bool:
    """
    Check if interaction is happening in a guild (not DM).
    
    Args:
        interaction: Discord interaction object
        
    Returns:
        True if in a guild context
    """
    return interaction.guild is not None


async def check_guild_context(interaction: discord.Interaction) -> bool:
    """
    Ensure interaction is in a guild. If not, send error and return False.
    
    Args:
        interaction: Discord interaction object
        
    Returns:
        True if in guild, False otherwise (error already sent)
    """
    if not is_guild_context(interaction):
        await interaction.response.send_message(
            _get_no_guild_message(),
            ephemeral=True
        )
        return False
    return True


async def check_permission(
    interaction: discord.Interaction,
    admin_only: bool = False,
) -> bool:
    """統一檢查 Annaway 權限。
    
    admin_only=True  -> 只允許 Annaway_Admin 或 DB is_initial=1
    admin_only=False -> Annaway_Admin / Annaway_Manager / DB is_initial=1 都可用
    """
    
    PERMISSION_ERROR_MESSAGE = "❌ You do not have permission to perform this action."
    
    # CRITICAL: 立即寫入 debug log 到檔案，確認函式被執行
    try:
        import datetime
        with open("permission_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now()}] check_permission CALLED\n")
            f.flush()
    except Exception as e:
        print(f"ERROR writing debug log: {e}")
    
    user = interaction.user
    guild = interaction.guild
    
    # 私訊或沒有 guild 的情況，一律擋掉
    if guild is None:
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    PERMISSION_ERROR_MESSAGE, ephemeral=True
                )
            else:
                await interaction.followup.send(
                    PERMISSION_ERROR_MESSAGE, ephemeral=True
                )
        except Exception:
            pass
        return False
    
    # --- 1. 取得角色物件 ---
    admin_role_name = "Annaway_Admin"
    manager_role_name = "Annaway_Manager"
    
    admin_role = discord.utils.get(guild.roles, name=admin_role_name)
    manager_role = discord.utils.get(guild.roles, name=manager_role_name)
    
    has_admin_role = admin_role in user.roles if admin_role else False
    has_manager_role = manager_role in user.roles if manager_role else False
    
    # --- 2. 查 DB，看是不是「全域管理員」(is_initial = 1) ---
    is_global_admin_db = False
    try:
        conn = sqlite3.connect("db/settings.sqlite")
        cur = conn.cursor()
        cur.execute("SELECT is_initial FROM admin WHERE id = ?", (user.id,))
        row = cur.fetchone()
        is_global_admin_db = bool(row and row[0] == 1)
        conn.close()
    except Exception as e:
        print(f"[PERMISSION DEBUG] DB error in check_permission: {e}")
    
    # --- 3. 判斷是否允許 ---
    if admin_only:
        # Admin-only: 需要 Annaway_Admin 或 DB is_initial=1
        allowed = has_admin_role or is_global_admin_db
    else:
        # Manager 級：Admin / Manager / 全域管理員 都可以
        allowed = has_admin_role or has_manager_role or is_global_admin_db
    
    # --- 4. Debug log（方便排錯）---
    custom_id = "unknown"
    try:
        custom_id = interaction.data.get("custom_id", "unknown")
    except Exception:
        pass
    
    # 寫入完整 debug log 到檔案
    try:
        with open("permission_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\n========================================\n")
            f.write(f"custom_id: {custom_id}\n")
            f.write(f"admin_only: {admin_only}\n")
            f.write(f"user.id: {user.id}\n")
            f.write(f"user.name: {user.name}\n")
            f.write(f"guild.id: {guild.id}\n")
            f.write(f"guild.name: {guild.name}\n")
            f.write(f"User roles (names): {[r.name for r in user.roles]}\n")
            f.write(f"has_admin_role: {has_admin_role}\n")
            f.write(f"has_manager_role: {has_manager_role}\n")
            f.write(f"is_global_admin (DB is_initial): {is_global_admin_db}\n")
            f.write(f"allowed: {allowed}\n")
            f.flush()
    except Exception as e:
        print(f"ERROR writing full debug log: {e}")
    
    if not allowed:
        try:
            with open("permission_debug.log", "a", encoding="utf-8") as f:
                f.write(f"❌ DENIED - insufficient permission\n")
                f.write(f"========================================\n")
                f.flush()
        except Exception:
            pass
        
        # 統一錯誤訊息出口：確保先 defer 再發送
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    PERMISSION_ERROR_MESSAGE,
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    PERMISSION_ERROR_MESSAGE,
                    ephemeral=True,
                )
        except discord.InteractionResponded:
            # Already responded, try followup
            try:
                await interaction.followup.send(PERMISSION_ERROR_MESSAGE, ephemeral=True)
            except Exception as e2:
                print(f"[PERMISSION DEBUG] error in followup: {e2}")
        except Exception as e:
            print(f"[PERMISSION DEBUG] error while sending permission error: {e}")
        return False
    
    try:
        with open("permission_debug.log", "a", encoding="utf-8") as f:
            f.write(f"✅ ALLOWED\n")
            f.write(f"========================================\n")
            f.flush()
    except Exception:
        pass
    
    return True


def requires_annaway_role(admin_only: bool = False):
    """
    Decorator for slash commands that require Annaway roles.
    
    Usage:
        @app_commands.command()
        @requires_annaway_role()
        async def my_command(self, interaction: discord.Interaction):
            ...
    
    Args:
        admin_only: If True, require Annaway_Admin specifically
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if not await check_permission(interaction, admin_only=admin_only):
                return
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator


def requires_annaway_role_button(admin_only: bool = False):
    """
    Decorator for button/select callbacks that require Annaway roles.
    
    Usage:
        @discord.ui.button(...)
        @requires_annaway_role_button()
        async def my_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            ...
    
    Args:
        admin_only: If True, require Annaway_Admin specifically
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # For button callbacks, we need to check permissions differently
            if not is_guild_context(interaction):
                await interaction.response.send_message(
                    _get_no_guild_message(),
                    ephemeral=True
                )
                return
            
            member = interaction.user
            if not isinstance(member, discord.Member):
                await interaction.response.send_message(
                    "❌ **無法驗證權限**\n\n無法取得您的成員資訊。",
                    ephemeral=True
                )
                return
            
            # Check role
            if admin_only:
                if not has_admin_role(member):
                    await interaction.response.send_message(
                        _get_permission_error_message(admin_only=True),
                        ephemeral=True
                    )
                    return
            else:
                if not has_annaway_role(member):
                    await interaction.response.send_message(
                        _get_permission_error_message(admin_only=False),
                        ephemeral=True
                    )
                    return
            
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

