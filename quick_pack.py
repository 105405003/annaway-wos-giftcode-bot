#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速打包腳本"""

import shutil
import datetime
import os

# 生成時間戳
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
output_name = f'wos_bot_batch_add_{timestamp}'
output_file = f'{output_name}.zip'

# 要打包的文件和目錄
items_to_pack = [
    'main.py',
    'requirements.txt',
    'bot_config.env.example',
    'i18n_manager.py',
    'i18n_config.py',
    'permission_manager.py',
    'cogs',
    'i18n',
    'models',
    'fonts',
    'README.md',
    'PERMISSION_SYSTEM.md',
    'FEATURE_STATUS.md',
]

print("[PACK] Starting...")

# 創建臨時目錄
temp_dir = 'temp_deploy'
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# 複製文件
for item in items_to_pack:
    if os.path.exists(item):
        if os.path.isdir(item):
            shutil.copytree(item, os.path.join(temp_dir, item), 
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            shutil.copy2(item, temp_dir)
        print(f"  OK: {item}")
    else:
        print(f"  SKIP: {item} (not found)")

# 打包
print("\n[COMPRESS] Compressing...")
shutil.make_archive(output_name, 'zip', temp_dir)

# 清理
shutil.rmtree(temp_dir)

# 顯示結果
size_mb = round(os.path.getsize(output_file) / 1024 / 1024, 2)
print(f"\n[SUCCESS] Pack completed!")
print(f"File: {output_file}")
print(f"Size: {size_mb} MB")
print(f"\nUpload to VM:")
print(f"  gcloud compute scp {output_file} wos-giftcode-bot:~/ --zone=asia-east1-b")

