#models.py - Структура данных (заявки и пользователи)
#Это 1-й модуль

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

#Статус заявки
class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

#Структура пользователя
@dataclass
class User:
    id: int
    name: str
    is_responsible: bool = False

#Структура заявки
@dataclass
class Ticket:
    id: int
    title: str
    description: str
    created_by: int #ID Юзера
    created_at: datetime
    status: TicketStatus = TicketStatus.OPEN
    responsible_person_id: Optional[int] = None
    closed_at: Optional[datetime] = None
    closing_comment: Optional[str] = None