#!/usr/bin/env python3
"""
Harper's Evidence Viewer (Lightweight Web App)
A zero-dependency local web UI to browse OCR CSV results and preview evidence files.
- Serves a local website at http://127.0.0.1:8777
- Lists CSVs from the output directory and renders them in a searchable table
- Optional image/document preview when file paths are accessible

No external Python packages required. Uses stdlib only.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
import mimetypes
import json
import csv
import os
import sys
from datetime import datetime

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
EVIDENCE_DIRS = [
    BASE_DIR / "custody_screenshots_smart_renamed",
    BASE_DIR / "custody_screenshots_organized",
    BASE_DIR / "custody_screenshots",
]
PORT = int(os.environ.get("HARPER_VIEWER_PORT", "8777"))

HTML_INDEX = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Harper's Evidence Viewer</title>
<link rel="icon" href="data:," />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/simpledotcss/simple.min.css">
<style>
body{font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif}
#app{max-width: 1400px; margin: auto}
.table-wrap{overflow:auto; max-height:65vh; border:1px solid #ddd; border-radius:6px}
.table{width:100%; border-collapse:collapse; font-size:14px}
.table th, .table td{padding:8px 10px; border-bottom:1px solid #eee; vertical-align:top}
.table th{position:sticky; top:0; background:#fafafa; z-index:1}
.controls{display:flex; gap:10px; flex-wrap:wrap}
.badge{padding:2px 8px; border-radius:12px; background:#eef; font-size:12px}
.small{font-size:12px; color:#666}
pre{white-space:pre-wrap; word-break:break-word}
.preview{max-width:380px; max-height:420px; border:1px solid #ddd; border-radius:6px}
.footer{margin-top:20px; font-size:12px; color:#666}
.code{font-family: ui-monospace, SFMono-Regular, Menlo, monospace;}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body>
<main id="app">
  <h1>Harper's Evidence Viewer</h1>
  <p class="small">Local viewer for OCR results. Data is read-only; no extra data is written.</p>

  <section>
    <div class="controls">
      <label>CSV File:
        <select id="csvSelect"></select>
      </label>
      <label>Rows:
        <select id="limitSelect">
          <option>200</option>
          <option>500</option>
          <option>1000</option>
          <option value="0">All</option>
        </select>
      </label>
      <label>Search Text:
        <input type="text" id="searchBox" placeholder="Search text_content, filename..." />
      </label>
      <label>Priority:
        <select id="priorityFilter">
          <option value="">Any</option>
          <option>HIGH</option>
          <option>MEDIUM</option>
          <option>LOW</option>
        </select>
      </label>
      <button id="refreshBtn">Refresh</button>
    </div>
  </section>

  <section class="table-wrap" id="tableWrap">
    <table class="table" id="dataTable"></table>
  </section>

  <section>
    <div class="controls">
      <button id="downloadBtn">Download CSV (filtered)</button>
      <button id="insightsBtn">Insights</button>
    </div>
  </section>

  <section id="insights" style="display:none">
    <h3>Insights</h3>
    <div id="statsSummary" class="small"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">
      <div>
        <h4>By Category</h4>
        <canvas id="catChart" height="180"></canvas>
      </div>
      <div>
        <h4>By Priority</h4>
        <canvas id="prioChart" height="180"></canvas>
      </div>
    </div>
    <div>
      <h4>Timeline (by date_extracted)</h4>
      <canvas id="timeChart" height="140"></canvas>
    </div>
  </section>

  <section>
    <h3>Preview</h3>
    <div class="controls">
      <button id="openBtn">Open in Explorer</button>
    </div>
    <div id="preview"></div>
  </section>

  <div class="footer">Serving from <span class="code">/output</span>. Evidence paths are resolved from known evidence folders.</div>
</main>
<script>
const $ = sel => document.querySelector(sel);
const dataTable = $('#dataTable');
const csvSelect = $('#csvSelect');
const limitSelect = $('#limitSelect');
const searchBox = $('#searchBox');
const priorityFilter = $('#priorityFilter');
const refreshBtn = $('#refreshBtn');
const preview = $('#preview');
const openBtn = $('#openBtn');
let lastSelectedPath = null;
const insights = $('#insights');
const insightsBtn = $('#insightsBtn');
const downloadBtn = $('#downloadBtn');

async function getJSON(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error('HTTP '+r.status);
  return await r.json();
}

async function getText(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error('HTTP '+r.status);
  return await r.text();
}

function esc(s){
  return (''+s).replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
}

function renderTable(columns, rows){
  // Build header
  let thead = '<thead><tr>' + columns.map(c=>'<th>'+esc(c)+'</th>').join('') + '</tr></thead>';
  // Build body (limit client-side as safeguard)
  let tbody = '<tbody>' + rows.map(r=>{
    return '<tr onclick="rowClick(this)" data-path="'+esc(r.file_path||'')+'">' +
      columns.map(c=>{
        let v = r[c];
        if(c==='priority' && v){
          return '<td><span class="badge">'+esc(v)+'</span></td>';
        }
        if(c==='text_content'){
          return '<td class="small"><pre>'+esc(v||'')+'</pre></td>';
        }
        return '<td>'+esc(v==null?'':v)+'</td>';
      }).join('') + '</tr>';
  }).join('') + '</tbody>';
  dataTable.innerHTML = thead + tbody;
}

async function loadCSVs(){
  const list = await getJSON('/api/list_csvs');
  csvSelect.innerHTML = list.files.map(f=>'<option>'+esc(f)+'</option>').join('');
}

async function loadData(){
  const file = csvSelect.value; if(!file) return;
  const limit = limitSelect.value;
  const q = searchBox.value.trim();
  const pr = priorityFilter.value;
  const params = new URLSearchParams({file, limit});
  if(q) params.set('q', q);
  if(pr) params.set('priority', pr);
  const res = await getJSON('/api/csv?'+params.toString());
  renderTable(res.columns, res.rows);
}

function rowClick(tr){
  const rel = tr.getAttribute('data-path');
  if(!rel){ preview.innerHTML = '<em>No file path in this row</em>'; return; }
  lastSelectedPath = rel;
  const url = '/api/file?path='+encodeURIComponent(rel);
  const ext = rel.split('.').pop().toLowerCase();
  if(['png','jpg','jpeg','gif','bmp','webp'].includes(ext)){
    preview.innerHTML = '<img class="preview" src="'+url+'"/>';
  } else if(['pdf'].includes(ext)){
    preview.innerHTML = '<iframe class="preview" style="width:100%;height:420px" src="'+url+'"></iframe>';
  } else {
    preview.innerHTML = '<a href="'+url+'" target="_blank">Open file</a>';
  }
}

refreshBtn.onclick = loadData;
openBtn.onclick = async ()=>{
  if(!lastSelectedPath){ alert('Select a row first'); return; }
  try{
    await getText('/api/open?path='+encodeURIComponent(lastSelectedPath));
  }catch(e){ alert('Failed to open: '+e.message); }
};
downloadBtn.onclick = async ()=>{
  const file = csvSelect.value; if(!file) return;
  const limit = limitSelect.value;
  const q = searchBox.value.trim();
  const pr = priorityFilter.value;
  const params = new URLSearchParams({file, limit});
  if(q) params.set('q', q);
  if(pr) params.set('priority', pr);
  window.location = '/api/export_csv?'+params.toString();
};

insightsBtn.onclick = async ()=>{
  insights.style.display = insights.style.display==='none' ? 'block':'none';
  if(insights.style.display==='block'){
    const file = csvSelect.value; if(!file) return;
    const res = await getJSON('/api/stats?file='+encodeURIComponent(file));
    $('#statsSummary').innerText = `Rows: ${res.total_rows} | Categories: ${Object.keys(res.by_category).length} | People (top): ${res.top_people.map(p=>p[0]).slice(0,5).join(', ')}`;
    drawCharts(res);
  }
};

let catChart, prioChart, timeChart;
function drawCharts(res){
  const catCtx = document.getElementById('catChart');
  const prioCtx = document.getElementById('prioChart');
  const timeCtx = document.getElementById('timeChart');
  const colors = ['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1','#ff9da7','#9c755f','#bab0ab'];

  const catLabels = Object.keys(res.by_category);
  const catData = Object.values(res.by_category);
  if(catChart) catChart.destroy();
  catChart = new Chart(catCtx, {type:'bar', data:{labels:catLabels, datasets:[{label:'Count', data:catData, backgroundColor:colors}]}, options:{plugins:{legend:{display:false}}, scales:{x:{ticks:{autoSkip:false}}}}});

  const prioLabels = Object.keys(res.by_priority);
  const prioData = Object.values(res.by_priority);
  if(prioChart) prioChart.destroy();
  prioChart = new Chart(prioCtx, {type:'bar', data:{labels:prioLabels, datasets:[{label:'Count', data:prioData, backgroundColor:colors}]}, options:{plugins:{legend:{display:false}}}});

  const tLabels = res.timeline.map(t=>t[0]);
  const tData = res.timeline.map(t=>t[1]);
  if(timeChart) timeChart.destroy();
  timeChart = new Chart(timeCtx, {type:'line', data:{labels:tLabels, datasets:[{label:'Items', data:tData, borderColor:'#4e79a7', backgroundColor:'rgba(78,121,167,0.2)'}]}, options:{plugins:{legend:{display:false}}, scales:{x:{ticks:{maxRotation:0, autoSkip:true}}}});
}

(async function init(){
  try{
    await loadCSVs();
    await loadData();
  }catch(e){
    console.error(e);
    alert('Failed to load data: '+e.message);
  }
})();
</script>
</body>
</html>
"""

class ViewerHandler(BaseHTTPRequestHandler):
    server_version = "EvidenceViewer/1.0"

    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, text, status=200, ctype='text/html; charset=utf-8'):
        data = text.encode('utf-8', errors='replace')
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)

            if path == '/':
                return self._send_text(HTML_INDEX)

            if path == '/api/list_csvs':
                files = []
                if OUTPUT_DIR.exists():
                    for p in sorted(OUTPUT_DIR.glob('*.csv')):
                        files.append(p.name)
                return self._send_json({'files': files})

            if path == '/api/csv':
                file = qs.get('file', [''])[0]
                file = unquote(file)
                limit = int(qs.get('limit', ['200'])[0] or '200')
                query = (qs.get('q', [''])[0] or '').strip().lower()
                priority = (qs.get('priority', [''])[0] or '').strip().upper()

                csv_path = OUTPUT_DIR / file
                if not csv_path.exists() or not csv_path.is_file():
                    return self._send_json({'error': 'CSV not found'}, 404)

                rows = []
                columns = []
                count = 0
                with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
                    reader = csv.DictReader(f)
                    columns = reader.fieldnames or []
                    for row in reader:
                        # Basic filtering
                        if query:
                            haystack = ' '.join([str(row.get('text_content','')), str(row.get('filename','')), str(row.get('people_mentioned',''))]).lower()
                            if query not in haystack:
                                continue
                        if priority and (row.get('priority','').upper() != priority):
                            continue
                        rows.append(row)
                        count += 1
                        if limit > 0 and len(rows) >= limit:
                            break
                return self._send_json({'columns': columns, 'rows': rows, 'returned': len(rows), 'limit': limit, 'total_scanned': count})

            if path == '/api/export_csv':
                file = qs.get('file', [''])[0]
                file = unquote(file)
                limit = int(qs.get('limit', ['200'])[0] or '200')
                query = (qs.get('q', [''])[0] or '').strip().lower()
                priority = (qs.get('priority', [''])[0] or '').strip().upper()
                csv_path = OUTPUT_DIR / file
                if not csv_path.exists():
                    return self._send_text('CSV not found', 404, 'text/plain; charset=utf-8')
                # Stream filtered rows as CSV
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="filtered_{file}"')
                self.end_headers()
                with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []
                    header_line = ','.join(headers) + '\n'
                    self.wfile.write(header_line.encode('utf-8', errors='replace'))
                    count = 0
                    for row in reader:
                        if query:
                            haystack = ' '.join([str(row.get('text_content','')), str(row.get('filename','')), str(row.get('people_mentioned',''))]).lower()
                            if query not in haystack:
                                continue
                        if priority and (row.get('priority','').upper() != priority):
                            continue
                        # Write CSV row (quote if contains comma)
                        values = []
                        for h in headers:
                            val = str(row.get(h, '') or '')
                            if ',' in val or '"' in val or '\n' in val:
                                val = '"' + val.replace('"', '""') + '"'
                            values.append(val)
                        line = ','.join(values) + '\n'
                        self.wfile.write(line.encode('utf-8', errors='replace'))
                        count += 1
                        if limit > 0 and count >= limit:
                            break
                return

            if path == '/api/stats':
                file = qs.get('file', [''])[0]
                file = unquote(file)
                csv_path = OUTPUT_DIR / file
                if not csv_path.exists():
                    return self._send_json({'error': 'CSV not found'}, 404)
                by_category = {}
                by_priority = {}
                by_date = {}
                people_counts = {}
                total_rows = 0
                with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_rows += 1
                        cat = (row.get('folder_category') or 'unknown').lower()
                        prio = (row.get('priority') or 'UNKNOWN').upper()
                        date_str = (row.get('date_extracted') or 'unknown')
                        by_category[cat] = by_category.get(cat, 0) + 1
                        by_priority[prio] = by_priority.get(prio, 0) + 1
                        # Normalize date format
                        if date_str.isdigit() and len(date_str) == 8:
                            day = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                        else:
                            day = 'unknown'
                        by_date[day] = by_date.get(day, 0) + 1
                        # People
                        ppl = (row.get('people_mentioned') or '').split(';')
                        for p in ppl:
                            p = p.strip()
                            if not p:
                                continue
                            people_counts[p] = people_counts.get(p, 0) + 1
                # Prepare timeline sorted
                timeline = sorted([(k, v) for k, v in by_date.items() if k != 'unknown'], key=lambda x: x[0])
                top_people = sorted(people_counts.items(), key=lambda x: x[1], reverse=True)[:20]
                return self._send_json({
                    'total_rows': total_rows,
                    'by_category': by_category,
                    'by_priority': by_priority,
                    'timeline': timeline,
                    'top_people': top_people,
                })
            if path == '/api/file':
                rel = qs.get('path', [''])[0]
                rel = Path(unquote(rel))
                # Normalize and ensure path is under known evidence roots
                abs_target = None
                for base in EVIDENCE_DIRS:
                    candidate = (base / rel.name) if rel.is_absolute() else (base / rel)
                    if candidate.exists():
                        abs_target = candidate.resolve()
                        break
                if abs_target is None:
                    # Try absolute path if it exists and is under workspace
                    cand = (BASE_DIR / rel) if not rel.is_absolute() else rel
                    if cand.exists():
                        abs_target = cand.resolve()

                if abs_target is None or not abs_target.exists() or not abs_target.is_file():
                    return self._send_text('Not Found', 404, 'text/plain; charset=utf-8')

                ctype, _ = mimetypes.guess_type(str(abs_target))
                try:
                    data = abs_target.read_bytes()
                except Exception:
                    return self._send_text('Failed to read file', 500, 'text/plain; charset=utf-8')
                self.send_response(200)
                self.send_header('Content-Type', ctype or 'application/octet-stream')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            if path == '/api/open':
                # Attempt to open the file in Explorer (Windows only)
                rel = qs.get('path', [''])[0]
                rel = Path(unquote(rel))
                abs_target = None
                for base in EVIDENCE_DIRS:
                    candidate = (base / rel.name) if rel.is_absolute() else (base / rel)
                    if candidate.exists():
                        abs_target = candidate.resolve()
                        break
                if abs_target is None:
                    cand = (BASE_DIR / rel) if not rel.is_absolute() else rel
                    if cand.exists():
                        abs_target = cand.resolve()
                if abs_target is None or not abs_target.exists():
                    return self._send_text('Not Found', 404, 'text/plain; charset=utf-8')
                try:
                    if os.name == 'nt':
                        os.startfile(str(abs_target))  # type: ignore[attr-defined]
                    else:
                        return self._send_text('Open not supported on this OS', 400, 'text/plain; charset=utf-8')
                except Exception as e:
                    return self._send_text('Failed to open: '+str(e), 500, 'text/plain; charset=utf-8')
                return self._send_text('OK', 200, 'text/plain; charset=utf-8')

            return self._send_text('Not Found', 404, 'text/plain; charset=utf-8')
        except Exception as e:
            self._send_text('Server Error: ' + str(e), 500, 'text/plain; charset=utf-8')


def run_server():
    addr = ('127.0.0.1', PORT)
    httpd = HTTPServer(addr, ViewerHandler)
    print(f"\nEvidence Viewer running at http://{addr[0]}:{addr[1]}\nPress Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run_server()
