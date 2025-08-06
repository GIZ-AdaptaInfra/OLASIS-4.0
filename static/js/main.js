// Additional client‑side logic for OLASIS 4.0
//
// This script augments the existing JavaScript in the HTML template.  It
// intercepts form submissions for search and chat and reroutes them
// through the Flask API.  The original script still controls page
// transitions and translations; we simply hook into DOM events to
// replace the dummy behaviour with live data.

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
            const authors = item.authors && item.authors.length ? `<p><strong>Autores:</strong> ${item.authors.join(', ')}</p>` : '';
            const year = item.year ? `<p><strong>Ano:</strong> ${item.year}</p>` : '';
            
            // Create links section with icons
            let linksHtml = '<div class="article-links">';
            if (item.url) {
              linksHtml += `<a href="${item.url}" target="_blank" class="article-link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z"/>
                </svg>
                Ver Artigo
              </a>`;
            }
            if (item.doi) {
              const doiUrl = item.doi.startsWith('https://') ? item.doi : `https://doi.org/${item.doi.replace(/^(https?:\/\/)?doi\.org\//i, '')}`;
              linksHtml += `<a href="${doiUrl}" target="_blank" class="doi-link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z"/>
                </svg>
                DOI
              </a>`;
            }
            linksHtml += '</div>';
            
            card.innerHTML = `<h3>${item.title || 'Sin título'}</h3>${authors}${year}${linksHtml}`;
            articlesGrid.appendChild(card);
          });
        }
        // Populate specialists
        if (data.specialists && Array.isArray(data.specialists)) {
          data.specialists.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            const fullName = item.full_name || [item.given_names, item.family_names].filter(Boolean).join(' ').trim() || 'Nome não disponível';
            const orcid = item.orcid ? `<p class="orcid"><strong>ORCID:</strong> ${item.orcid}</p>` : '';
            
            let profileLink = '';
            if (item.profile_url) {
              profileLink = `<div class="specialist-links">
                <a href="${item.profile_url}" target="_blank" class="profile-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                  </svg>
                  Ver Perfil ORCID
                </a>
              </div>`;
            }
            
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
        botBubble.textContent = reply;
        inlineChatMessages.appendChild(botBubble);
        inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;
      } catch (err) {
        const errBubble = document.createElement('div');
        errBubble.className = 'chat-bubble bot';
        errBubble.textContent = 'Lo siento, ocurrió un error.';
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