--task_3.sql - Основной модуль из 2-о задания
--Здесь создается БД и таблицы

--Создание таблицы users
CREATE TABLE [users] (
  [user_id] integer PRIMARY KEY,
  [user_name] varchar(50) UNIQUE NOT NULL,
  [email] varchar(100) UNIQUE NOT NULL,
  [password] varchar(255) NOT NULL,
  [full_name] varchar(100) NOT NULL,
  [role] varchar(50) DEFAULT 'user',
  [department_id] integer,
  [phone] varchar(20),
  [avatar_url] text,
  [is_active] boolean DEFAULT (true),
  [created_at] timestamp DEFAULT (now()),
  [last_login] timestamp
)
GO

--Создание таблицы departaments
CREATE TABLE [departments] (
  [dept_id] integer PRIMARY KEY,
  [dept_name] varchar(100) UNIQUE NOT NULL,
  [manager_id] integer,
  [location] varchar(200),
  [description] text,
  [color] varchar(7) DEFAULT '#3498db',
  [icon] varchar(50),
  [created_at] timestamp DEFAULT (now())
)
GO

--Создание categories
CREATE TABLE [categories] (
  [category_id] integer PRIMARY KEY,
  [name] varchar(50) UNIQUE NOT NULL,
  [description] text,
  [color] varchar(7) DEFAULT '#3498db',
  [icon] varchar(50),
  [created_at] timestamp DEFAULT (now())
)
GO

--Создание tickets 
CREATE TABLE [tickets] (
  [ticket_id] integer PRIMARY KEY,
  [title] varchar(200) NOT NULL,
  [description] text NOT NULL,
  [status] varchar(50) DEFAULT 'open',
  [priority] varchar(10) DEFAULT 'medium',
  [category_id] integer,
  [created_by] integer NOT NULL,
  [created_at] timestamp DEFAULT (now()),
  [assigned_to] integer,
  [assigned_at] timestamp,
  [closed_by] integer,
  [closed_at] timestamp,
  [closing_notes] text,
  [deadline] date,
  [updated_at] timestamp DEFAULT (now())
)
GO

--Создание comments
CREATE TABLE [comments] (
  [comment_id] integer PRIMARY KEY,
  [ticket_id] integer NOT NULL,
  [user_id] integer NOT NULL,
  [comment_text] text NOT NULL,
  [is_internal] boolean DEFAULT (false),
  [created_at] timestamp DEFAULT (now())
)
GO

--Создание таблицы attachments
CREATE TABLE [attachments] (
  [file_id] integer PRIMARY KEY,
  [ticket_id] integer NOT NULL,
  [user_id] integer NOT NULL,
  [filename] varchar(255) NOT NULL,
  [filepath] text NOT NULL,
  [file_size] integer,
  [mime_type] varchar(100),
  [uploaded_at] timestamp DEFAULT (now())
)
GO

--Создание таблицы ticket_history
CREATE TABLE [ticket_history] (
  [history_id] integer PRIMARY KEY,
  [ticket_id] integer NOT NULL,
  [changed_by] integer NOT NULL,
  [change_type] varchar(50) NOT NULL,
  [old_value] text,
  [new_value] text,
  [changed_at] timestamp DEFAULT (now())
)
GO

--Добавляю внешние ключи:
ALTER TABLE [users] ADD FOREIGN KEY ([department_id]) REFERENCES [departments] ([dept_id])
GO

ALTER TABLE [departments] ADD FOREIGN KEY ([manager_id]) REFERENCES [users] ([user_id])
GO

ALTER TABLE [tickets] ADD FOREIGN KEY ([category_id]) REFERENCES [categories] ([category_id])
GO

ALTER TABLE [tickets] ADD FOREIGN KEY ([created_by]) REFERENCES [users] ([user_id])
GO

ALTER TABLE [tickets] ADD FOREIGN KEY ([assigned_to]) REFERENCES [users] ([user_id])
GO

ALTER TABLE [tickets] ADD FOREIGN KEY ([closed_by]) REFERENCES [users] ([user_id])
GO

ALTER TABLE [comments] ADD FOREIGN KEY ([ticket_id]) REFERENCES [tickets] ([ticket_id])
GO

ALTER TABLE [comments] ADD FOREIGN KEY ([user_id]) REFERENCES [users] ([user_id])
GO

ALTER TABLE [attachments] ADD FOREIGN KEY ([ticket_id]) REFERENCES [tickets] ([ticket_id])
GO

ALTER TABLE [attachments] ADD FOREIGN KEY ([user_id]) REFERENCES [users] ([user_id])
GO

ALTER TABLE [ticket_history] ADD FOREIGN KEY ([ticket_id]) REFERENCES [tickets] ([ticket_id])
GO

ALTER TABLE [ticket_history] ADD FOREIGN KEY ([changed_by]) REFERENCES [users] ([user_id])
GO
