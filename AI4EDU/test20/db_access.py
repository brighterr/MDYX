# db_access.py
import sqlite3
from datetime import datetime
from typing import List, Tuple

DATABASE_PATH = "/home/zhangyuheng/AIEDU/demo0301/data/chat.db"

def create_connection():
    """创建数据库连接"""
    return sqlite3.connect(DATABASE_PATH, check_same_thread=False)

def init_database():
    """初始化数据库表结构"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    with create_connection() as conn:
        conn.execute(create_table_sql)

def insert_message(username: str, role: str, message: str):
    """插入聊天记录"""
    insert_sql = """
    INSERT INTO chat_history (username, role, message)
    VALUES (?, ?, ?)
    """
    with create_connection() as conn:
        conn.execute(insert_sql, (username, role, message))
        conn.commit()

def get_messages_by_user(username: str, limit: int = 100) -> List[Tuple]:
    """获取指定用户的聊天记录"""
    query_sql = """
    SELECT role, message, timestamp 
    FROM chat_history 
    WHERE username = ?
    ORDER BY timestamp DESC
    LIMIT ?
    """
    with create_connection() as conn:
        cursor = conn.execute(query_sql, (username, limit))
        return cursor.fetchall()