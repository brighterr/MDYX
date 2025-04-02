import json

def remove_duplicates_by_url(json_path):
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 使用字典来去重，以url为键
    unique_entries = {}
    for entry in data:
        url = entry['url']
        if url not in unique_entries:
            unique_entries[url] = entry
    
    # 将字典值转换回列表
    deduplicated_data = list(unique_entries.values())
    
    # 写回文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(deduplicated_data, f, ensure_ascii=False, indent=2)
    
    print(f"去重完成。原始条目数: {len(data)}, 去重后条目数: {len(deduplicated_data)}")

# 使用你的文件路径
json_path = "/home/zhangyuheng/GTTS/0402/think_tank.json"
remove_duplicates_by_url(json_path)