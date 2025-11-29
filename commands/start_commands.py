from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from state.state import ensure_user
from utils.logger import log_event

def register_start_handlers(app):
    @app.on_message(filters.command("start") & filters.private)
    async def handle_start(client, message):
        u = message.from_user.id
        ensure_user(u)
        log_event("info","user.seen", actor=u)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Iniciar Conversa", callback_data="start_conversation")]])
        await client.send_message(u, (
            "Bem-vindo ao Chat Anônimo!\n"
            "/conversar — iniciar pareamento\n"
            "/bloquear — bloquear o parceiro atual\n"
            "/novo — encerrar e procurar novo ouvinte\n"
            "/parar — pausar\n"
            "/banir — solicitar banimento (revisão por desenvolvedor)"
        ), reply_markup=keyboard)
