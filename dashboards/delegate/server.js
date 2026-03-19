const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3847;
const LOG_FILE = path.join(__dirname, '..', '..', 'logs', 'delegations.md');
const INDEX_FILE = path.join(__dirname, 'index.html');
const BRAND_DIR = path.join(__dirname, '..', '..', 'brand-assets');

const HEADER = `# Delegation Log

Track of all delegated tasks.

---\n`;

function ensureLogFile() {
  const dir = path.dirname(LOG_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(LOG_FILE)) fs.writeFileSync(LOG_FILE, HEADER, 'utf8');
}

function parseTasks(md) {
  const tasks = [];
  const blocks = md.split(/^### /m).filter(b => b.trim());
  for (const block of blocks) {
    const lines = block.trim().split('\n');
    const headerMatch = lines[0].match(/^\[(\d{4}-\d{2}-\d{2})\]\s+(.+)/);
    if (!headerMatch) continue;
    const task = { date: headerMatch[1], title: headerMatch[2].trim(), assignee: '', deadline: '', status: '', notes: '' };
    for (let i = 1; i < lines.length; i++) {
      const m = lines[i].trim().match(/^-\s+\*\*(.+?):\*\*\s*(.+)/);
      if (!m) continue;
      const key = m[1].toLowerCase().trim();
      const val = m[2].trim();
      if (key === 'assigned to') task.assignee = val;
      else if (key === 'deadline') task.deadline = val;
      else if (key === 'status') task.status = val;
      else if (key === 'notes') task.notes = val;
    }
    tasks.push(task);
  }
  return tasks;
}

function tasksToMarkdown(tasks) {
  let md = HEADER;
  for (const t of tasks) {
    md += `\n### [${t.date}] ${t.title}\n`;
    md += `- **Assigned to:** ${t.assignee}\n`;
    md += `- **Deadline:** ${t.deadline || 'None specified'}\n`;
    md += `- **Status:** ${t.status || 'Delegated'}\n`;
    md += `- **Notes:** ${t.notes || ''}\n`;
  }
  return md;
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', c => data += c);
    req.on('end', () => { try { resolve(JSON.parse(data)); } catch(e) { reject(e); } });
    req.on('error', reject);
  });
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function json(res, code, data) {
  cors(res);
  res.writeHead(code, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

const server = http.createServer(async (req, res) => {
  cors(res);

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  // API routes
  if (req.url === '/api/tasks' && req.method === 'GET') {
    ensureLogFile();
    const md = fs.readFileSync(LOG_FILE, 'utf8');
    return json(res, 200, parseTasks(md));
  }

  if (req.url === '/api/tasks' && req.method === 'POST') {
    try {
      const body = await readBody(req);
      if (!body.title || !body.assignee) return json(res, 400, { error: 'title and assignee are required' });
      ensureLogFile();
      const md = fs.readFileSync(LOG_FILE, 'utf8');
      const tasks = parseTasks(md);
      tasks.unshift({
        date: body.date || new Date().toISOString().slice(0, 10),
        title: body.title,
        assignee: body.assignee,
        deadline: body.deadline || 'None specified',
        status: body.status || 'Delegated',
        notes: body.notes || ''
      });
      fs.writeFileSync(LOG_FILE, tasksToMarkdown(tasks), 'utf8');
      return json(res, 201, { ok: true, count: tasks.length });
    } catch(e) { return json(res, 400, { error: e.message }); }
  }

  if (req.url.startsWith('/api/tasks/') && req.method === 'PATCH') {
    const idx = parseInt(req.url.split('/').pop(), 10);
    ensureLogFile();
    const md = fs.readFileSync(LOG_FILE, 'utf8');
    const tasks = parseTasks(md);
    if (isNaN(idx) || idx < 0 || idx >= tasks.length) return json(res, 404, { error: 'task not found' });
    try {
      const body = await readBody(req);
      if (body.status) tasks[idx].status = body.status;
      fs.writeFileSync(LOG_FILE, tasksToMarkdown(tasks), 'utf8');
      return json(res, 200, { ok: true, task: tasks[idx] });
    } catch(e) { return json(res, 400, { error: e.message }); }
  }

  if (req.url.startsWith('/api/tasks/') && req.method === 'DELETE') {
    const idx = parseInt(req.url.split('/').pop(), 10);
    ensureLogFile();
    const md = fs.readFileSync(LOG_FILE, 'utf8');
    const tasks = parseTasks(md);
    if (isNaN(idx) || idx < 0 || idx >= tasks.length) return json(res, 404, { error: 'task not found' });
    tasks.splice(idx, 1);
    fs.writeFileSync(LOG_FILE, tasksToMarkdown(tasks), 'utf8');
    return json(res, 200, { ok: true, count: tasks.length });
  }

  // Brand assets
  if (req.url.startsWith('/brand-assets/')) {
    const assetPath = path.join(BRAND_DIR, decodeURIComponent(req.url.replace('/brand-assets/', '')));
    const ext = path.extname(assetPath);
    const mimeTypes = {
      '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon', '.svg': 'image/svg+xml',
      '.otf': 'font/otf', '.ttf': 'font/ttf', '.woff': 'font/woff', '.woff2': 'font/woff2'
    };
    if (fs.existsSync(assetPath)) {
      res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
      fs.createReadStream(assetPath).pipe(res);
    } else {
      res.writeHead(404); res.end('Not found');
    }
    return;
  }

  // Static files
  let filePath = req.url === '/' ? INDEX_FILE : path.join(__dirname, req.url);
  const ext = path.extname(filePath);
  const mimeTypes = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css' };

  if (fs.existsSync(filePath)) {
    res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
    fs.createReadStream(filePath).pipe(res);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`Delegation Board running at http://localhost:${PORT}`);
});
