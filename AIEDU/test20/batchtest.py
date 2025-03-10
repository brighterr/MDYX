import requests
import time
import concurrent.futures
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from db_access import init_database, insert_message

# API配置
API_URL = "http://10.77.110.129:8000/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}
MODEL = "/home/zhangyuheng/.cache/modelscope/hub/Qwen/Qwen2.5-7B-Instruct"

# 测试配置
TEST_MESSAGE = "品牌简介 Canva可画是全球领先的视觉传播平台，2013年诞生于悉尼，2018年进入中国市场。秉承“赋予世界设计的力量”的使命，Canva可画为用户提供AI赋能的零门槛设计编辑工具(网页端/App/桌面端/小程序)，海量免费精美设计模板和千万级版权素材内容。使不具备任何专业设计技能的“设计小白”，只需简单的拖拽和编辑，也能轻松做出想要的好设计。 每月2亿来自全球190多个国家的活跃用户通过Canva可画，创造工作和生活中使用的设计。至今他们已经在Canva可画上发布了超过300亿个设计，现在平均每天就有3850万个设计被创建。无数关于设计的美好故事正在发生，被科技创新驱动的设计，也在更多人的生活中折射出巨大能量。 品牌使命 赋予世界设计的力量 (Empower the world to design) 品牌价值 人性化 Human 赋能感 Empowering 启发性 Inspiring品牌内涵 赋能每个人 Empower everyone 创作任何设计 Design anything 使用各类素材 Every Ingredient 使用每种语言 In every language 在任何设备上 On every device Canva可画致力于追求设计平权，我们相信每个人都应该享有平等的设计机会。通过把分散割裂的设计生态汇集到一个平台上，并使它对全世界用户都简单易用、触手可及，让精彩设计随时随地。品牌目标群体 Canva可画是一款人人可用的零门槛AI设计工具，本次命题创作可围绕以下较为集中的用户群体展开： ● 在校学生与老师 ● 年轻职场人 ● 自媒体创作者 ● 中小企业主主推功能 Canva可画魔力工作室——一站式AI创作套件，从素材生成、图片编辑，到文案润色，为视觉创作的各个环节注入“AI魔力”，辅助没有设计基础的用户更简单、高效、个性化地完成各类设计需求。主要功能包括： AI生图：把想象中的图画“变现” 使用AI生图，见证你输入的文字变成想象中的图片或插画，完美适配当前的设计。用AI的魔力打破图库素材局限，可自由选择极简风、长曝光、3D模型、概念艺术等20+种图片插画风格；快速生成用于海报设计、课件配图、脚本示意图、绘本故事等各个场景需求的视觉素材。 AI写作：简单指令快速成文 写文档、出文案、想点子没有头绪？只需描述主题和要求，如“为蓝牙耳机写5条营销策略”，AI写作就会立即帮你生成项目方案、宣传文案、多角度卖点、会议日程等多种类型的内容初稿，让出稿过程从容不迫。在文档、海报、演示文稿等任一Canva可画创作场景中，都可以随时调用文字助手和你一起创作。 AI改图：打字就能改图，改色换装改一切 AI改图可以轻松对照片进行修改替换。涂抹需要修改的地方，然后输入想要替换的内容，照片就能快速“魔法变身”。比如把一头黑色头发改成金色，把穿着的旗袍改成公主裙，或者把海报照片上的面包改成汉堡，都能在1分钟之内完成。广告主题 以“所想皆可画”为主题，推广Canva可画，广告内容中须包含并展示Canva可画魔力工作室相关产品功能，请结合上述产品主推功能及具体的使用场景（如“海报制作”、“PPT制作”等），在目标群体中推广Canva可画，吸引目标群体使用产品。围绕广告主题，以开学季为推广的时间节点，在高校策划推广Canva可画校园营销方案。吸引高校师生了解并使用Canva可画，方案中须展示介绍Canva可画魔力工作室产品功能，要求有明确的费用预算及投入产出比测算，执行性强。活动预算不超过200万元人民币。推广方案须包含传播目标、核心创意阐释、活动前期预热节奏及上线时间线安排、传播策略、传播渠道、具体活动内容等部分。"
TIMEOUT = 300  # 超时时间
CONCURRENT_USER_COUNTS = list(range(5, 55, 5))  # 5, 10, 15, ..., 50


def build_request_data():
    """构建请求数据模板"""
    return {
        "model": MODEL,
        "messages": [{"role": "user", "content": TEST_MESSAGE}],
        "temperature": 0.7,
        "top_p": 0.8,
        "repetition_penalty": 1.05,
        "max_tokens": 512,
    }


def send_request(user_id: int):
    """发送单个请求并返回结果"""
    start_time = time.time()
    status = "success"
    error = ""
    response_length = 0
    username = f"stress_test_{user_id}"
    
    try:
        insert_message(username, "user", TEST_MESSAGE)
        response = requests.post(API_URL, headers=HEADERS, json=build_request_data(), timeout=TIMEOUT)
        response_time = time.time() - start_time

        if response.status_code == 200:
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            response_length = len(content)
            insert_message(username, "assistant", content)
        else:
            status = f"error_{response.status_code}"
            error = response.text[:200]
            insert_message(username, "assistant", f"HTTP Error {response.status_code}: {error}")
    except Exception as e:
        response_time = time.time() - start_time
        status = "failed"
        error = str(e)[:200]
        insert_message(username, "assistant", f"Request Failed: {error}")
    
    return {
        "user_id": user_id,
        "status": status,
        "response_time": round(response_time, 2),
        "error": error,
        "response_length": response_length,
    }


def run_batch_test():
    """批量执行不同并发用户数的测试"""
    init_database()
    all_results = []
    summary_results = []
    
    for concurrent_users in CONCURRENT_USER_COUNTS:
        print(f"\n开始测试并发用户数：{concurrent_users}")
        stats = defaultdict(int)
        results = []
        total_time = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            start = time.time()
            futures = [executor.submit(send_request, i) for i in range(concurrent_users)]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                stats[result["status"]] += 1
                total_time += result["response_time"]

        total_test_time = time.time() - start
        success_count = stats.get("success", 0)
        avg_time = round(total_time / success_count, 2) if success_count > 0 else None
        
        print(f"并发数 {concurrent_users}: 平均响应时间 {avg_time}s，成功请求 {success_count}/{concurrent_users}")
        summary_results.append({"concurrent_users": concurrent_users, "avg_response_time": avg_time})
        all_results.extend(results)
    
    # 保存详细结果
    df_all = pd.DataFrame(all_results)
    df_all.to_csv("stress_test_results.csv", index=False)
    
    # 保存汇总结果
    df_summary = pd.DataFrame(summary_results)
    df_summary.to_csv("batch_test_results.csv", index=False)
    
    print("\n测试完成，详细结果保存在 stress_test_results.csv，汇总结果保存在 batch_test_results.csv")
    plot_results()


def plot_results():
    """基于 batch_test_results.csv 生成顶会论文格式的可视化结果图"""
    df = pd.read_csv("batch_test_results.csv")
    
    plt.figure(figsize=(8, 6))
    plt.plot(df["concurrent_users"], df["avg_response_time"], marker='o', linestyle='-', color='b', label='Avg Response Time')
    
    plt.xlabel("Concurrent Users", fontsize=14)
    plt.ylabel("Average Response Time (s)", fontsize=14)
    plt.title("Performance Evaluation of Concurrent Requests", fontsize=16)
    plt.xticks(df["concurrent_users"], fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    
    plt.savefig("batch_test_results.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("\n可视化结果已保存为 batch_test_results.png")


if __name__ == "__main__":
    run_batch_test()
