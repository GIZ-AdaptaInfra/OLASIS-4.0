"""Flask application for OLASIS 4.0.

This module defines a small web server that powers the OLASIS 4.0
interface with pagination support.
"""

import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from olasis import Chatbot, search_articles, search_specialists

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
    natural_prompt = f"""Responde de forma natural y conversacional, como un asistente especializado en investigación científica académica. NO uses formato markdown, negritas, cursivas, listas con asteriscos o numeradas. Responde con texto plano y natural, usando párrafos simples separados por saltos de línea cuando sea necesario. 

Pregunta del usuario: {message}"""
    
    # Ask the chatbot for a response
    reply = chatbot.ask(natural_prompt)
    
    # Check if the response indicates an API error and provide a more helpful message
    if reply and ("[Chatbot not available" in reply or "[Sorry, I couldn't generate" in reply):
        reply = f"""Hola! Soy el asistente de OLASIS 4.0 especializado en investigación científica.

Tu pregunta sobre "{message}" es muy interesante. 

En este momento la API de inteligencia artificial no está disponible, pero puedo ayudarte de otras formas:

1. Usa la búsqueda avanzada arriba para encontrar artículos científicos y especialistas relacionados con tu consulta.

2. Puedes buscar por términos como: "diabetes", "sostenibilidad", "inteligencia artificial", "medicina", etc.

3. Los resultados incluyen enlaces directos a los artículos y perfiles de especialistas con sus datos de contacto.

¿Te gustaría que busque información específica sobre "{message}" en nuestra base de datos?"""
    
    return {"response": reply}, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)