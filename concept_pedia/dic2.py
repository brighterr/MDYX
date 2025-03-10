import PyPDF2
import re
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def extract_glossary_from_pdf(pdf_path):
    """
    从 PDF 文件中提取词汇和注释。
    """
    glossary = {}
    
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text = text.replace("\n", " ").strip()   
                pattern = r'([A-Za-z\s-]+)\s+\(p\.? ?\d+(?:,\s?\d+)*\)\s+(.*?)(?=\s+[A-Za-z\s-]+\s+\(p\.? ?\d+(?:,\s?\d+)*\)|\Z)'
                matches = re.findall(pattern, text, re.DOTALL)
                
                for term, definition in matches:
                    glossary[term.strip()] = definition.strip()
    
    return glossary

def get_related_terms(target_term, glossary):
    """
    获取与目标术语直接关联的术语。
    """
    related_terms = set()
    
    for term, definition in glossary.items():
        if target_term.lower() in definition.lower():
            related_terms.add(term)
        if term.lower() in glossary.get(target_term, "").lower():
            related_terms.add(term)
    
    return list(related_terms)

def visualize_related_terms(target_term, glossary):
    """
    可视化与目标术语直接关联的术语及其关系。
    """
    graph = nx.DiGraph()
    
    graph.add_node(target_term)
    
    related_terms = get_related_terms(target_term, glossary)
    
    for term in related_terms:
        graph.add_node(term)
        if target_term.lower() in glossary.get(term, "").lower():
            graph.add_edge(term, target_term)
        if term.lower() in glossary.get(target_term, "").lower():
            graph.add_edge(target_term, term)
    
    pos = nx.spring_layout(graph, k=0.5, iterations=50)  # k 控制节点间距
    plt.figure(figsize=(10, 8))
    
    nx.draw_networkx_nodes(graph, pos, node_size=3000, node_color="lightblue", alpha=0.8)
    nx.draw_networkx_edges(graph, pos, width=1.5, alpha=0.6, edge_color="gray", arrows=True)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight="bold")
    
    plt.title(f"Related Terms for: {target_term}", fontsize=14)
    plt.axis("off")  
    plt.show()

def get_definition(term, glossary):
    """
    根据术语从词汇表中获取释义。
    """
    return glossary.get(term, None)

def create_tables(glossary):
    """
    创建两个表格：
    表1：每个术语及其概念解释
    表2：每个术语及其相关的若干个术语（和其相关度）
    """
    # 表1：术语及其概念解释
    df_definitions = pd.DataFrame(list(glossary.items()), columns=["Term", "Definition"])
    
    # 表2：术语及其相关术语
    related_terms_data = []
    for term in glossary.keys():
        related_terms = get_related_terms(term, glossary)
        related_terms_data.append({"Term": term, "Related Terms": related_terms})
    
    df_related_terms = pd.DataFrame(related_terms_data)
    
    return df_definitions, df_related_terms

# 示例使用
pdf_path = r"Advertising & IMC- Principles and Practice (9th Edition).pdf"  # PDF 文件路径
glossary = extract_glossary_from_pdf(pdf_path)

# 创建表格
df_definitions, df_related_terms = create_tables(glossary)

# 显示表格
print("表1：术语及其概念解释")
print(df_definitions)
print("\n表2：术语及其相关术语")
print(df_related_terms)
df_definitions.to_csv("glossary_definitions.csv", index=False, encoding="utf-8")
df_related_terms.to_csv("glossary_related_terms.csv", index=False, encoding="utf-8")


