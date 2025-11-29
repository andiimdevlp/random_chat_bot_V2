from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from state.state import USERS
from core.pairing import end_conversation

def register_pause_handlers(app):
    @app.on_message(filters.command("parar") & filters.private)
    async def handle_pause(client, message):
        u = message.from_user.id
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Iniciar Nova Conversa", callback_data="start_conversation")]])
        us = USERS.get(u)
        if us and us.status == "conversando" and us.partner:
            partner = us.partner
            end_conversation(us.last_conversation_id, u, partner, "pausa")
            await client.send_message(u, "Você foi pausado e a conversa foi encerrada. Não receberá novas conexões até retomar.", reply_markup=kb)
            await client.send_message(partner, "Seu parceiro pausou a conversa. Clique abaixo para iniciar uma nova.", reply_markup=kb)
            return
        await client.send_message(u, "Você foi pausado. Não receberá novas conexões até usar /conversar.", reply_markup=kb)
