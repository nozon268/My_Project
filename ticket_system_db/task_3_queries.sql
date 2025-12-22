--task_3_queries.sql - 3-й модуль
--Основные запросы из 3-о задания

--1. Вывожу список текущих заявок:
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
GO

--2. Вывожу список заявок, закрытых в этом месяце:
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
GO

--3. Вывожу список заявок, ответственным за которые является/был конкретный администратор
DECLARE @responsible_id INT = 2;  -- ID ответственного (например, Анна Петрова)

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
WHERE t.assigned_to = @responsible_id
ORDER BY 
    CASE t.status
        WHEN 'in_progress' THEN 1
        WHEN 'open' THEN 2
        WHEN 'closed' THEN 3
    END,
    t.created_at DESC
GO

--4. Вывести список всех польхователей:
DECLARE @user_id INT = 1;  -- ID пользователя (например, Иван Иванов)

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
WHERE t.created_by = @user_id
ORDER BY 
    CASE t.status
        WHEN 'open' THEN 1
        WHEN 'in_progress' THEN 2
        WHEN 'closed' THEN 3
    END,
    t.created_at DESC
GO

--5. Вывести информацию о пользователе, создавшем конкретную заявку:
DECLARE @ticket_id INT = 1;  -- ID заявки

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
    WHERE ticket_id = @ticket_id
)
GO
