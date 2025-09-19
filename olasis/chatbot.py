"""
OLABOT - Chatbot Inteligente para Pesquisa Científica
====================================================

Versão otimizada:
- Primeira resposta: saudação curta ("Olá! Como vai?", "Hello! How are you?", "¡Hola! ¿Cómo estás?")
- Respostas seguintes: explicações moderadas (2–4 parágrafos), claras e embasadas,
  com contexto científico ou boas práticas em controle externo quando pertinente
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional

try:
    from google import genai  # type: ignore
except Exception:
    genai = None

try:
    from langdetect import detect  # type: ignore
except Exception:
    detect = None

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
        # Armazenar pares de mensagens (usuário/assistente) para manter contexto
        # Estrutura: {"role": "user" | "assistant", "content": str, "lang": str}
        self._conversation_log: List[Dict[str, str]] = []
        self._first_answer: bool = True  # <-- controla intro inicial

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

    @property
    def first_answer(self) -> bool:
        """Compatibilidade para código legado que usa `first_answer` sem underscore."""
        return self._first_answer

    @first_answer.setter
    def first_answer(self, value: bool) -> None:
        self._first_answer = bool(value)

    # ------------------------------
    # Chamada principal
    # ------------------------------
    def ask(
        self,
        question: str,
        lang: str | None = None,
        context_type: str | None = None,
        conversation_history: Optional[List[str]] = None,
        user_profile: Optional[Dict] = None,
        reset: bool = False,
        **kwargs,
    ) -> str:
        if reset:
            self._first_answer = True
            self._history.clear()
            self._conversation_log.clear()

        self._history.append(question)

        lang = (lang or "").lower()
        if lang not in ("en", "es", "pt"):
            if detect is not None:
                try:
                    guess = detect(question)
                    if guess.startswith("pt"):
                        lang = "pt"
                    elif guess.startswith("en"):
                        lang = "en"
                    else:
                        lang = "es"
                except Exception:
                    lang = "es"
            else:
                lang = "es"
        
        if self._client is None:
            unavailable = {
                "en": "[Chatbot not available. Please check your API key and dependencies.]",
                "pt": "[Chatbot indisponível. Verifique sua chave de API e dependências.]",
                "es": "[Chatbot no disponible. Por favor verifica tu API key y dependencias.]",
            }
            return unavailable.get(lang, unavailable["es"])
            
        try:
            # Intro curta apenas na primeira resposta
            intro_prompts = {
                "en": (
                    "You are OLABOT, a research assistant for OLASIS 4.0. "
                    "In the first response, begin exactly with the sentence 'Hello! How are you?'. "
                    "Right after that sentence, answer the user's question succinctly and avoid repeating extra greetings. Respond in English."
                ),
                "es": (
                    "Eres OLABOT, asistente especializado en investigación científica del OLASIS 4.0. "
                    "En la primera respuesta, comienza exactamente con la frase '¡Hola! ¿Cómo estás?'. "
                    "Justo después de esa frase, responde a la pregunta del usuario sin repetir saludos adicionales. Responde en español."
                ),
                "pt": (
                    "Você é o OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0. "
                    "Na primeira resposta, comece exatamente com a frase 'Olá! Como vai?'. "
                    "Logo após essa frase, responda à pergunta do usuário de forma objetiva, sem repetir saudações adicionais. Responda em português."
                ),
            }

            follow_prompts = {
                "en": (
                    "You are OLABOT, a research assistant for OLASIS 4.0. "
                    "Answer the user's question directly in a clear, detailed way, but limit the answer to 2 to 4 paragraphs. "
                    "Provide scientific context or best practices in external oversight when relevant, avoid overly long responses, and do not begin with greetings—go straight to the content. Respond in English."
                ),
                "es": (
                    "Eres OLABOT, asistente especializado en investigación científica del OLASIS 4.0. "
                    "Responde directamente a la pregunta del usuario de forma clara y detallada, "
                    "pero limita la respuesta a 2 a 4 párrafos como máximo. Proporciona contexto científico o buenas prácticas en control externo cuando sea pertinente, evita respuestas demasiado largas y no comiences con saludos; ve directo al contenido. Responde en español."
                ),
                "pt": (
                    "Você é o OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0. "
                    "Responda diretamente à pergunta do usuário de forma clara, detalhada e embasada, "
                    "mas limite a resposta a 2 a 4 parágrafos no máximo. Forneça contexto científico ou boas práticas em controle externo quando fizer sentido, evite respostas excessivamente longas e não inicie com saudações; vá direto ao conteúdo. Responda em português."
                ),
            }

            user_labels = {"en": "User", "es": "Usuario", "pt": "Usuário"}
            assistant_labels = {"en": "OLABOT", "es": "OLABOT", "pt": "OLABOT"}

            system_rules = (intro_prompts if self._first_answer else follow_prompts).get(
                lang,
                intro_prompts["es"] if self._first_answer else follow_prompts["es"],
            )
            user_label = user_labels.get(lang, "Usuario")

            # Construir contexto da conversa (últimas 5 interações = 10 mensagens)
            history_snippets: List[str] = []
            max_messages = 10

            if conversation_history:
            # Histórico externo já vem formatado; usar últimas entradas
                history_snippets.extend(conversation_history[-max_messages:])
            else:
                if self._conversation_log:
                    for entry in self._conversation_log[-max_messages:]:
                        entry_lang = (entry.get("lang") or lang) or "es"
                        if entry.get("role") == "assistant":
                            label = assistant_labels.get(entry_lang, assistant_labels["es"])
                        else:
                            label = user_labels.get(entry_lang, user_labels["es"])
                        history_snippets.append(f"{label}: {entry.get('content', '')}")

            if history_snippets:
                history_text = "\n".join(history_snippets)
                full_prompt = f"{system_rules}\n\n{history_text}\n{user_label}: {question}"
            else:
                full_prompt = f"{system_rules}\n\n{user_label}: {question}"

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

            was_first_answer = self._first_answer
            processed = self._enforce_greeting_rules(processed, lang, was_first_answer)

            if self._first_answer:
                self._first_answer = False
                
            # Atualizar histórico da conversa com a nova interação
            self._conversation_log.append({
                "role": "user",
                "content": question,
                "lang": lang,
            })
            self._conversation_log.append({
                "role": "assistant",
                "content": processed,
                "lang": lang,
            })
            if len(self._conversation_log) > max_messages:
                self._conversation_log = self._conversation_log[-max_messages:]

            return processed

        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            api_error = {
                "en": "[Sorry, I couldn't generate a response due to an API error.]",
                "es": "[Lo siento, no pude generar una respuesta debido a un error en la API.]",
                "pt": "[Desculpe, não consegui gerar uma resposta por causa de um erro na API.]",
            }
            return api_error.get(lang, api_error["es"])

    # ------------------------------
    # Pós-processamento
    # ------------------------------
    def _postprocess(self, raw_answer: str) -> str:
        return (raw_answer or "").strip()

    def _enforce_greeting_rules(self, text: str, lang: str, is_first_answer: bool) -> str:
        """Standardise greeting behaviour for the supported languages."""

        greeting_configs = {
            "en": {
                "intro": "Hello! How are you?",
                "legacy_intros": [
                    "Hello! I am OLABOT, a research assistant for OLASIS 4.0.",
                    "Hello! I'm OLABOT, the virtual assistant for the OLASIS platform.",
                ],
                "pattern": re.compile(
                    r"^(?P<greeting>(hello|hi|greetings|good\s+(morning|afternoon|evening|day))[!,.:\-]*\s+)",
                    re.IGNORECASE,
                ),
            },
            "es": {
                "intro": "¡Hola! ¿Cómo estás?",
                "legacy_intros": [
                    "¡Hola! Soy OLABOT, asistente de investigación para OLASIS 4.0.",
                    "¡Hola! Soy OLABOT, la asistente virtual de la plataforma OLASIS.",
                ],
                "pattern": re.compile(
                    r"^(?P<greeting>(hola|buenos\s+d[ií]as|buenas\s+tardes|buenas\s+noches)[!,.:\-]*\s+)",
                    re.IGNORECASE,
                ),
            },
            "pt": {
                "intro": "Olá! Como vai?",
                "legacy_intros": [
                    "Olá! Eu sou o OLABOT, seu assistente especializado em pesquisa científica do OLASIS 4.0.",
                    "Olá! Sou a OLABOT, a assistente virtual da plataforma OLASIS.",
                ],
                "pattern": re.compile(
                    r"^(?P<greeting>(olá|oi|saudações|bom\s+dia|boa\s+tarde|boa\s+noite)[!,.:\-]*\s+)",
                    re.IGNORECASE,
                ),
            },
        }

        cleaned = text.strip()
        config = greeting_configs.get(lang)

        if not config:
            return cleaned

        legacy_intros = config.get("legacy_intros", [])
        for legacy_intro in legacy_intros:
            if not legacy_intro:
                continue
            if cleaned.startswith(legacy_intro):
                cleaned = cleaned[len(legacy_intro):].lstrip()
            elif legacy_intro in cleaned:
                cleaned = cleaned.replace(legacy_intro, " ").strip()

        intro = config["intro"]
        if is_first_answer:
            if cleaned.startswith(intro):
                return cleaned

            if intro in cleaned:
                _, remainder = cleaned.split(intro, 1)
                combined = f"{intro}{remainder}".strip()
                return combined or intro

            if not cleaned:
                return intro

            separator = " " if not cleaned.startswith(('.', ',', ';', ':', '!', '?')) else ""
            return f"{intro}{separator}{cleaned}".strip()

        pattern = config["pattern"]
        result = cleaned
        while True:
            match = pattern.match(result)
            if not match:
                break
            result = result[match.end():].lstrip()

        if result.startswith(intro):
            result = result[len(intro):].lstrip()


        return result or cleaned

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
