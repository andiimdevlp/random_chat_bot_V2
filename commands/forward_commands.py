from pyrogram import filters
from core.forward import forward_text

def register_forward_handlers(app):
    @app.on_message(filters.text & filters.private & ~filters.command(["conversar","bloquear","novo","banir","parar","ban"]))
    async def handle_forward(client, message):
        ok, err = await forward_text(app, message.from_user.id, message.text)
        if not ok and err:
            await message.reply(err)
