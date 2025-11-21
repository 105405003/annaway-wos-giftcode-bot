#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文化管理器
Internationalization Manager for WOS Gift Code Redemption Bot
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

class I18nManager:
    """中文化管理器類別"""
    
    def __init__(self, language: str = None):
        """
        初始化中文化管理器
        
        Args:
            language: 語言代碼 (預設: 從環境變量讀取或 zh_TW)
        """
        if language is None:
            language = os.getenv("LANGUAGE", "zh_TW")
        
        self.language = language
        self.fallback_language = "en"
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """載入翻譯文件"""
        try:
            # 載入主要語言
            main_file = f"i18n/{self.language}.py"
            if os.path.exists(main_file):
                # 動態載入 Python 模組
                import importlib.util
                spec = importlib.util.spec_from_file_location("translations", main_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 取得所有翻譯字典
                for attr_name in dir(module):
                    if not attr_name.startswith('_') and isinstance(getattr(module, attr_name), dict):
                        self.translations[attr_name] = getattr(module, attr_name)
            
            # 如果主要語言載入失敗，載入備用語言
            if not self.translations and self.language != self.fallback_language:
                self.language = self.fallback_language
                self.load_translations()
                
        except Exception as e:
            print(f"載入翻譯文件時發生錯誤: {e}")
            # 使用預設的英文翻譯
            self._load_default_translations()
    
    def _load_default_translations(self):
        """載入預設的英文翻譯"""
        self.translations = {
            "COMMON": {
                "success": "✅ Success",
                "error": "❌ Error",
                "warning": "⚠️ Warning",
                "info": "ℹ️ Info",
                "loading": "⏳ Loading...",
                "processing": "🔄 Processing...",
                "completed": "✅ Completed",
                "failed": "❌ Failed",
                "cancelled": "🚫 Cancelled",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "save": "Save",
                "delete": "Delete",
                "edit": "Edit",
                "add": "Add",
                "remove": "Remove",
                "search": "Search",
                "filter": "Filter",
                "sort": "Sort",
                "refresh": "Refresh",
                "close": "Close",
                "open": "Open",
                "settings": "Settings",
                "help": "Help",
                "about": "About"
            },
            "PERMISSIONS": {
                "admin_required": "❌ Only administrators can use this command",
                "global_admin_required": "❌ Only global administrators can use this command",
                "insufficient_permissions": "❌ Insufficient permissions",
                "bot_admin_required": "🤖 Bot needs **Administrator** permissions to function properly.\nGo to server settings → Roles → find bot role → scroll down and turn on Administrator",
                "dm_not_allowed": "❌ This command must be used in a server, not in DMs"
            }
        }
    
    def get(self, key: str, category: str = "COMMON", **kwargs) -> str:
        """
        取得翻譯文字
        
        Args:
            key: 翻譯鍵值
            category: 翻譯分類 (預設: COMMON)
            **kwargs: 格式化參數
            
        Returns:
            翻譯後的文字
        """
        try:
            if category in self.translations and key in self.translations[category]:
                text = self.translations[category][key]
                # 如果有格式化參數，進行格式化
                if kwargs:
                    try:
                        text = text.format(**kwargs)
                    except (KeyError, ValueError):
                        # 如果格式化失敗，返回原始文字
                        pass
                return text
            else:
                # 如果找不到翻譯，返回鍵值本身
                return f"[{category}.{key}]"
        except Exception as e:
            print(f"取得翻譯時發生錯誤: {e}")
            return f"[{category}.{key}]"
    
    def format_datetime(self, dt: datetime) -> str:
        """
        格式化日期時間
        
        Args:
            dt: 日期時間物件
            
        Returns:
            格式化後的日期時間字串
        """
        formats = {
            "zh_TW": "%Y年%m月%d日 %H:%M:%S",
            "zh_CN": "%Y年%m月%d日 %H:%M:%S", 
            "en": "%Y-%m-%d %H:%M:%S",
            "ja": "%Y年%m月%d日 %H:%M:%S"
        }
        
        format_str = formats.get(self.language, formats["en"])
        return dt.strftime(format_str)
    
    def format_number(self, number: int) -> str:
        """
        格式化數字
        
        Args:
            number: 數字
            
        Returns:
            格式化後的數字字串
        """
        return f"{number:,}"
    
    def set_language(self, language: str):
        """
        設定語言
        
        Args:
            language: 語言代碼
        """
        if language != self.language:
            self.language = language
            self.translations.clear()
            self.load_translations()
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        取得可用語言列表
        
        Returns:
            語言代碼到語言名稱的對應字典
        """
        return {
            "zh_TW": "繁體中文",
            "zh_CN": "簡體中文",
            "en": "English", 
            "ja": "日本語"
        }

# 全域實例
i18n = I18nManager()

# 便利函數
def _(key: str, category: str = "COMMON", **kwargs) -> str:
    """
    取得翻譯文字的便利函數
    
    Args:
        key: 翻譯鍵值
        category: 翻譯分類
        **kwargs: 格式化參數
        
    Returns:
        翻譯後的文字
    """
    return i18n.get(key, category, **kwargs)

def set_language(language: str):
    """
    設定語言的便利函數
    
    Args:
        language: 語言代碼
    """
    i18n.set_language(language)

def format_datetime(dt: datetime) -> str:
    """
    格式化日期時間的便利函數
    
    Args:
        dt: 日期時間物件
        
    Returns:
        格式化後的日期時間字串
    """
    return i18n.format_datetime(dt)

def format_number(number: int) -> str:
    """
    格式化數字的便利函數
    
    Args:
        number: 數字
        
    Returns:
        格式化後的數字字串
    """
    return i18n.format_number(number)
