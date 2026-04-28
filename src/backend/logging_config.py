import logging
import os
from logging.handlers import TimedRotatingFileHandler

_LOG_DIR = "logs"
_LOG_FILE = "nova.log"


def _build_file_handler() -> TimedRotatingFileHandler:
    """Create and return the shared TimedRotatingFileHandler."""
    os.makedirs(_LOG_DIR, exist_ok=True)
    log_path = os.path.join(_LOG_DIR, _LOG_FILE)

    handler = TimedRotatingFileHandler(
        log_path,
        when="midnight",   # roll over at 00:00 local time
        interval=1,        # every 1 day
        backupCount=30,    # keep 30 days, then delete
        encoding="utf-8",
        utc=False,         # set True if you prefer UTC rollover times
    )
    handler.suffix = "%Y-%m-%d"  # archive name: nova.log.2026-04-17
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    return handler


def get_uvicorn_log_config() -> dict:
    """
    Return a log_config dict to pass directly to uvicorn.run().
    This ensures startup messages ("Started server process", "Application
    startup complete", etc.) are captured before the app module loads.
    """
    os.makedirs(_LOG_DIR, exist_ok=True)
    log_path = os.path.join(_LOG_DIR, _LOG_FILE)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "default",
                "filename": log_path,
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf-8",
                "utc": False,
            },
        },
        # Wire every uvicorn logger + root to both console and file from the start.
        "loggers": {
            "uvicorn":        {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
            "uvicorn.error":  {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
            "httpx":          {"handlers": ["console", "file"], "level": "WARNING", "propagate": False},
            "httpcore":       {"handlers": ["console", "file"], "level": "WARNING", "propagate": False},
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    }


def configure_logging() -> None:
    """
    Attach the file handler to the root logger for any app-level
    logging.getLogger(__name__) calls made outside of uvicorn's own loggers.
    Call this once at module load time in app.py.
    """
    file_handler = _build_file_handler()
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    if not any(isinstance(h, TimedRotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)
    
    # Suppress noisy HTTP transport logs from Ollama's httpx/httpcore client
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)