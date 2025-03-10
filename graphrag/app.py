import streamlit as st
from que import graphrag_query

# 设置页面标题
st.title("GraphRAG 问答系统\n Advertising & IMC- Principles and Practice (9th Edition)")

# 在页面上添加一个输入框，用户可以输入问题
user_input = st.text_input("请输入您的问题：")

# 当用户输入问题并按下回车键时
if user_input:
    # 调用 graphrag_query 函数获取答案
    answer = graphrag_query(user_input)
    
    # 在页面上显示答案
    st.write("答案：")
    st.write(answer)