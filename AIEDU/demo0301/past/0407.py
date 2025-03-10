# /home/zhangyuheng/AIEDU/demo0301/aipower/aipower_app.py
import streamlit as st
import requests
import json
import os
import uuid
from datetime import datetime

# 共享数据路径
DATA_DIR = "/home/zhangyuheng/AIEDU/demo0301/data"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")

# API 配置
AI_URL = "http://10.77.110.129:8000/v1/chat/completions"
AI_HEADERS = {"Content-Type": "application/json"}
AI_MODEL = "/home/zhangyuheng/.cache/modelscope/hub/Qwen/Qwen2.5-7B-Instruct"
MAX_TOKENS = 512

# 初始化函数
def init_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    for file in [QUESTIONS_FILE, SUBMISSIONS_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)

def load_questions():
    with open(QUESTIONS_FILE, "r") as f:
        return json.load(f)

def save_submission(submission):
    submissions = []
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "r") as f:
            submissions = json.load(f)
    submissions.append(submission)
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(submissions, f)

# AI 对话功能
def ai_query(msgs):
    data = {
        "model": AI_MODEL,
        "messages": msgs,
        "temperature": 0.7,
        "top_p": 0.8,
        "repetition_penalty": 1.05,
        "max_tokens": MAX_TOKENS,
    }
    try:
        response = requests.post(AI_URL, headers=AI_HEADERS, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"API请求错误: {response.status_code}"
    except Exception as e:
        return f"API连接失败: {str(e)}"

# 主界面
def main():
    init_files()
    st.title("智能学习助手")

    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 初始化输入框状态
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    # 侧边栏导航
    app_mode = st.sidebar.selectbox(
        "功能导航",
        ["课堂问题提交", "AI对话助手"],
        index=0
    )

    # 公共学生信息输入
    student_name = st.sidebar.text_input("请输入你的姓名", max_chars=20)
    
    if app_mode == "课堂问题提交":
        handle_question_submission(student_name)
    else:
        handle_ai_chat(student_name)

def handle_question_submission(student_name):
    st.header("课堂问题提交")
    
    if not student_name:
        st.warning("请先在侧边栏输入姓名")
        return

    questions = load_questions()
    if not questions:
        st.info("当前没有待回答问题")
        return

    selected_question = st.selectbox(
        "选择要回答的问题",
        options=questions,
        format_func=lambda x: f"{x['timestamp']} - {x['content'][:50]}..."
    )

    # 问题复制功能
    col1, col2 = st.columns([3, 1])
    with col1:
        with st.expander("📝 查看完整问题"):
            st.write(selected_question["content"])
    with col2:
        if st.button("📋 复制到AI对话", key="copy_btn"):
            # 设置双重状态保证数据传递
            st.session_state.copied_question = selected_question["content"]
            st.session_state.ai_input = selected_question["content"]
            st.success("问题已复制！请切换到AI对话界面")

    answer = st.text_area("输入你的答案", 
                        height=200, 
                        placeholder="在这里写下你的回答...",
                        key="answer_input")
    
    if st.button("提交答案", type="primary"):
        if not answer:
            st.error("答案内容不能为空")
        else:
            new_submission = {
                "question_id": selected_question["id"],
                "student_name": student_name,
                "content": answer,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_submission(new_submission)
            st.success("答案提交成功！")
            st.balloons()

def handle_ai_chat(student_name):
    st.header("AI对话助手")
    
    # 处理复制的提问内容
    if "copied_question" in st.session_state:
        st.session_state.ai_input = st.session_state.pop("copied_question")

    # 显示对话历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 对话输入区
    with st.form("ai_chat_form"):
        user_input = st.text_input(
            "输入消息（可直接编辑）", 
            value=st.session_state.ai_input,
            key="ai_chat_input"
        )
        submitted = st.form_submit_button("🚀 发送")
        
        if submitted:
            if user_input.strip():
                # 处理消息
                process_message(student_name, user_input)
                # 清空输入框
                st.session_state.ai_input = ""
                st.rerun()
            else:
                st.warning("请输入有效内容")

    # 侧边栏功能
    with st.sidebar:
        if st.button("🧹 清空对话历史"):
            st.session_state.messages = []
            st.session_state.ai_input = ""
            st.rerun()

def process_message(student_name, user_input):
    if not student_name:
        st.warning("请先在侧边栏输入姓名")
        return
    
    # 添加带标识的用户消息
    user_msg = {
        "role": "user",
        "content": f"[学生 {student_name}]: {user_input}"
    }
    st.session_state.messages.append(user_msg)
    
    # 获取AI回复
    with st.spinner("🔍 AI正在思考中..."):
        ai_response = ai_query(st.session_state.messages)
    
    # 添加AI回复
    ai_msg = {
        "role": "assistant",
        "content": f"🤖 AI助手: {ai_response}"
    }
    st.session_state.messages.append(ai_msg)

if __name__ == "__main__":
    main()