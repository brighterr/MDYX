# json2json.py
import json
from typing import List, Dict
from datetime import datetime
from model import DeepseekClient

class JsonProcessor:
    def __init__(self, api_key: str, debug_mode=True, log_timestamp=True):
        self.client = DeepseekClient(api_key)
        self.debug_mode = debug_mode
        self.log_timestamp = log_timestamp
        
    def _print_debug(self, message: str):
        """调试信息输出"""
        prefix = f"[{datetime.now().strftime('%H:%M:%S')}] " if self.log_timestamp else ""
        print(f"{prefix}{message}")

    def process(self, input_path: str, output_path: str):
        """处理JSON文件主流程"""
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data: List[Dict] = json.load(f)
                if self.debug_mode:
                    self._print_debug(f"📂 已加载文件：{input_path}")
                    self._print_debug(f"📊 总记录数：{len(data)} 条")
        except Exception as e:
            self._print_debug(f"❌ 文件读取失败：{str(e)}")
            return

        start_time = datetime.now()
        success, errors = 0, 0

        for idx, item in enumerate(data, 1):
            try:
                if self.debug_mode:
                    title_preview = item['title'][:30].replace('\n', ' ') + "..."
                    self._print_debug(f"🔄 处理中 [{idx}/{len(data)}] | {title_preview}")

                classification = self.client.classify_content(
                    title=item["title"],
                    text=item["text"]
                )
                item.update(classification)
                success += 1
                
            except Exception as e:
                errors += 1
                if self.debug_mode:
                    self._print_debug(f"⚠️ 条目处理失败 [{idx}] - {type(e).__name__}: {str(e)}")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            if self.debug_mode:
                duration = (datetime.now() - start_time).total_seconds()
                self._print_debug(
                    f"⏱️ 总耗时：{duration:.1f}秒 | "
                    f"✅ 成功：{success}条 | "
                    f"❌ 失败：{errors}条 | "
                    f"💾 保存路径：{output_path}"
                )
                
        except Exception as e:
            self._print_debug(f"❌ 文件保存失败：{str(e)}")

if __name__ == "__main__":
    processor = JsonProcessor(
        api_key="sk-wIWKVhO72EqAvHtgNInrEa6cv6RzrsFq9spbKXN7P7Tbxqr4",
        debug_mode=True
    )
    processor.process("think_tank.json", "output.json")