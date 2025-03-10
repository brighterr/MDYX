import datetime
import os

# 设置数据文件夹路径
data_folder2 = '/home/aicourse/ai_course/ADHD/data/raw'
data_folder1 = '/home/aicourse/ai_course/allweibodata'

# 设置日期范围
start_date = datetime.date(2024, 7, 1)
end_date = datetime.date(2024, 10, 31)

# 定义要检查的关键字列表
keywords = ['ADHD','adhd']  # 可以根据需要添加更多关键字
# no 儿童 娃 小孩 孩子 
# 字数太小的不要20字
# no 吴宣仪 

# 遍历日期范围
for single_date in (start_date + datetime.timedelta(n) for n in range((end_date - start_date).days + 1)):
    # 构建输入文件名
    input_file = os.path.join(data_folder1, f"weibo_freshdata.{single_date:%Y-%m-%d}")
    
    # 构建输出文件名
    output_file = os.path.join(data_folder2, f"ADHDdata_{single_date:%Y-%m-%d}")
    
    # 检查文件是否存在
    if os.path.exists(input_file):
        try:
            # 打开输入文件和输出文件
            with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
                # 逐行读取输入文件
                for line in infile:
                    # 检查当前行是否包含任意一个关键字
                    if any(keyword in line for keyword in keywords):
                        # 如果包含，则将这一行写入输出文件
                        outfile.write(line)
            print(f"已处理文件：{input_file}，输出文件：{output_file}")
        except Exception as e:
            print(f"处理文件 {input_file} 时出错: {e}")
    else:
        print(f"文件不存在：{input_file}")
        
# 这是extract.py


