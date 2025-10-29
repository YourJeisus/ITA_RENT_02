#!/usr/bin/env python3
"""Runner for the notification worker."""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from src.core.config import settings  # noqa: E402
from src.workers.notification_worker import NotificationWorker  # noqa: E402


def configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch notification worker to dispatch user alerts"
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Override interval between runs in seconds",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run only a single notification cycle",
    )
    parser.add_argument(
        "--delay-first",
        action="store_true",
        help="Wait for one interval before the first run",
    )
    return parser.parse_args()


def validate_environment() -> None:
    missing = []
    if not settings.DATABASE_URL:
        missing.append("DATABASE_URL")

    if missing:
        raise RuntimeError(
            "Отсутствуют обязательные переменные окружения: " + ", ".join(missing)
        )

    if not settings.TELEGRAM_BOT_TOKEN:
        logging.getLogger(__name__).warning(
            "⚠️ TELEGRAM_BOT_TOKEN не установлен. Telegram уведомления будут отключены."
        )


async def async_main(args: argparse.Namespace) -> None:
    worker = NotificationWorker(
        interval_seconds=args.interval,
        run_once=args.once,
        run_immediately=not args.delay_first,
    )
    await worker.run()


def main() -> None:
    args = parse_args()
    configure_logging(settings.DEBUG_NOTIFICATIONS)

    try:
        validate_environment()
    except RuntimeError as exc:
        logging.getLogger(__name__).error("❌ %s", exc)
        sys.exit(1)

    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("🛑 Notification worker остановлен пользователем")
    except Exception:  # noqa: BLE001
        logging.getLogger(__name__).exception("❌ Критическая ошибка notification worker")
        sys.exit(1)


if __name__ == "__main__":
    # Railway convention: WORKER_TYPE=notifications для запуска этого воркера
    worker_type = os.getenv("WORKER_TYPE", "").lower()
    if worker_type and worker_type not in {"notification", "notifications"}:
        logging.getLogger(__name__).error(
            "❌ Неверный тип воркера: %s. Ожидается: notification", worker_type
        )
        sys.exit(1)

    main() 