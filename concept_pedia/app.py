import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import ast

# 定义 find_definition 函数
def find_definition(term, csv_file='glossary_definitions.csv'):
    """
    查找术语的定义
    """
    df = pd.read_csv(csv_file)
    result = df[df['Term'] == term]
    if not result.empty:
        return result['Definition'].values[0]
    else:
        return "Term not found."

# 定义 plot_related_terms_network 函数
def plot_related_terms_network(target_term, csv_file='glossary_related_terms.csv'):
    """
    绘制目标术语的相关词关系网络图
    """
    df = pd.read_csv(csv_file)
    target_row = df[df['Term'] == target_term]
    if target_row.empty:
        st.warning(f"Term '{target_term}' not found in the glossary.")
        return
    
    # 获取相关词列表
    related_terms = ast.literal_eval(target_row['Related Terms'].values[0])
    
    # 创建图
    G = nx.Graph()
    G.add_node(target_term)
    for term in related_terms:
        G.add_edge(target_term, term)
    
    # 计算布局
    pos = nx.spring_layout(G, k=0.6, iterations=50)
    
    # 调整节点大小和颜色
    node_sizes = {n: 2500 if n == target_term else 1200 for n in G.nodes}
    
    # 绘制图形
    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(
        G, pos,
        node_size=[node_sizes[n] for n in G.nodes],
        node_color=['#1f78b4' if n == target_term else '#a6cee3' for n in G.nodes],
        alpha=0.7
    )
    nx.draw_networkx_edges(
        G, pos,
        width=1.5,
        edge_color='#666666',
        alpha=0.6
    )
    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_weight='bold',
        font_family='sans-serif',
        font_color='#333333'
    )
    plt.title(f"'{target_term}' Related Terms Network", fontsize=14, color='#333333')
    plt.axis('off')
    st.pyplot(plt)

# Streamlit 应用
def main():
    st.title("Glossary Explorer")
    st.write("Enter a term to find its definition and view its related terms network.")

    # 输入框
    term = st.text_input("Enter a term:")

    if term:
        # 查找定义
        definition = find_definition(term)
        st.subheader(f"Definition of '{term}':")
        st.write(definition)

        # 绘制相关词网络图
        st.subheader(f"Related Terms Network for '{term}':")
        plot_related_terms_network(term)

# 运行应用
if __name__ == "__main__":
    main()