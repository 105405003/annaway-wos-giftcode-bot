#!/usr/bin/env python3
"""修復 main.py 的縮排問題"""

# 讀取文件
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修復第 347-349 行（索引 346-348）
# 這些行應該在 if 語句內部，使用 2 個縮排層級（8 個空格）
lines[346] = '        print("! Warning: requirements.txt not found")\n'
lines[347] = '        print("! Please ensure requirements.txt exists in the project directory")\n'
lines[348] = '        return False\n'

# 寫回文件
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed main.py indentation")
print("   - Line 347: 8 spaces (inside if block)")
print("   - Line 348: 8 spaces (inside if block)")
print("   - Line 349: 8 spaces (inside if block)")

# Verify syntax
import py_compile
try:
    py_compile.compile('main.py', doraise=True)
    print("Syntax check passed!")
except SyntaxError as e:
    print(f"Syntax error: {e}")

