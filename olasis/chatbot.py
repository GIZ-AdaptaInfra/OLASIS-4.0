"""
OLABOT - Chatbot Inteligente para Pesquisa Científica
====================================================

Versão otimizada:
- Primeira resposta: intro curta do OLABOT
- Respostas seguintes: explicações moderadas (2–4 parágrafos), claras e embasadas
"""

from __future__ import annotations
import os
import logging
from typing import List, Optional, Dict

try:
    from google import genai  # type: ignore
except Exception:
    genai = None

logger = logging.getLogger(__name__)


class Chatbot:
    """Chatbot com intro inicial e respostas moderadas."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.6,         # ligeiramente menor p/ reduzir divagações
        top_p: float = 0.9,
        max_output_tokens: int = 2000,    # limite de tamanho moderado
        enable_prompt_engineering: bool = True,
    ) -> None:
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")

        self.api_key: str | None = api_key
        self.model: str = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.enable_prompt_engineering = enable_prompt_engineering

        self._client = None
        self._history: List[str] = []
        self.first_answer: bool = True  # <-- controla intro inicial

        if genai is None:
            logger.warning("google-genai library is not installed; Chatbot will be disabled.")
            return
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY is not set; Chatbot will be disabled.")
            return

        os.environ["GEMINI_API_KEY"] = self.api_key
        try:
            self._client = genai.Client()
            logger.info("Chatbot otimizado — model=%s", self.model)
        except Exception as exc:
            logger.error("Failed to initialise Google GenAI client: %s", exc)
            self._client = None

        self.model_info = {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_output_tokens": self.max_output_tokens,
            "prompt_engineering": self.enable_prompt_engineering,
        }

    # ------------------------------
    # Chamada principal
    # ------------------------------
    def ask(
        self,
        question: str,
        context_type: str | None = None,
        conversation_history: Optional[List[str]] = None,
        user_profile: Optional[Dict] = None,
        **kwargs,
    ) -> str:
        self._history.append(question)

        if self._client is None:
            return "[Chatbot not available. Please check your API key and dependencies.]"

        try:
            # Intro curta apenas na primeira resposta
            if self.first_answer:
                system_rules = (
                    "Você é o OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0. "
                    "Na primeira resposta, apresente-se em UM parágrafo curto, explique sua função e disponibilidade. "
                    "Não faça textos longos na introdução."
                )
            else:
                system_rules = (
                    "Você é o OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0. "
                    "Responda diretamente à pergunta do usuário de forma clara, detalhada e embasada, "
                    "mas limite a resposta a 2 a 4 parágrafos no máximo. "
                    "Forneça contexto científico ou histórico quando relevante e use exemplos práticos quando possível. "
                    "Evite respostas excessivamente longas."
                )

            full_prompt = f"{system_rules}\n\nUsuário: {question}"

            resp = self._client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config={
                    "temperature": float(self.temperature),
                    "top_p": float(self.top_p),
                    "max_output_tokens": int(self.max_output_tokens),
                },
            )

            answer_raw = getattr(resp, "text", str(resp))
            processed = self._postprocess(answer_raw)

            if self.first_answer:
                self.first_answer = False

            return processed

        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            return "[Desculpe, não consegui gerar uma resposta por causa de um erro na API.]"

    # ------------------------------
    # Pós-processamento
    # ------------------------------
    def _postprocess(self, raw_answer: str) -> str:
        return (raw_answer or "").strip()

    # ------------------------------
    # Estatísticas de sessão
    # ------------------------------
    def get_session_stats(self) -> dict:
        return {
            "total_questions": len(self._history),
            "last_question": self._history[-1] if self._history else None,
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_output_tokens": self.max_output_tokens,
            "prompt_engineering": self.enable_prompt_engineering,
        }
