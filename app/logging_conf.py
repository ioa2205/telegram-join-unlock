import logging
from logging.config import dictConfig

from .config import Settings


class UserIdFilter(logging.Filter):
    """A logging filter to add user context if available."""
    def filter(self, record):
        # This is a placeholder; real user ID will be injected by a middleware if needed.
        # For now, it ensures the attribute exists.
        record.user_id = getattr(record, 'user_id', 'N/A')
        return True


def setup_logging(config: Settings):
    """Configures logging for the application."""
    log_level = "DEBUG" if config.is_dev else "INFO"
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [User: %(user_id)s] - %(message)s",
            },
        },
        "filters": {
            "userIdFilter": {
                "()": UserIdFilter,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "filters": ["userIdFilter"],
                "level": log_level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": {
            "aiogram": {
                "level": "INFO",
            },
            "aiosqlite": {
                "level": "INFO",
            },
        },
    }
    dictConfig(logging_config)