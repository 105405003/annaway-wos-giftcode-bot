import zipfile
from datetime import datetime
import os

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
output = f'hotfix_gift_ops_{ts}.zip'

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('cogs/gift_operations.py')

size = os.path.getsize(output)
print(f'\nHotfix package created: {output} ({size:,} bytes)\n')
print('Upload to VM and run:')
print(f'  cd ~')
print(f'  unzip -o {output}')
print(f'  cp cogs/gift_operations.py wos_bot/cogs/')
print(f'  cd wos_bot')
print(f'  pkill -f "python.*main.py"')
print(f'  sleep 2')
print(f'  nohup python main.py > bot.log 2>&1 &')
print(f'  sleep 5')
print(f'  tail -30 bot.log')
print()




