"""Flask application for OLASIS 4.0.

This module defines a small web server that powers the OLASIS 4.0
interface with pagination support.
"""

import logging
import os
import secrets
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from olasis import OlaBot, search_articles, search_specialists

load_dotenv()

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

def _is_production_environment() -> bool:
    """Best-effort detection of production/staging deployment."""

    for env_var in ("FLASK_ENV", "ENVIRONMENT", "OLASIS_ENV"):
        value = os.getenv(env_var, "").strip().lower()
        if value in {"production", "prod", "staging"}:
            return True
    return False


def _resolve_secret_key() -> str:
    """Return a strong secret key, warning locally if unset."""

    configured_key = os.getenv("SECRET_KEY")
    if configured_key:
        return configured_key

    running_tests = os.getenv("PYTEST_CURRENT_TEST") is not None

    if running_tests or not _is_production_environment():
        logger.warning(
            "SECRET_KEY not set; generating ephemeral key for local/testing use."
        )
        # Generate an ephemeral key for non-production environments.
        return secrets.token_urlsafe(32)

    raise RuntimeError(
        "SECRET_KEY environment variable must be set in production environments."
    )

secret_key = _resolve_secret_key()

app.secret_key = secret_key

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,   # deixe True em produção
    SECRET_KEY=secret_key,
)

# Inicializar OLABOT v2 com engenharia de prompt
olabot = OlaBot(
    api_key=os.getenv("GOOGLE_API_KEY"), 
    model="gemini-2.5-flash",
    temperature=0.7,
    enable_prompt_engineering=True
)

# -------------------------
# Tratamento de erros
# -------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404

@app.errorhandler(500) 
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# -------------------------
# Rotas principais
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------
# Rota: Busca com paginação
# -------------------------
@app.route("/api/search")
def api_search():
    """Search API with pagination support - 6 results per page."""
    query = request.args.get("q", "").strip()
    if not query:
        return {"error": "No search query provided."}, 400
        
    page = max(1, int(request.args.get("page", 1)))
    per_page = 6
    
    all_articles = search_articles(query, per_page=50)
    all_specialists = search_specialists(query, rows=50)
    
    # Articles pagination
    articles_start = (page - 1) * per_page
    articles_end = articles_start + per_page
    articles_page = all_articles[articles_start:articles_end]
    articles_total = len(all_articles)
    articles_total_pages = (articles_total + per_page - 1) // per_page
    
    # Specialists pagination
    specialists_start = (page - 1) * per_page
    specialists_end = specialists_start + per_page
    specialists_page = all_specialists[specialists_start:specialists_end]
    specialists_total = len(all_specialists)
    specialists_total_pages = (specialists_total + per_page - 1) // per_page
    
    return {
        "articles": articles_page,
        "specialists": specialists_page,
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "articles": {
                "total": articles_total,
                "total_pages": articles_total_pages,
                "has_next": page < articles_total_pages,
                "has_prev": page > 1
            },
            "specialists": {
                "total": specialists_total,
                "total_pages": specialists_total_pages,
                "has_next": page < specialists_total_pages,
                "has_prev": page > 1
            }
        }
    }, 200

# -------------------------
# Rota: Chat principal
# -------------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Conversar com o OLABOT, com suporte a múltiplos idiomas."""
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        lang = data.get("lang")  # permitir detecção automática
        reset = bool(data.get("reset"))

        if not message:
            return jsonify({"response": "Por favor, envie uma mensagem válida."}), 400

        reply = olabot.ask(message, lang=lang, reset=reset)

        return jsonify({
            "response": reply,
            "lang": lang
        }), 200

    except Exception as exc:
        logger.error("Erro em /api/chat: %s", exc, exc_info=True)
        return jsonify({"response": "Erro interno no servidor."}), 500

# -------------------------
# Rota: Sugestões de Chat
# -------------------------
@app.route("/api/chat/suggestions", methods=["GET"])
def api_chat_suggestions():
    """Get contextual chat suggestions for OLABOT."""
    try:
        from olasis.prompt_engineering import ChatSuggestions
        
        context_type = request.args.get('context', 'general')
        requested_limit = request.args.get('count', request.args.get('limit', 4))
        try:
            limit = max(1, int(requested_limit))
        except (TypeError, ValueError):
            return {"error": "Invalid limit provided."}, 400

        max_limit = 10
        if limit > max_limit:
            return {"error": f"Maximum allowed suggestions is {max_limit}."}, 400
        field = request.args.get('field', None)
        user_history = request.args.getlist('history') if request.args.getlist('history') else None
        
        if field:
            suggestions = ChatSuggestions.get_suggestions_by_field(field, limit)
        elif user_history:
            suggestions = ChatSuggestions.get_adaptive_suggestions(user_history, limit)
        else:
            suggestions = ChatSuggestions.get_contextual_suggestions(context_type, limit)
        
        return {
            "suggestions": suggestions,
            "context": context_type,
            "field": field,
            "count": len(suggestions)
        }, 200
        
    except Exception as e:
        return {
            "suggestions": [
                "O que é inteligência artificial?",
                "Como fazer uma pesquisa científica?",
                "Onde encontrar artigos acadêmicos?",
                "Como avaliar fontes científicas?"
            ],
            "context": "fallback",
            "error": str(e)
        }, 200

# -------------------------
# Rota: Estatísticas
# -------------------------
@app.route("/api/stats")
def api_stats():
    """Get real-time statistics from OpenAlex and ORCID APIs."""
    try:
        timeout_seconds = 10

        openalex_resp = requests.get(
            'https://api.openalex.org/works?filter=type:article&per-page=1',
            timeout=timeout_seconds,
        )
        if openalex_resp.status_code == 200:
            openalex_data = openalex_resp.json()
            total_articles = openalex_data.get('meta', {}).get('count', 200000000)
        else:
            total_articles = 200000000
        

        orcid_resp = requests.get(
            'https://pub.orcid.org/v3.0/search/?q=*&rows=1',
            timeout=timeout_seconds,
        )
        if orcid_resp.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(orcid_resp.content)
            for elem in root.iter():
                if 'num-found' in elem.attrib:
                    total_specialists = int(elem.attrib['num-found'])
                    break
            else:
                total_specialists = 20005117
        else:
            total_specialists = 20005117
        
        return {
            "articles": total_articles,
            "specialists": total_specialists,
            "last_updated": datetime.now().isoformat()
        }, 200
    
    except Exception:
        return {
            "articles": 200000000,
            "specialists": 20005117,
            "last_updated": datetime.now().isoformat(),
            "error": "Using cached data"
        }, 200

# -------------------------
# Execução local
# -------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
