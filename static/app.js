const form = document.querySelector('#query-form');
const input = document.querySelector('#question');
const askButton = document.querySelector('#ask-button');
const emptyState = document.querySelector('#empty-state');
const loadingState = document.querySelector('#loading-state');
const answerArea = document.querySelector('#answer-area');
const errorState = document.querySelector('#error-state');
const answerText = document.querySelector('#answer-text');
const tableWrap = document.querySelector('#table-wrap');
const resultCount = document.querySelector('#result-count');
const answerLabel = document.querySelector('#answer-label');

input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}

function renderTable(columns, rows) {
  if (!columns.length || !rows.length) return '';
  const heads = columns.map(column => `<th scope="col">${esc(column.replaceAll('_', ' '))}</th>`).join('');
  const body = rows.map(row => `<tr>${columns.map(column => `<td>${esc(row[column])}</td>`).join('')}</tr>`).join('');
  return `<table class="result-table"><thead><tr>${heads}</tr></thead><tbody>${body}</tbody></table>`;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  askButton.disabled = true;
  emptyState.classList.add('hidden');
  answerArea.classList.add('hidden');
  errorState.classList.add('hidden');
  loadingState.classList.remove('hidden');
  resultCount.textContent = '';
  answerLabel.textContent = 'Answer';
  try {
    const response = await fetch('/api/query', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question})
    });
    const payload = await response.json();
    loadingState.classList.add('hidden');
    if (!response.ok || payload.error) {
      answerLabel.textContent = 'Could not answer';
      errorState.textContent = payload.error || 'Something went wrong. Please try again.';
      errorState.classList.remove('hidden');
      return;
    }
    answerText.textContent = payload.answer || 'No matching records were found.';
    tableWrap.innerHTML = renderTable(payload.columns || [], payload.rows || []);
    if (payload.rows?.length) resultCount.textContent = `${payload.rows.length} ${payload.rows.length === 1 ? 'row' : 'rows'}`;
    answerArea.classList.remove('hidden');
  } catch (_) {
    loadingState.classList.add('hidden');
    answerLabel.textContent = 'Could not answer';
    errorState.textContent = 'Could not reach the catalog. Check that the app server is running and try again.';
    errorState.classList.remove('hidden');
  } finally {
    askButton.disabled = false;
  }
});
