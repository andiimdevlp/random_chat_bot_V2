import json
from datetime import datetime, timezone
from storage.parquet_store import write_row

def log_event(level: str, event_type: str, actor: int | None = None,
              conversation_id: str | None = None, details: dict | None = None):
    write_row("app_events", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "event_type": event_type,
        "actor_user_id": actor,
        "conversation_id": conversation_id,
        "details": json.dumps(details or {}, ensure_ascii=False)
    })

    print(f"[{level.upper()}] {event_type} - actor: {actor}, conv: {conversation_id}, details: {details}")