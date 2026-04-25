// app.js

let currentReport = '';
let iterationCount = 0;

const TOOL_ICONS = {
  web_search:            '🔍',
  fetch_page:            '📄',
  extract_key_points:    '🔑',
  verify_claim:          '✅',
  detect_contradictions: '⚡'
};

const TOOL_LABELS = {
  web_search:            'Searching the web',
  fetch_page:            'Reading page',
  extract_key_points:    'Extracting key points',
  verify_claim:          'Verifying claim',
  detect_contradictions: 'Checking for contradictions'
};

async function startResearch() {
  const query = document.getElementById('query-input').value.trim();
  if (!query) return;

  // Reset state
  iterationCount = 0;
  currentReport = '';
  document.getElementById('feed-items').innerHTML = '';
  document.getElementById('report-panel').classList.add('hidden');
  document.getElementById('report-content').innerHTML = '';

  // Show feed, disable input
  document.getElementById('feed-panel').classList.remove('hidden');
  document.getElementById('research-btn').disabled = true;
  document.getElementById('research-btn').textContent = 'Researching...';

  try {
    // Start research session
    const res = await fetch('/research', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query})
    });
    const {session_id} = await res.json();

    // Open SSE stream
    const eventSource = new EventSource(`/stream/${session_id}`);

    eventSource.addEventListener('thinking', (e) => {
      const data = JSON.parse(e.data);
      addFeedItem('thinking', null, data.message);
    });

    eventSource.addEventListener('tool_call', (e) => {
      const data = JSON.parse(e.data);
      iterationCount = data.iteration || iterationCount + 1;
      document.getElementById('iteration-count').textContent =
        `Step ${iterationCount}`;
      addToolCallItem(data.tool, data.args);
    });

    eventSource.addEventListener('tool_result', (e) => {
      const data = JSON.parse(e.data);
      updateLastToolResult(data.tool, data.result);
    });

    eventSource.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data);
      currentReport = data.report;
      renderReport(data.report);
      eventSource.close();
      document.getElementById('research-btn').disabled = false;
      document.getElementById('research-btn').textContent = 'Research ▶';
      addFeedItem('done', null,
        `✅ Complete in ${data.iterations} steps`);
    });

    eventSource.addEventListener('error', (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'error') {
        addFeedItem('error', null, `❌ ${data.message}`);
        eventSource.close();
        document.getElementById('research-btn').disabled = false;
        document.getElementById('research-btn').textContent = 'Research ▶';
      }
    });

  } catch (err) {
    addFeedItem('error', null, `Failed to start: ${err.message}`);
    document.getElementById('research-btn').disabled = false;
    document.getElementById('research-btn').textContent = 'Research ▶';
  }
}

function addToolCallItem(toolName, args) {
  const feed = document.getElementById('feed-items');
  const icon = TOOL_ICONS[toolName] || '🔧';
  const label = TOOL_LABELS[toolName] || toolName;

  // Build human-readable arg summary
  let argSummary = '';
  if (args.query)   argSummary = `"${args.query}"`;
  if (args.url)     argSummary = shortenUrl(args.url);
  if (args.claim)   argSummary = `"${args.claim.slice(0, 60)}..."`;
  if (args.topic)   argSummary = `"${args.topic}"`;

  const item = document.createElement('div');
  item.className = 'feed-item tool-call';
  item.id = `tool-${Date.now()}`;
  item.innerHTML = `
    <div class="feed-item-header">
      <span class="tool-icon">${icon}</span>
      <span class="tool-label">${label}</span>
      <span class="tool-arg">${argSummary}</span>
      <span class="feed-spinner">⟳</span>
    </div>
    <div class="tool-result-preview" id="result-${item.id}"></div>
  `;
  feed.appendChild(item);
  feed.scrollTop = feed.scrollHeight;
  return item.id;
}

function updateLastToolResult(toolName, result) {
  // Find the last unresolved tool call item for this tool
  const items = document.querySelectorAll('.feed-item.tool-call');
  const last = Array.from(items).reverse().find(el =>
    el.querySelector('.tool-label')?.textContent === TOOL_LABELS[toolName]
  );
  if (!last) return;

  last.querySelector('.feed-spinner').textContent = '✓';
  last.classList.add('resolved');

  const preview = last.querySelector('.tool-result-preview');
  if (!preview) return;

  // Render a compact preview based on tool type
  if (toolName === 'web_search' && result.results) {
    preview.innerHTML = result.results.slice(0, 3).map(r =>
      `<div class="result-link">↳ ${r.title || r.url}</div>`
    ).join('');
  } else if (toolName === 'fetch_page' && result.char_count) {
    preview.innerHTML = `↳ Read ${result.char_count.toLocaleString()} characters`;
  } else if (toolName === 'extract_key_points' && result.points) {
    preview.innerHTML = `↳ Extracted ${result.points.length} key points`;
  } else if (toolName === 'verify_claim' && result.verdict) {
    const emoji = result.verdict === 'supported' ? '✅' :
                  result.verdict === 'refuted'   ? '❌' : '⚠️';
    preview.innerHTML = `↳ ${emoji} ${result.verdict}
      (confidence: ${Math.round((result.confidence || 0) * 100)}%)`;
  } else if (toolName === 'detect_contradictions' && result.contradictions) {
    const n = result.contradictions.length;
    preview.innerHTML = `↳ ${n === 0 ? 'No contradictions found' :
      `${n} contradiction${n > 1 ? 's' : ''} detected`}`;
  }
}

function addFeedItem(type, tool, message) {
  const feed = document.getElementById('feed-items');
  const item = document.createElement('div');
  item.className = `feed-item ${type}`;
  item.innerHTML = `<span class="feed-message">${message}</span>`;
  feed.appendChild(item);
  feed.scrollTop = feed.scrollHeight;
}

function renderReport(markdown) {
  document.getElementById('report-panel').classList.remove('hidden');
  // Simple markdown → HTML (for demo; swap in marked.js for full support)
  const html = markdown
    .replace(/^# (.+)$/gm,   '<h1>$1</h1>')
    .replace(/^## (.+)$/gm,  '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,   '<em>$1</em>')
    .replace(/^- (.+)$/gm,   '<li>$1</li>')
    .replace(/\n/g, '<br>');
  document.getElementById('report-content').innerHTML = html;
  document.getElementById('report-panel').scrollIntoView({behavior: 'smooth'});
}

function copyReport() {
  navigator.clipboard.writeText(currentReport);
}

function resetApp() {
  document.getElementById('feed-panel').classList.add('hidden');
  document.getElementById('report-panel').classList.add('hidden');
  document.getElementById('feed-items').innerHTML = '';
  document.getElementById('query-input').value = '';
}

function shortenUrl(url) {
  try { return new URL(url).hostname; }
  catch { return url.slice(0, 40); }
}

// Allow Enter+Shift to submit
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('query-input')
    ?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        startResearch();
      }
    });
});
