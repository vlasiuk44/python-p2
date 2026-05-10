from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


@router.message(Command("token"))
async def token_command_handler(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /token <jwt>")
        return

    token = parts[1].strip()
    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer("Токен невалиден или истек. Получите новый в Auth Service.")
        return

    redis_client = get_redis()
    await redis_client.set(f"token:{message.from_user.id}", token, ex=60 * 60 * 24)
    await message.answer("Токен сохранен. Теперь отправьте ваш вопрос к LLM.")


@router.message(F.text)
async def text_handler(message: Message) -> None:
    redis_client = get_redis()
    key = f"token:{message.from_user.id}"
    token = await redis_client.get(key)

    if not token:
        await message.answer("Нет JWT токена. Сначала выполните /token <jwt> после авторизации.")
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await redis_client.delete(key)
        await message.answer("JWT невалиден или истек. Авторизуйтесь заново в Auth Service.")
        return

    llm_request.delay(tg_chat_id=message.chat.id, prompt=message.text)
    await message.answer("Запрос принят в обработку, ожидайте ответ.")
