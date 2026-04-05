import pytest
import respx
from httpx import Response

from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
async def test_call_openrouter_with_respx():
    with respx.mock(assert_all_called=True) as mock:
        route = mock.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=Response(
                200,
                json={"choices": [{"message": {"content": "Mocked LLM response"}}]},
            )
        )

        text = await call_openrouter("test prompt")
        assert text == "Mocked LLM response"
        assert route.called
