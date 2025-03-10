import pandas as pd
import os
# 定义输入文件路径
input_file = '/home/aicourse/ai_course/ADHD/data/selected/summary.csv'
output_file = '/home/aicourse/ai_course/ADHD/data/sample/ADHD共同标注的100条.xlsx'
# 读取CSV文件
df = pd.read_csv(input_file)
# 随机抽取200行
sampled_df = df.sample(n=100, random_state=57)  # random_state 保证结果可复现

# 提取 weibo_content 列
df_filtered = sampled_df[['weibo_content', 'is_retweet', 'r_weibo_content', 'id']].copy()
#df_filtered.insert(0, 'reason', '')
df_filtered.insert(0, 'tag', '')
weibo_contents = df_filtered

# 保存结果到新的Excel文件
if os.path.exists(output_file):
    os.remove(output_file)
weibo_contents.to_excel(output_file, index=False)

print(f"随机筛选完成，结果已保存到 {output_file}")
