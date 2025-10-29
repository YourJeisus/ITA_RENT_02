"""Notification worker for periodic dispatch of user alerts."""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional

from src.core.config import settings
from src.services.notification_service import run_notification_dispatcher

logger = logging.getLogger(__name__)


class NotificationWorker:
    """Background worker that periodically triggers notification dispatch."""

    def __init__(
        self,
        interval_seconds: Optional[int] = None,
        run_once: bool = False,
        run_immediately: bool = True,
    ) -> None:
        self.debug_mode = bool(settings.DEBUG_NOTIFICATIONS)
        self.interval_seconds = self._resolve_interval(interval_seconds)
        self.run_once = run_once
        self.run_immediately = run_immediately
        self._stopped = False
        self._stop_event: Optional[asyncio.Event] = None

    def _resolve_interval(self, override: Optional[int]) -> int:
        if override is not None:
            return max(1, int(override))
        default = (
            settings.NOTIFICATION_WORKER_DEBUG_INTERVAL_SECONDS
            if self.debug_mode
            else settings.NOTIFICATION_WORKER_INTERVAL_SECONDS
        )
        return max(1, int(default))

    def _register_signal_handlers(self, loop: asyncio.AbstractEventLoop) -> None:
        if sys.platform.startswith("win"):
            return  # signal handlers недоступны в asyncio на Windows

        def _stop_from_signal() -> None:
            logger.info("🛑 Получен сигнал остановки, завершаем работу воркера...")
            self.stop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _stop_from_signal)
            except NotImplementedError:
                logger.debug("Cannot add signal handler for %s", sig)

    def stop(self) -> None:
        if not self._stopped:
            self._stopped = True
            if self._stop_event and not self._stop_event.is_set():
                self._stop_event.set()

    async def run_cycle(self) -> Optional[dict]:
        start_time = datetime.now()
        logger.info("🔔 Запуск цикла уведомлений...")
        try:
            stats = await run_notification_dispatcher()
            elapsed = (datetime.now() - start_time).total_seconds()
            if stats:
                logger.info(
                    "✅ Цикл уведомлений завершен (%.2f c). Пользователей: %s, уведомлений: %s, ошибок: %s",
                    elapsed,
                    stats.get("users_processed", 0),
                    stats.get("notifications_sent", 0),
                    stats.get("errors", 0),
                )
            else:
                logger.info(
                    "ℹ️ Цикл уведомлений завершен без статистики (%.2f c)", elapsed
                )
            return stats
        except Exception as exc:  # noqa: BLE001
            logger.exception("❌ Ошибка во время цикла уведомлений: %s", exc)
            return None

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()
        self._register_signal_handlers(loop)

        logger.info(
            "🚀 Запуск NotificationWorker (interval=%s сек, debug=%s, once=%s)",
            self.interval_seconds,
            self.debug_mode,
            self.run_once,
        )

        if self.run_immediately:
            await self.run_cycle()
            if self.run_once:
                return
        elif self.run_once and not self.run_immediately:
            logger.info(
                "⏳ Ожидаем %s секунд перед единственным циклом уведомлений",
                self.interval_seconds,
            )

        while not self._stopped:
            if self.run_immediately or self.run_once:
                # после первого запуска переходим в обычный режим ожидания
                self.run_immediately = False

            try:
                logger.info(
                    "⏳ Ожидаем %s секунд до следующего запуска уведомлений",
                    self.interval_seconds,
                )
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=self.interval_seconds
                )
                # Если событие установлено, выходим из цикла
                break
            except asyncio.TimeoutError:
                pass  # время ожидания вышло — запускаем цикл

            await self.run_cycle()
            if self.run_once:
                break

        logger.info("👋 NotificationWorker остановлен")


async def run_worker(
    interval_seconds: Optional[int] = None,
    run_once: bool = False,
    run_immediately: bool = True,
) -> None:
    worker = NotificationWorker(
        interval_seconds=interval_seconds,
        run_once=run_once,
        run_immediately=run_immediately,
    )
    await worker.run()
