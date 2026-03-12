import sqlite3
from datetime import datetime
import pytz
from typing import List, Optional, Tuple

DB_NAME = "tugas.db"
WIB = pytz.timezone("Asia/Jakarta")

def init_db():
    """Initialize database with tasks table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mata_kuliah TEXT NOT NULL,
            nama_tugas TEXT NOT NULL,
            deadline TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_task(user_id: int, mata_kuliah: str, nama_tugas: str, deadline: str) -> int:
    """Add a new task to database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, mata_kuliah, nama_tugas, deadline, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, mata_kuliah, nama_tugas, deadline, datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"))
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_tasks(user_id: int) -> List[Tuple]:
    """Get all tasks for a user, sorted by deadline."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, mata_kuliah, nama_tugas, deadline FROM tasks WHERE user_id = ? ORDER BY deadline ASC",
        (user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id: int) -> Optional[Tuple]:
    """Get a single task by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, mata_kuliah, nama_tugas, deadline FROM tasks WHERE id = ?",
        (task_id,)
    )
    task = cursor.fetchone()
    conn.close()
    return task

def delete_task(task_id: int) -> bool:
    """Delete a task by ID. Returns True if successful."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_all_tasks() -> List[Tuple]:
    """Get all tasks from all users for reminder checking."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, mata_kuliah, nama_tugas, deadline FROM tasks ORDER BY deadline ASC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks
