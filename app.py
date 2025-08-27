"""Flask application for OLASIS 4.0.

This module defines a small web server that powers the OLASIS 4.0
interface with pagination support.
"""

import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from olasis import OlaBot, search_articles, search_specialists
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'olasis4-secret-key-change-in-production')

# Inicializar OLABOT v2 com engenharia de prompt
olabot = OlaBot(
    api_key=os.getenv("GOOGLE_API_KEY"), 
    model="gemini-2.5-flash",
    temperature=0.7,
    enable_prompt_engineering=True
)

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404

@app.errorhandler(500) 
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def api_search():
    """Search API with pagination support - 6 results per page."""
    query = request.args.get("q", "").strip()
    if not query:
        return {"error": "No search query provided."}, 400
        
    # Get pagination parameters
    page = max(1, int(request.args.get("page", 1)))
    per_page = 6
    
    # Fetch all results first
    all_articles = search_articles(query, per_page=50)
    all_specialists = search_specialists(query, rows=50)
    
    # Calculate pagination for articles
    articles_start = (page - 1) * per_page
    articles_end = articles_start + per_page
    articles_page = all_articles[articles_start:articles_end]
    articles_total = len(all_articles)
    articles_total_pages = (articles_total + per_page - 1) // per_page
    
    # Calculate pagination for specialists  
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

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Generate a chatbot response using OLABOT v2 with prompt engineering."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return {"response": "Por favor, faça uma pergunta específica sobre pesquisa científica."}, 400
    
    # Use OLABOT v2 with automatic context detection
    reply = olabot.ask(message, context_type="auto")
    
    # Get session statistics for monitoring
    stats = olabot.get_session_stats()
    
    return {
        "response": reply,
        "meta": {
            "context_detected": True,
            "session_stats": stats,
            "model_info": olabot.model_info
        }
    }, 200

@app.route("/api/chat/suggestions", methods=["GET"])
def api_chat_suggestions():
    """Get contextual chat suggestions for OLABOT."""
    try:
        from olasis.prompt_engineering import ChatSuggestions
        
        # Get parameters
        context_type = request.args.get('context', 'general')
        limit = int(request.args.get('count', request.args.get('limit', 4)))
        field = request.args.get('field', None)
        
        # Get user history if available (from session or parameter)
        user_history = request.args.getlist('history') if request.args.getlist('history') else None
        
        # Generate suggestions based on context
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

@app.route("/api/stats")
def api_stats():
    """Get real-time statistics from OpenAlex and ORCID APIs."""
    try:
        # Get OpenAlex statistics (total works count)
        openalex_resp = requests.get('https://api.openalex.org/works?filter=type:article&per-page=1')
        if openalex_resp.status_code == 200:
            openalex_data = openalex_resp.json()
            total_articles = openalex_data.get('meta', {}).get('count', 200000000)
        else:
            total_articles = 200000000  # Fallback
        
        # Get ORCID statistics (approximate from search results)
        orcid_resp = requests.get('https://pub.orcid.org/v3.0/search/?q=*&rows=1')
        if orcid_resp.status_code == 200:
            # Parse XML response to get num-found
            import xml.etree.ElementTree as ET
            root = ET.fromstring(orcid_resp.content)
            # Find num-found attribute in search:search element
            for elem in root.iter():
                if 'num-found' in elem.attrib:
                    total_specialists = int(elem.attrib['num-found'])
                    break
            else:
                total_specialists = 20005117  # Fallback if not found
        else:
            total_specialists = 20005117  # Fallback
        
        return {
            "articles": total_articles,
            "specialists": total_specialists,
            "last_updated": datetime.now().isoformat()
        }, 200
    
    except Exception as e:
        # Return fallback numbers if APIs fail
        return {
            "articles": 200000000,
            "specialists": 20005117,
            "last_updated": datetime.now().isoformat(),
            "error": "Using cached data"
        }, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)