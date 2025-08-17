# app/handlers/start.py
import logging

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from app.config import Settings
from app.db import Database
from app.keyboards import get_pre_verify_keyboard
from app.locales import MSG_START_NO_PAYLOAD, MSG_START_PRE_VERIFY_WITH_SLUG
from app.services import analytics, slugs

log = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message,
    db: Database,
    config: Settings,
    state: FSMContext,
):
    user = message.from_user
    chat_id = message.chat.id
    payload = (message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None)

    user_query = """
    INSERT INTO users (user_id, chat_id, selected_slug) VALUES (?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        selected_slug = excluded.selected_slug,
        updated_at = CURRENT_TIMESTAMP;
    """
    await db.execute(user_query, (user.id, chat_id, payload))

    if not payload or not slugs.is_valid_slug(payload):
        await message.answer(MSG_START_NO_PAYLOAD)
        log.warning("User %d started without a valid payload.", user.id)
        return

    slug_data = await slugs.get_slug_data(db, payload)
    if not slug_data:
        await message.answer(MSG_START_NO_PAYLOAD)
        log.warning("User %d started with an invalid or inactive slug: %s", user.id, payload)
        return

    await analytics.log_event(db, user.id, "start", slug=payload)
    
    welcome_text = MSG_START_PRE_VERIFY_WITH_SLUG.format(
        user_name=hbold(user.first_name),
        slug_label=slug_data['label']
    )
    
    keyboard = get_pre_verify_keyboard(config.invite_url)
    await message.answer(welcome_text, reply_markup=keyboard)
    log.info("User %d started with slug '%s'. Sent verification prompt.", user.id, payload)