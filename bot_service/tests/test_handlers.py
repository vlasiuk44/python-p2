from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.bot.handlers import text_handler, token_command_handler
from app.core.config import settings


@dataclass
class FakeFromUser:
    id: int


@dataclass
class FakeChat:
    id: int


@dataclass
class FakeMessage:
    text: str
    from_user: FakeFromUser
    chat: FakeChat
    answers: list[str] = field(default_factory=list)

    async def answer(self, text: str) -> None:
        self.answers.append(text)


def _make_valid_token(sub: str = "1") -> str:
    payload = {
        "sub": sub,
        "role": "user",
        "exp": int((datetime.now(tz=UTC) + timedelta(minutes=10)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


@pytest.mark.asyncio
async def test_token_command_saves_token(fake_redis):
    message = FakeMessage(
        text=f"/token {_make_valid_token()}",
        from_user=FakeFromUser(id=100),
        chat=FakeChat(id=200),
    )

    await token_command_handler(message)  # type: ignore[arg-type]

    saved = await fake_redis.get("token:100")
    assert saved is not None
    assert message.answers


@pytest.mark.asyncio
async def test_text_handler_without_token_does_not_enqueue(fake_redis, mocker):
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")
    message = FakeMessage(text="hello", from_user=FakeFromUser(id=100), chat=FakeChat(id=200))

    await text_handler(message)  # type: ignore[arg-type]

    delay_mock.assert_not_called()
    assert "Нет JWT токена" in message.answers[-1]


@pytest.mark.asyncio
async def test_text_handler_with_token_enqueues_task(fake_redis, mocker):
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")
    await fake_redis.set("token:100", _make_valid_token())
    message = FakeMessage(text="explain async", from_user=FakeFromUser(id=100), chat=FakeChat(id=200))

    await text_handler(message)  # type: ignore[arg-type]

    delay_mock.assert_called_once_with(tg_chat_id=200, prompt="explain async")
    assert "Запрос принят" in message.answers[-1]
