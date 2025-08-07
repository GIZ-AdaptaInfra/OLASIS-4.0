"""Flask application for OLASIS 4.0.

This module defines a small web server that powers the OLASIS 4.0
interface with pagination support.
"""

import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from olasis import Chatbot, search_articles, search_specialists
import requests
from datetime import datetime
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'olasis4-secret-key-change-in-production')

# Inicializar chatbot
chatbot = Chatbot(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash")

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
    """Generate a chatbot response to the user's message."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return {"response": "Por favor, proporcione un mensaje."}, 400
    
    # Add instruction for natural conversation without markdown formatting
    natural_prompt = f"""Responde de forma natural e conversacional, como um assistente especializado em pesquisa científica acadêmica. NÃO use formatação markdown, negrito, itálico, listas com asteriscos ou numeradas. Responda com texto plano e natural, usando parágrafos simples separados por quebras de linha quando necessário. 

Pergunta do usuário: {message}"""
    
    # Ask the chatbot for a response
    reply = chatbot.ask(natural_prompt)
    
    # Check if the response indicates an API error and provide a more helpful message
    if reply and ("[Chatbot not available" in reply or "[Sorry, I couldn't generate" in reply):
        reply = f"""Olá! Sou o assistente do OLASIS 4.0 especializado em pesquisa científica.

Sua pergunta sobre "{message}" é muito interessante. 

No momento, a API de inteligência artificial não está disponível, mas posso ajudar de outras formas:

1. Use a busca avançada acima para encontrar artigos científicos e especialistas relacionados à sua consulta.

2. Você pode procurar por termos como: "diabetes", "sustentabilidade", "inteligência artificial", "medicina", etc.

3. Os resultados incluem links diretos para os artigos e perfis de especialistas com seus dados de contato.

Gostaria que eu buscasse informações específicas sobre "{message}" em nossa base de dados?"""
    
    return {"response": reply}, 200

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