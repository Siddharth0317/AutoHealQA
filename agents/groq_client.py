import os
import json
import logging
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"


class GroqClientManager:
    """
    Groq LLM Client Wrapper with model fallback, JSON extraction,
    and mock response generator when API key is missing or unconfigured.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.is_mock = not self.api_key or self.api_key.startswith("gsk_placeholder")
        self._client = None

        if not self.is_mock:
            try:
                from groq import AsyncGroq
                self._client = AsyncGroq(api_key=self.api_key)
                logger.info("Groq Async Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}. Falling back to mock mode.")
                self.is_mock = True

    async def generate_chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        json_mode: bool = True,
        mock_fallback_response: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates chat completions via Groq Cloud API with structured JSON support.
        Falls back from 70B model to 8B model if rate-limited or errored.
        Returns a dictionary containing content, model_used, execution_time_ms, and token metrics.
        """
        start_time = time.time()

        if self.is_mock:
            logger.info("Operating in Mock Mode (No valid GROQ_API_KEY provided).")
            execution_time = int((time.time() - start_time) * 1000)
            mock_data = mock_fallback_response or {"status": "mock", "message": "Mock completion response."}
            return {
                "content": json.dumps(mock_data) if json_mode else str(mock_data),
                "parsed": mock_data,
                "model_used": "mock-groq-llama-3.3-70b",
                "execution_time_ms": execution_time,
                "prompt_tokens": 120,
                "completion_tokens": 250,
                "total_tokens": 370,
                "is_mock": True
            }

        models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]
        last_exception = None

        for model in models_to_try:
            try:
                logger.info(f"Sending prompt to Groq API using model: {model}")
                response_format = {"type": "json_object"} if json_mode else None

                completion = await self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    response_format=response_format
                )

                content = completion.choices[0].message.content or ""
                execution_time = int((time.time() - start_time) * 1000)

                parsed_json = None
                if json_mode:
                    try:
                        parsed_json = json.loads(content)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON output from model {model}")
                        parsed_json = {"raw_content": content}

                usage = getattr(completion, "usage", None)
                prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
                completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

                return {
                    "content": content,
                    "parsed": parsed_json,
                    "model_used": model,
                    "execution_time_ms": execution_time,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "is_mock": False
                }
            except Exception as e:
                logger.warning(f"Error calling Groq API model {model}: {e}")
                last_exception = e

        # If all models failed, log error and return mock fallback response
        logger.error(f"All Groq models failed. Error: {last_exception}")
        execution_time = int((time.time() - start_time) * 1000)
        mock_data = mock_fallback_response or {"error": "Groq API error", "details": str(last_exception)}
        return {
            "content": json.dumps(mock_data) if json_mode else str(mock_data),
            "parsed": mock_data,
            "model_used": "fallback-mock",
            "execution_time_ms": execution_time,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "is_mock": True
        }


# Singleton instance
groq_client = GroqClientManager()
