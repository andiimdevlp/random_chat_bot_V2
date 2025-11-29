from pyrogram import filters
from state.state import USERS
from core.moderation import request_ban, approve_ban, reject_ban
import os

ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x]

def register_ban_handlers(app):
    @app.on_message(filters.command("banir") & filters.private)
    async def handle_banir(client, message):
        requester = message.from_user.id
        us = USERS.get(requester)
        if not us or not us.partner or not us.last_conversation_id:
            await message.reply("Use este comando durante uma conversa.")
            return
        target = us.partner
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else "Sem descrição fornecida"
        request_ban(target, requester, us.last_conversation_id, None, reason)
        await message.reply("Solicitação de ban registrada. O desenvolvedor analisará antes de qualquer ação.")

    @app.on_message(filters.command("ban") & filters.private)
    async def handle_ban_admin(client, message):
        admin_id = message.from_user.id
        if admin_id not in ADMINS:
            await message.reply(" Você não tem permissão para usar este comando.")
            return
        if len(message.command) < 3:
            await message.reply("Uso: /ban aprovar <user_id> [nota] ou /ban rejeitar <user_id> [nota]")
            return
        action = message.command[1].lower()
        target = int(message.command[2])
        note = " ".join(message.command[3:]) if len(message.command) > 3 else None
        if action == "aprovar":
            approve_ban(target, admin_id, note)
            await message.reply(f"Ban de {target} aprovado.")
        elif action == "rejeitar":
            reject_ban(target, admin_id, note)
            await message.reply(f"Ban de {target} rejeitado.")
        else:
            await message.reply("Ação inválida. Use: aprovar|rejeitar")
