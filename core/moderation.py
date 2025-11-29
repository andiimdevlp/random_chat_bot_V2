import json
from storage.parquet_store import write_row
from utils.logger import log_event
from state.state import USERS

def request_ban(target_id:int, requested_by:int, evidence_conversation_id:str, evidence_message_ids:list|None, reason_user:str):
    write_row("bans", {
        "ban_id": None,
        "target_user_id": target_id,
        "requested_by_user_id": requested_by,
        "status": "pendente",
        "reason_user": reason_user,
        "evidence_conversation_id": evidence_conversation_id,
        "evidence_message_ids": json.dumps(evidence_message_ids or []),
    })
    log_event("info","ban.requested", actor=requested_by, conversation_id=evidence_conversation_id, details={"target_user_id":target_id})
    return True

def approve_ban(target_user_id:int, reviewer_id:int, notes:str|None=None, evidence_conversation_id:str|None=None):
    us = USERS.get(target_user_id)
    if us:
        us.status = "banido"
    write_row("bans", {
        "ban_id": None,
        "target_user_id": target_user_id,
        "requested_by_user_id": None,
        "status": "aprovado",
        "reason_user": notes or "",
        "evidence_conversation_id": evidence_conversation_id or (us.last_conversation_id if us else None),
        "evidence_message_ids": "[]",
    })
    write_row("users_status_changes", {
        "user_id": target_user_id,
        "new_status": "banido"
    })
    log_event("info","ban.approved", actor=reviewer_id, conversation_id=evidence_conversation_id, details={"target_user_id":target_user_id})

def reject_ban(target_user_id:int, reviewer_id:int, notes:str|None=None, evidence_conversation_id:str|None=None):
    write_row("bans", {
        "ban_id": None,
        "target_user_id": target_user_id,
        "requested_by_user_id": None,
        "status": "rejeitado",
        "reason_user": notes or "",
        "evidence_conversation_id": evidence_conversation_id,
        "evidence_message_ids": "[]",
    })
    log_event("info","ban.rejected", actor=reviewer_id, conversation_id=evidence_conversation_id, details={"target_user_id":target_user_id})
