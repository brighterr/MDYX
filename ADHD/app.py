import streamlit as st
import requests
import pandas as pd
import random
import asyncio
# API 配置
url = "http://10.77.110.129:8000/v1/chat/completions"
headers = {"Content-Type": "application/json"}

# 模型配置
model = "/home/zhangyuheng/.cache/modelscope/hub/Qwen/Qwen2.5-7B-Instruct"
max_tokens = 512

def load_weibo_data():
    """从Excel文件加载微博内容"""
    try:
        file_adhd="/home/zhangyuheng/ADHD/ans100.csv"
        df = pd.read_csv(file_adhd)
        return df["weibo_content"].tolist()
    except Exception as e:
        st.error(f"读取文件失败: {str(e)}")
        return []

def query(msgs):
    """调用API获取回复"""
    data = {
        "model": model,
        "messages": msgs,
        "temperature": 0.7,
        "top_p": 0.8,
        "repetition_penalty": 1.05,
        "max_tokens": max_tokens,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"API请求错误: {response.status_code}"
    except Exception as e:
        return f"API连接失败: {str(e)}"

# 界面设置
st.title("AI 对话助手")

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 侧边栏操作
with st.sidebar:
    st.header("批量处理操作")
    if st.button("随机选取5条微博并生成回复"):
        weibo_contents = load_weibo_data()
        if len(weibo_contents) >= 5:
            selected = random.sample(weibo_contents, 5)
            progress_bar = st.progress(0)
            for i, content in enumerate(selected):
                # 添加用户消息
                st.session_state.messages.append({"role": "user", "content": content})
                
                # 获取AI回复
                with st.spinner(f"正在处理第 {i+1} 条微博..."):
                    ai_response = query(st.session_state.messages)
                
                # 添加AI回复
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # 更新进度条
                progress_bar.progress((i+1)/5)
            st.success("5条微博处理完成！")
            st.rerun()
        else:
            st.warning("Excel文件中数据不足5条")

# 单条消息处理
with st.form("single_input"):
    user_input = st.text_input("输入你的消息:", key="user_input")
    submitted = st.form_submit_button("发送")
    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 获取AI回复
        with st.spinner("思考中..."):
            ai_response = query(st.session_state.messages)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

# 清空历史按钮
if st.sidebar.button("清空对话历史"):
    st.session_state.messages = []
    st.rerun()
    
