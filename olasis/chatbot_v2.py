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


class OlaBot:
    """
    Chatbot inteligente especializado em pesquisa científica para OLASIS 4.0.
    
    Sistema avançado que combina Google Gemini com engenharia de prompt profissional
    para fornecer assistência contextualizada em pesquisa acadêmica.

    Características principais:
    - Prompts contextualizados automaticamente
    - Detecção inteligente do tipo de consulta
    - Respostas otimizadas para texto plano
    - Integração com ferramentas do OLASIS
    - Histórico de conversa inteligente
    - Filtros de qualidade e segurança

    Parameters
    ----------
    api_key: str | None
        Chave da API do Google Gemini. Se None, será lida da variável GOOGLE_API_KEY.
    model: str
        Nome do modelo a usar (padrão: gemini-2.5-flash).
    temperature: float
        Controle de criatividade (0.0 - 1.0, padrão: 0.7).
    enable_prompt_engineering: bool
        Ativar sistema avançado de engenharia de prompt (padrão: True).
    """

    def __init__(
        self, 
        api_key: str | None = None, 
        model: str = 'gemini-2.5-flash',
        temperature: float = 0.7,
        enable_prompt_engineering: bool = True
    ) -> None:
        
        # Configuração básica
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY')
        self.api_key: str | None = api_key
        self.model: str = model
        self.temperature: float = temperature
        self.enable_prompt_engineering: bool = enable_prompt_engineering
        
        # Estado interno
        self._client = None
        self._conversation_history: List[Dict[str, str]] = []
        self._session_stats = {
            "total_queries": 0,
            "successful_responses": 0,
            "error_count": 0,
            "session_start": time.time()
        }
        
        # Inicializar componentes de engenharia de prompt
        if self.enable_prompt_engineering and PromptBuilder is not None:
            self.prompt_builder = PromptBuilder()
            self.response_optimizer = ResponseOptimizer()
        else:
            self.prompt_builder = None
            self.response_optimizer = None
            if self.enable_prompt_engineering:
                logger.warning("Prompt engineering module not available, using basic mode")

        # Validação e inicialização
        if genai is None:
            logger.warning("google-genai library is not installed; OlaBot will be disabled.")
            return
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY is not set; OlaBot will be disabled.")
            return
            
        # Configurar cliente Google Gemini
        os.environ['GEMINI_API_KEY'] = self.api_key
        try:
            self._client = genai.Client()
            logger.info(f"OlaBot initialized successfully with model {self.model}")
        except Exception as exc:
            logger.error("Failed to initialise Google GenAI client: %s", exc)
            self._client = None

    def ask(self, question: str, context_type: str = "auto") -> str:
        """
        Faz uma pergunta ao OlaBot e retorna uma resposta contextualizada.

        Utiliza engenharia de prompt avançada para fornecer respostas de alta
        qualidade específicas para pesquisa científica e acadêmica.

        Parameters
        ----------
        question: str
            Pergunta ou consulta do usuário.
        context_type: str
            Tipo de contexto ("auto", "search", "methodology", "concept", "general").
            Se "auto", detecta automaticamente o tipo baseado na pergunta.

        Returns
        -------
        str
            Resposta contextualizada e otimizada do OlaBot.
        """
        
        # Atualizar estatísticas
        self._session_stats["total_queries"] += 1
        
        # Validar entrada
        if not question or not question.strip():
            return "Por favor, faça uma pergunta específica sobre pesquisa científica."
            
        # Verificar se o cliente está disponível
        if self._client is None:
            return self._get_fallback_response(question)
            
        try:
            # Construir prompt contextualizado
            if self.prompt_builder and context_type != "simple":
                # Detectar contexto automaticamente se necessário
                if context_type == "auto":
                    context_type = self.prompt_builder.detect_context_type(question)
                
                # Construir prompt avançado
                prompt = self.prompt_builder.build_contextual_prompt(
                    user_message=question,
                    context_type=context_type,
                    conversation_history=self._get_recent_history()
                )
            else:
                # Prompt simples para compatibilidade
                prompt = self._build_simple_prompt(question)
            
            # Fazer chamada para a API
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'temperature': self.temperature,
                    'max_output_tokens': BEST_PRACTICES_CONFIG.get('max_response_length', 2000)
                }
            )
            
            # Extrair texto da resposta
            response_text = getattr(response, 'text', str(response))
            
            # Otimizar resposta se disponível
            if self.response_optimizer:
                response_text = self.response_optimizer.format_response(response_text)
                response_text = self.response_optimizer.add_olasis_integration(response_text, question)
                
                # Validar qualidade
                quality_check = self.response_optimizer.validate_response_quality(response_text)
                if not quality_check.get("has_content", True):
                    return self._get_fallback_response(question)
            
            # Salvar no histórico
            self._add_to_history(question, response_text, context_type)
            
            # Atualizar estatísticas
            self._session_stats["successful_responses"] += 1
            
            return response_text
            
        except Exception as exc:
            # Log do erro e atualização das estatísticas
            logger.error("OlaBot API call failed: %s", exc)
            self._session_stats["error_count"] += 1
            
            return self._get_fallback_response(question)
    
    def _build_simple_prompt(self, question: str) -> str:
        """Constrói um prompt simples para compatibilidade."""
        return f"""Você é OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0.
        
Responda de forma natural e conversacional, sem formatação markdown.
Use texto plano e parágrafos bem estruturados.
Foque em pesquisa científica e acadêmica.

Pergunta: {question}"""
    
    def _get_fallback_response(self, question: str) -> str:
        """Retorna uma resposta de fallback quando a API não está disponível."""
        return f"""Olá! Sou o OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0.

Sua pergunta sobre "{question}" é muito interessante, mas no momento estou com limitações técnicas.

Posso ajudar de outras formas:

1. Use a ferramenta de busca avançada acima para encontrar artigos científicos relacionados ao seu tópico
2. Explore nossa base de especialistas para encontrar pesquisadores da área
3. Acesse links diretos para publicações e perfis acadêmicos

O OLASIS integra as bases OpenAlex e ORCID, oferecendo acesso a milhões de artigos e pesquisadores globalmente.

Gostaria que eu orientasse sobre termos de busca específicos para "{question}"?"""
    
    def _add_to_history(self, question: str, response: str, context_type: str) -> None:
        """Adiciona interação ao histórico da conversa."""
        interaction = {
            "timestamp": time.time(),
            "question": question,
            "response": response,
            "context_type": context_type
        }
        
        self._conversation_history.append(interaction)
        
        # Manter apenas as últimas N interações
        max_history = BEST_PRACTICES_CONFIG.get('max_history_length', 5)
        if len(self._conversation_history) > max_history:
            self._conversation_history = self._conversation_history[-max_history:]
    
    def _get_recent_history(self) -> List[str]:
        """Retorna histórico recente formatado para contexto."""
        if not self._conversation_history:
            return []
            
        history_entries = []
        for interaction in self._conversation_history[-3:]:  # Últimas 3 interações
            entry = f"Q: {interaction['question']}\nR: {interaction['response'][:200]}..."
            history_entries.append(entry)
            
        return history_entries
    
    def get_session_stats(self) -> Dict:
        """Retorna estatísticas da sessão atual."""
        current_time = time.time()
        session_duration = current_time - self._session_stats["session_start"]
        
        stats = self._session_stats.copy()
        stats["session_duration_minutes"] = round(session_duration / 60, 2)
        stats["success_rate"] = (
            stats["successful_responses"] / max(stats["total_queries"], 1) * 100
        )
        
        return stats
    
    def clear_history(self) -> None:
        """Limpa o histórico da conversa."""
        self._conversation_history.clear()
        logger.info("OlaBot conversation history cleared")
    
    def set_temperature(self, temperature: float) -> None:
        """
        Ajusta a temperatura do modelo para controlar criatividade.
        
        Parameters
        ----------
        temperature: float
            Valor entre 0.0 (mais determinístico) e 1.0 (mais criativo).
        """
        if 0.0 <= temperature <= 1.0:
            self.temperature = temperature
            logger.info(f"OlaBot temperature set to {temperature}")
        else:
            logger.warning(f"Invalid temperature {temperature}, must be between 0.0 and 1.0")
    
    @property
    def history(self) -> List[Dict[str, str]]:
        """Retorna o histórico completo da conversa."""
        return self._conversation_history.copy()
    
    @property
    def is_available(self) -> bool:
        """Verifica se o OlaBot está disponível para uso."""
        return self._client is not None
    
    @property
    def model_info(self) -> Dict[str, any]:
        """Retorna informações sobre o modelo atual."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "prompt_engineering": self.enable_prompt_engineering,
            "available": self.is_available,
            "session_stats": self.get_session_stats()
        }


# Manter compatibilidade com código existente
class Chatbot(OlaBot):
    """
    Alias para OlaBot mantendo compatibilidade com código existente.
    
    Deprecated: Use OlaBot diretamente para novos desenvolvimentos.
    """
    
    def __init__(self, api_key: str | None = None, model: str = 'gemini-2.5-flash') -> None:
        logger.warning("Chatbot class is deprecated, use OlaBot instead")
        super().__init__(
            api_key=api_key, 
            model=model, 
            enable_prompt_engineering=False  # Modo simples para compatibilidade
        )
    
    def ask(self, question: str) -> str:
        """Método compatível com implementação original."""
        return super().ask(question, context_type="simple")
