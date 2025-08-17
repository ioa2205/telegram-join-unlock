import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from app.db import Database
from app.services.analytics import log_event

log = logging.getLogger(__name__)


async def get_all_chat_ids(db: Database) -> list[int]:
    """Fetches all user chat_ids from the database."""
    query = "SELECT chat_id FROM users"
    rows = await db.fetchall(query)
    return [row["chat_id"] for row in rows]


async def send_broadcast(
    bot: Bot,
    db: Database,
    from_chat_id: int,
    message: Message,
    rate_limit_sec: int
):
    """Sends a broadcast message to all users."""
    chat_ids = await get_all_chat_ids(db)
    user_count = len(chat_ids)
    log.info("Starting broadcast to %d users.", user_count)

    sleep_interval = 1 / rate_limit_sec
    success_count = 0
    fail_count = 0

    for chat_id in chat_ids:
        try:
            if message.text:
                await bot.send_message(chat_id, message.text, entities=message.entities)
            elif message.photo:
                await bot.send_photo(chat_id, message.photo[-1].file_id, caption=message.caption, caption_entities=message.caption_entities)
            elif message.video:
                await bot.send_video(chat_id, message.video.file_id, caption=message.caption, caption_entities=message.caption_entities)
            elif message.document:
                await bot.send_document(chat_id, message.document.file_id, caption=message.caption, caption_entities=message.caption_entities)

            # Log broadcast success for the target user, not the admin who triggered it
            await log_event(db, user_id=0, event_type="broadcast_sent", slug=f"target_chat:{chat_id}")
            success_count += 1
            log.debug("Broadcast message sent to chat_id: %d", chat_id)
        except TelegramAPIError as e:
            if e.message == "Forbidden: bot was blocked by the user":
                log.warning("User %d blocked the bot. Skipping.", chat_id)
            else:
                log.error("Failed to send message to %d: %s", chat_id, e)
            fail_count += 1
        except Exception as e:
            log.error("An unexpected error occurred sending to %d: %s", chat_id, e)
            fail_count += 1
        
        await asyncio.sleep(sleep_interval)
    
    summary = f"📢 Broadcast finished.\n\n✅ Sent: {success_count}\n❌ Failed: {fail_count}"
    await bot.send_message(from_chat_id, summary)
    log.info("Broadcast finished. Sent: %d, Failed: %d", success_count, fail_count)