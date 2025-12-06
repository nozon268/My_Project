#app.py - Главное Flask приложение
#Это 4-й модуль

from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser as web
import threading as thread
import time

#Мои модули
from storage import *
from services import *
from models import *

app = Flask(__name__)
app.secret_key = 'MY-SECRET-KEY-!'

#Установка сервисов
storage = Storage()
service = TicketService(storage)

def setup():
    """Создание тестовых пользователей"""
    regular_user = service.create_user("Иван Петров (Пользователь)")
    responsible_user = service.create_user("Анна Сидорова (Ответственный)", is_responsible=True)
    print(f"Создан пользователь: {regular_user.name} (ID: {regular_user.id})")
    print(f"Создан ответственный: {responsible_user.name} (ID: {responsible_user.id})")

def open_browser():
    """Открывает браузер после небольшой задержки"""
    time.sleep(1.5)
    web.open_new('http://127.0.0.1:5000')

@app.before_request
def before_first_request():
    """Выполняется перед первым запросом"""
    if not hasattr(app, 'has_stup'):
        setup()
        app.has_setup = True

@app.route('/')
def index():
    """Главная страница"""
    users = storage.get_all_users()
    tickets_count = len(storage.get_all_tickets())
    return render_template('index.html', users=users, ticket_count=tickets_count)

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    """Создание заявки"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Пользователь(ID=1) создает заявку
        try:
            ticket = service.create_ticket(title, description, 1)
            flash(f"Заявка #{ticket.id} успешно создана!", "success")
            return redirect(url_for("tickets_list"))
        except ValueError as e:
            flash(f"Ошибка: {e}", "error")
    return render_template("create_ticket.html")

@app.route('/tickets')
def tickets_list():
    tickets = service.get_all_tickets()
    open_tickets = service.get_open_ticket()
    in_progress_tickets = service.get_in_progress_tickets()
    closed_tickets = service.get_closed_ticket()

    return render_template('tickets_list.html', tickets=tickets, open_tickets=open_tickets, in_progress_tickets=in_progress_tickets, closed_tickets=closed_tickets)

@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        flash("Заявка не найдена", "error")
        return redirect(url_for("tickets_list"))
    
    create_by = storage.get_user(ticket.created_by)
    responsible = (storage.get_user(ticket.responsible_person_id) if ticket.responsible_person_id else None)
    return render_template("ticket_detail.html", ticket=ticket, create_by=create_by, responsible=responsible)

@app.route('/manager_ticket/<int:ticket_id>', methods = ['GET', 'POST'])
def manage_ticket(ticket_id):
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        flash("Заявка не найдена", "error")
        return redirect(url_for("tickets_list"))
    
    if request.method == 'POST':
        action = request.form["action"]
        #Ответственный сотрудник(ID=2)
        responsible_id = 2

        try:
            if action == "assign":
                service.assign_ticket(ticket_id, responsible_id)
                flash("Заявка принята в работу!", "success")
            elif action == "close":
                comment = request.form["comment"]
                service.close_ticket(ticket_id, responsible_id, comment)
                flash("Заявка закрыта!", "success")
        except ValueError as e:
            flash(f"Ошибка: {e}", "error")

        return redirect(url_for("ticket_detail", ticket_id=ticket_id))
    
    return render_template("manage_ticket.html", ticket=ticket)

@app.route('/users')
def users_list():
    users = storage.get_all_users()
    return render_template("users_list.html", users = users)

if __name__ == "__main__":
    print("Запуск системы обработки заявок...")
    print("Сервер запускается, пожалуйста подождите...")

    #Создаю тестовых пользователей сразу при запуске
    setup()

    #Запускаю открытие браузера в отдельном потоке
    thread.Thread(target=open_browser).start()

    #Запускаю Flask приложение
    print("Сервер запущен! Открываю браузер...")
    print("Приложение доступно по адресу: http://127.0.0.1:5000")
    print("Чтобы остановить сервер, нажмите Ctrl+C в этом окне")

    app.run(debug=True, use_reloader=False)
    