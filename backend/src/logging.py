import logging
import sys
from pythonjsonlogger import jsonlogger  # pip: python-json-logger


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes structured JSON to stdout.

    Every log line will look like this (one line, pretty-printed here for clarity):
    {
        "asctime":  "2024-01-01 12:00:00,000",
        "name":     "pipeline",
        "levelname":"INFO",
        "message":  "Pipeline started",
        "topic":    "AI agents",         <-- any extra kwargs you pass
        "request_id": "abc-123"          <-- great for tracing a request end-to-end
    }

    Usage anywhere in the codebase:
        logger = get_logger(__name__)
        logger.info("Pipeline started", extra={"topic": topic, "request_id": req_id})
    """

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # StreamHandler writes to stdout (Docker/systemd picks this up naturally)
    handler = logging.StreamHandler(sys.stdout)

    # JsonFormatter turns the LogRecord into a flat JSON object.
    # The format string controls which built-in fields are always included.
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Don't propagate to the root logger — avoids duplicate output
    logger.propagate = False

    return logger