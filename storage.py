#storage.py - Хранит и манипулирует данными (БД)
#Это 2-й модуль

from typing import Dict, List, Optional

#Мой 1-й модуль
from models import Ticket, User

class Storage:

    def __init__(self):
        self.tickets: Dict[int, Ticket] = {}
        self.users: Dict[int, User] = {}
        self.next_user_id = 1
        self.next_ticket_id = 1

    def add_user(self, user: User) -> User:
        """Добовляет пользователя и присваевает ему ID"""
        user.id = self.next_user_id
        self.users[user.id] = user
        self.next_user_id += 1
        return user

    def add_ticket(self, ticket: Ticket) -> Ticket:
        """Добовляет заявку и присваевает ей ID"""
        ticket.id = self.next_ticket_id
        self.tickets[ticket.id] = ticket
        self.next_ticket_id += 1
        return ticket
    
    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Возвращает заявку по ID или None если не найдена"""
        return self.tickets.get(ticket_id)
    
    def get_all_tickets(self) -> List[Ticket]:
        """Возвращает список всех заявок"""
        return list(self.tickets.values())
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Возвращает пользователя по ID или None если не найден"""
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """ВОзвращает список всех пользователелей"""
        return list(self.users.values())
    
    def update_ticket(self, ticket: Ticket) -> None:
        """Обновляет заявку в хранилище"""
        if ticket.id in self.tickets:
            self.tickets[ticket.id] = ticket

    def delete_ticket(self, ticket_id: int) -> bool:
        """Удаляет заявку по ID и возвращает True если удалено"""
        if ticket_id in self.tickets:
            del self.tickets[ticket_id]
            return True
        return False