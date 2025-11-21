#!/usr/bin/env python3
# 2CAPTCHA Service for WOS Discord Bot
# 當OCR測試四次未通過時，使用2CAPTCHA服務

import aiohttp
import asyncio
import logging
import time
from typing import Optional, Tuple

class TwoCaptchaService:
    def __init__(self, api_key: str):
        """
        初始化2CAPTCHA服務
        
        Args:
            api_key: 2CAPTCHA API密鑰
        """
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
        self.logger = logging.getLogger("2captcha_service")
        
        # 設定日誌
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def solve_captcha(self, image_base64: str, timeout: int = 300) -> Tuple[bool, Optional[str], str]:
        """
        使用2CAPTCHA解碼驗證碼
        
        Args:
            image_base64: Base64編碼的驗證碼圖片
            timeout: 超時時間（秒）
            
        Returns:
            Tuple[成功, 解碼結果, 錯誤訊息]
        """
        try:
            # 1. 提交驗證碼到2CAPTCHA
            captcha_id = await self._submit_captcha(image_base64)
            if not captcha_id:
                return False, None, "無法提交驗證碼到2CAPTCHA"
            
            self.logger.info(f"驗證碼已提交到2CAPTCHA，ID: {captcha_id}")
            
            # 2. 等待解碼結果
            result = await self._wait_for_result(captcha_id, timeout)
            if result:
                self.logger.info(f"2CAPTCHA解碼成功: {result}")
                return True, result, ""
            else:
                return False, None, "2CAPTCHA解碼超時或失敗"
                
        except Exception as e:
            self.logger.exception(f"2CAPTCHA解碼過程中發生錯誤: {e}")
            return False, None, f"2CAPTCHA解碼錯誤: {str(e)}"
    
    async def _submit_captcha(self, image_base64: str) -> Optional[str]:
        """提交驗證碼到2CAPTCHA"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'key': self.api_key,
                    'method': 'base64',
                    'body': image_base64,
                    'json': 1
                }
                
                async with session.post(f"{self.base_url}/in.php", data=data) as response:
                    result = await response.json()
                    
                    if result.get('status') == 1:
                        return result.get('request')
                    else:
                        self.logger.error(f"2CAPTCHA提交失敗: {result.get('error_text', '未知錯誤')}")
                        return None
                        
        except Exception as e:
            self.logger.exception(f"提交驗證碼到2CAPTCHA時發生錯誤: {e}")
            return None
    
    async def _wait_for_result(self, captcha_id: str, timeout: int) -> Optional[str]:
        """等待2CAPTCHA解碼結果"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    }
                    
                    async with session.get(f"{self.base_url}/res.php", params=params) as response:
                        result = await response.json()
                        
                        if result.get('status') == 1:
                            return result.get('request')
                        elif result.get('error_text') == 'CAPCHA_NOT_READY':
                            # 還未解碼完成，等待5秒後重試
                            await asyncio.sleep(5)
                            continue
                        else:
                            self.logger.error(f"2CAPTCHA解碼失敗: {result.get('error_text', '未知錯誤')}")
                            return None
                            
            except Exception as e:
                self.logger.exception(f"等待2CAPTCHA結果時發生錯誤: {e}")
                await asyncio.sleep(5)
                continue
        
        self.logger.warning(f"2CAPTCHA解碼超時，ID: {captcha_id}")
        return None
    
    async def get_balance(self) -> Tuple[bool, float, str]:
        """獲取2CAPTCHA帳戶餘額"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': self.api_key,
                    'action': 'getbalance',
                    'json': 1
                }
                
                async with session.get(f"{self.base_url}/res.php", params=params) as response:
                    result = await response.json()
                    
                    if result.get('status') == 1:
                        balance = float(result.get('request', 0))
                        return True, balance, ""
                    else:
                        error_msg = result.get('error_text', '未知錯誤')
                        return False, 0.0, error_msg
                        
        except Exception as e:
            self.logger.exception(f"獲取2CAPTCHA餘額時發生錯誤: {e}")
            return False, 0.0, f"獲取餘額錯誤: {str(e)}"
    
    def is_configured(self) -> bool:
        """檢查2CAPTCHA是否已配置"""
        return bool(self.api_key and self.api_key.strip())

# 使用範例
async def example_usage():
    """使用範例"""
    # 初始化2CAPTCHA服務
    captcha_service = TwoCaptchaService("YOUR_2CAPTCHA_API_KEY")
    
    # 檢查是否已配置
    if not captcha_service.is_configured():
        print("2CAPTCHA未配置，請設定API密鑰")
        return
    
    # 獲取餘額
    success, balance, error = await captcha_service.get_balance()
    if success:
        print(f"2CAPTCHA餘額: ${balance:.2f}")
    else:
        print(f"獲取餘額失敗: {error}")
    
    # 解碼驗證碼（需要實際的base64圖片）
    # success, result, error = await captcha_service.solve_captcha("base64_image_data")
    # if success:
    #     print(f"解碼結果: {result}")
    # else:
    #     print(f"解碼失敗: {error}")

if __name__ == "__main__":
    asyncio.run(example_usage())

