"""
Exemplo de Integração do OLABOT v2 no app.py
===========================================

Este arquivo mostra como integrar o novo sistema OLABOT com engenharia 
de prompt no app principal do OLASIS 4.0.
"""

import os
from flask import Flask, request, jsonify
from olasis import OlaBot, search_articles, search_specialists

app = Flask(__name__)

# Inicializar OLABOT v2 com engenharia de prompt
olabot = OlaBot(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash",
    temperature=0.7,
    enable_prompt_engineering=True
)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Endpoint de chat melhorado com OLABOT v2.
    
    Características:
    - Detecção automática de contexto
    - Prompts contextualizados
    - Respostas otimizadas
    - Integração inteligente com OLASIS
    """
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        
        if not message:
            return {
                "response": "Por favor, faça uma pergunta específica sobre pesquisa científica.",
                "status": "error"
            }, 400
        
        # Usar OLABOT v2 com detecção automática de contexto
        response = olabot.ask(message, context_type="auto")
        
        # Obter estatísticas da sessão para monitoramento
        stats = olabot.get_session_stats()
        
        return {
            "response": response,
            "status": "success",
            "meta": {
                "context_detected": True,
                "session_stats": stats,
                "model_info": olabot.model_info
            }
        }, 200
        
    except Exception as e:
        # Log do erro (implementar logging apropriado)
        print(f"Erro no chat: {e}")
        
        # Resposta de fallback elegante
        return {
            "response": f"""Olá! Sou o OLABOT, assistente de pesquisa científica do OLASIS 4.0.

No momento, estou com dificuldades técnicas, mas posso ajudar de outras formas:

1. Use a ferramenta de busca avançada para encontrar artigos sobre "{message}"
2. Explore nossa base de especialistas relacionados ao seu tópico
3. Acesse links diretos para publicações e perfis acadêmicos

O OLASIS integra OpenAlex e ORCID com milhões de recursos científicos.""",
            "status": "fallback",
            "error": str(e)
        }, 200

@app.route("/api/chat/context", methods=["POST"])
def api_chat_context():
    """
    Endpoint para chat com contexto específico.
    
    Permite forçar um tipo de contexto específico para a resposta.
    """
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        context_type = data.get("context_type", "auto")
        
        # Validar tipo de contexto
        valid_contexts = ["auto", "search", "methodology", "concept", "general"]
        if context_type not in valid_contexts:
            return {
                "response": f"Contexto inválido. Use: {', '.join(valid_contexts)}",
                "status": "error"
            }, 400
        
        if not message:
            return {
                "response": "Por favor, forneça uma mensagem.",
                "status": "error"
            }, 400
        
        # Usar contexto específico
        response = olabot.ask(message, context_type=context_type)
        
        return {
            "response": response,
            "status": "success",
            "meta": {
                "context_used": context_type,
                "model_info": olabot.model_info
            }
        }, 200
        
    except Exception as e:
        return {
            "response": "Erro interno do servidor.",
            "status": "error",
            "error": str(e)
        }, 500

@app.route("/api/chat/stats", methods=["GET"])
def api_chat_stats():
    """Endpoint para obter estatísticas do chatbot."""
    try:
        stats = olabot.get_session_stats()
        model_info = olabot.model_info
        
        return {
            "session_stats": stats,
            "model_info": model_info,
            "history_length": len(olabot.history),
            "available": olabot.is_available
        }, 200
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }, 500

@app.route("/api/chat/history", methods=["GET"])
def api_chat_history():
    """Endpoint para obter histórico da conversa."""
    try:
        history = olabot.history
        
        # Limitar histórico para evitar sobrecarga
        limited_history = history[-10:] if len(history) > 10 else history
        
        return {
            "history": limited_history,
            "total_interactions": len(history),
            "showing": len(limited_history)
        }, 200
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }, 500

@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    """Endpoint para limpar histórico da conversa."""
    try:
        olabot.clear_history()
        return {
            "message": "Histórico limpo com sucesso.",
            "status": "success"
        }, 200
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }, 500

@app.route("/api/chat/config", methods=["POST"])
def api_chat_config():
    """Endpoint para ajustar configurações do chatbot."""
    try:
        data = request.get_json(silent=True) or {}
        
        # Ajustar temperatura se fornecida
        if "temperature" in data:
            temperature = float(data["temperature"])
            olabot.set_temperature(temperature)
        
        return {
            "message": "Configurações atualizadas.",
            "current_config": olabot.model_info,
            "status": "success"
        }, 200
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }, 500

# Exemplo de integração com busca inteligente
@app.route("/api/smart-search", methods=["POST"])
def api_smart_search():
    """
    Busca inteligente que combina OLABOT com ferramentas de busca.
    
    O OLABOT analisa a consulta e sugere termos de busca otimizados.
    """
    try:
        data = request.get_json(silent=True) or {}
        query = (data.get("query") or "").strip()
        
        if not query:
            return {"error": "Consulta vazia"}, 400
        
        # Usar OLABOT para gerar sugestões de busca
        search_prompt = f"""Analise esta consulta de pesquisa e sugira:
1. Termos de busca otimizados em português e inglês
2. Sinônimos e variações
3. Filtros recomendados (área, ano, tipo)

Consulta: {query}

Responda de forma estruturada e prática."""
        
        suggestions = olabot.ask(search_prompt, context_type="search")
        
        # Executar busca real (implementação simplificada)
        articles = search_articles(query)
        specialists = search_specialists(query)
        
        return {
            "query": query,
            "suggestions": suggestions,
            "results": {
                "articles": articles[:5],  # Primeiros 5 resultados
                "specialists": specialists[:3]  # Primeiros 3 especialistas
            },
            "status": "success"
        }, 200
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }, 500

if __name__ == "__main__":
    # Verificar se OLABOT está disponível
    if olabot.is_available:
        print("✅ OLABOT v2 inicializado com sucesso!")
        print(f"📊 Configuração: {olabot.model_info}")
    else:
        print("⚠️ OLABOT v2 não disponível - verifique a API key")
    
    app.run(debug=True)
