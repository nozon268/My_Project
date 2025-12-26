#app.py - Главное Flask приложение
#Это 4-й модуль

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
import json
import webbrowser as web
import threading as thread
import time

#Мои модули
from storage import *
from services import *
from models import *

app = Flask(__name__)
app.secret_key = 'your-secret-key'

#Тестируем БД при запуске
print("Проверка подключения к БД...")
conn = Config.get_db_connection()
if conn:
    print("Подключение к БД успешно")
    conn.close()
else:
    print("Не удалось подключиться к БД")
    print("Создаем базу данных...")
    Config.setup_database()



# =============== МАРШРУТЫ ===============

@app.route('/')
def index():
    """Главная страница"""
    conn = Config.get_db_connection()
    if not conn:
        flash('Ошибка подключения к БД', 'error')
        return render_template('index.html', stats={})
    
    try:
        cursor = conn.cursor()
        
        # Получаем статистику из БД
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tickets")
        tickets_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
        open_tickets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'in_progress'")
        in_progress_tickets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'")
        closed_tickets = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        stats = {
            'users': users_count,
            'tickets': tickets_count,
            'open': open_tickets,
            'in_progress': in_progress_tickets,
            'closed': closed_tickets
        }
        
        return render_template('index.html', stats=stats)
        
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('index.html', stats={})


@app.route('/tables')
def show_tables():
    """Страница со списком таблиц (для отладки)"""
    tables = Config.get_all_tables()
    table_info = {}
    
    for table in tables:
        columns = Config.get_table_info(table)
        table_info[table] = columns
    
    return render_template('tables.html', tables=tables, table_info=table_info)


@app.route('/api/tickets')
def api_tickets():
    """API: Список заявок (запрос 1 из задания)"""
    conn = Config.get_db_connection()
    if not conn:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Используем запрос из 03_queries.sql
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.title,
                t.description,
                t.status,
                t.priority,
                t.created_at,
                u_creator.full_name AS created_by,
                u_assigned.full_name AS assigned_to,
                c.name AS category_name
            FROM tickets t
            LEFT JOIN users u_creator ON t.created_by = u_creator.user_id
            LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.user_id
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.status IN ('open', 'in_progress')
            ORDER BY 
                CASE t.priority 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                t.created_at DESC
        """)
        
        tickets = []
        columns = [column[0] for column in cursor.description]
        
        for row in cursor.fetchall():
            ticket = dict(zip(columns, row))
            if ticket['created_at']:
                ticket['created_at'] = ticket['created_at'].isoformat()
            tickets.append(ticket)
        
        cursor.close()
        conn.close()
        
        return jsonify(tickets)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/setup-db')
def setup_database():
    """API для настройки БД (только для разработки!)"""
    if Config.setup_database():
        return jsonify({'message': 'Database setup completed'})
    else:
        return jsonify({'error': 'Database setup failed'}), 500


@app.route('/tickets')
def tickets_list():
    """Страница со списком всех заявок"""
    conn = Config.get_db_connection()
    if not conn:
        flash('Ошибка подключения к БД', 'error')
        return render_template('tickets_list.html', tickets=[], 
                               open_tickets=[], in_progress_tickets=[], 
                               closed_tickets=[])
    
    try:
        cursor = conn.cursor()
        
        # Запрос 1: Текущие заявки (из вашего SQL файла)
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.title,
                t.description,
                t.status,
                t.priority,
                FORMAT(t.created_at, 'dd.MM.yyyy HH:mm') AS created_at,
                u_creator.full_name AS created_by,
                u_assigned.full_name AS assigned_to,
                c.name AS category_name
            FROM tickets t
            LEFT JOIN users u_creator ON t.created_by = u_creator.user_id
            LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.user_id
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.status IN ('open', 'in_progress')
            ORDER BY 
                CASE t.priority 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                t.created_at DESC
        """)
        
        columns = [column[0] for column in cursor.description]
        current_tickets = []
        for row in cursor.fetchall():
            current_tickets.append(dict(zip(columns, row)))
        
        # Для демонстрации используем упрощенный подход с Python моделями
        # В реальном проекте нужно адаптировать данные из БД к моделям Python
        
        cursor.close()
        conn.close()
        
        # Временный код для демонстрации (пока нет полной интеграции с БД)
        from storage import Storage
        from services import TicketService
        
        storage = Storage()
        service = TicketService(storage)
        
        # Создаем тестовые данные, если их нет
        if len(storage.get_all_tickets()) == 0:
            user1 = service.create_user("Иван Иванов")
            user2 = service.create_user("Анна Петрова", is_responsible=True)
            
            service.create_ticket("Не работает принтер", "Принтер в кабинете 301 не печатает", user1.id)
            service.create_ticket("Установить Windows", "Нужно установить Windows на новый ПК", user1.id)
            service.assign_ticket(1, user2.id)
        
        tickets = service.get_all_tickets()
        open_tickets = service.get_open_ticket()
        in_progress_tickets = service.get_in_progress_tickets()
        closed_tickets = service.get_closed_ticket()
        
        return render_template('tickets_list.html', 
                               tickets=tickets,
                               open_tickets=open_tickets,
                               in_progress_tickets=in_progress_tickets,
                               closed_tickets=closed_tickets)
        
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('tickets_list.html', tickets=[], 
                               open_tickets=[], in_progress_tickets=[], 
                               closed_tickets=[])


@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    """Страница с деталями заявки"""
    try:
        # Временный код - пока нет интеграции с БД
        from storage import Storage
        from services import TicketService
        
        storage = Storage()
        service = TicketService(storage)
        
        ticket = service.get_ticket(ticket_id)
        if not ticket:
            flash('Заявка не найдена', 'error')
            return redirect(url_for('tickets_list'))
        
        # Получаем пользователей
        created_by = storage.get_user(ticket.created_by)
        responsible = (storage.get_user(ticket.responsible_person_id) 
                       if ticket.responsible_person_id else None)
        
        return render_template('ticket_detail.html', 
                               ticket=ticket,
                               created_by=created_by,
                               responsible=responsible)
        
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('tickets_list'))


@app.route('/create-ticket', methods=['GET', 'POST'])
def create_ticket():
    """Страница создания новой заявки"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title or not description:
            flash('Заполните все поля', 'error')
            return render_template('create_ticket.html')
        
        try:
            from storage import Storage
            from services import TicketService
            
            storage = Storage()
            service = TicketService(storage)
            
            # Используем первого пользователя для демонстрации
            users = storage.get_all_users()
            if not users:
                user = service.create_user("Тестовый пользователь")
            else:
                user = users[0]
            
            ticket = service.create_ticket(title, description, user.id)
            flash(f'Заявка #{ticket.id} успешно создана!', 'success')
            return redirect(url_for('ticket_detail', ticket_id=ticket.id))
            
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('create_ticket.html')


@app.route('/manage-ticket/<int:ticket_id>', methods=['GET', 'POST'])
def manage_ticket(ticket_id):
    """Страница управления заявкой (назначение/закрытие)"""
    try:
        from storage import Storage
        from services import TicketService
        
        storage = Storage()
        service = TicketService(storage)
        
        ticket = service.get_ticket(ticket_id)
        if not ticket:
            flash('Заявка не найдена', 'error')
            return redirect(url_for('tickets_list'))
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'assign':
                # Находим ответственного пользователя
                responsible_users = [u for u in storage.get_all_users() if u.is_responsible]
                if responsible_users:
                    service.assign_ticket(ticket.id, responsible_users[0].id)
                    flash('Заявка назначена ответственному', 'success')
                else:
                    flash('Нет ответственных пользователей', 'error')
                    
            elif action == 'close':
                comment = request.form.get('comment', '')
                if not comment:
                    flash('Введите комментарий закрытия', 'error')
                    return render_template('manage_ticket.html', ticket=ticket)
                
                # Находим ответственного для закрытия
                responsible_users = [u for u in storage.get_all_users() if u.is_responsible]
                if responsible_users:
                    service.close_ticket(ticket.id, responsible_users[0].id, comment)
                    flash('Заявка успешно закрыта', 'success')
                else:
                    flash('Нет ответственных пользователей', 'error')
            
            return redirect(url_for('ticket_detail', ticket_id=ticket.id))
        
        return render_template('manage_ticket.html', ticket=ticket)
        
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('tickets_list'))


@app.route('/users')
def users_list():
    """Страница со списком пользователей"""
    try:
        from storage import Storage
        from services import TicketService
        
        storage = Storage()
        service = TicketService(storage)
        
        users = storage.get_all_users()
        tickets = service.get_all_tickets()
        
        return render_template('users_list.html', users=users, tickets=tickets)
        
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('users_list.html', users=[], tickets=[])


# =============== API ЭНДПОИНТЫ ДЛЯ ЗАПРОСОВ ИЗ ЗАДАНИЯ ===============

@app.route('/api/tickets/closed-this-month')
def api_tickets_closed_this_month():
    """API: Список заявок, закрытых в этом месяце (запрос 2)"""
    conn = Config.get_db_connection()
    if not conn:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Запрос 2 из задания
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.title,
                FORMAT(t.closed_at, 'dd.MM.yyyy HH:mm') AS closed_at,
                u_creator.full_name AS created_by,
                u_closer.full_name AS closed_by,
                t.closing_notes,
                DAY(t.closed_at) AS day_closed
            FROM tickets t
            JOIN users u_creator ON t.created_by = u_creator.user_id
            LEFT JOIN users u_closer ON t.closed_by = u_closer.user_id
            WHERE t.status = 'closed'
                AND YEAR(t.closed_at) = YEAR(GETDATE())
                AND MONTH(t.closed_at) = MONTH(GETDATE())
            ORDER BY t.closed_at DESC
        """)
        
        columns = [column[0] for column in cursor.description]
        tickets = []
        for row in cursor.fetchall():
            tickets.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify(tickets)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tickets/by-responsible/<int:responsible_id>')
def api_tickets_by_responsible(responsible_id):
    """API: Список заявок конкретного ответственного (запрос 3)"""
    conn = Config.get_db_connection()
    if not conn:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Запрос 3 из задания с параметром
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.title,
                t.status,
                FORMAT(t.created_at, 'dd.MM.yyyy') AS created_at,
                FORMAT(t.closed_at, 'dd.MM.yyyy') AS closed_at,
                u_creator.full_name AS created_by,
                CASE 
                    WHEN t.status = 'closed' THEN 'Закрыта'
                    WHEN t.status = 'in_progress' THEN 'В работе'
                    WHEN t.status = 'open' THEN 'Открыта'
                    ELSE t.status
                END AS status_text,
                DATEDIFF(DAY, t.created_at, ISNULL(t.closed_at, GETDATE())) AS days_in_work
            FROM tickets t
            JOIN users u_creator ON t.created_by = u_creator.user_id
            WHERE t.assigned_to = ?
            ORDER BY 
                CASE t.status
                    WHEN 'in_progress' THEN 1
                    WHEN 'open' THEN 2
                    WHEN 'closed' THEN 3
                END,
                t.created_at DESC
        """, responsible_id)
        
        columns = [column[0] for column in cursor.description]
        tickets = []
        for row in cursor.fetchall():
            tickets.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify(tickets)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tickets/by-user/<int:user_id>')
def api_tickets_by_user(user_id):
    """API: Список всех заявок пользователя (запрос 4)"""
    conn = Config.get_db_connection()
    if not conn:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Запрос 4 из задания с параметром
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.title,
                LEFT(t.description, 100) + '...' AS short_description,
                t.status,
                t.priority,
                FORMAT(t.created_at, 'dd.MM.yyyy') AS created_at,
                FORMAT(t.closed_at, 'dd.MM.yyyy') AS closed_at,
                u_assigned.full_name AS assigned_to,
                c.name AS category,
                (SELECT COUNT(*) FROM comments WHERE ticket_id = t.ticket_id) AS comments_count,
                (SELECT COUNT(*) FROM attachments WHERE ticket_id = t.ticket_id) AS attachments_count
            FROM tickets t
            LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.user_id
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.created_by = ?
            ORDER BY 
                CASE t.status
                    WHEN 'open' THEN 1
                    WHEN 'in_progress' THEN 2
                    WHEN 'closed' THEN 3
                END,
                t.created_at DESC
        """, user_id)
        
        columns = [column[0] for column in cursor.description]
        tickets = []
        for row in cursor.fetchall():
            tickets.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify(tickets)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ticket/<int:ticket_id>/creator')
def api_ticket_creator(ticket_id):
    """API: Информация о пользователе, создавшем заявку (запрос 5)"""
    conn = Config.get_db_connection()
    if not conn:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Запрос 5 из задания с параметром
        cursor.execute("""
            SELECT 
                u.user_id,
                u.full_name,
                u.email,
                u.phone,
                u.role,
                d.dept_name AS department,
                u_manager.full_name AS department_manager,
                FORMAT(u.created_at, 'dd.MM.yyyy') AS user_registered,
                FORMAT(u.last_login, 'dd.MM.yyyy HH:mm') AS last_login,
                u.is_active,
                -- Статистика пользователя
                (SELECT COUNT(*) FROM tickets WHERE created_by = u.user_id) AS total_tickets,
                (SELECT COUNT(*) FROM tickets WHERE created_by = u.user_id AND status = 'open') AS open_tickets,
                (SELECT COUNT(*) FROM tickets WHERE created_by = u.user_id AND status = 'closed') AS closed_tickets,
                -- Последняя заявка
                (SELECT TOP 1 title FROM tickets WHERE created_by = u.user_id ORDER BY created_at DESC) AS last_ticket
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.dept_id
            LEFT JOIN users u_manager ON d.manager_id = u_manager.user_id
            WHERE u.user_id = (
                SELECT created_by 
                FROM tickets 
                WHERE ticket_id = ?
            )
        """, ticket_id)
        
        columns = [column[0] for column in cursor.description]
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            return jsonify(dict(zip(columns, user)))
        else:
            return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/queries')
def queries_dashboard():
    """Страница с выполнением всех 5 SQL запросов из задания"""
    return render_template('queries_dashboard.html')


if __name__ == '__main__':
    print("Запуск системы заявок...")
    print(f"База данных: {Config.SQL_DATABASE}")
    print(f"Сервер: {Config.SQL_SERVER}")
    print("=" * 50)
    
    # Показываем таблицы при запуске
    tables = Config.get_all_tables()
    if tables:
        print("Найдены таблицы:")
        for table in tables:
            print(f"   - {table}")
    else:
        print("Таблицы не найдены")
    
    app.run(debug=True, host='127.0.0.1', port=5001)