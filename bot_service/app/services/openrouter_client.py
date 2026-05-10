import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": prompt}],
    }
    url = f"{settings.openrouter_base_url}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    body = response.json()
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Unexpected OpenRouter response format") from exc
