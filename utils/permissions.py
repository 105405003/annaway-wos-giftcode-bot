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


async def check_permission(interaction: discord.Interaction, admin_only: bool = False) -> bool:
    """
    Centralized permission check for all button interactions.
    
    admin_only=True  -> only Annaway_Admin (or BOT_OWNER_ID)
    admin_only=False -> Annaway_Admin or Annaway_Manager (or BOT_OWNER_ID)
    
    Args:
        interaction: Discord interaction object
        admin_only: If True, require Annaway_Admin role specifically
        
    Returns:
        True if user has permission, False otherwise (error already sent)
    """
    ERROR_MESSAGE = "❌ You do not have permission to perform this action."
    
    guild = interaction.guild
    user = interaction.user
    
    # Get custom_id for debugging
    custom_id = interaction.data.get("custom_id", "unknown") if interaction.data else "unknown"
    
    # DEBUG: Print basic info
    print(f"[PERMISSION DEBUG] ========================================")
    print(f"[PERMISSION DEBUG] custom_id: {custom_id}")
    print(f"[PERMISSION DEBUG] admin_only: {admin_only}")
    print(f"[PERMISSION DEBUG] user.id: {user.id}")
    print(f"[PERMISSION DEBUG] user.name: {user.name if hasattr(user, 'name') else 'unknown'}")
    print(f"[PERMISSION DEBUG] guild.id: {guild.id if guild else None}")
    print(f"[PERMISSION DEBUG] guild.name: {guild.name if guild else None}")
    
    # Check if user is bot owner (hard override)
    if BOT_OWNER_ID and user.id == BOT_OWNER_ID:
        print(f"[PERMISSION DEBUG] ✅ ALLOWED - User is BOT_OWNER")
        print(f"[PERMISSION DEBUG] ========================================")
        return True
    
    # If we are not in a guild context, deny by default
    if guild is None or not isinstance(user, discord.Member):
        print(f"[PERMISSION DEBUG] ❌ DENIED - Not in guild context or not a member")
        print(f"[PERMISSION DEBUG] ========================================")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(ERROR_MESSAGE, ephemeral=True)
            else:
                await interaction.followup.send(ERROR_MESSAGE, ephemeral=True)
        except Exception as e:
            print(f"[PERMISSION DEBUG] Error sending permission error: {e}")
        return False
    
    # DEBUG: Print all user roles
    user_role_names = [role.name for role in user.roles]
    user_role_ids = [role.id for role in user.roles]
    print(f"[PERMISSION DEBUG] User roles (names): {user_role_names}")
    print(f"[PERMISSION DEBUG] User roles (IDs): {user_role_ids}")
    
    # Fetch roles by name from environment
    print(f"[PERMISSION DEBUG] Looking for admin role: '{ADMIN_ROLE_NAME}'")
    print(f"[PERMISSION DEBUG] Looking for manager role: '{MANAGER_ROLE_NAME}'")
    
    admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
    manager_role = discord.utils.get(guild.roles, name=MANAGER_ROLE_NAME)
    
    print(f"[PERMISSION DEBUG] Admin role found in guild: {admin_role is not None}")
    if admin_role:
        print(f"[PERMISSION DEBUG] Admin role ID: {admin_role.id}")
    
    print(f"[PERMISSION DEBUG] Manager role found in guild: {manager_role is not None}")
    if manager_role:
        print(f"[PERMISSION DEBUG] Manager role ID: {manager_role.id}")
    
    has_annaway_admin_role = admin_role in user.roles if admin_role else False
    has_annaway_manager_role = manager_role in user.roles if manager_role else False
    
    print(f"[PERMISSION DEBUG] has_annaway_admin_role: {has_annaway_admin_role}")
    print(f"[PERMISSION DEBUG] has_annaway_manager_role: {has_annaway_manager_role}")
    
    # Determine if user is global admin or manager
    is_global_admin = has_annaway_admin_role
    is_manager = has_annaway_admin_role or has_annaway_manager_role
    
    print(f"[PERMISSION DEBUG] is_global_admin: {is_global_admin}")
    print(f"[PERMISSION DEBUG] is_manager: {is_manager}")
    
    # Admin-only actions: must be Annaway_Admin
    if admin_only:
        if is_global_admin:
            print(f"[PERMISSION DEBUG] ✅ ALLOWED - Admin-only action, user is global admin")
            print(f"[PERMISSION DEBUG] ========================================")
            return True
        print(f"[PERMISSION DEBUG] ❌ DENIED - Admin-only action, user is not global admin")
        print(f"[PERMISSION DEBUG] ========================================")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(ERROR_MESSAGE, ephemeral=True)
            else:
                await interaction.followup.send(ERROR_MESSAGE, ephemeral=True)
        except Exception as e:
            print(f"[PERMISSION DEBUG] Error sending permission error: {e}")
        return False
    
    # Manager-level actions: Annaway_Admin OR Annaway_Manager
    if is_manager:
        print(f"[PERMISSION DEBUG] ✅ ALLOWED - Manager-level action, user is manager or admin")
        print(f"[PERMISSION DEBUG] ========================================")
        return True
    
    print(f"[PERMISSION DEBUG] ❌ DENIED - Manager-level action, user is neither manager nor admin")
    print(f"[PERMISSION DEBUG] ========================================")
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(ERROR_MESSAGE, ephemeral=True)
        else:
            await interaction.followup.send(ERROR_MESSAGE, ephemeral=True)
    except Exception as e:
        print(f"[PERMISSION DEBUG] Error sending permission error: {e}")
    return False


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

