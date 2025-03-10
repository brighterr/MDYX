import pandas as pd
import os

# 定义输入文件路径和输出文件夹
input_file = '/home/aicourse/ai_course/ADHD/data/selected/summary.csv'
output_folder = '/home/aicourse/ai_course/ADHD/data/set'

# 确保输出目录存在
os.makedirs(output_folder, exist_ok=True)

# 读取 CSV 文件
df = pd.read_csv(input_file)

# 选取需要的列，并增加一个空的 `tag` 列
df_filtered = df[['weibo_content', 'is_retweet', 'r_weibo_content', 'id']].copy()
df_filtered.insert(0, 'tag', '')

# 取前 2000 条数据
df_filtered = df_filtered.iloc[:2000]

# 分成 4 组，每组 500 条
batch_size = 500
for i in range(4):
    start_idx = i * batch_size
    end_idx = start_idx + batch_size
    df_batch = df_filtered.iloc[start_idx:end_idx]

    # 生成 Excel 文件名
    output_file = os.path.join(output_folder, f'ADHD_set0{i+1}.xlsx')

    # 保存到 Excel
    df_batch.to_excel(output_file, index=False)

    print(f"已保存: {output_file}")

print("所有数据集处理完成！")
