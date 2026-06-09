const SESSION_ID = 'demo-session';
let state = null;

const elements = {
  history: document.querySelector('#history-list'),
  tree: document.querySelector('#data-tree'),
  messages: document.querySelector('#chat-messages'),
  outline: document.querySelector('#outline-preview'),
  detail: document.querySelector('#report-detail'),
  reportChip: document.querySelector('#current-report-chip'),
  form: document.querySelector('#chat-form'),
  input: document.querySelector('#chat-input'),
  sendButton: document.querySelector('#send-button'),
  error: document.querySelector('#app-error')
};

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `请求失败：${response.status}`);
  }
  return response.json();
}

function setLoading(isLoading) {
  elements.sendButton.disabled = isLoading;
  elements.sendButton.textContent = isLoading ? '发送中...' : '发送';
}

function showError(message = '') {
  elements.error.textContent = message;
  elements.error.hidden = !message;
}

async function loadState() {
  showError();
  state = await requestJson(`/api/state?session_id=${encodeURIComponent(SESSION_ID)}`);
  renderAll();
}

async function selectReport(reportId) {
  showError();
  state = await requestJson('/api/reports/select', {
    method: 'POST',
    body: JSON.stringify({ session_id: SESSION_ID, report_id: reportId })
  });
  renderAll();
}

async function toggleBinding(groupTitle, itemTitle) {
  showError();
  state = await requestJson('/api/bindings/toggle', {
    method: 'POST',
    body: JSON.stringify({ session_id: SESSION_ID, group_title: groupTitle, item_title: itemTitle })
  });
  renderAll();
}

async function sendMessage(message) {
  setLoading(true);
  showError();
  state = await requestJson('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ session_id: SESSION_ID, message })
  });
  renderAll();
  setLoading(false);
}

function renderHistory() {
  const activeId = state.activeReport.id;
  elements.history.innerHTML = state.history
    .map(
      report => `
        <button class="history-card ${report.id === activeId ? 'active' : ''}" type="button" data-report-id="${escapeHtml(report.id)}">
          <span class="history-card-title">${escapeHtml(report.title)}</span>
          <span class="history-card-summary">${escapeHtml(report.summary)}</span>
          <span class="history-meta">
            <span>${escapeHtml(report.date)}</span>
            <span class="status-dot">${escapeHtml(report.status)}</span>
          </span>
        </button>
      `
    )
    .join('');
}

function renderDataTree() {
  elements.tree.innerHTML = state.activeReport.boundData
    .map(
      group => `
        <div class="tree-group" role="group">
          <div class="tree-title" role="treeitem" aria-expanded="true">${escapeHtml(group.title)}</div>
          ${group.children
            .map(
              item => `
                <button class="tree-item ${item.bound ? 'bound' : ''}" type="button" role="treeitem" data-group-title="${escapeHtml(group.title)}" data-item-title="${escapeHtml(item.title)}">
                  ${escapeHtml(item.title)}
                </button>
              `
            )
            .join('')}
        </div>
      `
    )
    .join('');
}

function renderChat() {
  elements.reportChip.textContent = `${state.phase} · ${state.activeReport.title}`;
  elements.messages.innerHTML = state.activeReport.chat
    .map(message => `<div class="message ${escapeHtml(message.role)}">${escapeHtml(message.text)}</div>`)
    .join('');
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function renderOutline() {
  const outline = state.outline || state.activeReport.outline || [];
  elements.outline.innerHTML = outline
    .map(
      (item, index) => `
        <section class="outline-card">
          <span class="outline-index">${index + 1}</span>
          <h3>${escapeHtml(item.title)}</h3>
          <ul>${item.points.map(point => `<li>${escapeHtml(point)}</li>`).join('')}</ul>
        </section>
      `
    )
    .join('');
}

function renderDetail() {
  const report = state.activeReport;
  elements.detail.innerHTML = `
    <header class="report-cover">
      <h2>${escapeHtml(report.title)}</h2>
      <p>${escapeHtml(report.owner)} · ${escapeHtml(report.date)} · FastAPI 模拟数据</p>
    </header>
    <section class="metrics">
      ${report.metrics
        .map(metric => `<div class="metric"><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(metric.value)}</strong></div>`)
        .join('')}
    </section>
    <section class="detail-section">
      <h3>摘要</h3>
      <p>${escapeHtml(report.detail.lead)}</p>
      <div class="tag-row">${report.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}</div>
    </section>
    ${report.detail.sections
      .map(section => {
        const body = section.list
          ? `<ul>${section.list.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
          : `<p>${escapeHtml(section.content)}</p>`;
        return `<section class="detail-section"><h3>${escapeHtml(section.title)}</h3>${body}</section>`;
      })
      .join('')}
  `;
}

function renderAll() {
  renderHistory();
  renderDataTree();
  renderChat();
  renderOutline();
  renderDetail();
}

elements.history.addEventListener('click', event => {
  const card = event.target.closest('[data-report-id]');
  if (card) {
    selectReport(card.dataset.reportId).catch(error => showError(error.message));
  }
});

elements.tree.addEventListener('click', event => {
  const item = event.target.closest('[data-group-title][data-item-title]');
  if (item) {
    toggleBinding(item.dataset.groupTitle, item.dataset.itemTitle).catch(error => showError(error.message));
  }
});

elements.form.addEventListener('submit', event => {
  event.preventDefault();
  const message = elements.input.value.trim();
  if (!message) {
    showError('请输入消息后再发送。');
    return;
  }
  sendMessage(message)
    .then(() => {
      elements.input.value = '';
    })
    .catch(error => {
      setLoading(false);
      showError(error.message);
    });
});

loadState().catch(error => showError(`初始化失败：${error.message}`));
