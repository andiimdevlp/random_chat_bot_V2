# commands/chat_commands.py
from pyrogram import filters
from state.state import ensure_user
from core.pairing import try_match

def register_chat_handlers(app):
    @app.on_message(filters.command("conversar") & filters.private)
    async def handle_conversar(client, message):
        # ignora bots por segurança
        if getattr(message.from_user, "is_bot", False):
            return
        u = message.from_user.id
        ensure_user(u)
        conv, err = try_match(u)
        if err:
            await message.reply(err)
            return
        partner = conv["partner"]
        await client.send_message(u, "Você está conectado. Diga algo.")
        await client.send_message(partner, "Você está conectado. Diga algo.")

    @app.on_callback_query(filters.regex("start_conversation"))
    async def start_cb(client, cq):
        # quem clicou é o usuário correto
        if getattr(cq.from_user, "is_bot", False):
            await cq.answer()
            return
        u = cq.from_user.id
        ensure_user(u)
        conv, err = try_match(u)
        if err:
            await cq.message.reply(err)
            await cq.answer()
            return
        partner = conv["partner"]
        await client.send_message(u, "Você está conectado. Diga algo.")
        await client.send_message(partner, "Você está conectado. Diga algo.")
        await cq.answer()
