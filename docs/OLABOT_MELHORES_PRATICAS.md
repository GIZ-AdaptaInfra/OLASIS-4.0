# 🤖 OLABOT - Guia de Melhores Práticas

## 📋 Visão Geral

O OLABOT é um sistema de chatbot inteligente especializado em pesquisa científica, integrado ao OLASIS 4.0. Utiliza engenharia de prompt avançada e Google Gemini para fornecer assistência contextualizada de alta qualidade.

## 🎯 Características Principais

### ✨ Recursos Avançados
- **Prompts Contextualizados**: Detecta automaticamente o tipo de consulta e adapta as respostas
- **Respostas Otimizadas**: Formatação específica para pesquisa acadêmica sem markdown
- **Integração OLASIS**: Conecta automaticamente com ferramentas de busca do sistema
- **Histórico Inteligente**: Mantém contexto das conversas para respostas mais precisas
- **Filtros de Qualidade**: Validação automática de respostas e controle de segurança

### 🔧 Configurações Técnicas
- **Modelo**: Google Gemini 2.5 Flash
- **Temperatura**: 0.7 (equilibrio entre precisão e criatividade)
- **Comprimento**: 100-2000 caracteres por resposta
- **Idioma**: Português brasileiro (pt-BR)
- **Formato**: Texto plano sem formatação markdown

## 🚀 Como Usar

### Implementação Básica
```python
from olasis.chatbot_v2 import OlaBot

# Inicializar o chatbot
bot = OlaBot(
    api_key="sua_chave_gemini",
    model="gemini-2.5-flash", 
    temperature=0.7,
    enable_prompt_engineering=True
)

# Fazer uma pergunta
resposta = bot.ask("Como fazer uma revisão sistemática?")
print(resposta)
```

### Implementação Avançada com Contexto
```python
# Detecção automática de contexto
resposta = bot.ask("Quero pesquisar sobre diabetes", context_type="auto")

# Contexto específico para busca
resposta = bot.ask("Como encontrar artigos sobre IA?", context_type="search")

# Contexto para metodologia
resposta = bot.ask("Como fazer análise qualitativa?", context_type="methodology")

# Contexto para conceitos
resposta = bot.ask("O que é machine learning?", context_type="concept")
```

## 📊 Tipos de Contexto

### 1. 🔍 **Search** (Busca)
**Quando usar**: Perguntas sobre como encontrar literatura científica
**Palavras-chave**: buscar, procurar, encontrar, artigos, estudos, literatura
**Exemplo**: "Como posso encontrar artigos sobre sustentabilidade?"

### 2. 🧪 **Methodology** (Metodologia)
**Quando usar**: Perguntas sobre métodos de pesquisa
**Palavras-chave**: metodologia, método, como fazer, abordagem, protocolo
**Exemplo**: "Qual metodologia usar para pesquisa qualitativa?"

### 3. 💡 **Concept** (Conceito)
**Quando usar**: Perguntas sobre definições e explicações
**Palavras-chave**: o que é, definição, conceito, explique, significado
**Exemplo**: "O que é revisão sistemática?"

### 4. 🗨️ **General** (Geral)
**Quando usar**: Conversas gerais sobre pesquisa científica
**Exemplo**: "Estou começando meu mestrado, que dicas você tem?"

## 🎨 Engenharia de Prompt

### Estrutura dos Prompts

#### Prompt Base (Sistema)
```
Você é OLABOT, assistente especializado em pesquisa científica do OLASIS 4.0.

IDENTIDADE:
- Especialista em pesquisa acadêmica
- Orientador bibliográfico  
- Analista de metodologias científicas

DIRETRIZES:
- Responda em português brasileiro
- Use linguagem formal mas acessível
- Seja preciso e baseado em evidências
- NÃO use formatação markdown
- Termine com sugestões práticas
```

#### Prompts Contextuais

**Para Busca de Literatura:**
```
CONTEXTO: Assistência para busca de literatura científica

INSTRUÇÕES:
1. Analise os conceitos-chave da consulta
2. Sugira termos de busca alternativos
3. Recomende filtros (ano, área, tipo)
4. Oriente sobre estratégias booleanas
5. Mencione ferramentas do OLASIS
```

**Para Metodologia:**
```
CONTEXTO: Orientação sobre metodologia de pesquisa

INSTRUÇÕES:
1. Forneça orientações gerais sobre métodos
2. Sugira abordagens apropriadas ao estudo
3. Oriente sobre critérios de qualidade
4. Enfatize revisão por pares
5. SEMPRE recomende consultar orientadores
```

### Técnicas de Otimização

#### 1. **Detecção de Contexto**
```python
def detect_context_type(message):
    if "buscar" in message.lower():
        return "search"
    elif "metodologia" in message.lower():
        return "methodology"
    elif "o que é" in message.lower():
        return "concept"
    else:
        return "general"
```

#### 2. **Formatação de Resposta**
```python
def format_response(response):
    # Remover markdown
    response = response.replace("**", "").replace("*", "")
    # Melhorar espaçamento
    response = response.replace("\n\n\n", "\n\n")
    return response.strip()
```

#### 3. **Integração com OLASIS**
```python
def add_olasis_integration(response, user_message):
    if "olasis" not in response.lower():
        integration = f"""

Quer explorar mais sobre este tópico? Use a ferramenta de busca 
avançada acima para encontrar artigos e especialistas relacionados."""
        return response + integration
    return response
```

## 📈 Métricas de Qualidade

### Critérios de Validação
- ✅ **Conteúdo**: Resposta > 50 caracteres
- ✅ **Formatação**: Sem markdown (**, *, ##)
- ✅ **Comprimento**: Entre 100-2000 caracteres
- ✅ **Idioma**: Português brasileiro
- ✅ **Utilidade**: Contém orientações práticas

### Monitoramento
```python
# Obter estatísticas da sessão
stats = bot.get_session_stats()
print(f"Taxa de sucesso: {stats['success_rate']}%")
print(f"Total de consultas: {stats['total_queries']}")
print(f"Duração: {stats['session_duration_minutes']} min")
```

## 🛡️ Filtros de Segurança

### Conteúdo Médico
- ⚠️ Sempre incluir: "consulte um médico"
- ⚠️ Não fornecer diagnósticos específicos
- ⚠️ Orientar para fontes médicas confiáveis

### Integridade Acadêmica
- ✅ Enfatizar: "use fontes confiáveis"
- ✅ Mencionar: "verifique as referências"
- ✅ Recomendar: "literatura revisada por pares"

### Limitações
- 📝 Sempre mencionar: "estas são orientações gerais"
- 📝 Recomendar: "consulte especialistas"
- 📝 Sugerir: "verifique fontes adicionais"

## 💡 Exemplos Práticos

### Exemplo 1: Busca de Literatura
```
Usuário: "Como posso encontrar artigos sobre inteligência artificial na medicina?"

OLABOT: "Para sua pesquisa sobre inteligência artificial na medicina, 
recomendo começar com os termos: 'artificial intelligence', 'machine learning', 
'medical diagnosis', 'healthcare AI', 'clinical decision support'.

Termos em português: 'inteligência artificial médica', 'diagnóstico automatizado', 
'medicina digital'.

Estratégias de busca:
- Use operadores booleanos: 'AI AND medicine'
- Filtre por anos recentes (2020-2024)
- Foque em periódicos de medicina e tecnologia

Use a ferramenta de busca avançada acima para explorar nossa base 
integrada OpenAlex e ORCID, que oferece acesso a milhões de artigos 
científicos e perfis de pesquisadores especializados."
```

### Exemplo 2: Metodologia
```
Usuário: "Qual metodologia usar para estudar o impacto da tecnologia na educação?"

OLABOT: "Para estudar o impacto da tecnologia na educação, considere estas abordagens:

Pesquisa Quantitativa:
- Estudos experimentais com grupos controle
- Análise de dados de desempenho acadêmico
- Surveys com escalas validadas

Pesquisa Qualitativa:
- Entrevistas com professores e alunos
- Observação de aulas com tecnologia
- Análise de narrativas de experiências

Metodologia Mista:
- Combine dados quantitativos (notas, tempo) com qualitativos (percepções)
- Triangulação para maior robustez

Considere também estudos longitudinais para capturar mudanças ao longo do tempo.

Estas são orientações gerais. Para decisões metodológicas específicas, 
consulte sempre seu orientador e especialistas na área de educação e tecnologia."
```

## 🔧 Configurações Avançadas

### Ajuste de Temperatura
```python
# Mais determinístico (0.0-0.3)
bot.set_temperature(0.2)  # Para respostas mais precisas

# Equilibrado (0.4-0.7)
bot.set_temperature(0.7)  # Padrão recomendado

# Mais criativo (0.8-1.0)
bot.set_temperature(0.9)  # Para brainstorming
```

### Gestão de Histórico
```python
# Ver histórico
historico = bot.history
print(f"Conversas: {len(historico)}")

# Limpar histórico
bot.clear_history()

# Verificar disponibilidade
if bot.is_available:
    resposta = bot.ask("Sua pergunta")
```

## 📊 Integração com Flask

### Implementação na API
```python
from olasis.chatbot_v2 import OlaBot

# Inicializar globalmente
olabot = OlaBot(
    api_key=os.getenv("GOOGLE_API_KEY"),
    enable_prompt_engineering=True
)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    
    if not message:
        return {"response": "Por favor, faça uma pergunta."}, 400
    
    # Usar detecção automática de contexto
    response = olabot.ask(message, context_type="auto")
    
    return {"response": response}, 200
```

## 🎯 Casos de Uso Específicos

### 1. **Estudantes de Graduação**
- Orientação sobre pesquisa bibliográfica básica
- Explicação de conceitos científicos fundamentais
- Dicas para escrita acadêmica

### 2. **Pós-Graduandos**
- Metodologias de pesquisa avançadas
- Estratégias de revisão sistemática
- Orientação sobre publicação científica

### 3. **Pesquisadores**
- Identificação de gaps de pesquisa
- Colaborações interdisciplinares
- Análise de tendências científicas

### 4. **Profissionais**
- Aplicação prática de pesquisas
- Atualização em áreas específicas
- Transferência de conhecimento

## 📚 Recursos Adicionais

### Links Úteis
- [Google Gemini API](https://ai.google.dev/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAlex Documentation](https://docs.openalex.org/)
- [ORCID API Guide](https://info.orcid.org/documentation/)

### Documentação Técnica
- `olasis/chatbot_v2.py` - Implementação principal
- `olasis/prompt_engineering.py` - Sistema de prompts
- `app.py` - Integração Flask
- `README.md` - Documentação do projeto

---

**Desenvolvido para OLASIS 4.0 - Sistema de Busca Científica Inteligente**
