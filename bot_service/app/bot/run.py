import asyncio
import logging

from aiogram.exceptions import TelegramNetworkError
from app.bot.dispatcher import bot, dp

logger = logging.getLogger(__name__)

async def run_bot() -> None:
    while True:
        try:
            await dp.start_polling(bot)
            return
        except TelegramNetworkError as exc:
            logger.warning("Telegram network error, retry in 5s: %s", exc)
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())
