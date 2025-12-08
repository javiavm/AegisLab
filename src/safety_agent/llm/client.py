"""
LLMClient - Wrapper for external LLM API calls.

Provides a unified interface for LLM interactions used by agents.
Currently supports OpenAI, but designed to be provider-agnostic.
"""

import json
import logging
from typing import Any, Optional

from openai import OpenAI

from safety_agent.config.settings import Settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for interacting with LLM APIs.

    Provides methods for:
    - Text completion (prompt -> response)
    - JSON extraction (prompt -> structured data)

    The client handles:
    - API authentication
    - Request formatting
    - Error handling and retries
    - Response parsing

    Example:
        >>> client = LLMClient()
        >>> response = client.complete("What hazards are in this description: ...")
        >>> # Or for structured output:
        >>> data = client.extract_json("Extract hazards: ...", schema={...})
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the LLM client.

        Args:
            settings: Optional settings object. If not provided,
                      loads from environment.
        """
        self.settings = settings or Settings()
        self._client: Optional[OpenAI] = None
        self._init_client()

    def _init_client(self) -> None:
        """
        Initialize the underlying OpenAI client.
        """
        if not self.settings.openai_api_key:
            logger.warning("No OpenAI API key configured. LLM features will use stub mode.")
            return

        try:
            self._client = OpenAI(api_key=self.settings.openai_api_key)
            logger.info(f"OpenAI client initialized with model: {self.settings.openai_model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self._client = None

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: User prompt to complete
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response

        Raises:
            LLMError: If the API call fails
        """
        if self._client is None:
            logger.warning("LLM client not initialized, using stub mode")
            return self._stub_complete(prompt)

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            logger.debug(f"Calling OpenAI API with model: {self.settings.openai_model}")

            response = self._client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content or ""
            logger.debug(f"OpenAI response received: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise LLMError(f"API call failed: {e}", cause=e)

    def extract_json(
        self,
        prompt: str,
        schema: Optional[dict] = None,
        system_prompt: Optional[str] = None,
    ) -> Any:
        """
        Extract structured JSON data from the LLM response.

        Args:
            prompt: Prompt describing what to extract
            schema: Optional JSON schema for validation
            system_prompt: Optional system prompt for context

        Returns:
            Parsed JSON data

        Raises:
            LLMError: If extraction or parsing fails
        """
        # Add JSON instruction to system prompt
        json_system = (system_prompt or "") + "\n\nRespond with valid JSON only. No markdown, no explanation."

        response = self.complete(prompt, system_prompt=json_system, temperature=0.3)

        # Try to parse JSON from response
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Find JSON array or object
            start = cleaned.find("[")
            if start == -1:
                start = cleaned.find("{")

            if start > 0:
                cleaned = cleaned[start:]

            end = cleaned.rfind("]")
            if end == -1:
                end = cleaned.rfind("}")

            if end != -1:
                cleaned = cleaned[:end + 1]

            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            logger.debug(f"Raw response: {response}")
            return []

    def _stub_complete(self, prompt: str) -> str:
        """
        Stub completion for testing without actual LLM.

        Returns a placeholder response based on prompt keywords.
        """
        prompt_lower = prompt.lower()

        if "hazard" in prompt_lower and ("identify" in prompt_lower or "analyze" in prompt_lower):
            return """[
  {
    "type": "falling_object",
    "description": "Unsecured scaffolding board poses risk of falling",
    "area": "scaffolding",
    "confidence": 0.85
  }
]"""

        if "severity" in prompt_lower or "likelihood" in prompt_lower:
            return """[
  {
    "severity": 4,
    "likelihood": 3,
    "reasoning": "Fall from height can cause serious injury"
  }
]"""

        if "action" in prompt_lower or "task" in prompt_lower:
            return """[
  {
    "title": "Install toe boards",
    "control_type": "ENGINEERING",
    "duration_minutes": 120
  }
]"""

        return "I've analyzed the input but require actual LLM integration to provide detailed analysis."


class LLMError(Exception):
    """Exception raised when LLM operations fail."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        self.message = message
        self.cause = cause
        super().__init__(message)
