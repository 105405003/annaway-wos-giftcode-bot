#!/usr/bin/env python3
"""打包更新文件用於瀏覽器上傳"""

import os
import zipfile
from datetime import datetime

# 需要打包的文件
files_to_pack = [
    'cogs/gift_operations.py',
    'cogs/alliance_member_operations.py',
    'check_managers.py',
    'FINAL_UPDATE_20251009.md'
]

# 創建時間戳
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'update_files_{timestamp}.zip'

print(f'[打包] 開始打包更新文件...')
print(f'[打包] 輸出檔案: {output_file}')
print()

# 創建 zip 文件
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_path in files_to_pack:
        if os.path.exists(file_path):
            zipf.write(file_path, file_path)
            file_size = os.path.getsize(file_path)
            print(f'  OK: {file_path} ({file_size:,} bytes)')
        else:
            print(f'  SKIP: {file_path} (file not found)')

# 顯示結果
zip_size = os.path.getsize(output_file)
print()
print(f'[完成] 打包完成！')
print(f'[完成] 檔案: {output_file}')
print(f'[完成] 大小: {zip_size:,} bytes ({zip_size / 1024 / 1024:.2f} MB)')
print()
print('=' * 70)
print('UPLOAD STEPS:')
print('=' * 70)
print()
print('1. 開啟 Google Cloud Console')
print('   https://console.cloud.google.com/')
print()
print('2. 導航到 Compute Engine > VM 執行個體')
print()
print('3. 點擊 wos-giftcode-bot 的 SSH 按鈕')
print()
print('4. 在 SSH 視窗右上角點擊「設定」圖示 -> 上傳檔案')
print()
print(f'5. 選擇 {output_file}')
print()
print('6. 在 SSH 視窗執行:')
print()
print('   cd ~')
print('   unzip -o update_files_*.zip')
print('   cd wos_bot')
print('   source bot_venv/bin/activate')
print('   pip install pytz')
print('   pkill -f "python.*main.py"')
print('   sleep 2')
print('   nohup python main.py > bot.log 2>&1 &')
print('   tail -f bot.log')
print()
print('7. 確認看到自動重試日誌後按 Ctrl+C')
print()
print('8. 執行診斷:')
print()
print('   cd ~')
print('   source wos_bot/bot_venv/bin/activate')
print('   python check_managers.py')
print()
print('=' * 70)

