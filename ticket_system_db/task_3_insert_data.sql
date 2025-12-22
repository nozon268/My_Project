--task_3_insert_data.sql - 2-й модуль: \
--Создаются тестовые данные для дальнейший работы с ними

--Создаю БД
USE [TicketDB]
GO

--Вставляю отделы:
INSERT INTO departments (dept_name, location, description, color) 
VALUES 
('IT отдел', '3 этаж', 'Отдел информационных технологий', '#3498db'),
('Бухгалтерия', '2 этаж', 'Финансовый отдел', '#2ecc71'),
('HR отдел', '1 этаж', 'Отдел кадров', '#e74c3c'),
('Отдел продаж', '4 этаж', 'Коммерческий отдел', '#f39c12')
GO

--Вставляю пользователей:
INSERT INTO users (user_name, email, password, full_name, role, department_id, phone) 
VALUES 
('ivanov', 'ivanov@company.com', 'hashed_pass1', 'Иван Иванов', 'user', 1, '+79991112233'),
('petrova', 'petrova@company.com', 'hashed_pass2', 'Анна Петрова', 'responsible', 1, '+79992223344'),
('sidorov', 'sidorov@company.com', 'hashed_pass3', 'Петр Сидоров', 'admin', 2, '+79993334455'),
('smirnova', 'smirnova@company.com', 'hashed_pass4', 'Ольга Смирнова', 'responsible', 3, '+79994445566'),
('kozlov', 'kozlov@company.com', 'hashed_pass5', 'Алексей Козлов', 'user', 4, '+79995556677')
GO

--Обновляю менеджеров отделов:
UPDATE departments SET manager_id = 2 WHERE dept_id = 1  -- IT отдел: Петрова
UPDATE departments SET manager_id = 3 WHERE dept_id = 2  -- Бухгалтерия: Сидоров
UPDATE departments SET manager_id = 4 WHERE dept_id = 3  -- HR: Смирнова
GO

--Вставляю категории:
INSERT INTO categories (name, description, color) 
VALUES 
('Оборудование', 'Проблемы с оборудованием', '#e74c3c'),
('Программное обеспечение', 'Проблемы с ПО', '#3498db'),
('Сеть и интернет', 'Проблемы с подключением', '#2ecc71'),
('Учетные записи', 'Проблемы с доступом', '#f39c12'),
('Обучение', 'Запросы на обучение', '#9b59b6')
GO

--Вставляю заявки:
INSERT INTO tickets (title, description, status, priority, category_id, created_by, assigned_to) 
VALUES 
('Не работает принтер', 'Принтер в кабинете 301 не печатает', 'open', 'medium', 1, 1, 2),
('Установить Windows', 'Нужно установить Windows на новый ПК', 'in_progress', 'high', 2, 1, 2),
('Нет доступа к интернету', 'В отделе продаж нет интернета', 'open', 'high', 3, 5, NULL),
('Создать учетную запись', 'Новому сотруднику нужен доступ', 'closed', 'medium', 4, 5, 4),
('Обучение Excel', 'Нужно провести обучение по Excel', 'open', 'low', 5, 3, NULL),
('Сломался сканер', 'Сканер в бухгалтерии не работает', 'in_progress', 'medium', 1, 3, 2),
('Обновить антивирус', 'Требуется обновление антивирусного ПО', 'open', 'high', 2, 4, NULL)
GO

--Обновляю даты назначения и закрытия для некоторых заявок:
UPDATE tickets SET assigned_at = DATEADD(DAY, -2, GETDATE()) WHERE ticket_id IN (1, 2, 6)
UPDATE tickets SET closed_at = DATEADD(DAY, -1, GETDATE()), closed_by = 4 WHERE ticket_id = 4
UPDATE tickets SET closing_notes = 'Учетная запись создана, пароль отправлен на почту' WHERE ticket_id = 4
GO

--Вставляю комментарии:
INSERT INTO comments (ticket_id, user_id, comment_text, is_internal) 
VALUES 
(1, 2, 'Проверил принтер. Нужна замена картриджа.', 0),
(1, 1, 'Когда будет заменен картридж?', 0),
(2, 2, 'Windows установлена, требуется активация.', 0),
(4, 4, 'Учетная запись создана: login: new_user, пароль: Temp123', 1),
(6, 2, 'Сканер отправлен в ремонт. Ожидаем 3 дня.', 0)
GO

--Вставляю историю изменений:
INSERT INTO ticket_history (ticket_id, changed_by, change_type, old_value, new_value) 
VALUES 
(1, 2, 'assign', NULL, 'Назначено на Анна Петрова'),
(2, 2, 'status_change', 'open', 'in_progress'),
(4, 4, 'status_change', 'in_progress', 'closed'),
(4, 4, 'comment', NULL, 'Заявка закрыта'),
(6, 2, 'assign', NULL, 'Назначено на Анна Петрова')
GO
