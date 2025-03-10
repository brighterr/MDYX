import subprocess

def graphrag_query(query, path="./ragtest", method="global"):
    """
    封装的 GraphRag 查询函数。
    
    参数：
    - query: str，自定义问题
    - path: str，GraphRag 数据存储路径，默认为 "./ragtest"
    - method: str，查询方法，默认为 "global"

    返回：
    - result: str，查询返回的文本结果
    - error: str，错误信息（如果有）
    """
    command = [
        "graphrag", "query",
        "--root", path,
        "--method", method,
        "--query", query
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stderr:
        return None, result.stderr.strip()  # 返回错误信息
    return result.stdout.strip(), None  # 返回查询结果

if __name__ == "__main__":
    query = input("请输入自定义问题: ")
    answer, error = graphrag_query(query)

    if error:
        print("错误信息：", error)
    else:
        print("查询结果：", answer)
