#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 通用資訊
COMMON = {
    "success": "成功",
    "error": "錯誤",
    "warning": "警告",
    "info": "資訊",
    "loading": "載入中...",
    "processing": "處理中...",
    "completed": "完成",
    "failed": "失敗",
    "cancelled": "已取消",
    "confirm": "確認",
    "cancel": "取消",
    "yes": "是",
    "no": "否",
    "ok": "確定",
    "back": "返回",
    "main_menu": "主選單",
    "save": "儲存",
    "delete": "刪除",
    "edit": "編輯",
    "add": "新增",
    "remove": "移除",
    "search": "搜尋",
    "refresh": "重新整理",
    "close": "關閉",
    "settings": "設定",
    "help": "說明",
    "about": "關於",
    "member": "成員"
}

# 通用術語（GENERAL 別名）
GENERAL = COMMON

# 主選單相關
MENU = {
    "please_select_category": "請選擇分類：",
    "alliance_operations": "聯盟操作",
    "manage_alliances_settings": "管理聯盟和設定",
    "alliance_member_operations": "聯盟成員操作",
    "add_remove_view_members": "新增、移除和查看成員",
    "bot_operations": "機器人操作",
    "configure_bot_settings": "配置機器人設定",
    "gift_code_operations": "禮品碼操作",
    "manage_gift_codes_rewards": "管理禮品碼和獎勵",
    "alliance_history": "聯盟歷史",
    "view_alliance_changes_history": "查看聯盟變化和歷史",
    "support_operations": "支援操作",
    "access_support_features": "存取支援功能",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "other_features": "其他功能",
    "access_other_features": "存取其他功能",
    "menu_categories": "選單分類",
    "settings_menu": "設定選單"
}

# 權限相關
PERMISSIONS = {
    "no_permission_to_use_command": "您沒有權限使用此命令。",
    "no_permission_to_perform_action": "您沒有執行此操作的權限。",
    "access_level": "存取等級",
    "role": "角色",
    "global_admin": "全域管理員",
    "server_admin": "伺服器管理員",
    "this_action_requires_global_admin": "此操作需要全域管理員權限"
}

# 聯盟相關
ALLIANCE = {
    "alliance_operations": "聯盟操作",
    "please_select_operation": "請選擇操作：",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "add_alliance": "新增聯盟",
    "create_new_alliance": "建立新聯盟",
    "edit_alliance": "編輯聯盟",
    "modify_alliance_settings": "修改現有聯盟設定",
    "delete_alliance": "刪除聯盟",
    "remove_existing_alliance": "移除現有聯盟",
    "view_alliances": "查看聯盟",
    "list_available_alliances": "列出所有可用聯盟",
    "check_alliance": "檢查聯盟",
    "warning_action_cannot_be_undone": "警告：此操作無法復原！",
    "select_alliance_from_dropdown": "從下拉選單選擇聯盟",
    "use_navigation_buttons": "使用按鈕瀏覽頁面",
    "current_page": "目前頁面",
    "total_alliances": "總聯盟數",
    "warning_deleting_alliance_remove_data": "警告：刪除聯盟將移除所有相關資料！",
    "alliance_name_exists": "聯盟名稱已存在",
    "invalid_interval": "無效的間隔值，請輸入數字",
    "alliance_name": "聯盟名稱",
    "please_perform_in_channel": "請在Discord頻道中執行此操作",
    "control_interval": "控制間隔",
    "minutes": "分鐘",
    "gift_code_channel": "禮品碼頻道",
    "not_configured": "未配置",
    "alliance_created_success": "聯盟創建成功",
    "alliance_id": "聯盟ID",
    "alliance_created_instructions": "聯盟已創建完成，將使用全域禮品碼頻道進行自動兌換。"
}

# 聯盟成員操作相關
MEMBER_OPS = {
    "alliance_member_operations": "聯盟成員操作",
    "please_select_operation": "請選擇操作：",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "add_member": "新增成員",
    "add_member_description": "新增新成員到聯盟",
    "remove_member": "移除成員",
    "remove_member_description": "從聯盟中移除成員",
    "view_members": "查看成員",
    "view_members_description": "查看聯盟成員列表",
    "transfer_member": "轉移成員",
    "transfer_member_description": "將成員轉移到其他聯盟",
    "return_to_main_menu": "返回主選單",
    "select_option_to_continue": "選擇選項繼續",
    "all_members": "所有成員",
    "delete_all_members": "刪除所有成員",
    "delete_all_members_warning": "⚠️ 將刪除所有成員！",
    "select_member_to_remove": "👤 選擇要移除的成員...",
    "select_member_to_transfer": "👤 選擇要轉移的成員...",
    "page": "頁面",
    "select_page": "選擇頁面",
    "next_page": "下一頁",
    "previous_page": "上一頁",
    "remove_member_title": "移除成員",
    "transfer_member_title": "轉移成員",
    "no_members_found": "未找到成員",
    "member_selected": "已選擇成員",
    "operation_cancelled": "操作已取消",
    "member_successfully_removed": "成功移除成員",
    "member_transfer_started": "成員轉移已開始",
    "return_to_member_menu": "返回成員選單",
    "add_member_title": "新增成員",
    "add_member_modal_label": "暱稱",
    "add_member_modal_placeholder": "例：玩家暱稱",
    "remove_member_title": "移除成員",
    "member_removed": "成員已移除",
    "member_deleted": "成員已刪除",
    "view_members_title": "查看成員",
    "alliance_selection": "聯盟選擇",
    "transfer_member": "轉移成員",
    "transfer_successful": "轉移成功",
    "operation_queued": "操作已排隊",
    "add_member_to_alliance": "將成員新增到聯盟",
    "select_alliance_for_member": "選擇要新增成員的聯盟",
    "alliance_id": "聯盟ID"
}

# 機器人操作相關
BOT_OPERATIONS = {
    "bot_operations": "機器人操作",
    "please_choose_operation": "請選擇操作：",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "admin_management": "管理員管理",
    "manage_bot_administrators": "管理機器人管理員",
    "admin_permissions": "管理員權限",
    "view_manage_admin_permissions": "查看和管理管理員權限",
    "bot_updates": "機器人更新",
    "check_manage_updates": "檢查和管理更新",
    "add_admin": "新增管理員",
    "remove_admin": "移除管理員",
    "view_administrators": "查看管理員",
    "assign_alliance_to_admin": "指定聯盟給管理員",
    "delete_admin_permissions": "刪除管理員權限",
    "transfer_old_database": "轉移舊資料庫",
    "check_for_updates": "檢查更新",
    "log_system": "日誌系統",
    "alliance_control_messages": "聯盟控制訊息"
}

# 變化記錄相關
CHANGES = {
    "alliance_history": "聯盟歷史",
    "alliance_history_menu": "聯盟歷史選單",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "furnace_changes": "熔爐變化",
    "view_furnace_level_changes": "查看熔爐等級變化",
    "nickname_changes": "暱稱變化",
    "view_nickname_history": "查看暱稱歷史"
}

# 禮品碼相關
GIFT_CODE = {
    "gift_code_operations": "禮品碼操作",
    "please_select_operation": "請選擇操作：",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "add_gift_code": "新增禮品碼",
    "add_gift_code_description": "新增禮品碼並自動開始兌換",
    "add_gift_code_and_start_redeem": "新增禮品碼並自動開始兌換",
    "enter_gift_code": "輸入禮品碼",
    "gift_code_placeholder": "例：ABC123XYZ",
    "gift_code_creation_result": "禮品碼建立結果",
    "gift_code_added_pending": "禮品碼已新增（等待中）",
    "gift_code_details": "禮品碼詳情",
    "status": "狀態",
    "action": "動作",
    "added_for_later_validation": "已新增以供稍後驗證",
    "database_error": "資料庫錯誤",
    "failed_to_save_gift_code": "無法將禮品碼儲存到資料庫。請檢查日誌。",
    "gift_code_already_exists": "禮品碼已存在",
    "gift_code_validated_successfully": "禮品碼驗證成功",
    "gift_code_added_and_started_redeem": "禮品碼已新增並開始兌換",
    "validation_inconclusive": "驗證結果不確定",
    "auto_redemption_started": "已開始自動兌換",
    "alliances_enabled": "啟用的聯盟",
    "auto_redemption_settings": "自動兌換設定",
    # 禮品碼處理完成
    "process_complete": "🎁 禮品碼處理完成: {code}",
    "no_members_to_process": "ℹ️ 無成員需處理禮品碼: {code}",
    "status_for_alliance": "**聯盟狀態:** `{name}`",
    "total_members": "👥 **總成員數:** `{count}`",
    "success_count": "✅ **成功:** `{count}`",
    "already_redeemed": "ℹ️ **已兌換:** `{count}`",
    "retrying_count": "🔄 **重試中:** `{count}`",
    "failed_count": "❌ **失敗:** `{count}`",
    "processed_progress": "⏳ **已處理:** `{processed}/{total}`",
    "error_breakdown": "**錯誤明細:**",
    # 錯誤類型描述
    "error_vip_too_low": "💸 **{count}** 位成員因 VIP 等級不足而失敗。",
    "error_furnace_too_low": "🔥 **{count}** 位成員因熔爐等級不足而失敗。",
    "error_timeout": "⏱️ **{count}** 位成員因連線逾時而失敗。",
    "error_login_expired": "🔒 **{count}** 位成員因登入在處理中過期而失敗。",
    "error_login_failed": "🔐 **{count}** 位成員因登入問題而失敗。",
    "error_captcha_failed": "🤖 **{count}** 位成員因驗證碼失敗。",
    "error_captcha_solver": "🔧 **{count}** 位成員因驗證碼解析器問題而失敗。",
    "error_ocr_disabled": "🚫 **{count}** 位成員因 OCR 已停用而失敗。",
    "error_sign_error": "🔐 **{count}** 位成員因簽名錯誤而失敗。",
    "error_general": "❌ **{count}** 位成員因一般錯誤而失敗。",
    "error_unknown_response": "❓ **{count}** 位成員因未知的 API 回應而失敗。"
}

# 其他功能相關
OTHER_FEATURES = {
    "other_features": "其他功能",
    "access_other_features": "存取其他功能",
    "created_by_user_request": "此模組是根據用戶要求創建的",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "backup_system": "備份系統",
    "automatic_backup": "自動備份功能",
    "send_backup_to_dm": "將備份發送到私訊",
    "global_admin_only": "僅限全域管理員",
    "backup_system_module_not_found": "備份系統模組未找到",
    "error_loading_backup_system_menu": "載入備份系統選單時發生錯誤",
    "error_returning_to_main_menu": "返回主選單時發生錯誤",
    "error_occurred_try_again": "發生錯誤，請再試一次"
}

# 支援操作詳細翻譯
SUPPORT_OPS = {
    "support_operations": "支援操作",
    "please_select_operation": "請選擇操作：",
    "available_operations": "可用操作",
    "separator": "━━━━━━━━━━━━━━━━━━━━━━",
    "request_support": "請求支援",
    "get_help_support": "取得協助和支援",
    "about_project": "關於專案",
    "project_information": "專案資訊",
    "bot_support_information": "機器人支援資訊",
    "support_description": "如果您需要協助或有任何問題，請隨時在我們的Discord上詢問",
    "additional_resources": "其他資源：",
    "github_repository": "GitHub儲存庫：",
    "issues_bug_reports": "問題與錯誤回報：",
    "bot_description": "此機器人為開源專案，由WOSLand社群維護。您可以透過我們的Discord或GitHub儲存庫回報錯誤、請求功能或貢獻專案。",
    "technical_support": "如需技術支援，請確保提供您問題的詳細資訊。",
    "about_whiteout_project": "關於WOSLand專案",
    "open_source_bot": "開源機器人",
    "open_source_description": "這是WOSLand的開源Discord機器人。此專案由社群推動，任何人都可以免費使用。",
    "features": "功能",
    "feature_list": "• 聯盟成員管理\n• 禮品碼操作\n• 自動成員追蹤\n• 及更多...",
    "contributing": "貢獻",
    "contributing_description": "歡迎貢獻！請查看我們的GitHub儲存庫以回報問題、建議功能或提交pull request。",
    "made_with_love": "由WOSLand機器人團隊用心製作。"
}

# 命令描述相關
SETTINGS = {
    "open_settings_menu": "開啟設定選單"
}

# 錯誤訊息相關
ERRORS = {
    "error_occurred_try_again": "發生錯誤，請再試一次",
    "command_server_only": "此指令只能在伺服器中使用",
    "no_permission": "您沒有權限執行此操作",
    "bot_needs_admin_permission": "機器人需要「管理伺服器」權限才能使用此功能。請檢查機器人角色權限設定。",
    "no_permission_command": "❌ 您沒有權限使用此命令",
    "alliance_name_exists": "聯盟名稱已存在，請使用其他名稱",
    "alliance_not_found": "找不到聯盟",
    "invalid_interval_value": "無效的間隔值，請輸入數字",
    "error_updating_alliance": "更新聯盟時發生錯誤",
    "error_editing_alliance": "編輯聯盟時發生錯誤，請重試",
    "error_loading_edit_menu": "載入編輯選單時發生錯誤",
    "error_loading_delete_menu": "載入刪除選單時發生錯誤",
    "cannot_return_other_features": "❌ 無法返回其他功能選單",
    "remove_failed": "❌ 移除失敗"
}

# 標籤相關
LABEL = {
    "alliance_name": "聯盟名稱",
    "control_interval_minutes": "控制間隔（分鐘）",
    "your_permission_level": "**您的權限等級:** {level}",
    "available_commands": "**可用命令:** `/add` - 新增成員到聯盟",
    "fid_player_id": "FID（玩家ID）",
    "gift_code": "禮品碼"
}

# 佔位符相關
PLACEHOLDER = {
    "enter_alliance_name": "請輸入聯盟名稱",
    "enter_interval_or_zero": "輸入間隔分鐘（或輸入0禁用）",
    "select_alliance_to_edit": "選擇要編輯的聯盟 ({page}/{total})",
    "select_alliance_to_delete": "Select an alliance to delete",
    "enter_fid_placeholder": "輸入要新增的玩家FID（數字）",
    "enter_gift_code": "例：ABC123XYZ"
}

# 選項描述相關
OPTION_DESC = {
    "interval_minutes": "間隔: {interval} 分鐘",
    "members_click_delete": "部落成員: {count} | 點擊刪除"
}

# 按鈕相關
BUTTON = {
    "alliance_operations": "聯盟操作",
    "member_operations": "成員操作",
    "gift_code_operations": "禮品碼操作",
    "alliance_history": "聯盟歷史",
    "other_features": "其他功能",
    "permission_management": "權限管理",
    "add_alliance": "新增聯盟",
    "edit_alliance": "編輯聯盟",
    "delete_alliance": "刪除聯盟",
    "view_alliances": "查看聯盟",
    "check_alliance": "檢查聯盟",
    "main_menu": "主選單",
    "statistics_report": "統計報表",
    "set_global_gift_channel": "設定全域禮品碼頻道",
    "backup_system": "備份系統",
    "add_member": "新增成員",
    "remove_member": "移除成員",
    "view_members": "查看成員",
    "transfer_member": "轉移成員",
    "update_member_info": "更新成員資訊",
    "add_gift_code": "新增禮品碼",
    "furnace_changes": "熔爐變化",
    "nickname_changes": "暱稱變化",
    "confirm": "確認",
    "cancel": "取消",
    "back": "返回"
}

# 標題相關
TITLE = {
    "error": "❌ 錯誤",
    "alliance_created_success": "✅ 聯盟創建成功",
    "edit_alliance": "✏️ 編輯聯盟",
    "delete_alliance": "🗑️ 刪除聯盟",
    "alliance_updated_success": "✅ 聯盟更新成功",
    "global_giftcode_detection": "🎁 全域禮品碼檢測",
    "alliance_deleted_success": "✅ 聯盟刪除成功",
    "deletion_cancelled": "❌ 刪除已取消",
    "confirm_deletion": "⚠️ 確認刪除",
    "no_alliances_found": "❌ No Alliances Found",
    "remove_success": "✅ 移除成功",
    "operation_cancelled": "❌ 已取消"
}

# 描述相關
DESCRIPTION = {
    "permission_management_desc": "⚙️ **權限管理**\n└ 設定 Manager 的聯盟操作權限",
    "global_giftcode_detected": "檢測到禮品碼: **{code}**\n\n🔍 **狀態**: 已加入驗證佇列\n⏰ **檢測時間**: <t:{timestamp}:R>\n\n📋 **流程**:\n1️⃣ 驗證禮品碼有效性\n2️⃣ 為所有已啟用的聯盟兌換\n3️⃣ 回報兌換結果\n\n⌛ 請稍候，處理中...",
    "alliance_details": "🏰 **聯盟名稱:** {name}\n🆔 **聯盟ID:** {id}\n⏰ **控制間隔:** {interval} 分鐘\n\n✅ **聯盟創建完成並已啟用禮品碼控制**",
    "alliance_created_success_desc": "🏰 **聯盟名稱：** {name}\n🆔 **聯盟ID：** {id}\n⏰ **控制間隔：** {interval} 分鐘\n━━━━━━━━━━━━━━━━━━━━━━\n✅ **聯盟創建完成並已啟用禮品碼控制**",
    "alliance_updated_details": "聯盟詳情已更新如下：",
    "alliance_info_section": "**🛡️ 聯盟名稱**\n{name}\n\n**🔢 聯盟ID**\n{id}\n\n**📢 使用頻道**\n{channel}\n\n**⏱️ 控制間隔**\n{interval} 分鐘",
    "edit_instructions": "**說明：**\n━━━━━━━━━━━━━━━━━━━━━━\n1️⃣ 從下拉選單選擇要編輯的聯盟\n2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n**目前頁面：** {current}/{total}\n**總聯盟數：** {count}\n━━━━━━━━━━━━━━━━━━━━━━",
    "delete_warning": "**警告：刪除聯盟將移除所有相關數據**\n━━━━━━━━━━━━━━━━━━━━━━\n1️⃣ 從下拉選單選擇要刪除的聯盟\n2️⃣ 使用 ◀️ ▶️ 按鈕瀏覽頁面\n\n**目前頁面：** {current}/{total}\n**總聯盟數：** {count}\n━━━━━━━━━━━━━━━━━━━━━━",
    "no_alliances": "資料庫中沒有註冊的聯盟",
    "no_alliances_to_delete": "沒有可刪除的聯盟",
    "error_creating_alliance": "An error occurred while creating the alliance.",
    "alliance_deleted_success": "聯盟 {name} (ID: {id}) 已成功刪除\n\n已清理的資料：\n- 成員資料: {member_count} 筆\n- 禮品碼記錄: {gift_count} 筆\n- 聯盟設定: {setting_count} 筆",
    "alliance_deletion_cancelled": "聯盟刪除已取消",
    "confirm_delete_alliance": "⚠️ **確認刪除聯盟**\n\n您確定要刪除聯盟 **{name}** (ID: {id}) 嗎？\n\n**這將會刪除：**\n• 所有成員資料 ({member_count} 個成員)\n• 所有禮品碼兌換記錄\n• 所有聯盟設定\n\n**此操作無法復原！**",
    "member_removed_success": "已成功移除 **{name}** (FID: {fid})",
    "remove_operation_cancelled": "已取消移除操作"
}

# 狀態相關
STATUS = {
    "added_to_validation_queue": "已加入驗證佇列",
    "detection_time": "⏰ **檢測時間**: <t:{timestamp}:R>",
    "process_steps": "📋 **流程**:",
    "step1_validate": "1️⃣ 驗證禮品碼有效性",
    "step2_redeem": "2️⃣ 為所有已啟用的聯盟兌換",
    "step3_report": "3️⃣ 回報兌換結果",
    "please_wait_processing": "⌛ 請稍候，處理中..."
}

# Footer 相關
FOOTER = {
    "global_giftcode_source": "來源: {author} | 全域禮品碼頻道",
    "alliance_created_complete": "━━━━━━━━━━━━━━━━━━━━━━\n聯盟創建完成並已啟用禮品碼控制",
    "please_create_alliance_first": "請先使用聯盟操作創建一個聯盟",
    "select_alliance_to_edit": "選擇聯盟後可以修改名稱和控制間隔",
    "warning_delete_removes_data": "警告：刪除聯盟將移除所有相關數據",
    "alliance_settings_saved": "聯盟設定已成功儲存"
}

# 日誌相關（開發者用，保留中文或英文皆可）
LOG = {
    "global_listener_detected": "[全域監聽器] 檢測到禮品碼: {code} 在頻道 {channel}",
    "global_listener_cog_not_found": "[全域監聽器] GiftOperations cog 未找到",
    "global_listener_added_to_queue": "[全域監聽器] 禮品碼 {code} 已加入驗證佇列",
    "global_listener_error": "[全域監聽器] Error sending confirmation: {error}"
}
