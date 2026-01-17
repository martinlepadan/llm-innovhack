"""Featherless AI client for LLM interactions."""

from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config


class FeatherlessClient:
    """Client for interacting with Featherless AI API."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Featherless AI client.

        Args:
            api_key: Featherless API key (defaults to config).
            model: Model name to use (defaults to config).
        """
        self.api_key = api_key or config.llm.api_key
        self.model = model or config.llm.model
        self.base_url = config.llm.base_url

        if not self.api_key:
            raise ValueError(
                "Featherless API key not found. "
                "Set FEATHERLESS_API_KEY in .env file or pass as parameter."
            )

        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        print(f"✓ Featherless AI client initialized (model: {self.model})")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to Featherless AI.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Sampling temperature (defaults to config).
            max_tokens: Maximum tokens to generate (defaults to config).
            stream: Whether to stream the response.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            API response dictionary.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
            if temperature is not None
            else config.llm.temperature,
            "max_tokens": max_tokens
            if max_tokens is not None
            else config.llm.max_tokens,
            "top_p": kwargs.get("top_p", config.llm.top_p),
            "frequency_penalty": kwargs.get(
                "frequency_penalty", config.llm.frequency_penalty
            ),
            "stream": stream,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["top_p", "frequency_penalty"]
            },
        }

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Invalid API key. Please check your FEATHERLESS_API_KEY."
                )
            elif e.response.status_code == 429:
                raise RuntimeError("Rate limit exceeded. Please try again later.")
            else:
                raise RuntimeError(f"API error: {e.response.text}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {str(e)}")

    def generate_response(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs,
    ) -> str:
        """
        Generate a response to a user message.

        Args:
            user_message: User's message.
            system_message: Optional system message for context.
            conversation_history: Optional list of previous messages.
            stream: Whether to stream the response.
            **kwargs: Additional parameters for the chat API.

        Returns:
            Generated response text.
        """
        messages = []

        # Add system message
        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add user message
        messages.append({"role": "user", "content": user_message})

        # Get response
        response = self.chat(messages, stream=stream, **kwargs)

        # Extract generated text
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            raise RuntimeError("Unexpected API response format")

    def generate_response_stream(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ):
        """
        Generate a streaming response to a user message.

        Args:
            user_message: User's message.
            system_message: Optional system message for context.
            conversation_history: Optional list of previous messages.
            **kwargs: Additional parameters for the chat API.

        Yields:
            Chunks of generated text.
        """
        import json as json_module

        messages = []

        # Add system message
        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add user message
        messages.append({"role": "user", "content": user_message})

        # Prepare headers and payload
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", config.llm.temperature),
            "max_tokens": kwargs.get("max_tokens", config.llm.max_tokens),
            "top_p": kwargs.get("top_p", config.llm.top_p),
            "frequency_penalty": kwargs.get(
                "frequency_penalty", config.llm.frequency_penalty
            ),
            "stream": True,
        }

        try:
            with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
                stream=True,
            ) as response:
                response.raise_for_status()

                # Process streaming response
                for line in response.iter_lines():
                    if not line:
                        continue

                    # Decode the line properly
                    try:
                        line = line.decode("utf-8").strip()
                    except (UnicodeDecodeError, AttributeError):
                        continue

                    if not line:
                        continue

                    # Remove "data: " prefix if present
                    if line.startswith("data: "):
                        line = line[6:]

                    # Check for end of stream
                    if line.strip() == "[DONE]":
                        break

                    # Parse JSON chunk
                    try:
                        chunk = json_module.loads(line)

                        # Extract content from delta
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            choice = chunk["choices"][0]

                            # Check for content in delta
                            if "delta" in choice and "content" in choice["delta"]:
                                content = choice["delta"]["content"]
                                if content:  # Only yield non-empty content
                                    yield content

                            # Check if generation is finished
                            if choice.get("finish_reason") is not None:
                                break

                    except json_module.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue
                    except Exception as e:
                        # Log but continue for other errors
                        import sys

                        print(
                            f"Warning: Error processing stream chunk: {e}",
                            file=sys.stderr,
                        )
                        continue

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Invalid API key. Please check your FEATHERLESS_API_KEY."
                )
            elif e.response.status_code == 429:
                raise RuntimeError("Rate limit exceeded. Please try again later.")
            else:
                raise RuntimeError(f"API error: {e.response.text}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test the connection to Featherless AI.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            response = self.generate_response(
                user_message="Hello! Just testing the connection.", max_tokens=10
            )
            print(f"✓ Connection test successful. Response: {response[:50]}...")
            return True
        except Exception as e:
            print(f"✗ Connection test failed: {e}")
            return False


# Global instance
_llm_client = None


def get_llm_client() -> FeatherlessClient:
    """Get or create global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = FeatherlessClient()
    return _llm_client
