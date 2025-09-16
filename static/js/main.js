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

    const getCurrentLanguage = () => localStorage.getItem('language') || 'es';
  let activeLanguage = getCurrentLanguage();

  const resultsTexts = {
    es: {
      previous: '← Anterior',
      next: 'Siguiente →',
      pageInfo: (current, totalPages, totalItems) => `Página ${current} de ${totalPages} (${totalItems} resultados)`,
      loading: 'Cargando resultados...',
      noArticles: 'No se encontraron artículos en esta página.',
      year: 'Año',
      viewArticle: 'Ver artículo',
      untitledArticle: 'Sin título',
      noSpecialists: 'No se encontraron especialistas en esta página.',
      profile: 'Perfil',
      error: 'Error al cargar resultados. Inténtalo de nuevo.',
      noName: 'Sin nombre',
    },
    en: {
      previous: '← Previous',
      next: 'Next →',
      pageInfo: (current, totalPages, totalItems) => `Page ${current} of ${totalPages} (${totalItems} results)`,
      loading: 'Loading results...',
      noArticles: 'No articles found on this page.',
      year: 'Year',
      viewArticle: 'View article',
      untitledArticle: 'Untitled',
      noSpecialists: 'No specialists found on this page.',
      profile: 'Profile',
      error: 'Error loading results. Please try again.',
      noName: 'No name',
    },
    pt: {
      previous: '← Anterior',
      next: 'Próxima →',
      pageInfo: (current, totalPages, totalItems) => `Página ${current} de ${totalPages} (${totalItems} resultados)`,
      loading: 'Carregando resultados...',
      noArticles: 'Nenhum artigo encontrado nesta página.',
      year: 'Ano',
      viewArticle: 'Ver artigo',
      untitledArticle: 'Sem título',
      noSpecialists: 'Nenhum especialista encontrado nesta página.',
      profile: 'Perfil',
      error: 'Erro ao carregar resultados. Tente novamente.',
      noName: 'Sem nome',
    },
  };

  const getResultsText = (lang, key) => {
    const fallback = resultsTexts.es;
    const texts = resultsTexts[lang] || fallback;
    return texts[key] ?? fallback[key];
  };

  const formatPageInfo = (lang, current, totalPages, totalItems) => {
    const formatter = getResultsText(lang, 'pageInfo');
    return typeof formatter === 'function'
      ? formatter(current, totalPages, totalItems)
      : formatter;
  };

  const syncLanguage = (langOverride) => {
    activeLanguage = langOverride || getCurrentLanguage();
    return activeLanguage;
  };

  document.addEventListener('olasis-language-changed', (event) => {
    syncLanguage(event.detail?.lang);
    if (currentSearchQuery) {
      performSearch(currentSearchQuery, currentPage);
    }
  });

  // Function to create pagination controls
  function createPaginationControls(type, pagination, lang) {
    const controls = document.createElement('div');
    controls.className = 'pagination-controls';
   
    const info = pagination ? pagination[type] : null;
    if (!info || info.total_pages <= 1) return null;

    const previousLabel = getResultsText(lang, 'previous');
    const nextLabel = getResultsText(lang, 'next');
    const pageInfoText = formatPageInfo(lang, pagination.current_page, info.total_pages, info.total);

    if (info.has_prev) {
      const prevBtn = document.createElement('button');
      prevBtn.textContent = previousLabel;
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
    
    const pageInfo = document.createElement('span');
    pageInfo.textContent = pageInfoText;
    pageInfo.className = 'pagination-info';
    controls.appendChild(pageInfo);
    
    if (info.has_next) {
      const nextBtn = document.createElement('button');
      nextBtn.textContent = nextLabel;
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

    const lang = syncLanguage();
    
    // Show loading state
    const loadingMessage = getResultsText(lang, 'loading');
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
        const noArticlesMessage = getResultsText(lang, 'noArticles');
        const untitledLabel = getResultsText(lang, 'untitledArticle');
        const yearLabel = getResultsText(lang, 'year');
        const viewArticleLabel = getResultsText(lang, 'viewArticle');

        if (data.articles.length === 0) {
          articlesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">${noArticlesMessage}</div>`;
        } else {
          data.articles.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            const authors = item.authors && item.authors.length ? `<p>${item.authors.join(', ')}</p>` : '';
            const year = item.year ? `<p>${yearLabel}: ${item.year}</p>` : '';
            const doi = item.doi ? `<p>DOI: <a href="https://doi.org/${item.doi.replace(/^(https?:\/\/)?doi\.org\//i, '')}" target="_blank">${item.doi}</a></p>` : '';
            const articleLink = item.url ? `<p><a href="${item.url}" class="contact-link" target="_blank">${viewArticleLabel}</a></p>` : '';
            card.innerHTML = `<h3>${item.title || untitledLabel}</h3>${authors}${year}${doi}${articleLink}`;
            articlesGrid.appendChild(card);
          });
        }
        
        if (data.pagination && articlesGrid.parentNode) {
          const articlesPagination = createPaginationControls('articles', data.pagination, lang);
          if (articlesPagination) {
            articlesGrid.parentNode.appendChild(articlesPagination);
          }
        }
      }
      
      // Populate specialists
      if (data.specialists && Array.isArray(data.specialists)) {
        const noSpecialistsMessage = getResultsText(lang, 'noSpecialists');
        const profileLabel = getResultsText(lang, 'profile');
        const noNameLabel = getResultsText(lang, 'noName');

        if (data.specialists.length === 0) {
          specialistsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--color-gray-dark);">${noSpecialistsMessage}</div>`;
        } else {
          data.specialists.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            const fullName = item.full_name || [item.given_names, item.family_names].filter(Boolean).join(' ').trim() || noNameLabel;
            const orcid = item.orcid ? `<p class="orcid">ORCID: ${item.orcid}</p>` : '';
            const profileLink = item.profile_url ? `<a href="${item.profile_url}" class="contact-link" target="_blank">${profileLabel}</a>` : '';
            card.innerHTML = `<h3>${fullName}</h3>${orcid}${profileLink}`;
            specialistsGrid.appendChild(card);
          });
        }
        
        if (data.pagination && specialistsGrid.parentNode) {
          const specialistsPagination = createPaginationControls('specialists', data.pagination, lang);
          if (specialistsPagination) {
            specialistsGrid.parentNode.appendChild(specialistsPagination);
          }
        }
      }
      
      currentSearchQuery = query;
      currentPage = page;
      
      if (typeof window.showResults === 'function') {
        window.showResults(query);
      }
    } catch (err) {
      const errorMessage = getResultsText(lang, 'error');
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
