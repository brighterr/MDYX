import json
import csv
import datetime
import os

data_folder2 = '/home/aicourse/ai_course/ADHD/data/processed'
data_folder1 = '/home/aicourse/ai_course/ADHD/data/mid'
start_date = datetime.date(2024,7,1)
end_date = datetime.date(2024,10,31)

# 定义输入和输出文件名
#input_file = '/home/aicourse/ai_course/ADHD/data/ADHDdata_2024-07-01.json'
#output_file = '/home/aicourse/ai_course/ADHD/data/ADHDdata_2024-07-01.csv'

def json2csv(input_file,output_file):
    # 读取JSON数据
    with open(input_file, 'r', encoding='utf-8') as infile:
        weibo_data = json.load(infile)
    # 获取CSV字段名
    fieldnames = weibo_data[0].keys()  # 假设所有JSON对象的结构相同
    # 写入CSV文件
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()  # 写入表头
        for weibo in weibo_data:
            writer.writerow(weibo)  # 写入每一行
            
for single_date in (start_date + datetime.timedelta(n) for n in range((end_date - start_date).days + 1)):
    # 构建输入文件名
    input_file = os.path.join(data_folder1, f"weibo_freshdata_{single_date:%Y-%m-%d}.json")
    
    # 构建输出文件名
    output_file = os.path.join(data_folder2, f"weibo_freshdata_{single_date:%Y-%m-%d}.csv")
    
    # 检查文件是否存在
    if os.path.exists(input_file):
        try:
            json2csv(input_file,output_file)
            print(f"已处理文件：{input_file}，输出文件：{output_file}")
        except Exception as e:
            print(f"处理文件 {input_file} 时出错: {e}")
            
# 这是json2csv.py

