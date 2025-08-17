import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

log = logging.getLogger(__name__)

ALLOWED_STATUSES = ["member", "administrator", "creator"]


async def check_membership(bot: Bot, user_id: int, chat_id: int | str) -> bool:
    """Checks if a user is a member of the specified chat."""
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        is_member = member.status in ALLOWED_STATUSES
        log.info("Checked user %d membership in chat %s: status is '%s', result: %s", user_id, chat_id, member.status, is_member)
        return is_member
    except TelegramAPIError as e:
        log.error("Could not check membership for user %d in chat %s: %s", user_id, chat_id, e)
        return False
    except Exception as e:
        log.error("Unexpected error checking membership for user %d: %s", user_id, chat_id, e)
        return False