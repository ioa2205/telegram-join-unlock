import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery


class AntiSpamMiddleware(BaseMiddleware):
    """
    A middleware to prevent users from spamming callback buttons.
    """
    def __init__(self, limit_sec: int = 1):
        self.limit = limit_sec
        self.last_requests: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.monotonic()

        if user_id in self.last_requests and current_time - self.last_requests[user_id] < self.limit:
            await event.answer("Please do not press so often.", show_alert=False)
            return

        self.last_requests[user_id] = current_time
        return await handler(event, data)