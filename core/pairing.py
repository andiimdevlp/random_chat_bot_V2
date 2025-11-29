from datetime import datetime, timezone
from utils.idgen import new_id
from storage.parquet_store import write_row
from state.state import ensure_user, enqueue as q_enqueue, WAITING, start_conversation, end_conversation as st_end_conv
from utils.logger import log_event

def try_match(me: int):
    u = ensure_user(me)
    if u.status == "banido":
        return None, "Você está impedido de iniciar conversas no momento."

    partner = None
    for cand in list(WAITING):
        if cand != me:
            partner = cand
            break

    if partner is None:
        q_enqueue(me)
        log_event("info", "queue.enqueued", actor=me)
        return None, "Sem ouvintes disponíveis agora — você entrou na fila."

    conv_id = new_id()
    start_conversation(me, partner, conv_id)
    log_event("info", "match.created", actor=me, conversation_id=conv_id,
              details={"user_a": me, "user_b": partner})

    write_row("conversations", {
        "conversation_id": conv_id,
        "user_a_id": me,
        "user_b_id": partner,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
        "status": "ativa",
        "closed_reason": None,
    })
    return {"conversation_id": conv_id, "partner": partner}, None

def end_conversation(conv_id: str, a: int, b: int, reason: str):
    st_end_conv(a, b)
    log_event("info", "match.ended", conversation_id=conv_id, details={"reason": reason})

    write_row("conversations", {
        "conversation_id": conv_id,
        "user_a_id": a,
        "user_b_id": b,
        "started_at": None,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "status": "encerrada",
        "closed_reason": reason,
    })

    try:
        from core.compaction import compact_conversation_messages
        compact_conversation_messages(conv_id)
    except Exception as e:
        log_event("warn", "messages.compaction_failed", conversation_id=conv_id, details={"error": str(e)})
