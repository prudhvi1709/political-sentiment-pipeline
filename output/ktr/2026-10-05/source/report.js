(() => {
  'use strict';
  const controller = new AbortController();
  const options = { signal: controller.signal };
  const controls = { scope: document.getElementById('scope'), stance: document.getElementById('stance-filter'), topic: document.getElementById('topic-filter'), search: document.getElementById('search'), order: document.getElementById('order') };
  const theme = document.getElementById('theme');
  const evidenceList = document.getElementById('evidence-list');
  const elements = new Map([...document.querySelectorAll('[data-row]')].map(element => [Number(element.dataset.row), element]));
  const rowsById = new Map(reportRows.map(row => [row.id, row]));
  const dialog = document.getElementById('post-dialog');
  const dialogContent = document.getElementById('dialog-content');
  const allowed = { scope: ['recent', 'all', 'historical', 'excluded'], stance: ['all', 'supportive', 'critical', 'neutral', 'mixed', 'unclear', 'unrelated'], topic: ['all', ...new Set(reportRows.map(row => row.topic))], order: ['date', 'views', 'interactions'] };
  let searchTimer;
  let currentPage = 1;
  const pageSize = 20;
  function params() { const index = location.hash.indexOf('?'); return new URLSearchParams(index >= 0 ? location.hash.slice(index + 1) : ''); }
  function save() {
    const values = new URLSearchParams();
    for (const [key, control] of Object.entries(controls)) { if (control.value !== (key === 'scope' ? 'recent' : key === 'order' ? 'date' : key === 'search' ? '' : 'all')) values.set(key, control.value); }
    if (document.documentElement.dataset.theme === 'dark') values.set('theme', 'dark');
    if (currentPage > 1) values.set('page', String(currentPage));
    const base = location.hash.split('?')[0] || '#overview';
    const next = `${base}${values.size ? `?${values}` : ''}`;
    history.replaceState(null, '', next);
  }
  function setTheme(isDark) { document.documentElement.dataset.theme = isDark ? 'dark' : 'light'; theme.textContent = isDark ? 'Light theme' : 'Dark theme'; theme.setAttribute('aria-pressed', String(isDark)); }
  function matches(row) {
    const scope = controls.scope.value;
    if (scope === 'recent' && (row.day < '2026-09-01' || row.stance === 'unrelated')) return false;
    if (scope === 'historical' && row.day >= '2026-09-01') return false;
    if (scope === 'excluded' && row.stance !== 'unrelated') return false;
    if (controls.stance.value !== 'all' && row.stance !== controls.stance.value) return false;
    if (controls.topic.value !== 'all' && row.topic !== controls.topic.value) return false;
    const query = controls.search.value.trim().toLowerCase();
    return !query || `${row.summary} ${row.reason} ${row.handle ?? ''} ${row.topic}`.toLowerCase().includes(query);
  }
  function render() {
    const order = controls.order.value;
    const sorted = [...reportRows].sort((a, b) => order === 'date' ? b.date.localeCompare(a.date) : b[order] - a[order] || b.date.localeCompare(a.date));
    const matching = sorted.filter(matches);
    const count = matching.length;
    const pages = Math.max(1, Math.ceil(count / pageSize));
    currentPage = Math.min(Math.max(1, currentPage), pages);
    const visibleIds = new Set(matching.slice((currentPage - 1) * pageSize, currentPage * pageSize).map(row => row.id));
    const fragment = document.createDocumentFragment();
    for (const row of sorted) { const element = elements.get(row.id); element.hidden = !visibleIds.has(row.id); fragment.append(element); }
    evidenceList.append(fragment);
    document.getElementById('results').textContent = `${count} of ${reportRows.length} supplied posts match. Charts retain the fixed recent scope.`;
    document.getElementById('empty').hidden = count !== 0;
    document.getElementById('pagination').hidden = count === 0;
    document.getElementById('previous-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage === pages;
    document.getElementById('page-status').textContent = `Page ${currentPage} of ${pages}`;
  }
  function restore() {
    const values = params();
    for (const [key, control] of Object.entries(controls)) { const value = values.get(key); control.value = key === 'search' ? (value ?? '').slice(0, 200) : allowed[key].includes(value) ? value : key === 'scope' ? 'recent' : key === 'order' ? 'date' : 'all'; }
    const page = Number(values.get('page') ?? '1'); currentPage = Number.isInteger(page) && page > 0 ? page : 1;
    setTheme(values.get('theme') === 'dark'); render();
    if (location.hash.includes('?')) document.getElementById(location.hash.slice(1).split('?')[0])?.scrollIntoView({ behavior: 'instant' });
  }
  function paragraph(content, className = '') { const p = document.createElement('p'); p.textContent = content; p.className = className; return p; }
  function inspect(id) {
    const row = rowsById.get(id); if (!row) return;
    dialogContent.replaceChildren();
    const heading = document.createElement('h3'); heading.textContent = row.summary;
    dialogContent.append(paragraph(`Post ${row.id + 1} / ${row.day} / @${row.handle ?? '[missing]'}`, 'small'), heading, paragraph(`Stance: ${row.stance}. Tone: ${row.tone}. Topic: ${row.topic}.`), paragraph(row.reason), paragraph(`Context: ${row.clarity.replaceAll('_', ' ')}. Format: ${row.format.replaceAll('_', ' ')}.`, 'small'));
    const metrics = document.createElement('div'); metrics.className = 'dialog-metrics';
    for (const key of ['views', 'likes', 'reposts', 'replies', 'bookmarks', 'interactions']) metrics.append(paragraph(`${key}: ${new Intl.NumberFormat('en-IN').format(row[key])}`));
    const link = document.createElement('a'); link.href = row.link; link.textContent = 'Open original post on X'; link.target = '_blank'; link.rel = 'noopener noreferrer';
    dialogContent.append(metrics, link, paragraph('AI-assisted interpretation of supplied text. Media was not available for classification.', 'small'));
    dialog.showModal();
  }
  theme.addEventListener('click', () => { setTheme(document.documentElement.dataset.theme !== 'dark'); save(); }, options);
  document.getElementById('print').addEventListener('click', () => { const previous = document.documentElement.dataset.theme; setTheme(false); window.print(); setTheme(previous === 'dark'); }, options);
  for (const [key, control] of Object.entries(controls)) {
    control.addEventListener(key === 'search' ? 'input' : 'change', () => { currentPage = 1; if (key === 'search') { clearTimeout(searchTimer); searchTimer = setTimeout(() => { render(); save(); }, 200); } else { render(); save(); } }, options);
  }
  document.getElementById('reset').addEventListener('click', () => { currentPage = 1; for (const [key, control] of Object.entries(controls)) control.value = key === 'scope' ? 'recent' : key === 'order' ? 'date' : key === 'search' ? '' : 'all'; render(); save(); }, options);
  document.getElementById('previous-page').addEventListener('click', () => { currentPage -= 1; render(); save(); document.getElementById('evidence').scrollIntoView(); }, options);
  document.getElementById('next-page').addEventListener('click', () => { currentPage += 1; render(); save(); document.getElementById('evidence').scrollIntoView(); }, options);
  document.getElementById('close-dialog').addEventListener('click', () => dialog.close(), options);
  document.addEventListener('click', event => { const mark = event.target.closest('[data-id]'); if (mark) { event.preventDefault(); inspect(Number(mark.dataset.id)); return; } const link = event.target.closest('nav a, .primary-link, .secondary-link, .wordmark, .skip'); if (link) { event.preventDefault(); const destination = link.getAttribute('href'); const active = params(); history.replaceState(null, '', `${destination}${active.size ? `?${active}` : ''}`); document.querySelector(destination)?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' }); } }, options);
  window.addEventListener('hashchange', restore, options);
  window.addEventListener('pagehide', event => { if (!event.persisted) { clearTimeout(searchTimer); controller.abort(); } }, options);
  const mobileTimeline = matchMedia('(max-width: 850px)');
  function alignTimeline() {
    if (mobileTimeline.matches) {
      for (const chart of document.querySelectorAll('.chart-scroll .chart-frame')) chart.scrollLeft = chart.scrollWidth - chart.clientWidth;
    }
  }
  mobileTimeline.addEventListener('change', alignTimeline, options);
  restore();
  alignTimeline();
})();
