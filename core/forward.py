import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from storage.parquet_store import write_message_chunk
from utils.logger import log_event
from state.state import USERS

load_dotenv()
PRIVACY_STORE = os.getenv("PRIVACY_STORE_MESSAGE_CONTENT")

async def forward_text(app, from_id: int, text: str):
    try:
        us = USERS.get(from_id)
        if not us or us.status != "conversando" or not us.partner:
            return False, "Você não está em uma conversa no momento."
        
        partner = us.partner
        sent = await app.send_message(partner, f"Ouvinte disse: {text}")

        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "conversation_id": us.last_conversation_id,
            "from_user_id": from_id,
            "to_user_id": partner,
            "msg_type": "text",
            "size_bytes": len(text.encode("utf-8")) if text is not None else None,
            "meta": {"pyrogram_msg_id": sent.id},
            "content_present": PRIVACY_STORE,
        }
        if PRIVACY_STORE:
            row["content"] = text

        write_message_chunk(us.last_conversation_id, row)
        log_event("info", "msg.forwarded", actor=from_id, conversation_id=us.last_conversation_id,
                details={"pyrogram_msg_id": sent.id})
        return True, None
    
    except Exception as e:
        log_event("error", "msg.forward_failed", actor=from_id, 
                  details={"error": str(e)})
        return False, "Erro ao enviar mensagem. Tente novamente."