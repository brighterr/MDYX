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
    
    # 第一步：输入姓名
    if "student_name" not in st.session_state:
        with st.form("name_form"):
            name = st.text_input("请输入你的姓名", max_chars=20)
            if st.form_submit_button("开始使用"):
                if name:
                    st.session_state.student_name = name
                    st.rerun()
                else:
                    st.warning("请输入姓名")
        return

    # 主功能界面
    st.sidebar.markdown(f"**当前用户**: {st.session_state.student_name}")
    
    # 创建两列布局
    col_question, col_ai = st.columns([1, 1])

    with col_question:
        st.header("📝 课堂问题提交")
        questions = load_questions()
        
        if not questions:
            st.info("当前没有待回答问题")
        else:
            selected_question = st.selectbox(
                "选择要回答的问题",
                questions,
                format_func=lambda x: f"{x['timestamp']} - {x['content'][:30]}..."
            )
            
            # 显示完整问题内容
            st.markdown("**问题内容**")
            st.write(selected_question["content"])
            
            # 复制到AI按钮
            if st.button("📋 复制问题到AI对话", use_container_width=True):
                st.session_state.current_question = selected_question["content"]
                st.rerun()
            
            # 答案提交区
            answer = st.text_area("输入你的答案", height=150)
            if st.button("提交答案", type="primary", use_container_width=True):
                if not answer:
                    st.error("答案内容不能为空")
                else:
                    new_submission = {
                        "question_id": selected_question["id"],
                        "student_name": st.session_state.student_name,
                        "content": answer,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_submission(new_submission)
                    st.success("答案提交成功！")
                    st.balloons()

    with col_ai:
        st.header("🤖 AI学习助手")
        
        # 显示对话历史
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # 自动填充当前问题
        current_question = st.session_state.get("current_question", "")
        
        # 对话输入区
        with st.form("ai_form"):
            user_input = st.text_area(
                "与AI对话（支持多行输入）",
                value=current_question,
                height=100,
                key="ai_input"
            )
            submitted = st.form_submit_button("发送")
            if submitted:
                if user_input:
                    # 添加用户消息（带姓名标识）
                    full_msg = f"{st.session_state.student_name}: {user_input}"
                    st.session_state.messages.append({"role": "user", "content": full_msg})
                    
                    # 获取AI回复
                    with st.spinner("AI正在思考..."):
                        ai_response = ai_query(st.session_state.messages)
                    
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.session_state.current_question = ""  # 清空问题缓存
                    st.rerun()
                else:
                    st.warning("请输入对话内容")

        # 清空对话按钮
        if st.button("清空对话历史", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_question = ""
            st.rerun()

if __name__ == "__main__":
    main()