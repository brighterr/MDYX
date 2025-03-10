import time
import concurrent.futures
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from db_access import init_database, insert_message
from openai import OpenAI
def plot_results():
    """生成对比可视化结果图（符合顶会论文格式）"""
    # 读取两个模型的测试结果
    df_localqwen = pd.read_csv("localqwen_batch_test_results.csv")
    df_gpt4o = pd.read_csv("gpt4o_batch_test_results.csv")
    
    # 创建专业学术图表
    plt.figure(figsize=(8, 6), dpi=300)
    #plt.rcParams['font.family'] = 'Times New Roman'  # 使用学术标准字体
    
    # 绘制双曲线（调整线条参数符合出版要求）
    plt.plot(df_localqwen["concurrent_users"], df_localqwen["avg_response_time"], 
        marker='s', markersize=8, linestyle='--', linewidth=2, color='gold', 
        label='Local Qwen2.5-7B-Instruct')
    plt.plot(df_gpt4o["concurrent_users"], df_gpt4o["avg_response_time"], 
        marker='o', markersize=8, linestyle='-', linewidth=2, color='royalblue',
        label='API GPT-4o')
    
    # 设置坐标轴和标题
    plt.xlabel("Concurrent Users", fontsize=14, labelpad=10)
    plt.ylabel("Average Response Time (s)", fontsize=14, labelpad=10)
    plt.title("Concurrency Testing", fontsize=16, pad=20)
    
    # 设置刻度范围和样式
    max_users = max(df_gpt4o["concurrent_users"].max(), df_localqwen["concurrent_users"].max())
    plt.xticks(range(5, 55, 5), fontsize=12)
    plt.yticks(fontsize=12)
    plt.ylim(0, max(df_gpt4o["avg_response_time"].max(), df_localqwen["avg_response_time"].max())*1.1)
    
    # 添加辅助元素
    plt.grid(True, linestyle=':', color='gray', alpha=0.6)
    plt.legend(fontsize=12, loc='upper left', framealpha=0.9)
    
    # 优化布局并保存
    plt.tight_layout(pad=2.0)
    plt.savefig("concurrency_testing.png", dpi=600, bbox_inches='tight')  # 更高分辨率
    plt.close()  # 避免内存泄漏
    
    print("可视化结果已保存为 model_comparison.png（符合顶会出版要求）")
    
if __name__ == "__main__":
    plot_results()

