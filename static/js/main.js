// Additional client-side logic for OLASIS 4.0
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
  // ----- Search integration with pagination -----
  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  const articlesGrid = document.querySelector('#articles-results .results-grid');
  const specialistsGrid = document.querySelector('#specialists-results .results-grid');
  const resultsForm = document.getElementById('results-form');
  const resultsSearchInput = document.getElementById('results-search-input');
  
  // Pagination state
  let currentSearchQuery = '';
  let currentPage = 1;

  // Function to create pagination controls
  function createPaginationControls(type, pagination) {
    const controls = document.createElement('div');
    controls.className = 'pagination-controls';
    
    const info = pagination[type];
    if (info.total_pages <= 1) return controls; // No pagination needed
    
    // Previous button
    if (info.has_prev) {
      const prevBtn = document.createElement('button');
      prevBtn.textContent = '← Anterior';
      prevBtn.className = 'pagination-btn';
      prevBtn.setAttribute('data-page', pagination.current_page - 1);
      prevBtn.setAttribute('data-query', currentSearchQuery);

      const prevHandler = (e) => {
        e.preventDefault();
        e.stopPropagation();
        prevBtn.disabled = true;
        performSearch(currentSearchQuery, pagination.current_page - 1)
          .finally(() => { prevBtn.disabled = false; });
      };

      prevBtn.addEventListener('click', prevHandler);
      prevBtn.addEventListener('touchstart', prevHandler);
      controls.appendChild(prevBtn);
    }
    
    // Page info
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `Página ${pagination.current_page} de ${info.total_pages} (${info.total} resultados)`;
    pageInfo.className = 'pagination-info';
    controls.appendChild(pageInfo);
    
    // Next button
    if (info.has_next) {
      const nextBtn = document.createElement('button');
      nextBtn.textContent = 'Próxima →';
      nextBtn.className = 'pagination-btn';
      nextBtn.setAttribute('data-page', pagination.current_page + 1);
      nextBtn.setAttribute('data-query', currentSearchQuery);

      const nextHandler = (e) => {
        e.preventDefault();
        e.stopPropagation();
        nextBtn.disabled = true;
        performSearch(currentSearchQuery, pagination.current_page + 1)
          .finally(() => { nextBtn.disabled = false; });
      };

      nextBtn.addEventListener('click', nextHandler);
      nextBtn.addEventListener('touchstart', nextHandler);
      controls.appendChild(nextBtn);
    }
    
    return controls;
  }

  // Function to perform search with pagination
  async function performSearch(query, page = 1) {
    if (!query) return;
    
    // Show loading state
    const loadingMessage = 'Carregando resultados...';
    if (articlesGrid) {
      articlesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">${loadingMessage}</div>`;
    }
    if (specialistsGrid) {
      specialistsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">${loadingMessage}</div>`;
    }
    
    try {
      const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}&page=${page}`);
      if (!resp.ok) throw new Error('Search failed');
      const data = await resp.json();
      
      // Clear previous results
      if (articlesGrid) articlesGrid.innerHTML = '';
      if (specialistsGrid) specialistsGrid.innerHTML = '';
      
      document.querySelectorAll('.pagination-controls').forEach(el => el.remove());
      
      // Populate articles
      if (data.articles && Array.isArray(data.articles)) {
        if (data.articles.length === 0) {
          articlesGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">Nenhum artigo encontrado nesta página.</div>';
        } else {
          data.articles.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            const authors = item.authors && item.authors.length ? `<p>${item.authors.join(', ')}</p>` : '';
            const year = item.year ? `<p>Año: ${item.year}</p>` : '';
            const doi = item.doi ? `<p>DOI: <a href="https://doi.org/${item.doi.replace(/^(https?:\/\/)?doi\.org\//i, '')}" target="_blank">${item.doi}</a></p>` : '';
            const articleLink = item.url ? `<p><a href="${item.url}" class="contact-link" target="_blank">Ver artículo</a></p>` : '';
            card.innerHTML = `<h3>${item.title || 'Sin título'}</h3>${authors}${year}${doi}${articleLink}`;
            articlesGrid.appendChild(card);
          });
        }
        
        if (data.pagination && articlesGrid.parentNode) {
          const articlesPagination = createPaginationControls('articles', data.pagination);
          articlesGrid.parentNode.appendChild(articlesPagination);
        }
      }
      
      // Populate specialists
      if (data.specialists && Array.isArray(data.specialists)) {
        if (data.specialists.length === 0) {
          specialistsGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">Nenhum especialista encontrado nesta página.</div>';
        } else {
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
        
        if (data.pagination && specialistsGrid.parentNode) {
          const specialistsPagination = createPaginationControls('specialists', data.pagination);
          specialistsGrid.parentNode.appendChild(specialistsPagination);
        }
      }
      
      currentSearchQuery = query;
      currentPage = page;
      
      if (typeof window.showResults === 'function') {
        window.showResults(query);
      }
    } catch (err) {
      const errorMessage = 'Erro ao carregar resultados. Tente novamente.';
      if (articlesGrid) {
        articlesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">${errorMessage}</div>`;
      }
      if (specialistsGrid) {
        specialistsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">${errorMessage}</div>`;
      }
    }
  }

  if (searchForm && searchInput) {
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = searchInput.value.trim();
      currentPage = 1;
      await performSearch(query, currentPage);
    });
  }
  if (resultsForm && resultsSearchInput) {
    resultsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = resultsSearchInput.value.trim();
      currentPage = 1;
      await performSearch(query, currentPage);
    });
  }

  // ----- Inline chat integration -----
  const inlineChatForm = document.getElementById('inline-chat-form');
  const inlineChatInput = inlineChatForm ? inlineChatForm.querySelector('input') : null;
  const inlineChatMessages = document.querySelector('.inline-chat-messages');
  const inlineChatWelcome = inlineChatMessages ? inlineChatMessages.querySelector('.inline-chat-welcome') : null;
  const inlineChatWindow = document.getElementById('inline-chat-window');
  const inlineChatBtn = document.getElementById('olabot-inline-btn');
  let inlineFirstMessage = true;

  if (inlineChatBtn && inlineChatWindow) {
    inlineChatBtn.addEventListener('click', () => {
      if (!inlineChatWindow.classList.contains('show')) {
        inlineFirstMessage = true;
      }
    });
  }

  if (inlineChatForm && inlineChatInput && inlineChatMessages) {
    inlineChatForm.onsubmit = async (e) => {
      e.preventDefault();
      const userMessage = inlineChatInput.value.trim();
      if (!userMessage) return;

      // Recupera idioma atual do OLASIS (default: es)
      const currentLang = localStorage.getItem('language') || 'es';

      // Textos traduzidos
      const translations = {
        es: { error: "Lo siento, ocurrió un error." },
        en: { error: "Sorry, an error occurred." },
        pt: { error: "Desculpe, ocorreu um erro." }
      };

            const suggestions = {
        es: 'Para una experiencia completa de chat, haz clic en "OLABOT" en la esquina superior izquierda.',
        en: 'For a full chat experience, click on "OLABOT" in the top left corner.',
        pt: 'Para uma experiência completa de chat, clique em "OLABOT" no canto superior esquerdo.'
      };

      // Append user bubble
      if (inlineChatWelcome) inlineChatWelcome.style.display = 'none';
      const userBubble = document.createElement('div');
      userBubble.className = 'chat-bubble user';
      userBubble.textContent = userMessage;
      inlineChatMessages.appendChild(userBubble);
      inlineChatInput.value = '';
      inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;

      try {
        const payload = { message: userMessage, lang: currentLang };
        if (inlineFirstMessage) {
          payload.reset = true;
          inlineFirstMessage = false;
        }
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const data = await resp.json();
        const reply = data.response || data.message || translations[currentLang].error;

        // Limpa formatações Markdown
        const plainText = reply
          .replace(/\*\*(.*?)\*\*/g, '$1')
          .replace(/\*(.*?)\*/g, '$1')
          .replace(/__(.*?)__/g, '$1')
          .replace(/_(.*?)_/g, '$1')
          .replace(/###\s*/g, '')
          .replace(/##\s*/g, '')
          .replace(/#\s*/g, '')
          .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
          .replace(/\n\s*\*\s*/g, '\n• ')
          .replace(/\n\s*\d+\.\s*/g, '\n')
          .replace(/\n{3,}/g, '\n\n');

        const botBubble = document.createElement('div');
        botBubble.className = 'chat-bubble bot';
        const recommendation = suggestions[currentLang] || suggestions.es;
        botBubble.textContent = `${plainText}\n\n${recommendation}`;
        inlineChatMessages.appendChild(botBubble);
        inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;

      } catch (err) {
        const errBubble = document.createElement('div');
        errBubble.className = 'chat-bubble bot';
        errBubble.textContent = translations[currentLang].error;
        inlineChatMessages.appendChild(errBubble);
        inlineChatMessages.scrollTop = inlineChatMessages.scrollHeight;
      }
    };
  }
});
