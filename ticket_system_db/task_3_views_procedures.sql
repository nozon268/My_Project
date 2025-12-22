--task_3_views_procedures.sql - 4-й модуль
--Представление и хранение процедур

-- 1. Представление для текущих заявок
CREATE OR ALTER VIEW current_tickets_view AS
SELECT 
    t.ticket_id,
    t.title,
    t.status,
    t.priority,
    t.created_at,
    u_creator.full_name AS creator_name,
    u_assigned.full_name AS assigned_name,
    c.name AS category_name,
    DATEDIFF(DAY, t.created_at, GETDATE()) AS days_open
FROM tickets t
LEFT JOIN users u_creator ON t.created_by = u_creator.user_id
LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.user_id
LEFT JOIN categories c ON t.category_id = c.category_id
WHERE t.status IN ('open', 'in_progress')
GO

-- 2. Представление для статистики пользователей
CREATE OR ALTER VIEW user_stats_view AS
SELECT 
    u.user_id,
    u.full_name,
    u.email,
    u.role,
    d.dept_name,
    (SELECT COUNT(*) FROM tickets WHERE created_by = u.user_id) AS tickets_created,
    (SELECT COUNT(*) FROM tickets WHERE assigned_to = u.user_id) AS tickets_assigned,
    (SELECT COUNT(*) FROM tickets WHERE assigned_to = u.user_id AND status = 'closed') AS tickets_closed,
    (SELECT COUNT(*) FROM comments WHERE user_id = u.user_id) AS comments_written
FROM users u
LEFT JOIN departments d ON u.department_id = d.dept_id
GO

-- 3. Хранимая процедура: Получить заявки пользователя
CREATE OR ALTER PROCEDURE GetUserTickets
    @user_id INT
AS
BEGIN
    SELECT 
        t.ticket_id,
        t.title,
        t.status,
        t.priority,
        FORMAT(t.created_at, 'dd.MM.yyyy') AS created_date,
        u_assigned.full_name AS assigned_to,
        c.name AS category,
        (SELECT COUNT(*) FROM comments WHERE ticket_id = t.ticket_id) AS comments_count
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
        t.created_at DESC;
END
GO

-- 4. Хранимая процедура: Закрыть заявку
CREATE OR ALTER PROCEDURE CloseTicket
    @ticket_id INT,
    @closed_by INT,
    @closing_notes TEXT
AS
BEGIN
    BEGIN TRANSACTION;
    
    -- Обновляем заявку
    UPDATE tickets
    SET 
        status = 'closed',
        closed_by = @closed_by,
        closed_at = GETDATE(),
        closing_notes = @closing_notes,
        updated_at = GETDATE()
    WHERE ticket_id = @ticket_id;
    
    -- Запись в историю
    INSERT INTO ticket_history (ticket_id, changed_by, change_type, old_value, new_value)
    VALUES (@ticket_id, @closed_by, 'status_change', 'open/in_progress', 'closed');
    
    COMMIT TRANSACTION;
END
GO

-- 5. Хранимая процедура: Назначить ответственного
CREATE OR ALTER PROCEDURE AssignTicket
    @ticket_id INT,
    @assigned_to INT
AS
BEGIN
    BEGIN TRANSACTION;
    
    -- Обновляем заявку
    UPDATE tickets
    SET 
        assigned_to = @assigned_to,
        assigned_at = GETDATE(),
        updated_at = GETDATE()
    WHERE ticket_id = @ticket_id;
    
    -- Запись в историю
    INSERT INTO ticket_history (ticket_id, changed_by, change_type, old_value, new_value)
    SELECT 
        @ticket_id, 
        @assigned_to,
        'assign', 
        NULL,
        u.full_name
    FROM users u 
    WHERE u.user_id = @assigned_to;
    
    COMMIT TRANSACTION;
END
GO