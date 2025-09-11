"""OpenAlex integration for article search.

This module implements a minimal client for the OpenAlex API.  The API
endpoint for works is ``https://api.openalex.org/works``.  Supplying
``search=<query>`` in the query string performs a full‑text search across
titles, abstracts and the full text.  For example, the call

``https://api.openalex.org/works?search=BRAF%20AND%20melanoma``

retrieves works related to BRAF and melanoma【716426467391727†L90-L95】.  Use the
``per_page`` parameter to limit the number of records returned (between 1 and
200).

The functions defined here wrap the HTTP calls and return simplified Python
objects suitable for presentation in the Streamlit app.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .utils import http_get, extract_authors

OPENALEX_BASE_URL = 'https://api.openalex.org/works'


def search_articles(query: str, *, per_page: int = 5, mailto: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search OpenAlex for works matching a query.

    Parameters
    ----------
    query: str
        The search string.  OpenAlex uses a flexible query language; all
        whitespace and punctuation are treated as separators.  See the OpenAlex
        documentation for advanced usage.
    per_page: int
        Number of records to return (minimum 1, maximum 200).  Defaults to 5.
    mailto: str | None
        Optional contact email to include in the request.  Adding a mailto
        parameter is recommended when making large numbers of requests so that
        the OpenAlex team can contact you if needed.  When omitted a default
        placeholder email will be used if available in the ``OPENALEX_MAILTO``
        environment variable; otherwise no mailto is sent.

    Returns
    -------
    list of dict
        A list of articles with the keys ``title``, ``authors``, ``year``,
        ``openalex_id``, ``doi`` and ``url``.  If the request fails, an empty list
        will be returned.
    """
    per_page = max(1, min(per_page, 200))
    email = mailto or os.getenv('OPENALEX_MAILTO')
    params: Dict[str, Any] = {
        'search': query,
        'per_page': per_page,
    }
    if email:
        params['mailto'] = email

    data = http_get(OPENALEX_BASE_URL, params=params)
    if not data or 'results' not in data:
        return []

    articles: List[Dict[str, Any]] = []
    for result in data.get('results', []):
        # Each result is an OpenAlex work object.  See the documentation for
        # complete structure.
        title = result.get('display_name') or result.get('title') or 'Untitled'
        authorships = result.get('authorships') or []
        authors = extract_authors(authorships)
        publication_year = result.get('publication_year') or result.get('from_year')
        openalex_id = result.get('id')
        doi = result.get('doi')
        
        # Extract article URL from primary_location
        primary_location = result.get('primary_location') or {}
        article_url = primary_location.get('landing_page_url')
        
        # If no direct URL, try to get from best_oa_location
        if not article_url:
            best_oa_location = result.get('best_oa_location') or {}
            article_url = best_oa_location.get('landing_page_url')
        
        articles.append({
            'title': title,
            'authors': authors,
            'year': publication_year,
            'openalex_id': openalex_id,
            'doi': doi,
            'url': article_url,
        })
    return articles
