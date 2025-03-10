import json
import datetime
import os

# 定义输入和输出文件名
#input_file = '/home/aicourse/ai_course/ADHD/data/ADHDdata_2024-07-01'
#output_file = '/home/aicourse/ai_course/ADHD/data/ADHDdata_2024-07-01.json'

# 设置数据文件夹路径
data_folder2 = '/home/aicourse/ai_course/ADHD/data/mid'
data_folder1 = '/home/aicourse/ai_course/ADHD/data/raw'

# 设置日期范围
start_date = datetime.date(2024, 7, 1)
end_date = datetime.date(2024, 10, 31)

def raw2json(input_file,output_file):
    weibo_data = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
        # 去除行开头的数字和制表符
            json_str = line.split('\t', 1)[1]  # 只保留制表符后的部分
        # 解析 JSON 对象
            try:
                weibo_json = json.loads(json_str)
                weibo_data.append(weibo_json)
            except json.JSONDecodeError as e:
                print(f"解析错误: {e}，行内容: {json_str}")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(weibo_data, outfile, ensure_ascii=False, indent=4)
        
for single_date in (start_date + datetime.timedelta(n) for n in range((end_date - start_date).days + 1)):
    # 构建输入文件名
    input_file = os.path.join(data_folder1, f"ADHDdata_{single_date:%Y-%m-%d}")
    
    # 构建输出文件名
    output_file = os.path.join(data_folder2, f"weibo_freshdata_{single_date:%Y-%m-%d}.json")
    
    # 检查文件是否存在
    if os.path.exists(input_file):
        try:
            raw2json(input_file,output_file)
            print(f"已处理文件：{input_file}，输出文件：{output_file}")
        except Exception as e:
            print(f"处理文件 {input_file} 时出错: {e}")





#这是raw2json.py


