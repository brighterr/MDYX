# student_app.py
import streamlit as st
import json
import os
import uuid
from datetime import datetime

# 共享数据路径
DATA_DIR = "/home/zhangyuheng/AIEDU/demo0301/data"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")

# 初始化数据文件
def init_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    
    for file in [QUESTIONS_FILE, SUBMISSIONS_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)

# 读取问题数据
def load_questions():
    with open(QUESTIONS_FILE, "r") as f:
        return json.load(f)

# 保存提交记录
def save_submission(submission):
    submissions = []
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "r") as f:
            submissions = json.load(f)
    
    submissions.append(submission)
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(submissions, f)

# 学生端主界面
def main():
    init_files()
    st.title("课堂问题提交系统 - 学生端")
    
    # 学生信息输入
    student_name = st.text_input("请输入你的姓名", max_chars=20)
    if not student_name:
        st.warning("请先输入姓名")
        return
    
    # 加载问题列表
    questions = load_questions()
    if not questions:
        st.info("当前没有待回答问题")
        return
    
    # 问题选择
    selected_question = st.selectbox(
        "选择要回答的问题",
        options=questions,
        format_func=lambda x: f"{x['timestamp']} - {x['content'][:50]}..."
    )
    
    # 答案输入
    answer = st.text_area("输入你的答案", height=200,
                         placeholder="在这里写下你的回答...")
    
    # 提交按钮
    if st.button("提交答案"):
        if not answer:
            st.error("答案内容不能为空")
            return
        
        new_submission = {
            "question_id": selected_question["id"],
            "student_name": student_name,
            "content": answer,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_submission(new_submission)
        st.success("答案提交成功！")
        st.balloons()

if __name__ == "__main__":
    main()