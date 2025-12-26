import pyodbc

def test_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=TicketSystemDB;'
            'Trusted_Connection=yes;'
        )
        print("Подключено!!!")

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
        table_count = cursor.fetchone()[0]

        print(f"📊 Найдено таблиц: {table_count}")
        
        if table_count > 0:
            # Показываем список таблиц
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
            print("📋 Таблицы в базе:")
            for row in cursor.fetchall():
                print(f"  - {row[0]}")
        
        cursor.close()
        conn.close()
        return True

    except pyodbc.Error as e:
            print(f"❌ Ошибка подключения: {e}")
            print("\n🔧 Возможные решения:")
            print("1. Проверь, запущен ли SQL Server")
            print("2. Установлен ли ODBC Driver 17")
            print("3. Существует ли база TicketSystemDB")
            return False

if __name__ == "__main__":
    test_db_connection()