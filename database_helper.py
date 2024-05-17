import sqlite3
from sqlite3 import Cursor
from typing import Any, Dict, List, Tuple

class DatabaseHelper:
    utilization_by_task_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'project': 'TEXT',
        'week': 'TEXT',
        'task_name': 'TEXT',
        'hours': 'INTEGER'
    }

    utilization_by_resource_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'project': 'TEXT',
        'week': 'TEXT',
        'resource_name': 'TEXT',
        'hours': 'INTEGER'
    }

    task_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'project': 'TEXT',
        'week': 'TEXT',
        'task': 'TEXT',
        'status': 'TEXT',
        'etc': 'DATE',
        'comments': 'TEXT'
    }

    defect_summary_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'project': 'TEXT',
        'week': 'TEXT',
        'defect_id': 'TEXT',
        'defect_name': 'TEXT',
        'severity': 'TEXT',
        'status': 'TEXT',
        'assigned_to': 'TEXT',
        'etc': 'DATE',
        'comments': 'TEXT'
    }

    activity_columns: dict[str, str] = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'project': 'TEXT',
        'week': 'TEXT',
        'activity': 'TEXT',
        'count': 'INTEGER'
    }
    table_names: list[str] = ['utilization_by_task', 'utilization_by_resource', 'task_last_week', 'task_current_week', 'week_defect_summary', 'activity_this_week']
    table_columns: list[dict[str, str]] = [utilization_by_task_columns, utilization_by_resource_columns, task_columns, task_columns, defect_summary_columns, activity_columns]
    table_dict: dict = dict(zip(table_names, table_columns))
    
    def __init__(self, db_name: str) -> None:
        self.db_name: str = db_name
        for table_name, columns in zip(self.table_names, self.table_columns):
            self.create_table(table_name, columns)

    def get_table_names(self) -> List[str]:
        return self.table_names

    def get_table_columns(self) -> list[dict[str, str]]:
        return self.table_columns

    def get_table_dict(self) -> dict:
        return self.table_dict
    
    def execute_query(self, query: str, params: Tuple[Any] = ()) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor: Cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def fetch_all(self, query: str, params: Tuple[Any] = ()) -> List[Tuple[Any]]:
        with sqlite3.connect(self.db_name) as conn:
            cursor: Cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        columns_def: str = ', '.join([f"{name} {type}" for name, type in columns.items()])
        query: str = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        self.execute_query(query)

    def save_data(self, table_name: str, columns: dict, data: List[Tuple[Any]]) -> None:
        placeholders: str = ', '.join(['?' for _ in range(len(list(columns.keys())[1:]))])
        query: str = f"INSERT INTO {table_name} ({', '.join(list(columns.keys())[1:])}) VALUES ({placeholders})"
        with sqlite3.connect(self.db_name) as conn:
            cursor: Cursor = conn.cursor()
            cursor.executemany(query, data)
            conn.commit()

    def fetch_data(self, table_name: str, where_clause: str, params: Tuple[Any]) -> List[Tuple[Any]]:
        query: str = f"SELECT * FROM {table_name} WHERE {where_clause}"
        return self.fetch_all(query, params)

    def update_data(self, table_name: str, set_clause: str, where_clause: str, params: Tuple[Any]) -> None:
        query: str = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        self.execute_query(query, params)
