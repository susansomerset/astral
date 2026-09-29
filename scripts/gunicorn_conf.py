"""Gunicorn config: on Railway, gunicorn's own log lines go to stdout as JSON.

Gunicorn's `gunicorn.error` logger writes plain text to stderr, and Railway files every
stderr line as severity=error — so "[INFO] Booting worker" showed up as an error. The
master emits those lines before the Flask app is loaded, so this has to be gunicorn
config, not app code. Same {"level", "message"} shape as src/utils/logging's Railway
formatter (duplicated: gunicorn loads this file before `src` is importable).
Off Railway, gunicorn keeps its default text logging.
"""

import json
import logging
import os

_LEVELS = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warn",
    logging.ERROR: "error",
    logging.CRITICAL: "error",
}


class RailwayJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = f"{record.name}: {record.getMessage()}"
        if record.exc_info:
            msg = msg + "\n" + self.formatException(record.exc_info)
        return json.dumps(
            {"level": _LEVELS.get(record.levelno, "error"), "message": msg},
            ensure_ascii=False,
        )


def _stdout_json() -> dict:
    return {"class": "logging.StreamHandler", "formatter": "railway_json", "stream": "ext://sys.stdout"}


if os.environ.get("RAILWAY_ENVIRONMENT"):
    # Gunicorn merges this over its defaults per top-level key, so both of its handler
    # names are redefined (error_console was the stderr one). propagate=False keeps
    # each line from also reaching root's console handler.
    logconfig_dict = {
        "formatters": {"railway_json": {"()": RailwayJsonFormatter}},
        "handlers": {
            "console": _stdout_json(),
            "error_console": _stdout_json(),
        },
        "loggers": {
            "gunicorn.error": {"level": "INFO", "handlers": ["error_console"], "propagate": False},
            "gunicorn.access": {"level": "INFO", "handlers": ["console"], "propagate": False},
        },
    }
