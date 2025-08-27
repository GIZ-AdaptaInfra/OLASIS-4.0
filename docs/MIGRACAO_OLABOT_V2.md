# 🔄 Guia de Migração para OLABOT v2

## 📋 Visão Geral da Migração

Este guia mostra como migrar do sistema básico de chatbot para o OLABOT v2 com engenharia de prompt avançada.

## 🆚 Comparação: Antes vs Depois

### ❌ Sistema Antigo (Chatbot)
```python
from olasis import Chatbot

# Configuração básica
chatbot = Chatbot(api_key="sua_chave", model="gemini-2.5-flash")

# Prompt simples e manual
prompt = f"Responda naturalmente: {user_message}"
response = chatbot.ask(prompt)
```

### ✅ Sistema Novo (OlaBot v2)
```python
from olasis import OlaBot

# Configuração avançada
olabot = OlaBot(
    api_key="sua_chave",
    model="gemini-2.5-flash",
    temperature=0.7,
    enable_prompt_engineering=True
)

# Prompt automático e contextualizado
response = olabot.ask(user_message, context_type="auto")
```

## 🚀 Passos da Migração

### Passo 1: Atualizar Importações

**Antes:**
```python
from olasis.chatbot import Chatbot
```

**Depois:**
```python
from olasis.chatbot_v2 import OlaBot
# ou
from olasis import OlaBot
```

### Passo 2: Atualizar Inicialização

**Antes:**
```python
chatbot = Chatbot(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash"
)
```

**Depois:**
```python
olabot = OlaBot(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash",
    temperature=0.7,
    enable_prompt_engineering=True
)
```

### Passo 3: Atualizar Chamadas

**Antes:**
```python
# Prompt manual complexo
natural_prompt = f"""Responde de forma natural e conversacional, como um assistente especializado em pesquisa científica acadêmica. NÃO use formatação markdown, negrito, itálico, listas com asteriscos ou numeradas. Responda com texto plano e natural, usando parágrafos simples separados por quebras de linha quando necessário. 

Pergunta do usuário: {message}"""

reply = chatbot.ask(natural_prompt)
```

**Depois:**
```python
# Prompt automático e inteligente
reply = olabot.ask(message, context_type="auto")
```

### Passo 4: Adicionar Funcionalidades Avançadas

```python
# Verificar disponibilidade
if olabot.is_available:
    response = olabot.ask(message)
else:
    response = "Chatbot indisponível"

# Obter estatísticas
stats = olabot.get_session_stats()
print(f"Taxa de sucesso: {stats['success_rate']}%")

# Limpar histórico quando necessário
olabot.clear_history()

# Ajustar criatividade
olabot.set_temperature(0.5)  # Mais conservador
```

## 📝 Atualizando app.py

### Mudanças Necessárias

1. **Importação:**
```python
# Antes
from olasis import Chatbot

# Depois  
from olasis import OlaBot
```

2. **Inicialização Global:**
```python
# Antes
chatbot = Chatbot(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash")

# Depois
olabot = OlaBot(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash",
    temperature=0.7,
    enable_prompt_engineering=True
)
```

3. **Endpoint de Chat:**
```python
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    
    if not message:
        return {"response": "Por favor, faça uma pergunta."}, 400
    
    # Usar detecção automática de contexto
    response = olabot.ask(message, context_type="auto")
    
    # Verificar se houve erro e fornecer fallback melhorado
    if "[Chatbot not available" in response or "[Sorry, I couldn't generate" in response:
        response = olabot.ask(message)  # Fallback automático
    
    return {"response": response}, 200
```

### Fallback Melhorado

**Antes:**
```python
if reply and ("[Chatbot not available" in reply or "[Sorry, I couldn't generate" in reply):
    reply = f"""Olá! Sou o assistente do OLASIS 4.0...
    [mensagem longa e manual]"""
```

**Depois:**
```python
# O fallback é automático e contextualizado no OlaBot v2
response = olabot.ask(message, context_type="auto")
# Fallback inteligente já incluído automaticamente
```

## 🔧 Configurações Opcionais

### Diferentes Contextos
```python
# Busca de literatura
response = olabot.ask("Como encontrar artigos sobre IA?", context_type="search")

# Metodologia de pesquisa  
response = olabot.ask("Como fazer análise qualitativa?", context_type="methodology")

# Explicação de conceitos
response = olabot.ask("O que é machine learning?", context_type="concept")

# Conversa geral
response = olabot.ask("Estou começando minha pesquisa", context_type="general")
```

### Monitoramento Avançado
```python
# Estatísticas da sessão
stats = olabot.get_session_stats()
logger.info(f"Chatbot stats: {stats}")

# Informações do modelo
model_info = olabot.model_info
logger.info(f"Model info: {model_info}")

# Histórico de conversas
history = olabot.history
logger.info(f"Conversation history: {len(history)} interactions")
```

## 🧪 Testando a Migração

### Script de Teste Básico
```python
#!/usr/bin/env python3
"""Teste básico da migração"""

import os
from olasis import OlaBot

def test_migration():
    # Inicializar
    bot = OlaBot(
        api_key=os.getenv("GOOGLE_API_KEY"),
        enable_prompt_engineering=True
    )
    
    # Teste básico
    if bot.is_available:
        response = bot.ask("O que é inteligência artificial?")
        print(f"✅ Resposta: {response[:100]}...")
        
        stats = bot.get_session_stats()
        print(f"✅ Estatísticas: {stats}")
        
        print("🎉 Migração bem-sucedida!")
    else:
        print("❌ Chatbot não disponível - verifique API key")

if __name__ == "__main__":
    test_migration()
```

### Teste Completo
```bash
# Executar suite completa de testes
python tests/test_olabot_v2.py
```

## 🚨 Problemas Comuns e Soluções

### 1. Erro de Importação
**Problema:** `ImportError: cannot import name 'OlaBot'`

**Solução:**
```python
# Verificar se o arquivo existe
ls olasis/chatbot_v2.py

# Verificar __init__.py
cat olasis/__init__.py

# Se necessário, usar importação direta
from olasis.chatbot_v2 import OlaBot
```

### 2. API Key Não Encontrada
**Problema:** `GOOGLE_API_KEY is not set`

**Solução:**
```bash
# Verificar variável de ambiente
echo $GOOGLE_API_KEY

# Definir se necessário
export GOOGLE_API_KEY="sua_chave_aqui"

# Ou passar diretamente
bot = OlaBot(api_key="sua_chave_aqui")
```

### 3. Prompt Engineering Desabilitado
**Problema:** Respostas básicas mesmo com v2

**Solução:**
```python
# Garantir que está habilitado
bot = OlaBot(enable_prompt_engineering=True)

# Verificar se módulo está disponível
try:
    from olasis.prompt_engineering import PromptBuilder
    print("✅ Prompt engineering disponível")
except ImportError:
    print("❌ Módulo prompt_engineering não encontrado")
```

## 📊 Checklist de Migração

### Preparação
- [ ] Backup do código atual
- [ ] Verificar arquivos: `chatbot_v2.py`, `prompt_engineering.py`
- [ ] Testar importações básicas
- [ ] Verificar API key do Google Gemini

### Migração
- [ ] Atualizar importações em `app.py`
- [ ] Substituir `Chatbot` por `OlaBot`
- [ ] Atualizar inicialização com novos parâmetros
- [ ] Simplificar prompts manuais
- [ ] Adicionar tratamento de contexto

### Validação
- [ ] Executar testes unitários
- [ ] Testar endpoint `/api/chat`
- [ ] Verificar fallbacks funcionando
- [ ] Validar qualidade das respostas
- [ ] Monitorar estatísticas

### Otimização
- [ ] Ajustar temperatura se necessário
- [ ] Configurar limpeza de histórico
- [ ] Implementar logging avançado
- [ ] Adicionar endpoints de monitoramento

## 🎯 Benefícios da Migração

### Melhorias Técnicas
- ✅ **Prompts Contextualizados**: Respostas mais relevantes e precisas
- ✅ **Detecção Automática**: Sistema identifica tipo de consulta
- ✅ **Validação de Qualidade**: Controle automático de qualidade
- ✅ **Fallbacks Inteligentes**: Mensagens de erro mais úteis
- ✅ **Monitoramento**: Estatísticas e métricas detalhadas

### Melhorias para Usuário
- ✅ **Respostas Melhores**: Contextualizadas para pesquisa científica
- ✅ **Integração Fluida**: Conexão automática com ferramentas OLASIS
- ✅ **Consistência**: Formatação padronizada sem markdown
- ✅ **Confiabilidade**: Menos erros e mais estabilidade

### Melhorias para Desenvolvedores
- ✅ **Código Limpo**: Menos prompts manuais complexos
- ✅ **Manutenibilidade**: Sistema modular e bem estruturado
- ✅ **Extensibilidade**: Fácil adicionar novos contextos
- ✅ **Debugging**: Logs e estatísticas detalhadas

## 🚀 Próximos Passos

1. **Implementar** a migração seguindo este guia
2. **Testar** com usuários reais
3. **Monitorar** métricas de qualidade
4. **Ajustar** configurações baseado no feedback
5. **Expandir** com novos contextos conforme necessário

---

**Desenvolvido para OLASIS 4.0 - Sistema de Busca Científica Inteligente**
