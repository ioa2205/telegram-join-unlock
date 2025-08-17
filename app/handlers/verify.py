# app/handlers/verify.py
import logging

from aiogram import Bot, F, Router, types

from app.config import Settings
from app.db import Database
from app.keyboards import get_file_keyboard, get_rejoin_keyboard
from app.locales import MSG_LEFT_CHANNEL, MSG_VERIFY_FAIL, MSG_VERIFIED_SUCCESS
from app.services import analytics, membership, slugs

log = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "verify_join")
async def verify_join_handler(
    query: types.CallbackQuery,
    bot: Bot,
    db: Database,
    config: Settings
):
    user_id = query.from_user.id
    user_data = await db.fetchone("SELECT selected_slug, joined_ok FROM users WHERE user_id = ?", (user_id,))

    if not user_data or not user_data.get("selected_slug"):
        await query.answer("Please use /start with a valid link first.", show_alert=True)
        return

    selected_slug = user_data["selected_slug"]
    is_member = await membership.check_membership(bot, user_id=user_id, chat_id=config.verify_chat_id)

    if is_member:
        if not user_data["joined_ok"]:
            await db.execute("UPDATE users SET joined_ok = 1 WHERE user_id = ?", (user_id,))
        
        slug_data = await slugs.get_slug_data(db, selected_slug)
        if not slug_data:
            await query.message.edit_text("Error: The offer you requested is no longer available.")
            return

        await analytics.log_event(db, user_id, "verify_ok", slug=selected_slug)
        keyboard = get_file_keyboard(slug=selected_slug, label=slug_data["label"])
        await query.message.edit_text(MSG_VERIFIED_SUCCESS, reply_markup=keyboard)
        await query.answer()
        log.info("User %d successfully verified membership for slug %s", user_id, selected_slug)
    else:
        await analytics.log_event(db, user_id, "verify_fail", slug=selected_slug)
        keyboard = get_rejoin_keyboard(config.invite_url)
        
        if query.message.text == MSG_LEFT_CHANNEL:
             await query.answer(MSG_VERIFY_FAIL, show_alert=True)
        else:
            await query.message.edit_text(MSG_VERIFY_FAIL, reply_markup=keyboard)
        
        log.warning("User %d failed membership verification for slug %s", user_id, selected_slug)