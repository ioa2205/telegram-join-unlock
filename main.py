# main.py
import asyncio
import logging

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import Settings, load_config
from app.db import Database
from app.handlers import admin, files, start, verify
from app.locales import CMD_ADMIN, CMD_START, CMD_STATS
from app.logging_conf import setup_logging
from app.middlewares import AntiSpamMiddleware

async def set_bot_commands(bot: Bot, config: Settings):
    user_commands = [BotCommand(command="start", description=CMD_START)]
    await bot.set_my_commands(commands=user_commands, scope=BotCommandScopeDefault())
    admin_commands = [
        BotCommand(command="start", description=CMD_START),
        BotCommand(command="admin", description=CMD_ADMIN),
        BotCommand(command="stats", description=CMD_STATS),
    ]
    for admin_id in config.admin_ids:
        await bot.set_my_commands(commands=admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
    logging.info("Bot command menus have been set.")


async def on_startup(bot: Bot, config: Settings):
    """Function to be called on application startup (for webhook mode)."""
    await set_bot_commands(bot, config)
    await bot.set_webhook(
        url=config.webhook_url,
        drop_pending_updates=True,
        secret_token=config.bot_token.get_secret_value()[:10] # Optional secret for more security
    )
    logging.info("Webhook set to %s", config.webhook_url)

async def on_shutdown(bot: Bot):
    """Function to be called on application shutdown."""
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    logging.info("Webhook deleted.")


async def main():
    """Main function to start the bot."""
    config = load_config()
    setup_logging(config)
    log = logging.getLogger(__name__)
    log.info("Starting bot...")

    storage = MemoryStorage()
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)

    db = Database(config.postgres_dsn)
    await db.connect()

    dp.callback_query.middleware(AntiSpamMiddleware())
    
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(verify.router)
    dp.include_router(files.router)
    
    dp["db"] = db
    dp["config"] = config
    dp["bot"] = bot

    try:
        if config.use_webhook:
            # --- WEBHOOK MODE ---
            log.info("Running in webhook mode")
            # Register startup and shutdown handlers
            dp.startup.register(on_startup)
            dp.shutdown.register(on_shutdown)
            
            app = web.Application()
            webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
            webhook_requests_handler.register(app, path=config.webhook_path)
            
            setup_application(app, dp, bot=bot, config=config)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, config.web_server_host, config.web_server_port)
            await site.start()
            
            log.info("Web server started at http://%s:%s", config.web_server_host, config.web_server_port)
            await asyncio.Event().wait() # Keep the server running forever

        else:
            # --- POLLING MODE ---
            log.info("Running in polling mode")
            await set_bot_commands(bot, config)
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

    finally:
        await db.disconnect()
        log.info("Bot stopped and database connection closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("Bot shutdown initiated.")