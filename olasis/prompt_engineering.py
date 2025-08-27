"""
Engenharia de Prompt para OLABOT - Sistema de IA Especializado em Pesquisa Científica
================================================================================

Este módulo contém as melhores práticas de prompt engineering para o chatbot OLABOT,
incluindo templates de prompts, instruções de contexto e configurações otimizadas.
"""

from typing import Dict, List, Optional
import datetime


class PromptTemplates:
    """Templates de prompts profissionais para diferentes contextos do OLABOT."""
    
    # Prompt base com instruções fundamentais
    BASE_SYSTEM_PROMPT = """Você é OLABOT, um assistente de IA especializado em pesquisa científica e acadêmica, integrado ao sistema OLASIS 4.0.

IDENTIDADE E PAPEL:
- Nome: OLABOT (Assistente de Pesquisa Científica)
- Especialidade: Pesquisa acadêmica, análise científica, orientação bibliográfica
- Público-alvo: Pesquisadores, estudantes, acadêmicos e profissionais da ciência
- Plataforma: OLASIS 4.0 - Sistema de Busca Científica

DIRETRIZES DE COMUNICAÇÃO:
1. SEMPRE responda na linguagem do usuário. Espanhol, Portugues ou Inglês.
2. Use linguagem formal mas acessível
3. Seja preciso, objetivo e baseado em evidências
4. NÃO use formatação markdown (sem **, *, ##, etc.)
5. Use texto plano com parágrafos bem estruturados
6. Separe ideias com quebras de linha duplas quando apropriado

COMPETÊNCIAS PRINCIPAIS:
- Interpretação e análise de literatura científica
- Orientação sobre metodologias de pesquisa
- Sugestões de palavras-chave para busca
- Explicação de conceitos científicos complexos
- Recomendações bibliográficas
- Análise crítica de estudos e publicações
- Orientação sobre escrita acadêmica

LIMITAÇÕES IMPORTANTES:
- NÃO forneça conselhos médicos, jurídicos ou financeiros específicos
- NÃO cite artigos específicos sem ter certeza da veracidade
- SEMPRE mencione quando não tiver informações suficientes
- Recomende o uso das ferramentas de busca do OLASIS quando apropriado"""

    SEARCH_ASSISTANCE_PROMPT = """
CONTEXTO: O usuário está buscando ajuda para encontrar literatura científica.

INSTRUÇÕES ESPECÍFICAS:
1. Analise a consulta e identifique os conceitos-chave
2. Sugira termos de busca alternativos e sinônimos
3. Recomende filtros relevantes (ano, área, tipo de publicação)
4. Oriente sobre estratégias de busca booleana quando apropriado
5. Mencione o uso das ferramentas de busca avançada do OLASIS

EXEMPLO DE RESPOSTA:
"Para sua pesquisa sobre [TÓPICO], recomendo começar com os termos: [TERMOS]. 
Você pode refinar sua busca usando a ferramenta de busca avançada acima, 
que consulta as bases OpenAlex e ORCID simultaneamente."
"""

    METHODOLOGY_GUIDANCE_PROMPT = """
CONTEXTO: O usuário está buscando orientação sobre metodologia de pesquisa.

INSTRUÇÕES ESPECÍFICAS:
1. Forneça orientações gerais sobre métodos científicos
2. Sugira abordagens metodológicas apropriadas ao tipo de estudo
3. Oriente sobre critérios de qualidade da pesquisa
4. Mencione a importância da revisão por pares
5. SEMPRE recomende consultar orientadores e especialistas para decisões específicas

AVISO IMPORTANTE: 
"Estas são orientações gerais. Para decisões metodológicas específicas, 
consulte sempre seu orientador ou especialistas na área."
"""

    CONCEPT_EXPLANATION_PROMPT = """
CONTEXTO: O usuário está buscando explicação de conceitos científicos.

INSTRUÇÕES ESPECÍFICAS:
1. Defina o conceito de forma clara e acessível
2. Forneça contexto histórico quando relevante
3. Explique aplicações práticas
4. Mencione áreas de pesquisa relacionadas
5. Sugira termos de busca para aprofundamento no OLASIS

ESTRUTURA DA RESPOSTA:
- Definição principal
- Contexto e importância
- Aplicações práticas
- Áreas relacionadas para explorar
"""

    ERROR_HANDLING_PROMPT = """
CONTEXTO: Resposta para quando há limitações ou erros na API.

MENSAGEM PADRÃO:
"No momento, estou com limitações técnicas, mas posso ajudar de outras formas através do OLASIS 4.0:

1. Use a ferramenta de busca avançada acima para encontrar artigos científicos sobre seu tópico
2. Explore nossa base de dados de especialistas para encontrar pesquisadores da área
3. Acesse links diretos para publicações e perfis de pesquisadores

O OLASIS integra as bases OpenAlex e ORCID, oferecendo acesso a milhões de artigos e pesquisadores globalmente."
"""


class PromptBuilder:
    """Construtor de prompts contextual para diferentes situações."""
    
    def __init__(self):
        self.templates = PromptTemplates()
        
    def build_contextual_prompt(
        self, 
        user_message: str, 
        context_type: str = "general",
        conversation_history: Optional[List[str]] = None,
        user_profile: Optional[Dict] = None
    ) -> str:
        """
        Constrói um prompt contextualizado baseado na entrada do usuário.
        
        Args:
            user_message: Mensagem do usuário
            context_type: Tipo de contexto (general, search, methodology, concept)
            conversation_history: Histórico da conversa (opcional)
            user_profile: Perfil do usuário (opcional)
            
        Returns:
            Prompt completo formatado
        """
        
        # Prompt base
        prompt_parts = [self.templates.BASE_SYSTEM_PROMPT]
        
        # Adicionar contexto específico
        if context_type == "search":
            prompt_parts.append(self.templates.SEARCH_ASSISTANCE_PROMPT)
        elif context_type == "methodology":
            prompt_parts.append(self.templates.METHODOLOGY_GUIDANCE_PROMPT)
        elif context_type == "concept":
            prompt_parts.append(self.templates.CONCEPT_EXPLANATION_PROMPT)
            
        # Adicionar contexto temporal
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        prompt_parts.append(f"\nDATA ATUAL: {current_date}")
        
        # Adicionar histórico se disponível
        if conversation_history:
            history_context = "\n".join(conversation_history[-3:])  # Últimas 3 interações
            prompt_parts.append(f"\nCONTEXTO DA CONVERSA:\n{history_context}")
            
        # Adicionar mensagem do usuário
        prompt_parts.append(f"\nPERGUNTA DO USUÁRIO: {user_message}")
        
        # Instruções finais
        prompt_parts.append("""
INSTRUÇÕES FINAIS:
- Responda de forma direta e útil
- Use linguagem natural sem formatação markdown
- Seja específico e prático
- Mencione recursos do OLASIS quando apropriado
- Termine com uma pergunta ou sugestão de próximos passos quando pertinente""")
        
        return "\n".join(prompt_parts)
    
    def detect_context_type(self, user_message: str) -> str:
        """
        Detecta automaticamente o tipo de contexto baseado na mensagem do usuário.
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            Tipo de contexto detectado
        """
        message_lower = user_message.lower()
        
        # Palavras-chave para busca
        search_keywords = [
            "buscar", "procurar", "encontrar", "pesquisar", "artigos", "estudos", 
            "publicações", "literatura", "bibliografia", "referências"
        ]
        
        # Palavras-chave para metodologia
        methodology_keywords = [
            "metodologia", "método", "como fazer", "como pesquisar", "abordagem",
            "procedimento", "técnica", "protocolo", "análise", "coleta de dados"
        ]
        
        # Palavras-chave para conceitos
        concept_keywords = [
            "o que é", "o que significa", "definição", "conceito", "explique",
            "significado", "definir", "entender"
        ]
        
        if any(keyword in message_lower for keyword in search_keywords):
            return "search"
        elif any(keyword in message_lower for keyword in methodology_keywords):
            return "methodology"
        elif any(keyword in message_lower for keyword in concept_keywords):
            return "concept"
        else:
            return "general"


class ResponseOptimizer:
    """Otimizador de respostas para melhorar a qualidade das interações."""
    
    @staticmethod
    def format_response(response: str) -> str:
        """
        Formata a resposta removendo markdown e melhorando a estrutura.
        
        Args:
            response: Resposta bruta do modelo
            
        Returns:
            Resposta formatada
        """
        # Remover formatação markdown comum
        response = response.replace("**", "")
        response = response.replace("*", "")
        response = response.replace("###", "")
        response = response.replace("##", "")
        response = response.replace("#", "")
        
        # Melhorar espaçamento
        response = response.replace("\n\n\n", "\n\n")
        response = response.strip()
        
        return response
    
    @staticmethod
    def add_olasis_integration(response: str, user_message: str) -> str:
        """
        Adiciona sugestões de integração com ferramentas do OLASIS.
        
        Args:
            response: Resposta base
            user_message: Mensagem original do usuário
            
        Returns:
            Resposta com integração OLASIS
        """
        # Verificar se já menciona OLASIS
        if "olasis" in response.lower() or "busca" in response.lower():
            return response
            
        # Adicionar sugestão contextual
        integration_suffix = f"""

Quer explorar mais sobre este tópico? Use a ferramenta de busca avançada acima para encontrar artigos científicos e especialistas relacionados a sua consulta."""
        
        return response + integration_suffix
    
    @staticmethod
    def validate_response_quality(response: str) -> Dict[str, bool]:
        """
        Valida a qualidade da resposta baseado em critérios estabelecidos.
        
        Args:
            response: Resposta a ser validada
            
        Returns:
            Dicionário com resultados da validação
        """
        validation = {
            "has_content": len(response.strip()) > 50,
            "no_markdown": not any(md in response for md in ["**", "*", "###", "##", "#"]),
            "proper_length": 100 <= len(response) <= 2000,
            "portuguese": any(word in response.lower() for word in ["você", "sua", "este", "esta", "podem"]),
            "helpful": any(word in response.lower() for word in ["recomendo", "sugiro", "pode", "ajudar"])
        }
        
        return validation


class ChatSuggestions:
    """Gerador de sugestões contextuais de perguntas para o OLABOT."""
    
    # Sugestões categorizadas por tipo de usuário/contexto
    SUGGESTIONS_BY_CONTEXT = {
        "beginner": [
            "O que é uma revisão sistemática?",
            "Como começar uma pesquisa científica?",
            "Quais são as principais bases de dados acadêmicas?",
            "Como avaliar a qualidade de um artigo científico?"
        ],
        "intermediate": [
            "Como fazer uma análise bibliométrica?",
            "Qual metodologia usar para pesquisa qualitativa?",
            "Como encontrar gaps na literatura científica?",
            "Quais critérios usar para revisão por pares?"
        ],
        "advanced": [
            "Como conduzir uma meta-análise?",
            "Estratégias para publicar em periódicos de alto impacto",
            "Como estruturar uma proposta de financiamento?",
            "Tendências emergentes em inteligência artificial"
        ],
        "search_focused": [
            "Como encontrar artigos sobre sustentabilidade?",
            "Buscar especialistas em biotecnologia",
            "Onde encontrar dados sobre mudanças climáticas?",
            "Como acessar teses e dissertações?"
        ],
        "methodology_focused": [
            "Diferenças entre pesquisa quantitativa e qualitativa",
            "Como calcular o tamanho da amostra?",
            "Métodos de análise de dados textuais",
            "Como validar instrumentos de pesquisa?"
        ],
        "general": [
            "O que é inteligência artificial?",
            "Como citar artigos científicos corretamente?",
            "Quais são as tendências em pesquisa médica?",
            "Como colaborar com pesquisadores internacionais?"
        ]
    }
    
    # Sugestões por área de conhecimento
    SUGGESTIONS_BY_FIELD = {
        "medicina": [
            "Avanços recentes em medicina personalizada",
            "Como conduzir ensaios clínicos randomizados?",
            "Pesquisas sobre COVID-19 e suas sequelas",
            "Inovações em telemedicina"
        ],
        "tecnologia": [
            "Aplicações de machine learning na ciência",
            "Blockchain na pesquisa científica",
            "Internet das Coisas (IoT) em saúde",
            "Computação quântica: fundamentos e aplicações"
        ],
        "meio_ambiente": [
            "Pesquisas sobre energias renováveis",
            "Impactos das mudanças climáticas",
            "Biodiversidade e conservação",
            "Economia circular e sustentabilidade"
        ],
        "educacao": [
            "Metodologias ativas de aprendizagem",
            "Tecnologia educacional pós-pandemia",
            "Avaliação da aprendizagem online",
            "Inclusão digital na educação"
        ]
    }
    
    @classmethod
    def get_contextual_suggestions(cls, context_type: str = "general", limit: int = 4) -> List[str]:
        """
        Retorna sugestões contextualizadas baseadas no tipo de contexto.
        
        Args:
            context_type: Tipo de contexto ("general", "beginner", "search_focused", etc.)
            limit: Número máximo de sugestões a retornar
            
        Returns:
            Lista de sugestões de perguntas
        """
        import random
        
        suggestions = cls.SUGGESTIONS_BY_CONTEXT.get(context_type, cls.SUGGESTIONS_BY_CONTEXT["general"]).copy()
        
        # Adicionar algumas sugestões de área específica
        if context_type in ["general", "advanced"]:
            all_field_suggestions = []
            for field_suggestions in cls.SUGGESTIONS_BY_FIELD.values():
                all_field_suggestions.extend(field_suggestions)
            
            # Evitar duplicatas
            field_suggestions_to_add = [s for s in all_field_suggestions if s not in suggestions]
            if field_suggestions_to_add:
                suggestions.extend(random.sample(field_suggestions_to_add, min(2, len(field_suggestions_to_add))))
        
        # Embaralhar, remover duplicatas e limitar
        suggestions = list(dict.fromkeys(suggestions))  # Remove duplicatas preservando ordem
        random.shuffle(suggestions)
        return suggestions[:limit]
    
    @classmethod
    def get_suggestions_by_field(cls, field: str, limit: int = 4) -> List[str]:
        """
        Retorna sugestões específicas de uma área de conhecimento.
        
        Args:
            field: Área de conhecimento ("medicina", "tecnologia", etc.)
            limit: Número máximo de sugestões
            
        Returns:
            Lista de sugestões específicas da área
        """
        import random
        
        suggestions = cls.SUGGESTIONS_BY_FIELD.get(field, cls.SUGGESTIONS_BY_CONTEXT["general"])
        random.shuffle(suggestions)
        return suggestions[:limit]
    
    @classmethod
    def get_adaptive_suggestions(cls, user_history: Optional[List[str]] = None, limit: int = 4) -> List[str]:
        """
        Retorna sugestões adaptativas baseadas no histórico do usuário.
        
        Args:
            user_history: Histórico de perguntas do usuário
            limit: Número máximo de sugestões
            
        Returns:
            Lista de sugestões adaptadas ao perfil do usuário
        """
        import random
        
        if not user_history:
            return cls.get_contextual_suggestions("general", limit)
        
        # Analisar histórico para determinar nível e interesse
        history_text = " ".join(user_history).lower()
        
        # Detectar nível baseado em complexidade das perguntas
        complex_terms = ["meta-análise", "metodologia", "estatística", "análise", "correlação"]
        beginner_terms = ["o que é", "como", "definição", "básico", "introdução"]
        
        if any(term in history_text for term in complex_terms):
            context = "advanced"
        elif any(term in history_text for term in beginner_terms):
            context = "beginner"
        else:
            context = "intermediate"
        
        # Detectar área de interesse
        field_keywords = {
            "medicina": ["médico", "saúde", "clínico", "paciente", "doença"],
            "tecnologia": ["tecnologia", "algoritmo", "software", "dados", "inteligência"],
            "meio_ambiente": ["ambiente", "clima", "sustentável", "ecologia", "verde"],
            "educacao": ["educação", "ensino", "aprendizagem", "escola", "pedagógico"]
        }
        
        detected_field = None
        for field, keywords in field_keywords.items():
            if any(keyword in history_text for keyword in keywords):
                detected_field = field
                break
        
        # Combinar sugestões contextuais e de área
        suggestions = cls.get_contextual_suggestions(context, limit // 2)
        
        if detected_field:
            field_suggestions = cls.get_suggestions_by_field(detected_field, limit - len(suggestions))
            # Evitar duplicatas
            field_suggestions = [s for s in field_suggestions if s not in suggestions]
            suggestions.extend(field_suggestions)
        else:
            general_suggestions = cls.get_contextual_suggestions("general", limit - len(suggestions))
            # Evitar duplicatas
            general_suggestions = [s for s in general_suggestions if s not in suggestions]
            suggestions.extend(general_suggestions)
        
        # Remover duplicatas finais e limitar
        suggestions = list(dict.fromkeys(suggestions))
        return suggestions[:limit]
    

# Configurações de melhores práticas
BEST_PRACTICES_CONFIG = {
    "max_response_length": 2000,
    "min_response_length": 100,
    "temperature": 0.7,  # Equilibrio entre criatividade e precisão
    "top_p": 0.9,
    "max_history_length": 5,  # Manter últimas 5 interações para contexto
    "retry_attempts": 2,
    "timeout_seconds": 30,
    "supported_languages": ["pt-BR"],
    "response_format": "plain_text"
}

# Filtros de segurança e qualidade
CONTENT_FILTERS = {
    "medical_advice": [
        "consulte um médico", "procure ajuda médica", "não substitui orientação médica"
    ],
    "academic_integrity": [
        "use fontes confiáveis", "verifique as referências", "consulte literatura revisada por pares"
    ],
    "limitations_disclosure": [
        "estas são orientações gerais", "recomendo verificar fontes adicionais"
    ]
}

# Métricas de qualidade para monitoramento
QUALITY_METRICS = [
    "response_time",
    "user_satisfaction",
    "context_relevance", 
    "technical_accuracy",
    "language_appropriateness",
    "integration_usage"
]
