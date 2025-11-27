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

logger = logging.getLogger('permissions')

# Define required role names
ADMIN_ROLE_NAME = "Annaway_Admin"
MANAGER_ROLE_NAME = "Annaway_Manager"


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
    Check if user has required permissions. Sends error message if not.
    
    Args:
        interaction: Discord interaction object
        admin_only: If True, require Annaway_Admin role specifically
        
    Returns:
        True if user has permission, False otherwise (error already sent)
    """
    # First check if in guild
    if not await check_guild_context(interaction):
        return False
    
    member = interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message(
            "❌ Unable to verify your permissions.",
            ephemeral=True
        )
        return False
    
    # Check role requirement
    if admin_only:
        if not has_admin_role(member):
            await interaction.response.send_message(
                _get_permission_error_message(admin_only=True),
                ephemeral=True
            )
            return False
    else:
        if not has_annaway_role(member):
            await interaction.response.send_message(
                _get_permission_error_message(admin_only=False),
                ephemeral=True
            )
            return False
    
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

