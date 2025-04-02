import streamlit as st
import re
import logging
import json
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from que import graphrag_query
from typing import List, Dict, Tuple
from jsonsearch import JsonSearch
import pandas as pd

import os

# ===== 日志配置 =====
logging.basicConfig(
    filename='data_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ===== 自定义CSS样式 =====
st.markdown("""
<style>
    /* 通用样式 */
    .tab-content { padding: 1rem 0; }
    .search-filter { background: #f8f9fa; padding: 1rem; border-radius: 8px; }
    .world-tag { background: #E8F5E9; color: #2E7D32; border-radius: 12px; padding: 2px 8px; font-size: 0.8rem; display: inline-block; margin: 2px 3px; }
    .topic-tag { background: #F3E5F5; color: #6A1B9A; border-radius: 12px; padding: 2px 8px; font-size: 0.8rem; display: inline-block; margin: 2px 3px; }
    .spotlight-tag { background: #FFF3E0; color: #EF6C00; border-radius: 12px; padding: 2px 8px; font-size: 0.8rem; display: inline-block; margin: 2px 3px; }
    .snippet { color: #444; font-size: 0.95rem; line-height: 1.4; margin-top: 0.5rem; }
    .highlight { background-color: #FFF9C4; border-radius: 3px; padding: 0 2px; }
    .result-item { padding:1rem; margin:0.5rem 0; background:white; border-radius:0.5rem; box-shadow:0 2px 4px rgba(0,0,0,0.05); transition: all 0.3s ease; }
    .result-item:hover { transform: translateY(-2px); box-shadow:0 4px 8px rgba(0,0,0,0.1); }
    .match-info { color:#666; font-size:0.85rem; margin:0.3rem 0; }
    .data-panel { background:#f8f9fa; padding:1rem; border-radius:0.5rem; margin:1rem 0; }
    .stTextInput input { border-radius: 25px !important; }
    
    /* 智能生成报告样式 */
    .report-section {
        margin: 1.5rem 0;
        padding: 1.5rem;
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .section-title {
        color: #1a237e;
        font-weight: 600;
        border-left: 4px solid #1a237e;
        padding-left: 1rem;
        margin: 1.5rem 0;
    }
    .data-reference {
        background-color: #f5f5f5;
        color: #616161;
        font-size: 0.85em;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .analysis-content {
        line-height: 1.7;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== 数据处理逻辑 =====
def load_and_validate_data(file_path: str):
    """加载并验证数据，返回有效数据、无效数据和错误统计"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        logging.error(f"数据加载失败: {str(e)}")
        st.error("数据文件加载失败，请检查文件格式和路径")
        return [], [], {}

    url_map = {}
    invalid_items = []
    error_stats = {
        'missing_title': 0,
        'missing_url': 0,
        'invalid_url': 0,
        'empty_content': 0,
        'date_error': 0
    }

    for idx, item in enumerate(raw_data):
        try:
            errors = []
            item = {k.lower(): v for k, v in item.items()}  # 统一字段名
            
            title = str(item.get('title', '')).strip()
            raw_url = str(item.get('url', ''))
            raw_text = item.get('text', '')
            scraped_date = item.get('scraped_date', '')

            # 验证必要字段
            if not title:
                errors.append('missing_title')
            if not raw_url:
                errors.append('missing_url')
            elif not is_valid_url(raw_url):
                errors.append('invalid_url')
            if not raw_text or not str(raw_text).strip():
                errors.append('empty_content')

            if errors:
                for err in errors:
                    error_stats[err] += 1
                log_entry = {
                    'index': idx,
                    'title': title[:50] + '...' if title else '',
                    'errors': errors
                }
                invalid_items.append(log_entry)
                continue

            # 数据清洗
            clean_item = {
                'title': title,
                'url': normalize_url(raw_url),
                'text': clean_content(raw_text),
                'author': str(item.get('author', '未知作者')).strip(),
                'scraped_date': parse_date(scraped_date),
                'publish_date': parse_date(item.get('publish_date', '')),
                'website': (str(item.get('website', '')).strip() or '未标注来源')
            }

            # 去重逻辑（保留最新版本）
            existing = url_map.get(clean_item['url'])
            if not existing or (clean_item['scraped_date'] and 
                              clean_item['scraped_date'] > existing['scraped_date']):
                url_map[clean_item['url']] = clean_item
            if clean_item['website']:
                clean_item['website'] = clean_item['website'].replace(' ', '_')
            clean_item['date'] = (
                clean_item['publish_date'] 
                or clean_item['scraped_date'] 
                or None  # 设置默认日期
            )
            if clean_item['date'] and clean_item['date'].year > datetime.now().year + 2:
                logging.warning(f"异常未来日期：{clean_item['date']}")
                clean_item['date'] = None
            clean_item.update({
                'world': str(item.get('World') or item.get('world') or '未分类').strip(),
                'topic': str(item.get('Topic') or item.get('topic') or '未分类').strip().lower(),
                'spotlight': str(item.get('Spotlight') or item.get('spotlight') or 'none').strip().lower()
            })
            # 自动修正常见拼写变体
            if 'belt' in clean_item['spotlight'] and 'road' in clean_item['spotlight']:
                clean_item['spotlight'] = 'belt and road'
        except Exception as e:
            logging.error(f"处理第{idx}条数据失败: {str(e)}")
            continue

    return list(url_map.values()), invalid_items, error_stats

def is_valid_url(url: str) -> bool:
    """验证URL格式有效性"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """标准化URL格式"""
    try:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(query='', fragment=''))
    except:
        return url.split('?')[0].split('#')[0]

def clean_content(text: str) -> str:
    """清洗文本内容"""
    try:
        text = str(text)
        text = re.sub(r'\s+', ' ', text)  # 合并空白字符
        text = text.replace('\ufeff', '')   # 移除BOM字符
        return text.strip()
    except:
        return ""

def parse_date(date_str: str):
    """智能日期解析"""
    date_formats = [
        '%Y-%m-%d',         # ISO格式
        '%d/%m/%Y',         # 欧洲格式
        '%m/%d/%Y',         # 美国格式
        '%Y.%m.%d',         # 带点格式
        '%Y年%m月%d日'       # 中文格式
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def highlight_keywords(text: str, keywords: list) -> str:
    """高亮多个关键词"""
    for keyword in keywords:
        text = re.sub(
            f'({re.escape(keyword)})',
            r'<span class="highlight">\1</span>',
            text,
            flags=re.IGNORECASE
        )
    return text

def search_articles(data: list, query: str) -> list:
    """执行搜索并排序结果"""
    keywords = [k.lower() for k in re.split(r'\s+', query.strip()) if len(k) >= 2]
    if not keywords:
        return []
    
    scored_articles = []
    for article in data:
        title = article['title'].lower()
        text = article['text'].lower()
        
        # 必须包含所有关键词
        if not all(k in title or k in text for k in keywords):
            continue
        
        # 计算匹配分数
        title_matches = sum(title.count(k) for k in keywords)
        text_matches = sum(text.count(k) for k in keywords)
        score = title_matches * 3 + text_matches  # 标题匹配权重更高
        
        scored_articles.append({
            **article,
            'score': score,
            'title_match': title_matches > 0
        })
    
    # 排序：标题匹配优先 -> 分数降序 -> 日期降序
    return sorted(scored_articles, 
                 key=lambda x: (-x['title_match'], -x['score'], 
                               -x['scraped_date'].timestamp() if x['scraped_date'] else 0))

def generate_snippet(text: str, keywords: list, max_length: int = 300) -> str:
    """生成智能摘要"""
    text = text.replace('\n', ' ')
    
    # 寻找最佳匹配段落
    best_score = 0
    best_start = 0
    window_size = 200
    
    for i in range(0, len(text), window_size):
        chunk = text[i:i+window_size].lower()
        score = sum(chunk.count(k) for k in keywords)
        if score > best_score:
            best_score = score
            best_start = i
    
    # 截取上下文
    start = max(0, best_start - 50)
    end = min(len(text), best_start + window_size + 50)
    snippet = text[start:end]
    
    # 添加省略号指示截断
    if start > 0:
        snippet = '...' + snippet
    if end < len(text):
        snippet += '...'
    
    return snippet

# ===== 文献检索功能 =====
def show_filter_panel(data: list):
    """显示多维度筛选面板"""
    with st.sidebar:
        st.subheader("🔎 高级筛选")
        websites = list({d['website'] for d in data if d.get('website')})
        websites.sort()
        
        selected_authors = st.multiselect(
            "选择作者", 
            options=["全部"] + list({d['author'] for d in data}),
            default=["全部"],
            placeholder="选择作者..."
        )
        
        selected_websites = st.multiselect(
            "来源网站",
            options=["全部"] + websites,
            default=["全部"]
        )
        
        st.divider()
        st.subheader("🗂 主题分类筛选")
        
        with st.expander("🌍 地域分类（World）", expanded=True):
            world_options = ["Asia & Pacific", "North America", "Europe", 
                           "Middle East", "Africa", "South America", "Organizations"]
            selected_world = st.multiselect(
                "选择地域分类",
                options=world_options,
                default=[],
                placeholder="全选"
            )
        
        with st.expander("📚 主题分类（Topic）"):
            topic_options = ["economy&business", "politic", "technology",
                           "environment,climate&energy", "health&hygiene",
                           "military&wars", "education"]
            selected_topic = st.multiselect(
                "选择主题分类",
                options=topic_options,
                default=[],
                placeholder="全选"
            )
        
        with st.expander("🔦 重点专题（Spotlight）"):
            spotlight_options = ["belt and road", "none"]
            selected_spotlight = st.multiselect(
                "选择重点专题",
                options=spotlight_options,
                default=[],
                placeholder="全选"
            )

        return {          
            'world': selected_world,
            'topic': selected_topic,
            'spotlight': selected_spotlight,
            'authors': selected_authors,
            'website': selected_websites  
        }

def filter_articles(data: list, filters: dict) -> list:
    """应用筛选条件"""
    filtered = data
    
    if filters.get('authors') and "全部" not in filters['authors']:
        filtered = [item for item in filtered 
                   if item.get('author') in filters['authors']]
    
    selected_websites = filters.get('website', [])
    if selected_websites and "全部" not in selected_websites:
        filtered = [d for d in filtered 
                   if d.get('website') in selected_websites]
    
    def apply_category_filter(field, selected):
        if not selected:
            return
        nonlocal filtered
        selected_lower = [s.strip().lower() for s in selected]
        filtered = [
            d for d in filtered 
            if str(d.get(field, '')).strip().lower() in selected_lower
        ]    
    apply_category_filter('world', filters.get('world'))
    apply_category_filter('topic', filters.get('topic'))
    apply_category_filter('spotlight', filters.get('spotlight'))
    
    return filtered

def show_search_page():
    """显示文献检索页面"""
    st.header("文献检索系统")
    
    valid_data, invalid_items, error_stats = load_and_validate_data("output.json")
    
    if not valid_data:
        st.error("没有有效数据可供搜索，请检查数据源")
        return
    
    filters = show_filter_panel(valid_data)
    filtered_data = filter_articles(valid_data, filters)
    
    search_query = st.text_input("🔍 输入搜索关键词（支持多个关键词，空格分隔）", 
                               placeholder="例如：china africa")
    
    if not search_query.strip():
        st.info("💡 请输入关键词开始搜索（支持多个关键词AND搜索）")
        return
    
    results = search_articles(filtered_data, search_query)
    
    st.subheader(f"📄 找到 {len(results)} 条相关结果")
    
    keywords = [k.lower() for k in re.split(r'\s+', search_query.strip()) if k]
    for idx, article in enumerate(results[:50]):
        with st.container():
            title_hl = highlight_keywords(article['title'], keywords)
            snippet = generate_snippet(article['text'], keywords)
            
            tags_html = []
            if article.get('world'):
                tags_html.append(f'<span class="world-tag">🌍 {article["world"]}</span>')
            if article.get('topic'):
                tags_html.append(f'<span class="topic-tag">📚 {article["topic"]}</span>')
            if article.get('spotlight') and article['spotlight'] != 'none':
                tags_html.append(f'<span class="spotlight-tag">🔦 {article["spotlight"]}</span>')
            
            st.markdown(f"""
            <div class="result-item">
                <a href="{article['url']}" target="_blank" style="text-decoration:none;color:inherit;">
                    <div style="font-size:1.1rem;font-weight:500;margin-bottom:0.3rem;">
                        {title_hl}
                    </div>
                </a>
                <div class="match-info">
                    👤 {article['author']}  
                    💎 匹配强度：{article['score']}分
                    <div style="margin-top:0.3rem;">{" ".join(tags_html)}</div>
                </div>
                <div class="snippet">
                    {highlight_keywords(snippet, keywords)}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===== 智能生成功能 =====
#from que import graphrag_query  # 假设这是调用分析模型的接口
import subprocess

import requests

def graphrag_query(query, path="./ragtest", method="global"):
    """
    修改后的 GraphRag 查询函数，通过 HTTP API 访问
    
    参数：
    - query: str，自定义问题
    - path: str，GraphRag 数据存储路径，默认为 "./ragtest"
    - method: str，查询方法，默认为 "global"

    返回：
    - result: str，查询返回的文本结果
    - error: str，错误信息（如果有）
    """
    # GraphRAG API 的 URL（假设它运行在本地 5000 端口）
    api_url = "http://localhost:4001/query"  # 替换为实际的 GraphRAG API URL
    
    # 构造请求数据
    payload = {
        "query": query,
        "path": path,
        "method": method
    }
    
    try:
        # 发送 POST 请求
        response = requests.post(api_url, json=payload)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 成功响应，返回 answer 字段
            return response.json().get("answer"), None
        else:
            # 错误响应，返回错误信息
            error_msg = response.json().get("error", "Unknown error")
            return None, f"API Error: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        # 网络或连接错误
        return None, f"Request failed: {str(e)}"


def format_response(response_text):
    """格式化分析报告"""
    clean_text = response_text.replace("SUCCESS: Global Search Response:\n", "").strip()
    sections = re.split(r'\n## ', clean_text)
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
            
        parts = section.split("\n\n", 1)
        title = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ""
        
        with st.container():
            st.markdown(f'<div class="report-section">', unsafe_allow_html=True)
            st.markdown(f'<h3 class="section-title">{title}</h3>', unsafe_allow_html=True)
            
            paragraphs = content.split("\n\n")
            for p in paragraphs:
                if "[Data:" in p:
                    text_part, data_part = p.rsplit("[Data:", 1)
                    st.markdown(f'<div class="analysis-content">{text_part.strip()}</div>', 
                               unsafe_allow_html=True)
                    st.markdown(f'<div class="data-reference">数据来源: {data_part.strip(" ]")}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="analysis-content">{p}</div>', 
                               unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_generate_page():
    """显示智能生成页面"""
    st.header("智能分析生成")
    
    query = st.text_input("请输入分析请求（支持中英文）：", 
                        placeholder="示例：Chinese-Africa relationship",
                        key="generate_input")
    
    if query:
        response = graphrag_query(query)
        if response:
            st.markdown("---")
            st.markdown("### 综合分析报告")
            format_response(response[0])
        else:
            st.error("生成失败，请重试")

# ===== 主界面整合 =====
def main():
    st.title("智库综合平台")
    
    # 选项卡导航
    tab1, tab2 = st.tabs(["文献检索", "智能生成"])
    
    with tab1:
        show_search_page()
        
    with tab2:
        show_generate_page()

if __name__ == "__main__":
    main()