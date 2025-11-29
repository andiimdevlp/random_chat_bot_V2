from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import deque
import threading

LOCK = threading.Lock()

@dataclass
class UserState:
    user_id: int
    status: str = "livre"   # livre|conversando|pausado|banido
    partner: int | None = None
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_conversation_id: str | None = None

USERS: dict[int, UserState] = {}
WAITING: deque[int] = deque()

def now():
    return datetime.now(timezone.utc)

def ensure_user(u: int) -> UserState:
    us = USERS.get(u)
    if not us:
        us = UserState(user_id=u)
        USERS[u] = us
    us.last_seen = now()
    return us

def set_status(u: int, status: str):
    us = ensure_user(u)
    us.status = status
    us.last_seen = now()

def enqueue(u: int):
    with LOCK:
        us = ensure_user(u)
        if us.status == "banido":
            return False
        if u not in WAITING:
            WAITING.append(u)
        us.status = "livre"
        us.partner = None
        return True

def dequeue(u:int):
    try:
        WAITING.remove(u)
    except ValueError:
        pass

def start_conversation(a:int, b:int, conv_id:str):
    ua = ensure_user(a); ub = ensure_user(b)
    ua.status = "conversando"; ub.status = "conversando"
    ua.partner = b; ub.partner = a
    ua.last_conversation_id = conv_id; ub.last_conversation_id = conv_id
    dequeue(a); dequeue(b)

def end_conversation(a:int, b:int):
    ua = ensure_user(a); ub = ensure_user(b)
    ua.status = "livre"; ub.status = "livre"
    ua.partner = None; ub.partner = None
