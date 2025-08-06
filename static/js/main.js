// Additional client‑side logic for OLASIS 4.0
//
// This script augments the existing JavaScript in the HTML template.  It
// intercepts form submissions for search and chat and reroutes them
// through the Flask API.  The original script still controls page
// transitions and translations; we simply hook into DOM events to
// replace the dummy behaviour with live data.

// Função para converter Markdown básico para HTML
function markdownToHtml(text) {
  return text
    // Negrito (**texto** ou __texto__)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    // Itálico (*texto* ou _texto_)
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    // Links [texto](url)
    .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    // Quebras de linha duplas para parágrafos
    .replace(/\n\n/g, '</p><p>')
    // Quebras de linha simples para <br>
    .replace(/\n/g, '<br>')
    // Envolver tudo em parágrafos
    .replace(/^(.+)$/s, '<p>$1</p>')
    // Remover parágrafos vazios
    .replace(/<p><\/p>/g, '');
}

document.addEventListener('DOMContentLoaded', () => {
  // ----- Search integration -----
  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  const articlesGrid = document.querySelector('#articles-results .results-grid');
  const specialistsGrid = document.querySelector('#specialists-results .results-grid');

  if (searchForm && searchInput) {
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = searchInput.value.trim();
      if (!query) return;
      try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!resp.ok) throw new Error('Search failed');
        const data = await resp.json();
        // Clear any placeholder cards
        if (articlesGrid) articlesGrid.innerHTML = '';
        if (specialistsGrid) specialistsGrid.innerHTML = '';
        // Populate articles
        if (data.articles && Array.isArray(data.articles)) {
          data.articles.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            const authors = item.authors && item.authors.length ? `<p>${item.authors.join(', ')}</p>` : '';
            const year = item.year ? `<p>Año: ${item.year}</p>` : '';
            const doi = item.doi ? `<footer>DOI: <a href="https://doi.org/${item.doi.replace(/^(https?:\/\/)?doi\.org\//i, '')}" target="_blank">${item.doi}</a></footer>` : '<footer></footer>';
            card.innerHTML = `<h3>${item.title || 'Sin título'}</h3>${authors}${year}${doi}`;
            articlesGrid.appendChild(card);
          });
        }
        // Populate specialists
        if (data.specialists && Array.isArray(data.specialists)) {
          data.specialists.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            const fullName = item.full_name || [item.given_names, item.family_names].filter(Boolean).join(' ').trim() || 'Sin nombre';
            const orcid = item.orcid ? `<p class="orcid">ORCID: ${item.orcid}</p>` : '';
            const profileLink = item.profile_url ? `<a href="${item.profile_url}" class="contact-link" target="_blank">Perfil</a>` : '';
            card.innerHTML = `<h3>${fullName}</h3>${orcid}${profileLink}`;
            specialistsGrid.appendChild(card);
          });
        }
        // Trigger the built‑in page transition after populating results
        if (typeof window.showResults === 'function') {
          window.showResults(query);
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  // ----- Inline chat integration -----
  const inlineChatForm = document.getElementById('inline-chat-form');
  const inlineChatInput = inlineChatForm ? inlineChatForm.querySelector('input') : null;
  const inlineChatMessages = document.querySelector('.inline-chat-messages');
  if (inlineChatForm && inlineChatInput && inlineChatMessages) {
    // Remove the default handler defined in the template by reassigning the
    // event listener.  The existing listener uses setTimeout to append
    // placeholder text; our listener will call the back‑end instead.
    inlineChatForm.onsubmit = async (e) => {
      e.preventDefault();
      const userMessage = inlineChatInput.value.trim();
      if (!userMessage) return;
      // Append user bubble
      const userBubble = document.createElement('div');
      userBubble.className = 'chat-bubble user';
      userBubble.textContent = userMessage;
      inlineChatMessages.appendChild(userBubble);
      inlineChatInput.value = '';
      inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;
      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userMessage }),
        });
        const data = await resp.json();
        const reply = data.response || data.message || 'Lo siento, ocurrió un error.';
        const botBubble = document.createElement('div');
        botBubble.className = 'chat-bubble bot';
        botBubble.innerHTML = markdownToHtml(reply);
        inlineChatMessages.appendChild(botBubble);
        inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;
      } catch (err) {
        const errBubble = document.createElement('div');
        errBubble.className = 'chat-bubble bot';
        errBubble.innerHTML = '<p>Lo siento, ocurrió un error.</p>';
        inlineChatMessages.appendChild(errBubble);
        inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;
      }
    };
  }

  // Ensure counters reflect the correct pluralisation when numbers grow.
  // This code is intentionally minimal because the counters are updated
  // elsewhere; here we simply fix the Spanish plural if required.
  const articlesCounterEl = document.getElementById('articles-counter');
  const specialistsCounterEl = document.getElementById('specialists-counter');
  function updateCountersSuffix() {
    if (articlesCounterEl && /\bartículos\b/.test(articlesCounterEl.textContent)) {
      // nothing: the template already uses the correct suffix
    }
    if (specialistsCounterEl && /\bespecialistas\b/.test(specialistsCounterEl.textContent)) {
      // nothing
    }
  }
  setInterval(updateCountersSuffix, 5000);
});