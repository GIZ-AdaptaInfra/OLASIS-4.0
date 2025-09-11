"""
OLABOT - Chatbot Inteligente para Pesquisa Científica
====================================================

Sistema de chatbot avançado integrado ao OLASIS 4.0, especializado em pesquisa
científica e acadêmica. Utiliza engenharia de prompt profissional e integração
com Google Gemini para fornecer assistência contextualizada e de alta qualidade.

Características principais:
- Prompts contextualizados por tipo de consulta
- Respostas otimizadas para pesquisa acadêmica  
- Integração automática com ferramentas do OLASIS
- Filtros de qualidade e segurança
- Histórico de conversa inteligente

Referencias:
- Google Gemini API: https://ai.google.dev/
- Prompt Engineering Best Practices: https://platform.openai.com/docs/guides/prompt-engineering
"""
from __future__ import annotations

import os
import logging
import time
from typing import List, Dict, Optional

try:
    from google import genai  # type: ignore
except Exception:
    genai = None  # fall back if google-genai is not installed

# Importar classes de engenharia de prompt
try:
    from .prompt_engineering import (
        PromptBuilder, 
        ResponseOptimizer, 
        BEST_PRACTICES_CONFIG,
        CONTENT_FILTERS
    )
except ImportError:
    # Fallback para quando o módulo não estiver disponível
    PromptBuilder = None
    ResponseOptimizer = None
    BEST_PRACTICES_CONFIG = {}
    CONTENT_FILTERS = {}

logger = logging.getLogger(__name__)


class Chatbot:
    """Simple wrapper around Google’s Gemini API for conversational use.

    Parameters
    ----------
    api_key: str | None
        Your Gemini API key.  If ``None``, it will be read from the
        ``GOOGLE_API_KEY`` environment variable.  If the key is not found
        and the SDK cannot be imported, the chatbot will remain disabled.
    model: str
        Name of the model to use (default ``gemini-2.5-flash``).  See the
        Gemini API documentation for available models.
    """

    def __init__(self, api_key: str | None = None, model: str = 'gemini-2.5-flash') -> None:
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY')
        self.api_key: str | None = api_key
        self.model: str = model
        self._client = None
        self._history: List[str] = []

        if genai is None:
            logger.warning("google-genai library is not installed; Chatbot will be disabled.")
            return
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY is not set; Chatbot will be disabled.")
            return
        # Configure the API key.  If not set, the client will attempt to read
        # from environment variable GEMINI_API_KEY as per the SDK documentation.
        os.environ['GEMINI_API_KEY'] = self.api_key
        try:
            self._client = genai.Client()
        except Exception as exc:
            logger.error("Failed to initialise Google GenAI client: %s", exc)
            self._client = None

    def ask(self, question: str) -> str:
        """Send a question to Gemini and return the text response.

        If the client is not initialised properly, a fallback message will be
        returned.  The question is appended to internal history, but the
        underlying API call is stateless in this simple implementation.

        Parameters
        ----------
        question: str
            The user’s input.

        Returns
        -------
        str
            The model’s reply as plain text, or an error message if the
            request could not be fulfilled.
        """
        self._history.append(question)
        if self._client is None:
            return "[Chatbot not available.  Please check your API key and dependencies.]"
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=question
            )
            # The response object has a `.text` attribute containing the generated text.
            return getattr(response, 'text', str(response))
        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            return "[Sorry, I couldn’t generate a response due to an API error.]"

    @property
    def history(self) -> List[str]:
        """Return the list of previous user questions."""
        return self._history
