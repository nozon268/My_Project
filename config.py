import os
import pyodbc
from pathlib import Path

class Config:
    # Секретный ключ (можно установить в переменных окружения или здесь)
    DB_SCRIPTS_PATH = Path(__file__).parent / 'ticket_system_db'
    
    # Настройки SQL Server
    SQL_DATABASE = 'TicketSystemDB'
    SQL_SERVER = 'localhost'
    SQL_DRIVER = 'ODBC Driver 17 for SQL Server'
    
    @classmethod
    def get_db_connection(cls):
        """Создает подключение к БД"""
        try:
            conn_str = (
                f'DRIVER={{{cls.SQL_DRIVER}}};'
                f'SERVER={cls.SQL_SERVER};'
                f'DATABASE={cls.SQL_DATABASE};'
                f'Trusted_Connection=yes;'
            )
            conn = pyodbc.connect(conn_str)
            return conn
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return None
    
    @classmethod
    def check_database_exists(cls):
        """Проверяет, существует ли база данных"""
        try:
            # Подключаемся к master базе
            conn_str = (
                f'DRIVER={{{cls.SQL_DRIVER}}};'
                f'SERVER={cls.SQL_SERVER};'
                f'Trusted_Connection=yes;'
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Проверяем существование базы
            cursor.execute(f"""
                SELECT name 
                FROM sys.databases 
                WHERE name = '{cls.SQL_DATABASE}'
            """)
            
            exists = cursor.fetchone() is not None
            
            cursor.close()
            conn.close()
            
            return exists
        except:
            return False
    
    @classmethod
    def execute_sql_file(cls, file_path):
        """Выполняет SQL файл"""
        try:
            conn = cls.get_db_connection()
            if not conn:
                return False
            
            # Читаем SQL файл
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Разделяем на отдельные команды (разделитель GO)
            commands = sql_script.split('GO')
            
            cursor = conn.cursor()
            
            for command in commands:
                command = command.strip()
                if command:  # Пропускаем пустые команды
                    try:
                        cursor.execute(command)
                    except Exception as e:
                        print(f"⚠️ Ошибка в команде: {e}")
                        print(f"Команда: {command[:100]}...")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Файл {file_path.name} выполнен успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка выполнения файла {file_path}: {e}")
            return False
    
    @classmethod
    def setup_database(cls):
        """Создает и настраивает базу данных"""
        print("🔄 Настройка базы данных...")
        
        # 1. Проверяем, существует ли БД
        if cls.check_database_exists():
            print(f"✅ База данных '{cls.SQL_DATABASE}' уже существует")
        else:
            print(f"📦 Создаем базу данных '{cls.SQL_DATABASE}'...")
            
            # Подключаемся к master для создания БД
            try:
                master_conn_str = (
                    f'DRIVER={{{cls.SQL_DRIVER}}};'
                    f'SERVER={cls.SQL_SERVER};'
                    f'Trusted_Connection=yes;'
                )
                master_conn = pyodbc.connect(master_conn_str)
                cursor = master_conn.cursor()
                
                cursor.execute(f"CREATE DATABASE {cls.SQL_DATABASE}")
                master_conn.commit()
                
                cursor.close()
                master_conn.close()
                
                print(f"✅ База данных создана")
            except Exception as e:
                print(f"❌ Ошибка создания БД: {e}")
                return False
        
        # 2. Выполняем SQL файлы по порядку
        sql_files = [
            '01_create_database.sql',
            '02_insert_test_data.sql',
            '03_queries.sql',
            '04_views_procedures.sql'
        ]
        
        for sql_file in sql_files:
            file_path = cls.DB_SCRIPTS_PATH / sql_file
            if file_path.exists():
                print(f"📄 Выполняем {sql_file}...")
                cls.execute_sql_file(file_path)
            else:
                print(f"⚠️ Файл {sql_file} не найден")
        
        print("✅ Настройка базы данных завершена")
        return True
    
    @classmethod
    def get_all_tables(cls):
        """Возвращает список всех таблиц в БД"""
        try:
            conn = cls.get_db_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return tables
        except:
            return []
    
    @classmethod
    def get_table_info(cls, table_name):
        """Возвращает информацию о таблице"""
        try:
            conn = cls.get_db_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return columns
        except:
            return []

# =============== ТЕСТИРОВАНИЕ ===============

if __name__ == "__main__":
    print("Тестирование конфигурации БД")
    print("=" * 50)
    
    # 1. Проверяем подключение
    print("1. Проверка подключения...")
    conn = Config.get_db_connection()
    if conn:
        print("Подключение успешно")
        conn.close()
    else:
        print("Не удалось подключиться")
    
    # 2. Проверяем существование БД
    print("\n2. Проверка базы данных...")
    if Config.check_database_exists():
        print(f"База данных '{Config.SQL_DATABASE}' существует")
        
        # 3. Показываем таблицы
        print("\n3. Таблицы в базе данных:")
        tables = Config.get_all_tables()
        if tables:
            for table in tables:
                print(f"   - {table}")
        else:
            print("Таблицы не найдены")
    else:
        print(f"База данных '{Config.SQL_DATABASE}' не существует")
        print("\nХочешь создать базу данных?")
        print("Выполни: Config.setup_database()")
