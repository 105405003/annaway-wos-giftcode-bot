# Annaway Fork Notice

## 關於此專案

這個儲存庫是 [Reloisback/Whiteout-Survival-Discord-Bot](https://github.com/Reloisback/Whiteout-Survival-Discord-Bot) 的非官方 **Annaway Studio** 客製化分支版本。

## 原始專案授權

核心概念和大部分原始程式碼來自 **Reloisback**，原始專案的授權條款（`LICENSE` 檔案）適用於本專案的基礎部分。

**重要**：`LICENSE` 檔案屬於原作者，不得修改或移除。

## Annaway Studio 的修改

此分支版本由 Annaway Studio 維護，並加入以下額外功能：

### 🔐 多伺服器隔離 (Multi-Guild Isolation)
- 每個 Discord 伺服器的資料完全獨立
- 透過 `discord_server_id` 欄位實現資料隔離
- 不同伺服器之間的聯盟、成員、禮包碼資料互不干擾

### 👥 角色權限系統 (Role-Based Permissions)
- 新增 `Annaway_Admin` 角色 - 完整管理權限
- 新增 `Annaway_Manager` 角色 - 標準管理權限
- 統一的權限檢查裝飾器（`@requires_annaway_role()`）
- 詳見 `utils/permissions.py` 和 `PERMISSION_SYSTEM.md`

### 📚 繁體中文化 (Traditional Chinese i18n)
- 完整的繁體中文介面
- 可擴展的多語言支援框架
- 詳見 `i18n/` 目錄

### 🎨 使用者體驗改善 (UX Improvements)
- 統一的日誌格式化 (`utils/log_format.py`)
- 美觀的 Discord Embed 樣式 (`utils/embeds.py`)
- 一致的錯誤訊息 (`utils/messages.py`)
- 啟動時的 ASCII Banner (`utils/banner.py`)

### 📦 部署優化
- 移除自動更新機制（避免意外覆蓋客製化內容）
- 簡化的依賴管理
- Docker 支援
- Systemd 服務範例

### 📖 文件完善
- Annaway 專屬的 README (`README_ANNAWAY.md`)
- 詳細的權限系統文件 (`PERMISSION_SYSTEM.md`)
- 快速開始指南 (`QUICK_START.md`)
- 實作狀態追蹤

## 授權條款

### 原始專案部分
原始專案的程式碼和概念受 `LICENSE` 檔案約束，該檔案由 Reloisback 制定。

主要限制：
- ✅ 允許複製和修改
- ✅ 允許個人和教育用途
- ✅ 允許開源專案使用
- ❌ 商業使用需要書面許可
- ❌ 禁止在特定 Discord 伺服器販售
- ❌ 禁止在免費發行平台進行付費分發

### Annaway 修改部分
Annaway Studio 的額外修改和功能同樣遵循原始授權條款。

**所有使用者必須遵守原始 `LICENSE` 檔案中的條款。**

## 商業使用

如需商業使用，請直接聯絡原作者：
- Email: usabsz@gmail.com
- 原始專案：https://github.com/Reloisback/Whiteout-Survival-Discord-Bot

## 致謝

### 原作者
- **Reloisback** - 原始專案的創作者和主要維護者
- GitHub: https://github.com/Reloisback/Whiteout-Survival-Discord-Bot

### Annaway Studio
- 客製化功能開發和維護
- 多伺服器架構設計
- 使用者體驗優化

## 支援和貢獻

### 原始專案
如果您遇到與原始功能相關的問題，建議參考原始專案的文件或社群。

### Annaway 分支
如果您遇到與 Annaway 特定功能相關的問題（多伺服器隔離、權限系統等），請透過以下方式聯絡：
- 查看專案文件（`DOCUMENTATION_INDEX.md`）
- 聯絡 Annaway Studio 技術支援

## 重要提醒

1. **不要販售此軟體** - 違反原始授權條款
2. **保留授權聲明** - 所有衍生作品必須保留 `LICENSE` 和此聲明
3. **標示修改內容** - 任何修改必須明確標示為衍生作品
4. **尊重原作者** - 承認原始軟體和作者

---

**最後更新**: 2025-11-27  
**Annaway 分支版本**: 1.0.0-annaway

