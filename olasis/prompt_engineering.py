"""
Engenharia de Prompt para OLABOT - Sistema de IA Especializado em Pesquisa Científica
====================================================================================
"""
from typing import Dict, List, Optional
import datetime
from difflib import SequenceMatcher
import re


class PromptTemplates:
    BASE_SYSTEM_PROMPT = """Você é OLABOT, um assistente de IA especializado em pesquisa científica e acadêmica,
integrado ao sistema OLASIS 4.0.

IDENTIDADE E PAPEL:
- Nome: OLABOT (Assistente de Pesquisa Científica)
- Especialidade: Pesquisa acadêmica, análise científica, orientação bibliográfica
- Público-alvo: Pesquisadores, estudantes, acadêmicos e profissionais da ciência
- Plataforma: OLASIS 4.0 - Sistema de Busca Científica
- Apresente-se apenas uma vez no início da conversa; nas próximas respostas vá direto ao ponto.

DIRETRIZES DE COMUNICAÇÃO:
1. SEMPRE responda na linguagem do usuário (Espanhol, Português ou Inglês).
2. Use linguagem formal mas acessível.
3. Seja preciso, objetivo e baseado em evidências.
4. NÃO use formatação markdown (sem **, *, ##, etc.).
5. Use texto plano com parágrafos bem estruturados.
6. Separe ideias com quebras de linha duplas quando apropriado.
7. Não repita, não parafraseie e não ecoe a pergunta do usuário no início da resposta.
"""

    ERROR_HANDLING_PROMPT = """
No momento estou com limitações técnicas, mas posso ajudar de outras formas através do OLASIS 4.0:

1. Use a ferramenta de busca avançada acima para encontrar artigos científicos
2. Explore nossa base de dados de especialistas para encontrar pesquisadores da área
3. Acesse links diretos para publicações e perfis de pesquisadores

O OLASIS integra as bases OpenAlex e ORCID, oferecendo acesso a milhões de artigos e pesquisadores globalmente.
"""


class PromptBuilder:
    def __init__(self):
        self.templates = PromptTemplates()

    def build_contextual_prompt(
        self,
        user_message: str,
        context_type: str = "general",
        conversation_history: Optional[List[str]] = None,
        user_profile: Optional[Dict] = None,
    ) -> str:
        prompt_parts = [self.templates.BASE_SYSTEM_PROMPT]

        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        prompt_parts.append(f"\nDATA ATUAL: {current_date}")

        if conversation_history:
            history_context = "\n".join(conversation_history[-3:])
            prompt_parts.append(f"\nCONTEXTO DA CONVERSA:\n{history_context}")

        prompt_parts.append(
            """
INSTRUÇÕES FINAIS:
- Responda de forma direta e útil
- Use linguagem natural sem formatação markdown
- Seja específico e prático
- Mencione recursos do OLASIS quando apropriado
- Termine com uma pergunta ou sugestão de próximos passos quando pertinente"""
        )

        return "\n".join(prompt_parts)


class ResponseOptimizer:
    @staticmethod
    def format_response(response: str) -> str:
        response = response.replace("**", "")
        response = response.replace("*", "")
        response = response.replace("###", "")
        response = response.replace("##", "")
        response = response.replace("#", "")
        response = response.replace("\n\n\n", "\n\n")
        return response.strip()

    @staticmethod
    def anti_echo_guard(user_message: str, response: str) -> str:
        def norm(s: str) -> str:
            s = re.sub(r"\s+", " ", (s or "")).strip().strip('"').strip("'").lower()
            return s

        q, a = norm(user_message), norm(response)
        ratio = SequenceMatcher(None, q, a).ratio()

        if a == q or ratio > 0.85 or a.startswith(q[:60]):
            return (
                "Posso ajudar sem repetir sua pergunta. "
                "Por favor diga: 1) tema/palavras-chave, 2) período/idioma, "
                "e 3) se prefere artigos, autores ou instituições."
            )
        return response


BEST_PRACTICES_CONFIG = {
    "max_response_length": 4000,
    "min_response_length": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "max_history_length": 5,
    "retry_attempts": 2,
    "timeout_seconds": 30,
    "supported_languages": ["pt-BR"],
    "response_format": "plain_text",
}
