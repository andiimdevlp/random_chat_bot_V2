from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from state.state import USERS
from core.pairing import end_conversation, try_match

def register_new_handlers(app):
    @app.on_message(filters.command("novo") & filters.private)
    async def handle_new(client, message):
        u = message.from_user.id
        us = USERS.get(u)
        if us and us.status == "conversando" and us.partner:
            partner = us.partner
            end_conversation(us.last_conversation_id, u, partner, "novo")
            await client.send_message(u, "Você encerrou a conversa atual. Procurando um novo ouvinte...")
            await client.send_message(partner, "Seu ouvinte encerrou a conversa. Você está livre para uma nova conexão.")
        new_conv, err = try_match(u)
        if new_conv:
            await client.send_message(u, "Você está conectado. Diga algo ao seu novo ouvinte.")
            await client.send_message(new_conv["partner"], "Você está conectado. Diga algo ao seu novo ouvinte.")
        else:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("Iniciar Conversa", callback_data="start_conversation")]])
            await client.send_message(u, "Não há nenhum outro ouvinte disponível no momento. Aguarde ou tente novamente mais tarde.", reply_markup=kb)
