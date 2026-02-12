const form = document.getElementById('search-form');
const statusText = document.getElementById('status');
const summaryText = document.getElementById('summary');
const catalogue = document.getElementById('catalogue');
const cardTemplate = document.getElementById('card-template');

function placeholderImage(source) {
  const labels = {
    swiggy: 'Swiggy',
    blinkit: 'Blinkit',
    zepto: 'Zepto',
  };
  const text = encodeURIComponent(labels[source] || 'Store');
  return `https://placehold.co/640x360/e2e8f0/334155?text=${text}`;
}

function renderResults(data) {
  catalogue.innerHTML = '';
  summaryText.textContent = data.summary || '';
  statusText.textContent = `Found ${data.total} results for "${data.query}"`;

  if (!data.results.length) {
    statusText.textContent = `No products found for "${data.query}".`;
    return;
  }

  for (const item of data.results) {
    const node = cardTemplate.content.cloneNode(true);
    node.querySelector('.name').textContent = item.name;
    node.querySelector('.meta').textContent = `${item.source.toUpperCase()} • score ${item.score}`;
    node.querySelector('.price').textContent = item.price ? `₹${item.price} ${item.unit || ''}` : 'Price unavailable';
    const image = node.querySelector('.card-img');
    image.src = item.image || placeholderImage(item.source);
    image.alt = item.name;

    const link = node.querySelector('.link');
    link.href = item.link;
    catalogue.appendChild(node);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  if (!prompt) return;

  statusText.textContent = 'Searching Swiggy, Blinkit, and Zepto...';
  summaryText.textContent = '';

  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error('Search failed');
    }

    const data = await response.json();
    renderResults(data);
  } catch (error) {
    statusText.textContent = 'Unable to search right now. Please try again.';
  }
});
