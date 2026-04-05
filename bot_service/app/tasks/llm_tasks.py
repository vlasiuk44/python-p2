import asyncio

import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.infra.redis import get_redis
from app.services.openrouter_client import call_openrouter


@celery_app.task(name="app.tasks.llm_tasks.llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> dict:
    text = asyncio.run(call_openrouter(prompt))
    redis_client = get_redis()
    asyncio.run(redis_client.set(f"llm:last:{tg_chat_id}", text, ex=3600))

    # Учебный вариант: воркер отправляет ответ пользователю напрямую.
    if settings.telegram_bot_token:
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        try:
            httpx.post(url, json={"chat_id": tg_chat_id, "text": text}, timeout=20.0)
        except httpx.HTTPError:
            pass

    return {"chat_id": tg_chat_id, "response": text}
