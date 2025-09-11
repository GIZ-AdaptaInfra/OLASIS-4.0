"""Flask application for OLASIS 4.0 - Basic version for testing."""

import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from olasis import search_articles, search_specialists

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def api_search():
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
