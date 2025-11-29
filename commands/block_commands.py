from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from storage.parquet_store import write_row
from state.state import USERS
from core.pairing import end_conversation

def register_block_handlers(app):
    @app.on_message(filters.command("bloquear") & filters.private)
    async def handle_block(client, message):
        u = message.from_user.id
        us = USERS.get(u)
        if not us or us.status != "conversando" or not us.partner:
            await message.reply("Você não está em uma conversa no momento.")
            return
        partner = us.partner
        write_row("blocks", {"blocker_id": u, "blocked_id": partner, "reason": "user_action"})
        write_row("blocks", {"blocker_id": partner, "blocked_id": u, "reason": "user_action"})
        end_conversation(us.last_conversation_id, u, partner, "bloqueio")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Iniciar Nova Conversa", callback_data="start_conversation")]])
        await client.send_message(u, "Usuário bloqueado. Vocês não serão mais conectados.", reply_markup=kb)
        await client.send_message(partner, "O parceiro encerrou a conversa e bloqueou você.", reply_markup=kb)
