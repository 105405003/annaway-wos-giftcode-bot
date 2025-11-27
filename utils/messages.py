#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annaway Message Templates
統一的使用者訊息模板，提供一致的錯誤和提示訊息
"""

from utils.permissions import ADMIN_ROLE_NAME, MANAGER_ROLE_NAME


def no_permission_message_admin_only() -> str:
    """
    僅限 Admin 的權限錯誤訊息
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **權限不足**\n\n"
        f"此功能僅限 `{ADMIN_ROLE_NAME}` 身分組使用。\n\n"
        "📌 **如何獲得權限？**\n"
        "請聯絡伺服器管理員，或參考 Annaway 文件中的權限說明。"
    )


def no_permission_message_manager_or_admin() -> str:
    """
    需要 Manager 或 Admin 的權限錯誤訊息
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **權限不足**\n\n"
        f"此功能需要 `{ADMIN_ROLE_NAME}` 或 `{MANAGER_ROLE_NAME}` 身分組。\n\n"
        "📌 **如何獲得權限？**\n"
        "請聯絡伺服器管理員，或參考 Annaway 文件中的權限說明。"
    )


def no_guild_context_message() -> str:
    """
    不在伺服器中的錯誤訊息
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **無法在私訊中使用**\n\n"
        "這個指令只能在伺服器頻道使用，不能在私訊中使用。\n\n"
        "📌 **如何使用？**\n"
        "請回到你的伺服器頻道再試一次。"
    )


def no_alliance_configured_message() -> str:
    """
    伺服器尚未設定聯盟的訊息
    
    Returns:
        格式化的提示訊息
    """
    return (
        "⚠️ **尚未設定聯盟**\n\n"
        "此伺服器尚未設定任何聯盟。\n\n"
        "📌 **下一步**\n"
        "請使用以下指令來建立聯盟：\n"
        "1️⃣ 使用 `/settings` 指令\n"
        "2️⃣ 選擇 `Alliance Operations`\n"
        "3️⃣ 選擇 `Add Alliance`\n"
    )


def alliance_not_found_message(alliance_input: str) -> str:
    """
    找不到指定聯盟的訊息
    
    Args:
        alliance_input: 使用者輸入的聯盟名稱或 ID
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        f"❌ **找不到聯盟**\n\n"
        f"無法找到聯盟：`{alliance_input}`\n\n"
        "📌 **可能原因**\n"
        "• 聯盟名稱或 ID 輸入錯誤\n"
        "• 聯盟尚未在此伺服器建立\n"
        "• 聯盟屬於其他伺服器\n\n"
        "💡 **建議**\n"
        "使用 `/settings` → `View Alliances` 查看所有可用的聯盟。"
    )


def invalid_fid_message() -> str:
    """
    無效的 FID 格式訊息
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **FID 格式錯誤**\n\n"
        "FID（玩家 ID）必須是純數字。\n\n"
        "📌 **正確格式**\n"
        "例如：`123456789`"
    )


def api_error_message(error_details: str = "") -> str:
    """
    API 錯誤訊息
    
    Args:
        error_details: 錯誤詳細資訊
    
    Returns:
        格式化的錯誤訊息
    """
    base_message = (
        "❌ **API 連線錯誤**\n\n"
        "無法連接到遊戲 API 伺服器。\n\n"
    )
    
    if error_details:
        base_message += f"**錯誤詳情**\n```\n{error_details}\n```\n\n"
    
    base_message += (
        "📌 **可能原因**\n"
        "• 遊戲伺服器維護中\n"
        "• 網路連線問題\n"
        "• API 憑證過期\n\n"
        "💡 **建議**\n"
        "請稍後再試，或聯絡管理員檢查 API 設定。"
    )
    
    return base_message


def captcha_error_message() -> str:
    """
    驗證碼錯誤訊息
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **驗證碼處理失敗**\n\n"
        "無法自動處理驗證碼。\n\n"
        "📌 **可能原因**\n"
        "• 驗證碼服務未設定\n"
        "• 驗證碼服務額度不足\n"
        "• 驗證碼辨識失敗\n\n"
        "💡 **建議**\n"
        "請檢查 2Captcha API 設定或手動處理驗證碼。"
    )


def database_error_message() -> str:
    """
    資料庫錯誤訊息
    
    Returns:
        格式化的錯誤訊息
    """
    return (
        "❌ **資料庫錯誤**\n\n"
        "無法存取資料庫。\n\n"
        "📌 **可能原因**\n"
        "• 資料庫檔案損壞\n"
        "• 磁碟空間不足\n"
        "• 權限不足\n\n"
        "💡 **建議**\n"
        "請聯絡管理員檢查資料庫狀態。"
    )


def operation_success_message(operation: str, details: str = "") -> str:
    """
    操作成功訊息
    
    Args:
        operation: 操作名稱
        details: 額外詳細資訊
    
    Returns:
        格式化的成功訊息
    """
    message = f"✅ **{operation} 成功**\n\n"
    
    if details:
        message += f"{details}\n"
    
    return message


def operation_in_progress_message(operation: str) -> str:
    """
    操作進行中訊息
    
    Args:
        operation: 操作名稱
    
    Returns:
        格式化的進行中訊息
    """
    return f"⏳ **處理中**\n\n正在執行 {operation}，請稍候..."


def batch_operation_summary(
    operation: str,
    total: int,
    success: int,
    failed: int
) -> str:
    """
    批次操作摘要訊息
    
    Args:
        operation: 操作名稱
        total: 總數
        success: 成功數量
        failed: 失敗數量
    
    Returns:
        格式化的摘要訊息
    """
    success_rate = (success / total * 100) if total > 0 else 0
    
    return (
        f"📊 **{operation} 完成**\n\n"
        f"**總計**：{total}\n"
        f"✅ **成功**：{success}\n"
        f"❌ **失敗**：{failed}\n"
        f"📈 **成功率**：{success_rate:.1f}%"
    )


def help_message() -> str:
    """
    一般性幫助訊息
    
    Returns:
        格式化的幫助訊息
    """
    return (
        "📚 **Annaway WOS Giftcode Bot 說明**\n\n"
        "**主要功能**\n"
        "🎁 自動發送禮包碼\n"
        "👥 聯盟成員管理\n"
        "📋 出席記錄追蹤\n"
        "📊 統計資料分析\n\n"
        "**開始使用**\n"
        "使用 `/settings` 指令來設定機器人。\n\n"
        "**需要協助？**\n"
        "請參考文件或聯絡 Annaway Studio 支援團隊。"
    )


def feature_not_configured_message(feature: str) -> str:
    """
    功能尚未設定的訊息
    
    Args:
        feature: 功能名稱
    
    Returns:
        格式化的提示訊息
    """
    return (
        f"⚠️ **{feature} 尚未設定**\n\n"
        f"此功能需要先進行設定才能使用。\n\n"
        "📌 **下一步**\n"
        f"請使用 `/settings` 指令來設定 {feature}。"
    )

