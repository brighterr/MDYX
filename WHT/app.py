from flask import Flask, request, render_template, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import uuid

# 设置中文字体
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
# plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

app = Flask(__name__)

# 设置图片保存目录
UPLOAD_FOLDER = './static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 加载 Excel 文件
df = pd.read_excel('总表.xlsx')

# 确保日期列是日期格式
df['日期'] = pd.to_datetime(df['日期'])

def generate_plot(keyword):
    # 筛选出包含该热搜词条的数据
    keyword_data = df[df['热搜词条'].str.contains(keyword, na=False)]
    
    # 如果没有找到数据，返回 None
    if keyword_data.empty:
        return None
    
    # 按日期排序
    keyword_data = keyword_data.sort_values(by='日期')
    
    # 重置索引以便于绘图
    keyword_data.reset_index(inplace=True, drop=True)
    
    # 创建可视化
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=keyword_data, x='日期', y='热度', marker='o')
    
    # 设置标题和标签
    #plt.title(f"Hot Trends for: {keyword}", fontsize=16)  # 图形标题
    plt.title(f"Hot Trends", fontsize=16)  # 图形标题
    plt.xlabel("Date", fontsize=14)  # x 轴标签
    plt.ylabel("Hot", fontsize=14)  # y 轴标签
    
    # 选择均匀分布的 x 轴刻度
    num_xticks = min(10, len(keyword_data))  # 确保不超过10个刻度
    xticks_indices = np.linspace(0, len(keyword_data) - 1, num_xticks).astype(int)  # 选择均匀分布的索引
    xticks = keyword_data['日期'].iloc[xticks_indices]  # 获取对应的日期
    plt.xticks(xticks, rotation=45)  # 设置刻度并旋转
    
    plt.grid()
    plt.tight_layout()
    
    # 生成唯一的文件名
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # 保存图表到文件
    plt.savefig(filepath)
    plt.close()
    
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取用户输入的查询条件
        target_keyword = request.form['query']
        
        # 生成图表
        filename = generate_plot(target_keyword)
        
        if filename is None:
            return render_template('index.html', message="No data found for the given query.")
        
        # 返回图片的 URL
        return render_template('result.html', image_url=filename)
    
    # 如果是 GET 请求，返回查询表单
    return render_template('index.html')

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6016, debug=False)