document.addEventListener('DOMContentLoaded', function () {
  const pageBody = document.body;
  const heroForm = document.querySelector('.hero-form');
  const heroDropzone = document.getElementById('hero-dropzone');
  const heroFileInput = document.getElementById('note_file');
  const heroTextInput = document.getElementById('note_text');
  const heroWordBadge = document.getElementById('hero-word-badge');
  const heroFilePill = document.getElementById('hero-file-pill');
  const chooseFileButton = document.getElementById('choose-file-btn');
  const heroHistoryGallery = document.getElementById('hero-history-gallery');
  const deckPage = document.querySelector('.deck-page');
  const positionLabel = document.getElementById('card-position');
  const progressFill = document.getElementById('stage-progress-fill');
  const stageTopicTitle = document.getElementById('stage-topic-title');
  const cardContainer = document.getElementById('stage-card-container');
  const cardStack = document.getElementById('deck-card-stack');
  const savedCardList = document.getElementById('saved-card-list');
  const savedCardCount = document.getElementById('saved-card-count');
  const deckHistoryList = document.getElementById('deck-history-list');
  const deckHistoryCount = document.getElementById('deck-history-count');
  const preview = document.getElementById('saved-preview');
  const previewPanel = document.getElementById('saved-preview-panel');
  const previewQuestion = document.getElementById('saved-preview-question');
  const previewAnswer = document.getElementById('saved-preview-answer');
  const previewSource = document.getElementById('saved-preview-source');
  const previewMeta = document.getElementById('saved-preview-meta');
  const previewFlip = document.getElementById('saved-preview-flip');
  const previewClose = document.getElementById('saved-preview-close');
  const cardsJson = document.getElementById('deck-cards-json');

  const SAVED_CARDS_KEY = 'alexandria_saved_cards_v2';
  const DECK_HISTORY_KEY = 'alexandria_deck_history_v2';

  function startLoading() {
    if (pageBody) {
      pageBody.classList.add('is-loading');
    }
  }

  function safeParseStorage(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || '[]');
    } catch (error) {
      return [];
    }
  }

  function formatDateLabel(value) {
    if (!value) {
      return '';
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString('tr-TR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  if (heroForm) {
    heroForm.addEventListener('submit', function (event) {
      const submitter = event.submitter;
      if (submitter && submitter.name === 'action' && submitter.value === 'clear') {
        return;
      }
      startLoading();
    });
  }

  function updateHeroComposerState() {
    if (!heroForm || !heroTextInput) {
      return;
    }

    const textValue = heroTextInput.value.trim();
    const hasText = Boolean(textValue);
    const hasFile = Boolean(heroFileInput && heroFileInput.files && heroFileInput.files.length);
    const words = textValue ? textValue.split(/\s+/).filter(Boolean).length : 0;

    heroForm.dataset.hasInput = hasText || hasFile ? 'true' : 'false';

    if (heroWordBadge) {
      if (hasText) {
        heroWordBadge.textContent = `${words.toLocaleString('tr-TR')} WORDS`;
      } else if (hasFile) {
        heroWordBadge.textContent = 'FILE READY';
      } else {
        heroWordBadge.textContent = '0 WORDS';
      }
    }

    if (heroFilePill) {
      if (hasFile) {
        heroFilePill.hidden = false;
        heroFilePill.textContent = heroFileInput.files[0].name;
      } else {
        heroFilePill.hidden = true;
        heroFilePill.textContent = '';
      }
    }
  }

  function renderHeroHistoryGallery() {
    if (!heroHistoryGallery) {
      return;
    }

    const history = safeParseStorage(DECK_HISTORY_KEY)
      .filter(function (deck) {
        return deck && deck.id && Array.isArray(deck.cards) && deck.cards.length;
      })
      .sort(function (left, right) {
        return new Date(right.createdAt) - new Date(left.createdAt);
      });

    heroHistoryGallery.innerHTML = '';

    if (!history.length) {
      const emptyState = document.createElement('div');
      emptyState.className = 'hero-history-empty';
      emptyState.textContent = 'Henuz olusturulmus bir set yok. Ilk flashcard galerin burada gorunecek.';
      heroHistoryGallery.appendChild(emptyState);
      return;
    }

    history.forEach(function (deck) {
      const card = document.createElement('a');
      card.className = 'hero-history-card';
      card.setAttribute('aria-label', `${deck.title || 'Flashcard Seti'} kartlarini ac`);
      card.href = `/deck?history=${encodeURIComponent(deck.id)}`;

      const title = document.createElement('strong');
      title.textContent = deck.title || 'Flashcard Seti';

      const meta = document.createElement('div');
      meta.className = 'hero-history-card__meta';

      const count = document.createElement('span');
      count.textContent = `${deck.cards.length} kart`;

      const date = document.createElement('span');
      date.textContent = formatDateLabel(deck.createdAt);

      meta.appendChild(count);
      meta.appendChild(date);
      card.appendChild(title);
      card.appendChild(meta);
      card.addEventListener('click', startLoading);
      heroHistoryGallery.appendChild(card);
    });
  }

  function assignDroppedFile(fileList) {
    if (!heroFileInput || !fileList || !fileList.length) {
      return;
    }

    try {
      const transfer = new DataTransfer();
      Array.from(fileList).forEach(function (file) {
        transfer.items.add(file);
      });
      heroFileInput.files = transfer.files;
    } catch (error) {
      return;
    }
  }

  if (heroTextInput) {
    heroTextInput.addEventListener('input', updateHeroComposerState);
  }

  if (heroFileInput) {
    heroFileInput.addEventListener('change', updateHeroComposerState);
  }

  if (chooseFileButton && heroFileInput) {
    chooseFileButton.addEventListener('click', function (event) {
      event.stopPropagation();
      heroFileInput.click();
    });
  }

  if (heroDropzone) {
    heroDropzone.addEventListener('click', function () {
      if (heroTextInput) {
        heroTextInput.focus();
      }
    });

    heroDropzone.addEventListener('dragenter', function (event) {
      event.preventDefault();
      heroDropzone.classList.add('is-dragover');
    });

    heroDropzone.addEventListener('dragover', function (event) {
      event.preventDefault();
      heroDropzone.classList.add('is-dragover');
    });

    heroDropzone.addEventListener('dragleave', function (event) {
      if (event.target === heroDropzone) {
        heroDropzone.classList.remove('is-dragover');
      }
    });

    heroDropzone.addEventListener('drop', function (event) {
      event.preventDefault();
      heroDropzone.classList.remove('is-dragover');

      const transfer = event.dataTransfer;
      if (!transfer) {
        return;
      }

      if (transfer.files && transfer.files.length) {
        assignDroppedFile(transfer.files);
        updateHeroComposerState();
        return;
      }

      const droppedText = transfer.getData('text/plain');
      if (droppedText && heroTextInput) {
        heroTextInput.value = droppedText;
        updateHeroComposerState();
      }
    });
  }

  document.addEventListener('paste', function (event) {
    if (!heroForm || !heroTextInput) {
      return;
    }

    const target = event.target;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
      return;
    }

    const pastedText = event.clipboardData && event.clipboardData.getData('text/plain');
    if (pastedText) {
      heroTextInput.value = pastedText;
      updateHeroComposerState();
    }
  });

  updateHeroComposerState();
  renderHeroHistoryGallery();

  if (!deckPage || !cardsJson || !cardContainer || !cardStack) {
    return;
  }

  function safeParseString(value, fallbackValue) {
    try {
      return JSON.parse(value);
    } catch (error) {
      return fallbackValue;
    }
  }

  function setStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function buildTopicTitle(text) {
    const words = String(text || '').trim().split(/\s+/).filter(Boolean).slice(0, 7);
    if (!words.length) {
      return 'Flashcard Seti';
    }
    return words.join(' ');
  }

  function normalizeCard(card, fallbackDeckId, fallbackDeckTitle, fallbackIndex) {
    if (!card || typeof card !== 'object') {
      return null;
    }

    const question = String(card.question || '').trim();
    const answer = String(card.answer || '').trim();
    if (!question || !answer) {
      return null;
    }

    return {
      deckId: String(card.deckId || fallbackDeckId || ''),
      deckTitle: String(card.deckTitle || fallbackDeckTitle || buildTopicTitle(question)),
      cardIndex: Number.isFinite(Number(card.cardIndex)) ? Number(card.cardIndex) : fallbackIndex,
      question: question,
      answer: answer,
      source: String(card.source || '').trim(),
      savedAt: card.savedAt || null,
    };
  }

  function getSavedCards() {
    return safeParseStorage(SAVED_CARDS_KEY)
      .map(function (card) {
        return normalizeCard(card, card && card.deckId, card && card.deckTitle, card && card.cardIndex);
      })
      .filter(Boolean);
  }

  function getDeckHistory() {
    return safeParseStorage(DECK_HISTORY_KEY)
      .map(function (deck) {
        if (!deck || typeof deck !== 'object') {
          return null;
        }

        const deckId = String(deck.id || '');
        const cards = Array.isArray(deck.cards)
          ? deck.cards
              .map(function (card, index) {
                return normalizeCard(card, deckId, deck.title, index);
              })
              .filter(Boolean)
          : [];

        if (!deckId || !cards.length) {
          return null;
        }

        return {
          id: deckId,
          title: String(deck.title || buildTopicTitle(cards[0].question)),
          createdAt: deck.createdAt || new Date().toISOString(),
          activeIndex: Number.isFinite(Number(deck.activeIndex)) ? Number(deck.activeIndex) : 0,
          cards: cards.map(function (card, index) {
            return Object.assign({}, card, { deckId: deckId, cardIndex: index });
          }),
        };
      })
      .filter(Boolean);
  }

  const initialCards = safeParseString(cardsJson.textContent || '[]', []);

  let currentDeck = {
    id: deckPage.dataset.deckId || String(Date.now()),
    title: deckPage.dataset.deckTitle || 'Flashcard Seti',
    createdAt: deckPage.dataset.generatedAt || new Date().toISOString(),
    cards: initialCards
      .map(function (card, index) {
        return normalizeCard(card, deckPage.dataset.deckId || String(Date.now()), deckPage.dataset.deckTitle, index);
      })
      .filter(Boolean),
    activeIndex: 0,
  };

  function persistDeck(deck) {
    const history = getDeckHistory();
    const payload = {
      id: deck.id,
      title: deck.title,
      createdAt: deck.createdAt,
      activeIndex: deck.activeIndex,
      cards: deck.cards,
    };
    const existingIndex = history.findIndex(function (item) {
      return item.id === deck.id;
    });

    if (existingIndex >= 0) {
      history[existingIndex] = payload;
    } else {
      history.unshift(payload);
    }

    setStorage(DECK_HISTORY_KEY, history.slice(0, 30));
  }

  function isCardSaved(cardData) {
    return getSavedCards().some(function (item) {
      return item.deckId === cardData.deckId && item.cardIndex === cardData.cardIndex;
    });
  }

  function closeSavedPreview() {
    if (!preview) {
      return;
    }
    preview.hidden = true;
    if (previewPanel) {
      previewPanel.classList.remove('is-flipped');
    }
  }

  function isPreviewOpen() {
    return Boolean(preview && !preview.hidden);
  }

  function togglePreviewFlip() {
    if (!isPreviewOpen() || !previewPanel) {
      return;
    }
    previewPanel.classList.toggle('is-flipped');
  }

  function toggleActiveCardFlip() {
    const activeCard = cardStack.querySelector('.flashcard.active');
    if (activeCard) {
      activeCard.classList.toggle('flipped');
    }
  }

  function updateProgress() {
    const total = currentDeck.cards.length || 1;
    const currentPosition = Math.min(currentDeck.activeIndex + 1, total);

    if (positionLabel) {
      positionLabel.textContent = `${currentPosition} / ${total}`;
    }

    if (progressFill) {
      progressFill.style.width = `${(currentPosition / total) * 100}%`;
    }

    if (stageTopicTitle) {
      stageTopicTitle.textContent = currentDeck.title || 'Flashcard Seti';
    }
  }

  function updateSaveButtons() {
    const renderedCards = Array.from(cardStack.querySelectorAll('.flashcard'));
    renderedCards.forEach(function (cardElement, index) {
      const saveButton = cardElement.querySelector('.save-card-btn');
      const cardData = currentDeck.cards[index];
      if (!saveButton || !cardData) {
        return;
      }
      if (isCardSaved(cardData)) {
        saveButton.textContent = 'Kaydedildi';
        saveButton.classList.add('is-saved');
      } else {
        saveButton.textContent = 'Kaydet';
        saveButton.classList.remove('is-saved');
      }
    });
  }

  function renderSavedCards() {
    if (!savedCardList || !savedCardCount) {
      return;
    }

    const savedCards = getSavedCards();
    savedCardCount.textContent = String(savedCards.length);
    savedCardList.innerHTML = '';

    if (!savedCards.length) {
      const emptyState = document.createElement('p');
      emptyState.className = 'panel-empty';
      emptyState.textContent = 'Kaydettigin kartlar burada gorunecek.';
      savedCardList.appendChild(emptyState);
      return;
    }

    savedCards
      .slice()
      .sort(function (left, right) {
        return new Date(right.savedAt || 0) - new Date(left.savedAt || 0);
      })
      .forEach(function (card) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'saved-card-item';

        const title = document.createElement('strong');
        title.textContent = card.question;

        const meta = document.createElement('span');
        meta.className = 'saved-card-meta';
        meta.textContent = `${card.deckTitle} • ${card.cardIndex + 1}. kart`;

        button.appendChild(title);
        button.appendChild(meta);
        button.addEventListener('click', function () {
          openSavedPreview(card);
        });
        savedCardList.appendChild(button);
      });
  }

  function loadDeck(deck) {
    currentDeck = {
      id: deck.id,
      title: deck.title || buildTopicTitle((deck.cards[0] || {}).question),
      createdAt: deck.createdAt,
      cards: (deck.cards || [])
        .map(function (card, index) {
          return normalizeCard(card, deck.id, deck.title, index);
        })
        .filter(Boolean),
      activeIndex: Math.max(0, Math.min(deck.activeIndex || 0, (deck.cards || []).length - 1)),
    };

    renderDeckCards();
    renderDeckHistory();
    renderSavedCards();
    updateProgress();
  }

  function renderDeckHistory() {
    if (!deckHistoryList || !deckHistoryCount) {
      return;
    }

    const history = getDeckHistory();
    deckHistoryCount.textContent = String(history.length);
    deckHistoryList.innerHTML = '';

    if (!history.length) {
      const emptyState = document.createElement('p');
      emptyState.className = 'panel-empty';
      emptyState.textContent = 'Olusturdugun konu setleri burada listelenecek.';
      deckHistoryList.appendChild(emptyState);
      return;
    }

    history
      .slice()
      .sort(function (left, right) {
        return new Date(right.createdAt) - new Date(left.createdAt);
      })
      .forEach(function (deck) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'deck-history-item';
        if (deck.id === currentDeck.id) {
          button.classList.add('is-active');
        }
        button.textContent = `${deck.title} - ${formatDateLabel(deck.createdAt)}`;
        button.addEventListener('click', function () {
          loadDeck(deck);
        });
        deckHistoryList.appendChild(button);
      });
  }

  function saveCard(cardData) {
    const normalizedCard = normalizeCard(cardData, currentDeck.id, currentDeck.title, cardData.cardIndex);
    if (!normalizedCard) {
      return;
    }

    const savedCards = getSavedCards();
    const exists = savedCards.some(function (item) {
      return item.deckId === normalizedCard.deckId && item.cardIndex === normalizedCard.cardIndex;
    });

    if (!exists) {
      savedCards.unshift(
        Object.assign({}, normalizedCard, {
          savedAt: new Date().toISOString(),
        })
      );
      setStorage(SAVED_CARDS_KEY, savedCards.slice(0, 100));
    }

    const body = new URLSearchParams();
    body.set('question', normalizedCard.question);
    body.set('answer', normalizedCard.answer);
    body.set('source', normalizedCard.source);

    fetch('/save-card', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body.toString(),
    }).catch(function () {
      return null;
    });

    renderSavedCards();
    updateSaveButtons();
  }

  function openSavedPreview(card) {
    const normalizedCard = normalizeCard(card, card && card.deckId, card && card.deckTitle, card && card.cardIndex);
    if (
      !normalizedCard ||
      !preview ||
      !previewPanel ||
      !previewQuestion ||
      !previewAnswer ||
      !previewSource ||
      !previewMeta
    ) {
      return;
    }

    preview.hidden = false;
    previewPanel.classList.remove('is-flipped');
    previewQuestion.textContent = normalizedCard.question;
    previewAnswer.textContent = normalizedCard.answer;
    previewSource.textContent = normalizedCard.source ? `Kaynak: ${normalizedCard.source}` : '';
    previewMeta.textContent = `${normalizedCard.deckTitle} • ${normalizedCard.cardIndex + 1}. kart${
      card.savedAt ? ` • ${formatDateLabel(card.savedAt)}` : ''
    }`;
  }

  function goPrevious() {
    closeSavedPreview();
    const total = currentDeck.cards.length;
    currentDeck.activeIndex = currentDeck.activeIndex > 0 ? currentDeck.activeIndex - 1 : total - 1;
    renderDeckCards();
  }

  function goNext() {
    closeSavedPreview();
    const total = currentDeck.cards.length;
    currentDeck.activeIndex = currentDeck.activeIndex < total - 1 ? currentDeck.activeIndex + 1 : 0;
    renderDeckCards();
  }

  function renderDeckCards() {
    cardStack.innerHTML = '';

    currentDeck.cards.forEach(function (card, index) {
      const article = document.createElement('article');
      article.className = 'flashcard';
      if (index === currentDeck.activeIndex) {
        article.classList.add('active');
        article.style.opacity = '1';
        article.style.pointerEvents = 'auto';
      } else {
        article.style.opacity = '0';
        article.style.pointerEvents = 'none';
      }

      article.innerHTML = `
        <button class="card-nav card-nav--prev" type="button" aria-label="Onceki kart">&#8592;</button>
        <button class="card-nav card-nav--next" type="button" aria-label="Sonraki kart">&#8594;</button>
        <div class="card-quick-actions">
          <button class="mini-action flip-card-btn" type="button">Cevir (Space)</button>
          <button class="mini-action save-card-btn" type="button">Kaydet (S)</button>
        </div>
        <div class="card-panel">
          <div class="card-face card-front">
            <span class="card-chip">ON</span>
            <h2>${escapeHtml(card.question)}</h2>
            <p>Karti tiklayarak arkasini gor.</p>
          </div>
          <div class="card-face card-back">
            <span class="card-chip">ARKA</span>
            <h2>${escapeHtml(card.answer)}</h2>
            ${card.source ? `<p class="card-source">Kaynak: ${escapeHtml(card.source)}</p>` : ''}
          </div>
        </div>
      `;

      const prevButton = article.querySelector('.card-nav--prev');
      const nextButton = article.querySelector('.card-nav--next');
      const flipButton = article.querySelector('.flip-card-btn');
      const saveButton = article.querySelector('.save-card-btn');

      prevButton.addEventListener('click', function (event) {
        event.stopPropagation();
        goPrevious();
      });

      nextButton.addEventListener('click', function (event) {
        event.stopPropagation();
        goNext();
      });

      flipButton.addEventListener('click', function (event) {
        event.stopPropagation();
        article.classList.toggle('flipped');
      });

      saveButton.addEventListener('click', function (event) {
        event.stopPropagation();
        saveCard(card);
      });

      article.addEventListener('click', function (event) {
        if (event.target.closest('button')) {
          return;
        }
        article.classList.toggle('flipped');
      });

      cardStack.appendChild(article);
    });

    persistDeck(currentDeck);
    renderDeckHistory();
    updateProgress();
    updateSaveButtons();
  }

  if (previewClose) {
    previewClose.addEventListener('click', closeSavedPreview);
  }

  if (previewFlip) {
    previewFlip.addEventListener('click', function (event) {
      event.stopPropagation();
      togglePreviewFlip();
    });
  }

  if (preview) {
    preview.addEventListener('click', function (event) {
      if (event.target.classList.contains('saved-preview__backdrop')) {
        closeSavedPreview();
        return;
      }
      if (!event.target.closest('button')) {
        togglePreviewFlip();
      }
    });
  }

  document.addEventListener('keydown', function (event) {
    const target = event.target;
    const isTypingTarget =
      target &&
      (target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.tagName === 'SELECT' ||
        target.isContentEditable);

    if (isTypingTarget) {
      return;
    }

    if (event.code === 'KeyN') {
      const newFlashcardLink = document.querySelector('.panel-cta');
      if (newFlashcardLink) {
        window.location.href = newFlashcardLink.href;
      }
      return;
    }

    if (event.code === 'Escape' && isPreviewOpen()) {
      closeSavedPreview();
      return;
    }

    if (event.code === 'ArrowLeft' && !isPreviewOpen()) {
      event.preventDefault();
      goPrevious();
      return;
    }

    if (event.code === 'ArrowRight' && !isPreviewOpen()) {
      event.preventDefault();
      goNext();
      return;
    }

    if (event.code === 'Space') {
      event.preventDefault();
      if (isPreviewOpen()) {
        togglePreviewFlip();
      } else {
        toggleActiveCardFlip();
      }
      return;
    }

    if (event.code === 'KeyS' && !isPreviewOpen()) {
      event.preventDefault();
      const activeCard = currentDeck.cards[currentDeck.activeIndex];
      if (activeCard) {
        saveCard(activeCard);
      }
    }
  });

  const existingDecks = getDeckHistory();
  const requestedDeckId = new URLSearchParams(window.location.search).get('history');
  const existingDeck = existingDecks.find(function (item) {
    return item.id === currentDeck.id;
  });
  const requestedDeck = requestedDeckId
    ? existingDecks.find(function (item) {
        return item.id === requestedDeckId;
      })
    : null;

  if (requestedDeck) {
    currentDeck = {
      id: requestedDeck.id,
      title: requestedDeck.title,
      createdAt: requestedDeck.createdAt,
      cards: requestedDeck.cards,
      activeIndex: Math.max(0, Math.min(requestedDeck.activeIndex || 0, requestedDeck.cards.length - 1)),
    };
  } else if (existingDeck && typeof existingDeck.activeIndex === 'number') {
    currentDeck.activeIndex = Math.max(0, Math.min(existingDeck.activeIndex, currentDeck.cards.length - 1));
  }

  persistDeck(currentDeck);
  renderDeckCards();
  renderSavedCards();
});
