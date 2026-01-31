import httpx
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL
from .prompts import (
    SCRIPT_SYSTEM_PROMPT,
    MANIM_SYSTEM_PROMPT,
    build_script_prompt,
    build_code_prompt,
    build_user_prompt,
)


class LLMClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or LLM_MODEL
        self.base_url = OPENROUTER_BASE_URL
        self.conversation_history = []

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )

    def generate_script(self, user_request: str, context: str = None) -> str:
        """Generate an animation script from a user request.

        Phase 1: Think through the narrative and visuals.

        Args:
            user_request: Description of the desired animation
            context: Optional additional context (for RAG integration)

        Returns:
            Generated script as a string
        """
        user_prompt = build_script_prompt(user_request, context)

        messages = [
            {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        return self._call_llm(messages, enable_reasoning=True)

    def generate_code_from_script(self, script: str) -> str:
        """Generate Manim code from a script.

        Phase 2: Convert the refined script to working code.

        Args:
            script: The animation script from phase 1

        Returns:
            Generated Manim Python code as a string
        """
        user_prompt = build_code_prompt(script)

        # Store for potential fix_code calls
        self.conversation_history = [
            {"role": "system", "content": MANIM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        code = self._call_llm(self.conversation_history, enable_reasoning=False)
        return self._clean_code(code)

    def generate_manim_code(self, user_request: str, context: str = None) -> str:
        """Two-phase generation: script first, then code.

        Args:
            user_request: Description of the desired animation
            context: Optional additional context (for RAG integration)

        Returns:
            Generated Manim Python code as a string
        """
        # Phase 1: Generate script with reasoning
        print("Phase 1: Planning script...")
        script = self.generate_script(user_request, context)
        print(f"\n--- Generated Script ---\n{script[:500]}...")
        print("--- End Script Preview ---\n")

        # Phase 2: Generate code from script
        print("Phase 2: Generating Manim code from script...")
        code = self.generate_code_from_script(script)

        return code

    def fix_code(self, code: str, error: str) -> str:
        """Ask the LLM to fix code that failed to execute.

        Args:
            code: The code that failed
            error: The error message from Manim

        Returns:
            Fixed Manim Python code
        """
        # Add the failed code as assistant response
        self.conversation_history.append({
            "role": "assistant",
            "content": code
        })

        # Add error feedback
        fix_prompt = f"""The code you generated failed with this error:

```
{error}
```

Please fix the code. Common issues:
- Using methods that don't exist in ManimCommunity (e.g., move_arc_to_center doesn't exist)
- Passing wrong arguments to constructors (e.g., Circle doesn't accept 'point=')
- Using LaTeX environments that fail (avoid align*, use multiple MathTex)

Output ONLY the corrected Python code, nothing else."""

        self.conversation_history.append({
            "role": "user",
            "content": fix_prompt
        })

        code = self._call_llm(self.conversation_history, enable_reasoning=False)
        return self._clean_code(code)

    def _call_llm(self, messages: list, enable_reasoning: bool = False) -> str:
        """Make the API call to OpenRouter.

        Args:
            messages: The conversation messages
            enable_reasoning: Whether to enable extended thinking/reasoning

        Returns:
            The assistant's response content
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 8192,
        }

        # Enable reasoning/thinking if supported by the model
        # Note: Not all models support these - they're passed through to compatible ones
        if enable_reasoning:
            payload["temperature"] = 0.8  # Slightly higher for creative thinking
            # Only add reasoning params if model likely supports them
            # xiaomi/mimo-vl models may not support all params
            if "deepseek" in self.model or "qwen" in self.model:
                payload["reasoning"] = {"effort": "high"}
                payload["include_reasoning"] = True

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/ai-video-generator",
                    "X-Title": "AI Video Generator",
                },
                json=payload,
                timeout=120.0,  # Longer timeout for reasoning
            )

            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise ValueError(f"API request error: {type(e).__name__}: {e}")

        # Validate response structure
        if not data:
            raise ValueError("Empty response from API")

        if "choices" not in data:
            raise ValueError(f"No 'choices' in response: {list(data.keys())}")

        if not data["choices"]:
            raise ValueError("Empty 'choices' array in response")

        choice = data["choices"][0]
        if choice is None:
            raise ValueError("First choice is None")

        message = choice.get("message")
        if message is None:
            raise ValueError(f"No 'message' in choice: {choice}")

        content = message.get("content")

        if content is None:
            # Some models return content differently
            # Check for reasoning_content or other fields
            content = message.get("reasoning_content", "")
            if not content:
                raise ValueError(f"No content in response. Full message: {message}")

        # Log reasoning if present (for debugging)
        reasoning = message.get("reasoning")
        if reasoning:
            print(f"\n[Model reasoning]: {reasoning[:200]}...")

        return content

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
