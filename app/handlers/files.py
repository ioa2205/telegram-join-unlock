# app/handlers/files.py
import logging

from aiogram import Bot, F, Router, types

from app.config import Settings
from app.db import Database
from app.keyboards import get_rejoin_keyboard
from app.locales import MSG_LEFT_CHANNEL
from app.services import analytics, membership, slugs

log = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("send:"))
async def send_file_handler(
    query: types.CallbackQuery,
    bot: Bot,
    db: Database,
    config: Settings,
):
    user_id = query.from_user.id
    try:
        slug_to_send = query.data.split(":", 1)[1]
    except IndexError:
        await query.answer("Invalid request.", show_alert=True)
        return

    is_member = await membership.check_membership(bot, user_id=user_id, chat_id=config.verify_chat_id)

    if not is_member:
        keyboard = get_rejoin_keyboard(config.invite_url)
        await query.message.edit_text(MSG_LEFT_CHANNEL, reply_markup=keyboard)
        await query.answer()
        log.warning("User %d attempted to get file for slug %s but is no longer a member.", user_id, slug_to_send)
        return

    slug_data = await slugs.get_slug_data(db, slug_to_send)
    if not slug_data or slug_data["file_id"] == "MISSING":
        await query.answer("Sorry, this file is not available at the moment.", show_alert=True)
        return
        
    try:
        await bot.send_document(
            chat_id=query.from_user.id,
            document=slug_data["file_id"],
            caption=slug_data["label"]
        )
        await query.answer()
        log.info("Sent file for slug '%s' to user %d.", slug_to_send, user_id)
        
        await analytics.log_event(db, user_id, "file_sent", slug=slug_to_send)
    except Exception as e:
        log.error("Failed to send document for slug %s to user %d: %s", slug_to_send, user_id, e)
        await query.answer("An error occurred while sending the file.", show_alert=True)