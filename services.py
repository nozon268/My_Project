#services.py - Отвечает за работу заявок и пользователей
#Это 3-й модуль

from datetime import datetime
from typing import List, Optional

#Мои модули
from models import Ticket, User, TicketStatus
from storage import Storage

class TicketService:

    def __init__(self, storage: Storage):
        self.storage = storage

    def create_user(self, name: str, is_responsible: bool = False) -> User:
        """Создает нового пользователя"""
        user = User(id = 0, name = name, is_responsible = is_responsible)
        return self.storage.add_user(user)

    def create_ticket(self, title: str, description: str, user_id: int) -> Ticket:
        """Создает новую заявку от имени пользователя"""
        user = self.storage.get_user(user_id)
        if not user:
            raise ValueError("Пользователь не найден!")
        
        ticket = Ticket(
            id=0,
            title=title,
            description=description,
            created_by=user_id,
            created_at=datetime.now(),
            status=TicketStatus.OPEN
        )
        return self.storage.add_ticket(ticket)

    def get_all_tickets(self) -> List[Ticket]:
        """Возвращает все заявки"""
        return self.storage.get_all_tickets()

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Возвращает заявки по ID"""
        return self.storage.get_ticket(ticket_id)

    def get_user_tickets(self, user_id: int) -> List[Ticket]:
        """Возвращает заявки конкретного пользователя"""
        all_tickets = self.storage.get_all_tickets()
        return [ticket for ticket in all_tickets if ticket.created_by == user_id]

    def assign_ticket(self, ticket_id: int, responsible_user_id: int) -> Ticket:
        """Назначает ответственного на заявку"""
        ticket = self.storage.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Заявка с ID {ticket_id} не найдена")
        
        responsible_user = self.storage.get_user(responsible_user_id)
        if not responsible_user:
            raise ValueError(f"Пользователь с ID {responsible_user_id} не найден")
        
        if not responsible_user.is_responsible:
            raise ValueError(f"Пользователь {responsible_user.name} не является ответственным")
        
        if ticket.status == TicketStatus.CLOSED:
            raise ValueError("Нельзя назначить ответственного на закрытую заявку")

        ticket.status = TicketStatus.IN_PROGRESS
        ticket.responsible_person_id = responsible_user_id
        self.storage.update_ticket(ticket)
        return ticket

    def close_ticket(self, ticket_id: int, responsible_user_id: int, comment: str) -> Ticket:        
        """Закрывает заявки с комментарием"""
        ticket = self.storage.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Заявка с ID {ticket_id}")
        
        responsible_user = self.storage.get_user(responsible_user_id)
        if not responsible_user:
            raise ValueError(f"Пользователь с ID {responsible_user_id} не найден")
        
        if not responsible_user.is_responsible:
            raise ValueError(f"Пользователь {responsible_user.name} не является ответственным")
        
        if ticket.responsible_person_id != responsible_user_id:
            raise ValueError("Только назначенный ответственный может закрывать заявку")
        
        if ticket.status == TicketStatus.CLOSED:
            raise ValueError("Заявка уже закрыта")
        
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.now()
        ticket.closing_comment = comment
        self.storage.update_ticket(ticket)
        return ticket

    def get_open_ticket(self) -> List[Ticket]:
        """Возвращает открытые заявоки"""
        all_tickets = self.storage.get_all_tickets()
        return [ticket for ticket in all_tickets if ticket.status == TicketStatus.OPEN]

    def get_in_progress_tickets(self) -> List[Ticket]:
        """Возвращает заявки в работе"""
        all_tickets = self.storage.get_all_tickets()
        return [ticket for ticket in all_tickets if ticket.status == TicketStatus.IN_PROGRESS]

    def get_closed_ticket(self) -> List[Ticket]:
        """Возвращает закрытые заявки"""
        all_tickets = self.storage.get_all_tickets()
        return [ticket for ticket in all_tickets if ticket.status == TicketStatus.CLOSED]