import requests
import json

class TravelDeepSeekAPI:
    def __init__(self, deepseek_api_key: str):
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_base_url = "https://api.deepseek.com/chat/completions"
        self.deepseek_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }

    def generate_content(self, messages: list, temperature: float = 0.7) -> str:
        """支持对话历史的通用生成方法"""
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }

        try:
            response = requests.post(
                url=self.deepseek_base_url,
                headers=self.deepseek_headers,
                data=json.dumps(payload),
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"❌ 内容生成失败：{str(e)}"