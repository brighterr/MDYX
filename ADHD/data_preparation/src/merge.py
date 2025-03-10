import csv
import os

# 定义输入文件夹和输出文件
data_folder2 = '/home/aicourse/ai_course/ADHD/data/processed'
output_file = '/home/aicourse/ai_course/ADHD/data/merged/summary.csv'

def merge_csv_files(input_folder, output_file):
    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    
    # 确保有CSV文件可以合并
    if not csv_files:
        print("没有找到CSV文件。")
        return
    
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = None
        
        # 遍历每个CSV文件
        for csv_file in csv_files:
            input_file = os.path.join(input_folder, csv_file)
            
            with open(input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                
                # 如果是第一个文件，写入表头
                if writer is None:
                    fieldnames = reader.fieldnames
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writeheader()
                
                # 写入每一行数据
                for row in reader:
                    writer.writerow(row)
            
            print(f"已合并文件：{input_file}")
    
    print(f"所有文件已合并到：{output_file}")

# 调用合并函数
merge_csv_files(data_folder2, output_file)