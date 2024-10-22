from datetime import datetime, timedelta
import sqlite3

# Указываем имя базы данных
DB_NAME = 'todo.db'

# Функция для настройки базы данных и создания таблицы
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создаем таблицу, если она не существует
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_description TEXT NOT NULL,
        deadline TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def get_upcoming_tasks():
    current_time = datetime.now()
    upcoming_time = current_time + timedelta(minutes=30)

    connection = sqlite3.connect(DB_NAME)  # Используем общее имя базы данных
    cursor = connection.cursor()
    
    # SQL-запрос для получения задач, где дедлайн между current_time и upcoming_time
    query = """
    SELECT id, user_id, task_description, deadline
    FROM tasks
    WHERE deadline BETWEEN ? AND ?
    """
    cursor.execute(query, (current_time, upcoming_time))
    tasks = cursor.fetchall()

    connection.close()
    return tasks

def add_task_to_db(user_id, task_description, deadline):
    conn = sqlite3.connect(DB_NAME)  # Используем общее имя базы данных
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO tasks (user_id, task_description, deadline, status) VALUES (?, ?, ?, ?)", 
                   (user_id, task_description, deadline, 'active'))
    conn.commit()
    conn.close()

def get_active_tasks(user_id):
    conn = sqlite3.connect(DB_NAME)  # Используем общее имя базы данных
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'active'", (user_id,))
    return cursor.fetchall()

def delete_task_from_db(task_id):
    conn = sqlite3.connect(DB_NAME)  # Используем общее имя базы данных
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task_in_db(task_id, new_description, new_deadline):
    conn = sqlite3.connect(DB_NAME)  # Используем общее имя базы данных
    cursor = conn.cursor()

    cursor.execute("UPDATE tasks SET task_description = ?, deadline = ? WHERE id = ?", 
                   (new_description, new_deadline, task_id))
    conn.commit()
    conn.close()

# Если вы хотите автоматически создавать таблицу при запуске скрипта
if __name__ == '__main__':
    setup_db()  # Создает базу данных и таблицы, если они не существуют
