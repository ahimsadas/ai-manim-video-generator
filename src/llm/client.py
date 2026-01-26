import httpx
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL
from .prompts import MANIM_SYSTEM_PROMPT, build_user_prompt


class LLMClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or LLM_MODEL
        self.base_url = OPENROUTER_BASE_URL

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )

    def generate_manim_code(self, user_request: str, context: str | None = None) -> str:
        """Generate Manim code from a user request.

        Args:
            user_request: Description of the desired animation
            context: Optional additional context (for RAG integration)

        Returns:
            Generated Manim Python code as a string
        """
        user_prompt = build_user_prompt(user_request, context)

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": MANIM_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            timeout=60.0,
        )

        response.raise_for_status()
        data = response.json()

        code = data["choices"][0]["message"]["content"]
        return self._clean_code(code)

    def _clean_code(self, code: str) -> str:
        """Clean the generated code by removing markdown artifacts."""
        code = code.strip()

        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]

        if code.endswith("```"):
            code = code[:-3]

        return code.strip()
