# MDYX 明德云析


### 项目介绍
明德云析是由AI+EDU的跨学科智能教育平台，聚焦AI+教育创新场景，打造新一代课堂智能辅助系统，探索AI时代新传研究和人才培养的新范式。

### 本阶段工作
为课堂提供一个具有问题发放和提交、AI对话、AI教辅、收集学生使用ai的历史记录并分析等功能的课堂AI助手


### 已实现产品

**AI4EDU** 

AI辅助教学系统

教师端  http://10.77.110.129:8503

学生端  http://10.77.110.129:8505

对照端  http://10.77.110.129:8504


**GraphRag** http://10.77.110.129:8506

基于RAG技术的利用新传书本建立知识图谱的问答系统

**Concept_pedia** http://10.77.110.215:8503

新传概念百科


**ADHD**  http://10.77.110.129:8502

调试不同prompt的微博回复测试网站

**WHT** http://10.77.110.129:6016

微博热搜趋势图





### 目录
ADHD 一套完整的内容分析加ai回复疏导的交叉产品

    - app.py 网页


AI4EDU 课堂AI助手代码 

    -demo0301 目前版本

        - aipower 具有ai课堂助手的学生端
     
        - student 去除ai功能的对照组
     
        - teacher 教师端
     
    -test20 并发测试代码

concept_pedia 对于glossary的百科化实现 对于一个概念给出定义与相关概念

    - app.py 网页
  
    - glossary_difinitions 概念定义
  
    - glossary_related_terms.csv 相近词表格


Graphrag 对于Graphrag技术的部署

    - que.py 对于询问的转化代码 维护一个函数
    
    - app.py 实现网页

