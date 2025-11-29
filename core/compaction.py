from storage.parquet_store import compact_messages
from utils.logger import log_event

def compact_conversation_messages(conversation_id: str):
    stats = compact_messages(conversation_id, delete_chunks=True)
    log_event("info", "messages.compacted", conversation_id=conversation_id, details=stats)
    return stats
