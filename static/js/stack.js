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
  const savedCardsPage = document.querySelector('.saved-cards-page');
  const savedCardsGrid = document.getElementById('saved-cards-grid');
  const deckHistoryList = document.getElementById('deck-history-list');
  const deckHistoryCount = document.getElementById('deck-history-count');
  const preview = document.getElementById('saved-preview');
  const previewCard = document.getElementById('saved-preview-card');
  const previewFlip = document.getElementById('saved-preview-flip');
  const previewClose = document.getElementById('saved-preview-close');
  const deleteConfirmModal = document.getElementById('delete-confirm-modal');
  const deleteConfirmTitle = document.getElementById('delete-confirm-title');
  const deleteConfirmDescription = document.getElementById('delete-confirm-description');
  const deleteConfirmCancel = document.getElementById('delete-confirm-cancel');
  const deleteConfirmAccept = document.getElementById('delete-confirm-accept');
  const cardsJson = document.getElementById('deck-cards-json');

  const SAVED_CARDS_KEY = 'alexandria_saved_cards_v2';
  const DECK_HISTORY_KEY = 'alexandria_deck_history_v2';
  const HIDDEN_DECK_HISTORY_KEY = 'alexandria_hidden_deck_history_v1';
  let isLoadingLocked = false;
  let pendingDeleteAction = null;
  let savedCardsCache = null;
  let deckHistoryCache = null;
  let hiddenDeckIdsCache = null;

  const heroFormControls = heroForm
    ? Array.from(heroForm.querySelectorAll('button, input, textarea, select')).filter(function (element) {
        return element && element.type !== 'hidden';
      })
    : [];

  function setControlsDisabled(elements, disabled) {
    elements.forEach(function (element) {
      element.disabled = disabled;
    });
  }

  function isTypingTarget(target) {
    return Boolean(
      target &&
        (target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.tagName === 'SELECT' ||
          target.isContentEditable)
    );
  }

  function sortByNewest(items, key) {
    return items.slice().sort(function (left, right) {
      return new Date(right[key] || 0) - new Date(left[key] || 0);
    });
  }

  function startLoading() {
    if (isLoadingLocked) {
      return;
    }

    isLoadingLocked = true;
    if (pageBody) {
      pageBody.classList.add('is-loading');
    }

    setControlsDisabled(heroFormControls, true);
  }

  function stopLoading() {
    isLoadingLocked = false;
    if (pageBody) {
      pageBody.classList.remove('is-loading');
    }

    setControlsDisabled(heroFormControls, false);
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
      if (isLoadingLocked) {
        event.preventDefault();
        return;
      }
      startLoading();
    });
  }

  window.addEventListener('pageshow', function () {
    // Clear any loading state restored from the back/forward cache.
    stopLoading();
  });

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
        heroWordBadge.textContent = `${words.toLocaleString('tr-TR')} KELİME`;
      } else if (hasFile) {
        heroWordBadge.textContent = 'DOSYA HAZIR';
      } else {
        heroWordBadge.textContent = '0 KELİME';
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

    const history = sortByNewest(getDeckHistory(), 'createdAt');

    heroHistoryGallery.innerHTML = '';

    if (!history.length) {
      const emptyState = document.createElement('div');
      emptyState.className = 'hero-history-empty';
      emptyState.textContent = 'Henüz set oluşturulmadı. Oluşturulan setler burada görünür.';
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

    if (isTypingTarget(event.target)) {
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

  // Apply simple random animations to the file-type pills inside the dropzone
  function applyRandomAnimationsToFilePills() {
    const pills = Array.from(document.querySelectorAll('.hero-dropzone .file-type-pill'));
    if (!pills.length) return;
    const animClasses = ['anim-bounce', 'anim-rotate', 'anim-pulse', 'anim-sway'];

    function assign() {
      pills.forEach(function (pill) {
        // remove previous anim classes
        pill.classList.remove(...animClasses);
        const cls = animClasses[Math.floor(Math.random() * animClasses.length)];
        pill.classList.add(cls);
        // randomize duration and small delay for variety
        pill.style.animationDuration = (Math.random() * 1.2 + 0.6).toFixed(2) + 's';
        pill.style.animationDelay = (Math.random() * 0.9).toFixed(2) + 's';
      });
    }

    assign();
    // reassign every 5s for light random effect
    setInterval(assign, 5000);
  }

  applyRandomAnimationsToFilePills();

  function initSavedCardsPage() {
    if (!savedCardsPage || !savedCardsGrid) {
      return;
    }

    const savedCards = Array.from(savedCardsGrid.querySelectorAll('.saved-card-flashcard'));

    savedCards.forEach(function (article) {
      bindFlashcardInteractions(article, { enableKeyboard: true });

      const deleteForm = article.querySelector('form');
      if (deleteForm) {
        deleteForm.addEventListener('submit', function (event) {
          event.preventDefault();
          const button = deleteForm.querySelector('[data-delete-card]');
          const question = button ? button.getAttribute('data-card-question') || 'Bu kart' : 'Bu kart';

          openDeleteConfirm({
            title: 'Kaydedilen kart silinsin mi?',
            description: question,
            onConfirm: function () {
              deleteForm.submit();
            },
          });
        });
      }
    });
  }

  initDeleteConfirmHandlers();

  if (!deckPage || !cardsJson || !cardContainer || !cardStack) {
    initSavedCardsPage();
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

  function setSavedCards(cards) {
    savedCardsCache = cards;
    setStorage(SAVED_CARDS_KEY, cards);
  }

  function setHiddenDeckIds(hiddenDeckIds) {
    hiddenDeckIdsCache = hiddenDeckIds;
    setStorage(HIDDEN_DECK_HISTORY_KEY, hiddenDeckIds);
  }

  function setDeckHistory(history) {
    deckHistoryCache = history;
    setStorage(DECK_HISTORY_KEY, history);
  }

  function getHiddenDeckIds() {
    if (hiddenDeckIdsCache) {
      return hiddenDeckIdsCache;
    }

    hiddenDeckIdsCache = safeParseStorage(HIDDEN_DECK_HISTORY_KEY).filter(function (value) {
      return typeof value === 'string' && value.trim();
    });
    return hiddenDeckIdsCache;
  }

  function hideDeckId(deckId) {
    const hiddenDeckIds = getHiddenDeckIds().slice();
    if (!hiddenDeckIds.includes(deckId)) {
      hiddenDeckIds.unshift(deckId);
      setHiddenDeckIds(hiddenDeckIds.slice(0, 100));
    }
  }

  function closeDeleteConfirm() {
    if (!deleteConfirmModal) {
      return;
    }

    deleteConfirmModal.hidden = true;
    deleteConfirmModal.setAttribute('aria-hidden', 'true');
    pendingDeleteAction = null;
  }

  function openDeleteConfirm(options) {
    if (!deleteConfirmModal || !deleteConfirmTitle || !deleteConfirmDescription) {
      return;
    }

    deleteConfirmTitle.textContent = options && options.title ? options.title : 'Bu öğe silinsin mi?';
    deleteConfirmDescription.textContent = options && options.description ? options.description : '';
    pendingDeleteAction = options && typeof options.onConfirm === 'function' ? options.onConfirm : null;
    deleteConfirmModal.hidden = false;
    deleteConfirmModal.setAttribute('aria-hidden', 'false');

    window.requestAnimationFrame(function () {
      if (deleteConfirmCancel) {
        deleteConfirmCancel.focus();
      }
    });
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderFlashcardActions(card, options) {
    const actionButtons = [];

    if (options && options.showPrevButton) {
      actionButtons.push('<button class="card-nav card-nav--prev" type="button" aria-label="Onceki kart">&#8592;</button>');
    }

    if (options && options.showNextButton) {
      actionButtons.push('<button class="card-nav card-nav--next" type="button" aria-label="Sonraki kart">&#8594;</button>');
    }

    const quickActions = [];

    if (options && options.showFlipButton) {
      quickActions.push('<button class="mini-action flip-card-btn" type="button">Çevir (Space)</button>');
    }

    if (options && options.showSaveButton) {
      quickActions.push('<button class="mini-action save-card-btn" type="button">Kaydet (K)</button>');
    }

    if (options && options.showEditLink) {
      quickActions.push(
        `<a class="mini-action" href="${escapeHtml(options.editUrl || '#')}">Düzenle</a>`
      );
    }

    if (options && options.showDeleteButton) {
      quickActions.push(
        `<button class="mini-action saved-card-delete-btn" type="button" data-delete-card data-card-question="${escapeHtml(
          card.question
        )}">Sil</button>`
      );
    }

    if (quickActions.length) {
      actionButtons.push(`<div class="card-quick-actions">${quickActions.join('')}</div>`);
    }

    return actionButtons.join('');
  }

  function renderFlashcardMarkup(card, options) {
    const hintText =
      options && typeof options.hintText === 'string' ? options.hintText : 'Karti tiklayarak arkasini gor.';
    const showHint = !options || options.showHint !== false;
    const sourceText = card.source ? `<p class="card-source">Kaynak: ${escapeHtml(card.source)}</p>` : '';

    return `
      ${renderFlashcardActions(card, options || {})}
      <div class="card-panel">
        <div class="card-face card-front">
          <span class="card-chip">SORU</span>
          <h2>${escapeHtml(card.question)}</h2>
          ${showHint ? `<p>${escapeHtml(hintText)}</p>` : ''}
        </div>
        <div class="card-face card-back">
          <span class="card-chip">CEVAP</span>
          <h2>${escapeHtml(card.answer)}</h2>
          ${sourceText}
        </div>
      </div>
    `;
  }

  function bindFlashcardInteractions(article, options) {
    if (!article) {
      return;
    }

    if (options && options.enableKeyboard !== false) {
      article.tabIndex = 0;
    }

    article.addEventListener('click', function (event) {
      if (event.target.closest('button, a, form')) {
        return;
      }
      article.classList.toggle('flipped');
    });

    article.addEventListener('keydown', function (event) {
      if (event.code !== 'Space' && event.code !== 'Enter') {
        return;
      }
      if (event.target.closest('button, a, input, textarea, select')) {
        return;
      }
      event.preventDefault();
      article.classList.toggle('flipped');
    });
  }

  function createFlashcardElement(card, options) {
    const article = document.createElement('article');
    const className = (options && options.className) || 'flashcard';
    article.className = className;
    if (options && options.active) {
      article.classList.add('active');
    }
    if (options && options.cardId !== undefined && options.cardId !== null) {
      article.dataset.cardId = String(options.cardId);
    }
    article.innerHTML = renderFlashcardMarkup(card, options || {});
    bindFlashcardInteractions(article, options || {});
    return article;
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
    if (savedCardsCache) {
      return savedCardsCache;
    }

    savedCardsCache = safeParseStorage(SAVED_CARDS_KEY)
      .map(function (card) {
        return normalizeCard(card, card && card.deckId, card && card.deckTitle, card && card.cardIndex);
      })
      .filter(Boolean);
    return savedCardsCache;
  }

  function getDeckHistory() {
    if (deckHistoryCache) {
      return deckHistoryCache;
    }

    const hiddenDeckIds = getHiddenDeckIds();
    deckHistoryCache = safeParseStorage(DECK_HISTORY_KEY)
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

        if (hiddenDeckIds.includes(deckId)) {
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
    return deckHistoryCache;
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
    if (getHiddenDeckIds().includes(deck.id)) {
      return;
    }

    const history = getDeckHistory().slice();
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

    setDeckHistory(history.slice(0, 30));
  }

  function isCardSaved(cardData) {
    return getSavedCards().some(function (item) {
      return item.deckId === cardData.deckId && item.cardIndex === cardData.cardIndex;
    });
  }

  function getSavedCardKey(cardData) {
    if (!cardData) {
      return '';
    }

    return `${cardData.deckId || ''}:${cardData.cardIndex}`;
  }

  let activeSavedCardKey = '';

  function closeSavedPreview() {
    if (!preview) {
      return;
    }
    preview.hidden = true;
    if (previewCard) {
      previewCard.classList.remove('flipped');
    }
    activeSavedCardKey = '';
    renderSavedCards();
  }

  function isPreviewOpen() {
    return Boolean(preview && !preview.hidden);
  }

  function togglePreviewFlip() {
    if (!isPreviewOpen() || !previewCard) {
      return;
    }
    previewCard.classList.toggle('flipped');
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
        saveButton.textContent = 'Kaydet (K)';
        saveButton.classList.remove('is-saved');
      }
    });
  }

  function setEmptyState(container, message) {
    container.innerHTML = '';
    const emptyState = document.createElement('p');
    emptyState.className = 'panel-empty';
    emptyState.textContent = message;
    container.appendChild(emptyState);
  }

  function createSidebarItem(config) {
    const item = document.createElement('div');
    item.className = config.itemClassName;
    if (config.isActive) {
      item.classList.add('is-active');
    }

    const openButton = document.createElement('button');
    openButton.type = 'button';
    openButton.className = config.openClassName;

    const title = document.createElement(config.titleTagName || 'strong');
    title.className = config.titleClassName || '';
    title.textContent = config.title;

    const meta = document.createElement('span');
    meta.className = config.metaClassName;
    meta.textContent = config.meta;

    openButton.appendChild(title);
    openButton.appendChild(meta);
    openButton.addEventListener('click', config.onOpen);

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = config.deleteClassName;
    deleteButton.setAttribute('aria-label', config.deleteAriaLabel);
    deleteButton.textContent = '×';
    deleteButton.addEventListener('click', function (event) {
      event.stopPropagation();
      config.onDelete();
    });

    item.appendChild(openButton);
    item.appendChild(deleteButton);
    return item;
  }

  function renderSavedCards() {
    if (!savedCardList || !savedCardCount) {
      return;
    }

    const savedCards = getSavedCards();
    savedCardCount.textContent = String(savedCards.length);

    if (!savedCards.length) {
      setEmptyState(savedCardList, 'Kaydettigin kartlar burada gorunecek.');
      return;
    }

    savedCardList.innerHTML = '';
    sortByNewest(savedCards, 'savedAt').forEach(function (card) {
      savedCardList.appendChild(
        createSidebarItem({
          itemClassName: 'saved-card-item',
          openClassName: 'saved-card-item__open',
          title: card.question,
          meta: `${card.deckTitle || 'Flashcard Seti'} • ${card.cardIndex + 1}. kart`,
          metaClassName: 'saved-card-item__meta',
          deleteClassName: 'saved-card-delete-btn',
          deleteAriaLabel: `${card.question} kartını sil`,
          isActive: getSavedCardKey(card) === activeSavedCardKey,
          onOpen: function () {
            openSavedPreview(card);
          },
          onDelete: function () {
            openDeleteConfirm({
              title: 'Kaydedilen kart silinsin mi?',
              description: card.question,
              onConfirm: function () {
                deleteSavedCard(card);
              },
            });
          },
        })
      );
    });
  }

  function deleteSavedCard(cardData) {
    const targetKey = getSavedCardKey(cardData);
    const savedCards = getSavedCards().filter(function (item) {
      return getSavedCardKey(item) !== targetKey;
    });

    setSavedCards(savedCards);
    if (getSavedCardKey(cardData) === activeSavedCardKey) {
      closeSavedPreview();
    }
    renderSavedCards();
    updateSaveButtons();
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

    if (!history.length) {
      setEmptyState(deckHistoryList, 'Oluşturduğun konu setleri burada listelenecek.');
      return;
    }

    deckHistoryList.innerHTML = '';
    sortByNewest(history, 'createdAt').forEach(function (deck) {
      deckHistoryList.appendChild(
        createSidebarItem({
          itemClassName: 'deck-history-item',
          openClassName: 'deck-history-item__open',
          title: deck.title,
          titleTagName: 'span',
          titleClassName: 'deck-history-item__title',
          meta: `${formatDateLabel(deck.createdAt)} • ${deck.cards.length} kart`,
          metaClassName: 'deck-history-item__meta',
          deleteClassName: 'deck-history-item__delete',
          deleteAriaLabel: `${deck.title} konusunu sil`,
          isActive: deck.id === currentDeck.id,
          onOpen: function () {
            loadDeck(deck);
          },
          onDelete: function () {
            openDeleteConfirm({
              title: 'Oluşturulan konu silinsin mi?',
              description: deck.title,
              onConfirm: function () {
                deleteDeckHistory(deck.id);
              },
            });
          },
        })
      );
    });
  }

  function deleteDeckHistory(deckId) {
    const filteredHistory = getDeckHistory().filter(function (deck) {
      return deck.id !== deckId;
    });

    hideDeckId(deckId);
    setDeckHistory(filteredHistory);

    if (currentDeck.id === deckId) {
      currentDeck.activeIndex = Math.max(0, Math.min(currentDeck.activeIndex, currentDeck.cards.length - 1));
    }

    renderDeckHistory();
    updateProgress();
    renderSavedCards();
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
      setSavedCards(savedCards.slice(0, 100));
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
    if (!normalizedCard || !preview || !previewCard) {
      return;
    }

    preview.hidden = false;
    previewCard.classList.remove('flipped');
    previewCard.innerHTML = renderFlashcardMarkup(normalizedCard, {
      showPrevButton: false,
      showNextButton: false,
      showFlipButton: false,
      showSaveButton: false,
      showEditLink: false,
      showDeleteButton: false,
      showHint: true,
      hintText: 'Karti tiklayarak arkasini gor.',
    });
    activeSavedCardKey = getSavedCardKey(normalizedCard);
    renderSavedCards();
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
      const article = createFlashcardElement(card, {
        className: 'flashcard',
        active: index === currentDeck.activeIndex,
        showPrevButton: true,
        showNextButton: true,
        showFlipButton: true,
        showSaveButton: true,
        showHint: true,
      });

      if (index === currentDeck.activeIndex) {
        article.style.opacity = '1';
        article.style.pointerEvents = 'auto';
      } else {
        article.style.opacity = '0';
        article.style.pointerEvents = 'none';
      }

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

  function handleDeleteConfirmAccept() {
    const action = pendingDeleteAction;
    closeDeleteConfirm();
    if (typeof action === 'function') {
      action();
    }
  }

  function initDeleteConfirmHandlers() {
    if (deleteConfirmCancel) {
      deleteConfirmCancel.addEventListener('click', closeDeleteConfirm);
    }

    if (deleteConfirmModal) {
      deleteConfirmModal.addEventListener('click', function (event) {
        if (event.target && event.target.hasAttribute('data-delete-confirm-close')) {
          closeDeleteConfirm();
        }
      });
    }

    if (deleteConfirmAccept) {
      deleteConfirmAccept.addEventListener('click', handleDeleteConfirmAccept);
    }
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
    if (isTypingTarget(event.target)) {
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

    if (event.code === 'Escape' && deleteConfirmModal && !deleteConfirmModal.hidden) {
      closeDeleteConfirm();
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

    if (event.code === 'KeyK' && !isPreviewOpen()) {
      event.preventDefault();
      const activeCard = currentDeck.cards[currentDeck.activeIndex];
      if (activeCard) {
        saveCard(activeCard);
      }
    }
  });

  if (cardStack) {
    cardStack.addEventListener(
      'wheel',
      function (e) {
        if (isPreviewOpen()) return;
        if (Math.abs(e.deltaY) < 2) return;
        e.preventDefault();
        if (e.deltaY > 0) {
          goNext();
        } else {
          goPrevious();
        }
      },
      { passive: false }
    );
  }

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
