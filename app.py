"""Flask application for OLASIS 4.0.

This module defines a small web server that powers the OLASIS 4.0
interface with pagination support.
"""

import logging
import os
import re
import secrets
from datetime import datetime
from pathlib import Path

from olasis import OlaBot, search_articles, search_specialists
from olasis.dependencies import (
    require_dotenv_loader,
    require_flask,
    require_requests,
)
from jinja2 import TemplateNotFound

flask = require_flask()
Flask = flask.Flask
jsonify = flask.jsonify
render_template = flask.render_template
request = flask.request
url_for = flask.url_for
abort = flask.abort
stream_with_context = flask.stream_with_context

requests = require_requests()
load_dotenv = require_dotenv_loader()

dotenv_loaded = load_dotenv()

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
    if _is_production_environment() and not running_tests:
        raise RuntimeError(
            "SECRET_KEY environment variable must be configured in production."
        )

    generated_key = secrets.token_urlsafe(32)

    if not running_tests:
        logger.warning(
            "SECRET_KEY was not set – using an ephemeral value for local development."
        )

    return generated_key

def _resolve_google_api_key() -> str | None:
    """Return a configured Gemini API key with helpful logging."""

    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if key:
        return key

    fallback = os.getenv("GEMINI_API_KEY", "").strip()
    if fallback:
        logger.warning(
            "GOOGLE_API_KEY não foi definido, mas GEMINI_API_KEY está presente – "
            "usando fallback. Considere renomear a variável para manter compatibilidade."
        )
        return fallback

    if not dotenv_loaded:
        logger.warning(
            "Nenhum arquivo .env encontrado ao carregar variáveis – "
            "crie um .env ou defina GOOGLE_API_KEY/GEMINI_API_KEY manualmente."
        )

    return None


app.config.update(
    SECRET_KEY=_resolve_secret_key(),
)
olabot = OlaBot(
    api_key=_resolve_google_api_key(),
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


_VIDEOS_DIRECTORY = Path(app.root_path) / "static" / "videos"
_MAX_RANGE_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MiB, safely below Cloud Run limits

def _resolve_tutorial_path(lang: str) -> Path:
    """Return the filesystem path for the requested tutorial video."""

    language_map = {
        "es": "ESP_Tutorial_OLASIS.mp4",
        "en": "EN_Tutorial_OLASIS.mp4",
        "pt": "PT_Tutorial_OLASIS.mp4",
    }

    filename = language_map.get(lang.lower())
    if not filename:
        abort(404)

    video_path = (_VIDEOS_DIRECTORY / filename).resolve()
    if not video_path.is_file() or _VIDEOS_DIRECTORY not in video_path.parents:
        print(f"📂 Verificando caminho: {_VIDEOS_DIRECTORY}")
        print(f"🎬 Tentando abrir: {video_path}")
        print(f"✅ Existe arquivo? {video_path.exists()}")
        abort(404)

    return video_path


def _build_range_response(video_path: Path, range_header: str):
    """Return a partial content response for Range/seek support."""

    match = re.match(r"bytes=(\d+)-(\d*)", range_header)
    if not match:
        return None

    file_size = video_path.stat().st_size
    start = int(match.group(1))
    if start >= file_size:
        response = flask.Response(status=416)
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Content-Range"] = f"bytes */{file_size}"
        return response

    end_group = match.group(2)
    if end_group:
        end = int(end_group)
    else:
        end = start + _MAX_RANGE_CHUNK_SIZE - 1

    end = min(end, file_size - 1)

    if end - start + 1 > _MAX_RANGE_CHUNK_SIZE:
        end = start + _MAX_RANGE_CHUNK_SIZE - 1

    end = min(end, file_size - 1)
    if start > end:
        return None

    chunk_size = 8192
    length = end - start + 1

    def generate():
        with video_path.open("rb") as file_obj:
            file_obj.seek(start)
            remaining = length
            while remaining > 0:
                read_length = min(chunk_size, remaining)
                data = file_obj.read(read_length)
                if not data:
                    break
                yield data
                remaining -= len(data)

    response = flask.Response(
        stream_with_context(generate()), status=206, mimetype="video/mp4"
    )
    response.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Length"] = str(length)
    return response


def _build_full_response(video_path: Path):
    """Return a streaming response for the entire video file."""

    file_size = video_path.stat().st_size
    if file_size > _MAX_RANGE_CHUNK_SIZE:
        synthetic_range = f"bytes=0-{_MAX_RANGE_CHUNK_SIZE - 1}"
        limited_response = _build_range_response(video_path, synthetic_range)
        if limited_response is not None:
            return limited_response

    chunk_size = 8192

    def generate():
        with video_path.open("rb") as file_obj:
            while True:
                data = file_obj.read(chunk_size)
                if not data:
                    break
                yield data

    response = flask.Response(stream_with_context(generate()), mimetype="video/mp4")
    response.headers["Content-Length"] = str(file_size)
    response.headers["Accept-Ranges"] = "bytes"
    return response


@app.route("/media/tutorial/<lang>", methods=["GET", "HEAD"])
def tutorial_video(lang: str):
    """Serve tutorial videos with robust range/seek support for streaming."""

    video_path = _resolve_tutorial_path(lang)
    range_header = request.headers.get("Range")

    if range_header:
        range_response = _build_range_response(video_path, range_header)
        if range_response is not None:
            if request.method == "HEAD":
                range_response.response = []
                range_response.direct_passthrough = False
            return range_response

    response = _build_full_response(video_path)
    if request.method == "HEAD":
        response.response = []
        response.direct_passthrough = False
    return response


def _cookie_policy_url() -> str:
    """Return the policy URL, falling back gracefully if the route is missing."""

    if "cookie_policy" not in app.view_functions:
        return "/privacy/cookies"

    try:
        return url_for("cookie_policy")
    except Exception:  # pragma: no cover - defensive for misconfigured builds
        return "/privacy/cookies"


@app.context_processor
def inject_cookie_policy_url():
    """Expose the cookie policy URL with a safe fallback for templates."""

    return {"cookie_policy_url": _cookie_policy_url()}


@app.route("/privacy/cookies")
@app.route("/cookie-policy")
def cookie_policy():
    """Render the cookie policy page."""

    return _render_cookie_policy_template()


def _render_cookie_policy_template():
    """Render the cookie policy template with backwards compatibility."""

    last_error: TemplateNotFound | None = None
    for template_name in ("cookie_policy.html", "cookie-policy.html"):
        try:
            return render_template(template_name, datetime=datetime)
        except TemplateNotFound as exc:
            last_error = exc

    if last_error is not None:
        raise last_error

    raise TemplateNotFound("cookie_policy.html")


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
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

