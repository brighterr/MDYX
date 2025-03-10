import pandas as pd
import os

# 定义关键词列表
keywords = ['ADHD', 'adhd']
exceptwords = ['儿童', '娃', '小孩', '孩子','吴宣仪','丁程鑫','KAIYA_ADHD版','@ADHD']

# 读取 CSV 文件
input_file = '/home/aicourse/ai_course/ADHD/data/merged/summary.csv'
output_file = '/home/aicourse/ai_course/ADHD/data/selected/summary.csv'
df = pd.read_csv(input_file)

# 筛选包含关键词的行
filtered_df = df[
    df['weibo_content'].str.contains('|'.join(keywords), case=False, na=False)
]

# 排除包含 exceptwords 的行
filtered_df = filtered_df[
    ~filtered_df['weibo_content'].str.contains('|'.join(exceptwords), case=False, na=False)
]

# 只保留 weibo_content 字数大于 20 的行
filtered_df = filtered_df[filtered_df['weibo_content'].str.len() > 20]

# 如果输出文件存在，则先删除
if os.path.exists(output_file):
    os.remove(output_file)

# 保存筛选后的数据
filtered_df.to_csv(output_file, index=False, encoding='utf-8')

print(f"筛选完成，结果已保存到 {output_file}")
