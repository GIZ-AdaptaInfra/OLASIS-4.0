# OLASIS 4.0

## Overview

**OLASIS 4.0** (*Observatory for Sustainable Infrastructure System*) is a fully
fledged web application written in Python.  It provides three core services:

1. **Conversational assistant (OLABOT)** – an intelligent chatbot powered by
   Google’s Gemini models.  It can summarise documents, answer questions and
   provide guidance about sustainable infrastructure.  Under the hood it uses
   the [Gemini API quick‑start](https://ai.google.dev/gemini-api/docs/quickstart)
   client.  The application reads the API key from an environment variable
   (`GOOGLE_API_KEY`) and initialises a client through the `google‑genai` SDK
   to generate responses programmatically【549275489770013†L332-L347】.

2. **Article search** – queries the public [OpenAlex API](https://api.openalex.org)
   to retrieve scholarly works.  For example, the open source R package
   `openalexR` internally sends requests like:

   > `https://api.openalex.org/works?search=BRAF%20AND%20melanoma`【716426467391727†L90-L95】

   The application replicates this behaviour in Python to fetch metadata
   (title, authors, year, DOI, etc.) and display the most relevant records to
   the user.

3. **Specialist search** – interfaces with the
   [ORCID public search API](https://pub.orcid.org).  According to the
   Australian Access Federation’s ORCID FAQ, the public API allows anonymous
   queries by email address or organisation name; for instance,
   `https://pub.orcid.org/v3.0/search/?q=email:*@orcid.org` searches public
   email addresses and
   `https://pub.orcid.org/v3.0/search/?q=affiliation-org-name:"ORCID"` searches
   public records by affiliation【611596853467428†L25-L40】.  OLASIS 4.0 uses these
   search endpoints to find experts by name, affiliation or keyword and returns
   their ORCID identifier along with a brief profile.

## Repository structure

```
OLASIS-4.0/
│
├── README.md               # This file: description, installation and usage
├── requirements.txt        # Python dependencies for the app
├── app.py                  # Flask application entry point
├── templates/
│   └── index.html          # Main HTML page (adapted from Olasis4.html)
├── static/
│   └── js/
│       └── main.js         # Client‑side logic that integrates with the API
└── olasis/
    ├── __init__.py         # Python package marker
    ├── chatbot.py          # Wrapper around the Google Gemini client
    ├── articles.py         # Functions to query OpenAlex
    ├── specialists.py      # Functions to query ORCID
    └── utils.py            # Shared helper functions
```

## Installation

1. **Clone the repository** (or copy it into your project directory).

   ```sh
   git clone <your‑fork‑of‑this‑repo> olasis4
   cd olasis4
   ```

2. **Create a Python virtual environment** (optional but recommended).

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**.  The project requires Python 3.9 or later.

   ```sh
   pip install -r requirements.txt
   ```

4. **Set the Google API key**.  The Gemini API key must be provided via the
   `GOOGLE_API_KEY` environment variable.  You can obtain a free key from
   Google AI Studio and export it before running the app:

   ```sh
   export GOOGLE_API_KEY="your_api_key_here"
   ```

5. **Run the application** using Flask.  The server will start on
   `http://localhost:5000` by default.

   ```sh
   python app.py
   ```

## Deployment

OLASIS 4.0 uses a Flask back end and a static front end, which makes
deployment flexible.  You can run the application on any platform that
supports Python and [Flask](https://flask.palletsprojects.com/).  For
production use it is recommended to serve the app via a WSGI server such
as **gunicorn** behind a reverse proxy like **nginx**.  If you need to
deploy on a serverless platform (e.g. AWS Lambda, Netlify functions or
Cloud Run), you can decouple the `olasis` back‑end modules into
serverless handlers and host the `templates` and `static` directories as
a static site.

## Usage

The main page provides three core features:

* **Chatbot** – click the OLABOT icon to open a chat window and ask any
  question related to sustainable infrastructure.  Messages are sent to
  Google’s Gemini model via the back‑end and the response is displayed in
  the chat interface.  The default model is `gemini-2.5-flash`, but you
  can adjust it in `app.py`.

* **Artículos** – use the search bar on the landing page to look for
  scholarly articles.  The back‑end queries the OpenAlex API using your
  search term and returns the top five results.  Each result displays the
  title, authors, publication year and DOI (if available).  You can use
  the filters above the results to show only articles or only specialists.

* **Especialistas** – specialists are researchers registered in ORCID.  When
  you perform a search, the back‑end sends your query to the ORCID
  public API and returns up to five matching profiles.  Each profile
  includes the ORCID identifier and a link to the researcher’s public
  profile.

## Contributing and licence

This project is provided for demonstration purposes.  Pull requests are
welcome.  By contributing you agree to license your contributions under the
terms of the MIT licence.  See `LICENSE` for details.
