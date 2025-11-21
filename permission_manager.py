#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
權限管理系統
Permission Management System for WOS Gift Code Redemption Bot
"""

import discord
from enum import Enum
from typing import Optional, List, Dict, Any
from i18n_manager import i18n, _

class PermissionLevel(Enum):
    """權限等級枚舉"""
    USER = 1          # 基本使用者
    MANAGER = 2       # 管理員
    ADMIN = 3         # 最高管理員

class PermissionManager:
    """權限管理器"""
    
    def __init__(self):
        """初始化權限管理器"""
        # Discord 身分組名稱對應的權限等級
        self.role_permissions = {
            "Annaway_Admin": PermissionLevel.ADMIN,
            "Annaway_Manager": PermissionLevel.MANAGER,
            # 其他使用者預設為 USER 等級
        }
        
        # 權限功能對應表
        self.permission_functions = {
            PermissionLevel.ADMIN: {
                "alliance_management": True,      # 聯盟管理
                "permission_management": True,    # 權限管理
                "member_management": True,        # 成員管理
                "gift_code_management": True,     # 禮品碼管理
                "statistics_view": True,          # 統計查看
                "add_member": True,               # 新增成員
                "settings_access": True,          # 設定存取
            },
            PermissionLevel.MANAGER: {
                "alliance_management": False,     # 聯盟管理
                "permission_management": False,   # 權限管理
                "member_management": True,        # 成員管理
                "gift_code_management": True,     # 禮品碼管理
                "statistics_view": True,          # 統計查看
                "add_member": True,               # 新增成員
                "settings_access": True,          # 設定存取
            },
            PermissionLevel.USER: {
                "alliance_management": False,     # 聯盟管理
                "permission_management": False,   # 權限管理
                "member_management": False,       # 成員管理
                "gift_code_management": False,   # 禮品碼管理
                "statistics_view": False,         # 統計查看
                "add_member": True,               # 新增成員
                "settings_access": False,         # 設定存取
            }
        }
    
    def get_user_permission_level(self, member: discord.Member) -> PermissionLevel:
        """
        根據使用者的 Discord 身分組獲取權限等級
        
        Args:
            member: Discord 成員物件
            
        Returns:
            權限等級
        """
        # 檢查使用者是否擁有管理員身分組
        for role in member.roles:
            if role.name in self.role_permissions:
                return self.role_permissions[role.name]
        
        # 預設為 USER 等級
        return PermissionLevel.USER
    
    def has_permission(self, member: discord.Member, function: str) -> bool:
        """
        檢查使用者是否有特定功能的權限
        
        Args:
            member: Discord 成員物件
            function: 功能名稱
            
        Returns:
            是否有權限
        """
        permission_level = self.get_user_permission_level(member)
        return self.permission_functions.get(permission_level, {}).get(function, False)
    
    def get_permission_level_name(self, level: PermissionLevel) -> str:
        """
        獲取權限等級的中文名稱
        
        Args:
            level: 權限等級
            
        Returns:
            權限等級名稱
        """
        level_names = {
            PermissionLevel.ADMIN: "最高管理員",
            PermissionLevel.MANAGER: "管理員",
            PermissionLevel.USER: "基本使用者"
        }
        return level_names.get(level, "未知")
    
    def get_available_functions(self, member: discord.Member) -> List[str]:
        """
        獲取使用者可用的功能列表
        
        Args:
            member: Discord 成員物件
            
        Returns:
            可用功能列表
        """
        permission_level = self.get_user_permission_level(member)
        functions = []
        
        for function, has_permission in self.permission_functions[permission_level].items():
            if has_permission:
                functions.append(function)
        
        return functions
    
    def create_permission_embed(self, member: discord.Member) -> discord.Embed:
        """
        創建權限資訊嵌入
        
        Args:
            member: Discord 成員物件
            
        Returns:
            權限資訊嵌入
        """
        permission_level = self.get_user_permission_level(member)
        level_name = self.get_permission_level_name(permission_level)
        available_functions = self.get_available_functions(member)
        
        # 功能名稱對應
        function_names = {
            "alliance_management": "聯盟管理",
            "permission_management": "權限管理",
            "member_management": "成員管理",
            "gift_code_management": "禮品碼管理",
            "statistics_view": "統計查看",
            "add_member": "新增成員",
            "settings_access": "設定存取"
        }
        
        # 建立功能列表
        function_list = ""
        for function in available_functions:
            function_name = function_names.get(function, function)
            function_list += f"• {function_name}\n"
        
        embed = discord.Embed(
            title=f"權限資訊 - {member.display_name}",
            description=f"**權限等級：** {level_name}\n\n**可用功能：**\n{function_list}",
            color=discord.Color.blue()
        )
        
        return embed
    
    def check_permission_and_respond(self, interaction: discord.Interaction, function: str) -> bool:
        """
        檢查權限並回應（如果沒有權限）
        
        Args:
            interaction: Discord 互動物件
            function: 功能名稱
            
        Returns:
            是否有權限
        """
        if not self.has_permission(interaction.user, function):
            embed = discord.Embed(
                title="權限不足",
                description=f"您沒有使用此功能的權限。\n\n**您的權限等級：** {self.get_permission_level_name(self.get_user_permission_level(interaction.user))}\n**所需功能：** {function}",
                color=discord.Color.red()
            )
            interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

# 全域權限管理器實例
permission_manager = PermissionManager()

# 便利函數
def has_permission(member: discord.Member, function: str) -> bool:
    """
    檢查使用者是否有特定功能的權限
    
    Args:
        member: Discord 成員物件
        function: 功能名稱
        
    Returns:
        是否有權限
    """
    return permission_manager.has_permission(member, function)

def get_user_permission_level(member: discord.Member) -> PermissionLevel:
    """
    獲取使用者的權限等級
    
    Args:
        member: Discord 成員物件
        
    Returns:
        權限等級
    """
    return permission_manager.get_user_permission_level(member)

def check_permission_and_respond(interaction: discord.Interaction, function: str) -> bool:
    """
    檢查權限並回應（如果沒有權限）
    
    Args:
        interaction: Discord 互動物件
        function: 功能名稱
        
    Returns:
        是否有權限
    """
    return permission_manager.check_permission_and_respond(interaction, function)

