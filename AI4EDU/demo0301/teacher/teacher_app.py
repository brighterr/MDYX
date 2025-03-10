# teacher_app.py
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from db_access import init_database, insert_message, get_messages_by_user
# 数据文件路径（需要共享访问）
DATA_DIR = "/home/zhangyuheng/AIEDU/demo0301/data"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")

# 初始化数据目录和文件
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

# 读取提交数据
def load_submissions():
    with open(SUBMISSIONS_FILE, "r") as f:
        return json.load(f)

# 教师端主界面
def main():
    init_files()
    st.title("课堂问题管理系统 - 教师端")
    
    # 密码验证
    password = st.sidebar.text_input("教师密码", type="password")
    if password != "teacher123":
        st.error("请输入正确的教师密码")
        return
    
    menu = st.sidebar.selectbox("功能菜单", ["发布问题", "查看提交","历史记录"])
                   
                
    if menu == "发布问题":
        st.header("发布新问题")
        
        input_method = st.radio("输入方式", ["手动输入", "文件上传"])
        question_content = ""
        
        if input_method == "手动输入":
            question_content = st.text_area("问题内容", height=150)
        else:
            uploaded_file = st.file_uploader("上传问题文件", type=["txt", "md", "pdf", "docx"])
            if uploaded_file:
                try:
                    question_content = uploaded_file.getvalue().decode()
                except:
                    question_content = uploaded_file.getvalue()
        
        if st.button("发布") and question_content:
            new_question = {
                "id": str(uuid.uuid4()),
                "content": question_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            questions = load_questions()
            questions.append(new_question)
            with open(QUESTIONS_FILE, "w") as f:
                json.dump(questions, f)
            st.success("问题发布成功！")
    
    elif menu == "查看提交":
        st.header("学生提交记录")
        
        submissions = load_submissions()
        questions = load_questions()
        
        if not questions:
            st.warning("暂无已发布问题")
            return
        
        # 问题选择器
        selected_question = st.selectbox(
            "选择问题",
            options=questions,
            format_func=lambda x: f"{x['timestamp']} - {x['content'][:30]}..."
        )
        
        # 过滤提交记录
        filtered_subs = [s for s in submissions 
                        if s["question_id"] == selected_question["id"]]
        
        if not filtered_subs:
            st.info("该问题暂无提交记录")
            return
        
        # 显示统计信息
        st.subheader(f"共收到 {len(filtered_subs)} 份提交")
        
        # 详细查看
        for idx, sub in enumerate(filtered_subs, 1):
            with st.expander(f"提交 #{idx} - {sub['student_name']} ({sub['timestamp']})"):
                st.write("**学生姓名:**", sub["student_name"])
                st.write("**提交时间:**", sub["timestamp"])
                st.write("**答案内容:**")
                st.write(sub["content"])
                
                
    elif menu=="历史记录":
        search_username = st.text_input("查询用户名", value="")
        if st.button("搜索对话记录"):
            records = get_messages_by_user(search_username)
            if records:
                for role, msg, ts in records:
                    st.markdown(f"**{ts}** [{role}]：{msg[:50]}...")
            else:
                st.info("未找到相关记录") 
if __name__ == "__main__":
    main()