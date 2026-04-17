document.addEventListener('DOMContentLoaded', function () {
  const stack = document.getElementById('flashcard-stack');
  if (!stack) {
    return;
  }

  const cards = Array.from(stack.querySelectorAll('.stack-card'));
  let activeIndex = 0;

  const prevButton = document.getElementById('prev-card');
  const nextButton = document.getElementById('next-card');
  const positionLabel = document.getElementById('card-position');

  function updateStack() {
    cards.forEach((card, index) => {
      card.classList.remove('active', 'next', 'prev', 'hidden');
      if (index === activeIndex) {
        card.classList.add('active');
      } else if (index === activeIndex + 1) {
        card.classList.add('next');
      } else if (index === activeIndex - 1) {
        card.classList.add('prev');
      } else {
        card.classList.add('hidden');
      }
    });

    if (positionLabel) {
      positionLabel.textContent = `${activeIndex + 1} / ${cards.length}`;
    }
  }

  function showPrevious() {
    activeIndex = activeIndex > 0 ? activeIndex - 1 : cards.length - 1;
    updateStack();
  }

  function showNext() {
    activeIndex = activeIndex < cards.length - 1 ? activeIndex + 1 : 0;
    updateStack();
  }

  prevButton.addEventListener('click', showPrevious);
  nextButton.addEventListener('click', showNext);

  cards.forEach((card) => {
    card.addEventListener('click', () => {
      if (card.classList.contains('active')) {
        showNext();
      }
    });
  });

  updateStack();
});