# model.py
import json
import requests
import urllib3
from typing import Dict
from datetime import datetime
from prompt import get_classification_prompt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DeepseekClient:
    def __init__(self, api_key: str, base_url: str = "https://api2.aigcbest.top/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.classification_prompt = get_classification_prompt()
    
    def chat_and_response(self, messages: list, **kwargs) -> Dict:
        """通用对话接口"""
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            verify=False,
            timeout=60
        )
        response.raise_for_status()
        return response.json()

    def classify_content(self, title: str, text: str, max_retries=3) -> Dict:
        """分类专用接口"""
        messages = [
            {"role": "system", "content": self.classification_prompt},
            {"role": "user", "content": f"标题：{title}\n正文：{text[:3000]}"}
        ]
        
        for attempt in range(max_retries):
            try:
                result = self.chat_and_response(messages)
                response = json.loads(result["choices"][0]["message"]["content"])
                
                if not all(key in response for key in ["World", "Topic", "Spotlight"]):
                    raise ValueError("响应缺少必要字段")
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return {"World": "Unknown", "Topic": "Unknown", "Spotlight": "none"}