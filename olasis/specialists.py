"""ORCID integration for specialist search.

This module provides functions to query the ORCID public search API.  The
ORCID FAQ explains that you can search public email addresses and
affiliations using endpoints like ``https://pub.orcid.org/v3.0/search/?q=email:*@orcid.org``
or ``https://pub.orcid.org/v3.0/search/?q=affiliation-org-name:\"ORCID\"``【611596853467428†L25-L40】.
Here we generalise that behaviour: any user‑provided search string is
encoded into the ``q`` parameter.  Results are returned as simplified
dictionaries suitable for display in the Streamlit UI.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .utils import http_get

ORCID_SEARCH_URL = 'https://pub.orcid.org/v3.0/search/'
ORCID_RECORD_URL_TEMPLATE = 'https://pub.orcid.org/v3.0/{orcid}'


def search_specialists(query: str, *, rows: int = 5) -> List[Dict[str, Any]]:
    """Search for specialists in ORCID using a free‑text query.

    Parameters
    ----------
    query: str
        A Lucene query string.  ORCID supports wildcards and field names such
        as ``email``, ``family-name`` and ``affiliation-org-name``.  If you
        provide a plain name (e.g. "João Pereira") the API will search
        across multiple fields.
    rows: int
        Maximum number of search results to return.  ORCID allows up to 200
        results per request; a smaller number is recommended for speed.  The
        default is 5.

    Returns
    -------
    list of dict
        Each dictionary contains the keys ``orcid``, ``given_names``,
        ``family_names``, ``full_name`` and ``profile_url``.  If an error
        occurs or no results are found, an empty list is returned.
    """
    rows = max(1, min(rows, 200))
    params: Dict[str, Any] = {
        'q': query,
        'rows': rows,
    }
    # Request JSON; ORCID returns XML by default if no Accept header is sent.
    headers = {'Accept': 'application/json'}
    data = http_get(ORCID_SEARCH_URL, headers=headers, params=params)
    if not data or 'result' not in data:
        return []
    specialists: List[Dict[str, Any]] = []
    for item in data.get('result', []):
        # Each item is a dictionary containing 'orcid-identifier' and optionally
        # 'given-names' and 'family-names'.  See the ORCID API documentation
        # for details.
        orcid_identifier = item.get('orcid-identifier', {})
        path = orcid_identifier.get('path')
        uri = orcid_identifier.get('uri') or f'https://orcid.org/{path}' if path else None
        given = (item.get('given-names') or {}).get('value') if isinstance(item.get('given-names'), dict) else None
        family = (item.get('family-names') or {}).get('value') if isinstance(item.get('family-names'), dict) else None
        full_name = " ".join(filter(None, [given, family])) or None
        specialists.append({
            'orcid': path,
            'given_names': given,
            'family_names': family,
            'full_name': full_name,
            'profile_url': uri,
        })
    return specialists
