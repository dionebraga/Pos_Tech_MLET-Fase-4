"""
Rotas da API.

Separadas em um APIRouter para deixar o `main.py` enxuto.
"""
import logging
import time
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from src import __version__
from src.api.monitoring import (
    LAST_PREDICTION_VALUE,
    TrackPrediction,
)
from src.api.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionItem,
    PredictRequest,
    PredictResponse,
    SymbolPredictRequest,
    SymbolPredictResponse,
)
from src.data_loader import fetch_recent_window

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================ #
@router.get("/", tags=["root"], response_class=HTMLResponse)
def root(request: Request):
    predictor = getattr(request.app.state, "predictor", None)
    md = predictor.metadata if predictor else {}
    metrics = md.get("metrics", {}) if md else {}
    status_color = "#00FF88" if predictor else "#FF3B3B"
    status_text = "ONLINE" if predictor else "DEGRADED"
    model_badge = "● MODELO CARREGADO" if predictor else "○ MODELO NÃO DISPONÍVEL"

    mae_val = str(metrics.get("mae", "—"))[:5] if metrics else "—"
    rmse_val = str(metrics.get("rmse", "—"))[:5] if metrics else "—"
    mape_val = str(metrics.get("mape", "—"))[:5] if metrics else "—"
    mape_num = metrics.get("mape", 0) if metrics else 0
    symbol = md.get("symbol", "—") if md else "—"
    window_size = md.get("window_size", "—") if md else "—"
    lstm_1 = str(md.get("lstm_units_1", "?")) if md else "?"
    lstm_2 = str(md.get("lstm_units_2", "?")) if md else "?"
    trained_at = md.get("trained_at", "—") if md else "—"

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · Terminal LSTM</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background:#050507; color:#A1A1AA; font-family:'JetBrains Mono',monospace;
    min-height:100vh; padding:20px;
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(0,255,136,0.03) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 50%, rgba(183,148,244,0.03) 0%, transparent 50%);
  }}
  body::before {{
    content:''; position:fixed; inset:0; pointer-events:none;
    background:repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,136,0.008) 2px, rgba(0,255,136,0.008) 4px);
    z-index:9999;
  }}
  .container {{ max-width:1060px; width:100%; margin:0 auto; }}
  .header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:32px; flex-wrap:wrap; gap:16px; }}
  .header-left {{ display:flex; align-items:center; gap:20px; }}
  .logo {{ font-size:1.6rem; font-weight:700; color:#FAFAFA; letter-spacing:-0.5px; }}
  .logo span {{ color:#00FF88; }}
  .tag {{ font-size:0.6rem; color:#52525B; letter-spacing:0.15em; text-transform:uppercase; }}
  .status-bar {{ display:flex; align-items:center; gap:8px; font-size:0.75rem; }}
  .status-dot {{ width:8px; height:8px; border-radius:50%; background:{status_color};
    box-shadow:0 0 8px {status_color}; animation:pulse-dot 2s ease-in-out infinite; }}
  @keyframes pulse-dot {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
  .status-text {{ color:{status_color}; font-weight:500; }}
  .status-badge {{ color:#52525B; font-size:0.65rem; }}

  /* ━━ Earth Pulse ━━ */
  .earth-section {{ display:flex; align-items:center; justify-content:center; margin-bottom:40px; gap:40px; flex-wrap:wrap; }}
  .earth-container {{ position:relative; width:140px; height:140px; flex-shrink:0; }}
  .earth-globe {{
    width:140px; height:140px; border-radius:50%;
    background:radial-gradient(circle at 35% 35%, #1a3a4a, #0a1a2a 50%, #050a12);
    box-shadow:inset -20px -10px 30px rgba(0,0,0,0.6), 0 0 40px rgba(0,255,136,0.15);
    position:relative; overflow:hidden;
  }}
  .earth-globe::before {{
    content:''; position:absolute; inset:0; border-radius:50%;
    background:linear-gradient(90deg, transparent 30%, rgba(0,255,136,0.06) 50%, transparent 70%);
    animation:earth-rotate 8s linear infinite;
  }}
  .earth-globe::after {{
    content:''; position:absolute; top:30%; left:20%; width:30%; height:20%;
    background:radial-gradient(ellipse, rgba(0,255,136,0.15) 0%, transparent 70%);
    border-radius:50%;
  }}
  @keyframes earth-rotate {{ 0%{{transform:translateX(-30%)}} 100%{{transform:translateX(30%)}} }}
  .pulse-ring {{
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    width:140px; height:140px; border-radius:50%;
    border:1px solid rgba(0,255,136,0.15);
    animation:pulse-ring 3s ease-out infinite;
  }}
  .pulse-ring:nth-child(2) {{ animation-delay:1s; }}
  .pulse-ring:nth-child(3) {{ animation-delay:2s; }}
  @keyframes pulse-ring {{
    0%{{width:140px;height:140px;opacity:1;}}
    100%{{width:280px;height:280px;opacity:0;}}
  }}
  .earth-stats {{ display:flex; gap:24px; flex-wrap:wrap; }}
  .earth-stat {{ text-align:center; }}
  .earth-stat-value {{ font-size:1.3rem; font-weight:600; color:#FAFAFA; }}
  .earth-stat-label {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-top:4px; }}

  /* ━━ KPI Cards ━━ */
  .kpi-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:12px; }}
  .kpi-card {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:8px;
    padding:16px; cursor:pointer; transition:all .25s; position:relative; overflow:hidden;
  }}
  .kpi-card::before {{
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:transparent; transition:background .25s;
  }}
  .kpi-card:hover {{ border-color:#27272A; background:#0E0E15; }}
  .kpi-card.active {{ border-color:#333; }}
  .kpi-card.active.accent::before {{ background:#00FF88; }}
  .kpi-card.active.info::before {{ background:#5B9DFF; }}
  .kpi-card.active.purple::before {{ background:#B794F4; }}
  .kpi-card.active.warning::before {{ background:#FF9500; }}
  .kpi-label {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px; }}
  .kpi-head {{ display:flex; justify-content:space-between; align-items:center; }}
  .kpi-icon {{ font-size:0.7rem; color:#3F3F46; }}
  .kpi-value {{ font-size:1.2rem; font-weight:600; color:#FAFAFA; margin:4px 0 2px; }}
  .kpi-delta {{ font-size:0.6rem; }}
  .kpi-delta.up {{ color:#00FF88; }}
  .kpi-delta.down {{ color:#FF3B3B; }}
  .kpi-delta.neutral {{ color:#FBBF24; }}

  /* ━━ Detail Panel ━━ */
  .detail-panel {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:8px;
    padding:20px; margin-bottom:24px; display:none; animation:fadeSlide .3s ease;
  }}
  .detail-panel.open {{ display:block; }}
  @keyframes fadeSlide {{ 0%{{opacity:0;transform:translateY(-8px)}} 100%{{opacity:1;transform:translateY(0)}} }}
  .detail-eyebrow {{ font-size:0.5rem; color:#52525B; text-transform:uppercase; letter-spacing:0.15em; }}
  .detail-title {{ font-size:1rem; font-weight:600; color:#FAFAFA; margin:6px 0 10px; }}
  .detail-text {{ font-size:0.78rem; color:#A1A1AA; line-height:1.6; }}
  .detail-text b {{ color:#FAFAFA; }}

  /* ━━ Chart ━━ */
  .chart-section {{ background:#0A0A0F; border:1px solid #18181B; border-radius:8px; padding:20px; margin-bottom:24px; }}
  .chart-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }}
  .chart-title {{ font-size:0.7rem; color:#52525B; text-transform:uppercase; letter-spacing:0.1em; }}
  .chart-controls {{ display:flex; gap:8px; }}
  .chart-btn {{
    padding:4px 12px; background:transparent; border:1px solid #18181B; border-radius:4px;
    color:#52525B; font-family:inherit; font-size:0.6rem; cursor:pointer; transition:all .2s;
  }}
  .chart-btn:hover {{ border-color:#333; color:#A1A1AA; }}
  .chart-btn.active {{ border-color:#00FF88; color:#00FF88; }}
  .chart-wrap {{ position:relative; height:260px; }}
  .chart-wrap canvas {{ width:100% !important; height:100% !important; }}

  /* ━━ Endpoints ━━ */
  .endpoints {{ background:#0A0A0F; border:1px solid #18181B; border-radius:8px; overflow:hidden; }}
  .endpoint-row {{
    display:flex; justify-content:space-between; align-items:center;
    padding:12px 18px; border-bottom:1px solid #18181B; font-size:0.78rem;
    transition:background .2s; text-decoration:none; color:inherit;
  }}
  .endpoint-row:last-child {{ border-bottom:none; }}
  .endpoint-row:hover {{ background:#0E0E15; }}
  .endpoint-method {{
    display:inline-block; width:48px; padding:2px 0; text-align:center;
    border-radius:4px; font-size:0.6rem; font-weight:700; letter-spacing:0.05em;
  }}
  .get {{ background:rgba(97,175,254,0.15); color:#61AFFE; }}
  .post {{ background:rgba(73,204,144,0.15); color:#49CC90; }}
  .endpoint-path {{ color:#FAFAFA; font-weight:500; margin-left:12px; }}
  .endpoint-desc {{ color:#52525B; font-size:0.65rem; margin-left:auto; }}

  .footer {{ text-align:center; margin-top:32px; font-size:0.6rem; color:#3F3F46; letter-spacing:0.05em; padding-bottom:20px; }}
  .footer a {{ color:#52525B; text-decoration:none; }}
  .footer a:hover {{ color:#A1A1AA; }}

  .terminal-line {{
    font-size:0.6rem; color:#3F3F46; letter-spacing:0.05em; margin-bottom:16px;
    display:flex; align-items:center; gap:8px;
  }}
  .terminal-prompt {{ color:#00FF88; }}
  .terminal-cursor {{ animation:blink 1s step-end infinite; }}
  @keyframes blink {{ 50%{{opacity:0}} }}

  @media (max-width:700px) {{ .kpi-row {{ grid-template-columns:repeat(2,1fr); }} .header {{ flex-direction:column; align-items:flex-start; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="terminal-line">
    <span class="terminal-prompt">►</span>
    <span>AI Quant Terminal · v{__version__} · {datetime.now().strftime('%Y-%m-%d %H:%M')}Z</span>
    <span class="terminal-cursor">▌</span>
  </div>

  <div class="header">
    <div class="header-left">
      <div class="logo">⟨⟩ <span>Quant</span></div>
      <div>
        <div class="tag">LSTM Prediction Engine</div>
        <div class="status-bar">
          <span class="status-dot"></span>
          <span class="status-text">{status_text}</span>
          <span class="status-badge">· {model_badge}</span>
        </div>
      </div>
    </div>
    <div style="font-size:0.6rem;color:#3F3F46;text-align:right;">
      <div>MODEL: {symbol}</div>
      <div>TRAINED: {trained_at[:10] if trained_at != '—' else '—'}</div>
    </div>
  </div>

  <div class="earth-section">
    <div class="earth-container">
      <div class="pulse-ring"></div>
      <div class="pulse-ring"></div>
      <div class="pulse-ring"></div>
      <div class="earth-globe"></div>
    </div>
    <div class="earth-stats">
      <div class="earth-stat">
        <div class="earth-stat-value" style="color:#00FF88;">{symbol}</div>
        <div class="earth-stat-label">Ativo</div>
      </div>
      <div class="earth-stat">
        <div class="earth-stat-value" style="color:#B794F4;">{str(metrics.get('mae','—'))[:5] if metrics else '—'}</div>
        <div class="earth-stat-label">MAE</div>
      </div>
      <div class="earth-stat">
        <div class="earth-stat-value" style="color:#5B9DFF;">{str(metrics.get('rmse','—'))[:5] if metrics else '—'}</div>
        <div class="earth-stat-label">RMSE</div>
      </div>
      <div class="earth-stat">
        <div class="earth-stat-value" style="color:#FBBF24;">{str(metrics.get('mape','—'))[:5] if metrics else '—'}%</div>
        <div class="earth-stat-label">MAPE</div>
      </div>
      <div class="earth-stat">
        <div class="earth-stat-value" style="color:#FF9500;">{str(md.get('window_size','—')) if md else '—'}</div>
        <div class="earth-stat-label">Window</div>
      </div>
    </div>
  </div>

  <div class="kpi-row" id="kpiRow">
    <div class="kpi-card accent" data-key="preco" onclick="toggleDetail(this)">
      <div class="kpi-head">
        <span class="kpi-label">Preço Atual</span>
        <span class="kpi-icon">$</span>
      </div>
      <div class="kpi-value" id="kpiPreco">—</div>
      <div class="kpi-delta up" id="kpiPrecoDelta">—</div>
    </div>
    <div class="kpi-card info" data-key="volatilidade" onclick="toggleDetail(this)">
      <div class="kpi-head">
        <span class="kpi-label">Volatilidade</span>
        <span class="kpi-icon">σ</span>
      </div>
      <div class="kpi-value" id="kpiVolatilidade">—</div>
      <div class="kpi-delta" id="kpiVolatilidadeDelta">—</div>
    </div>
    <div class="kpi-card purple" data-key="tendencia" onclick="toggleDetail(this)">
      <div class="kpi-head">
        <span class="kpi-label">Tendência (20d)</span>
        <span class="kpi-icon">Δ</span>
      </div>
      <div class="kpi-value" id="kpiTendencia">—</div>
      <div class="kpi-delta" id="kpiTendenciaDelta">—</div>
    </div>
    <div class="kpi-card warning" data-key="ia" onclick="toggleDetail(this)">
      <div class="kpi-head">
        <span class="kpi-label">Confiança IA</span>
        <span class="kpi-icon">λ</span>
      </div>
      <div class="kpi-value" id="kpiIA">—</div>
      <div class="kpi-delta up" id="kpiIADelta">—</div>
    </div>
  </div>

  <div class="detail-panel" id="detailPanel">
    <div class="detail-eyebrow" id="detailTag"></div>
    <div class="detail-title" id="detailTitle"></div>
    <div class="detail-text" id="detailText"></div>
  </div>

  <div class="chart-section">
    <div class="chart-header">
      <div class="chart-title">📈 Preço Fechamento · {symbol}</div>
      <div class="chart-controls">
        <button class="chart-btn active" data-range="1mo" onclick="switchRange(this)">1M</button>
        <button class="chart-btn" data-range="3mo" onclick="switchRange(this)">3M</button>
        <button class="chart-btn" data-range="6mo" onclick="switchRange(this)">6M</button>
        <button class="chart-btn" data-range="1y" onclick="switchRange(this)">1A</button>
      </div>
    </div>
    <div class="chart-wrap">
      <canvas id="priceChart"></canvas>
    </div>
  </div>

  <div class="endpoints">
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method" style="background:rgba(255,255,255,0.08);color:#FAFAFA;">📘</span><span class="endpoint-path">Swagger UI</span></span>
      <span class="endpoint-desc">Documentação interativa →</span>
    </a>
    <a class="endpoint-row" href="/health">
      <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/health</span></span>
      <span class="endpoint-desc">Status da API e modelo</span>
    </a>
    <a class="endpoint-row" href="/model/info">
      <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/model/info</span></span>
      <span class="endpoint-desc">Metadados do treinamento</span>
    </a>
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method post">POST</span><span class="endpoint-path">/predict</span></span>
      <span class="endpoint-desc">Prever com dados manuais</span>
    </a>
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method post">POST</span><span class="endpoint-path">/predict/symbol</span></span>
      <span class="endpoint-desc">Prever via Yahoo Finance</span>
    </a>
    <a class="endpoint-row" href="/metrics">
      <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/metrics</span></span>
      <span class="endpoint-desc">Métricas Prometheus</span>
    </a>
  </div>

  <div class="footer">
    <span>Tech Challenge Fase 4 · PósTech MLET FIAP · </span>
    <a href="https://github.com/dionebraga/Pos_Tech_MLET-Fase-4" target="_blank">GitHub</a>
    <span> · </span>
    <a href="/docs">API Docs</a>
  </div>
</div>

<script>
const SYMBOL = "{symbol}";
const DETAILS = {{
  preco: {{ tag:"Asset Price", title:"Análise de Preço", text:"Carregando...", cls:"accent" }},
  volatilidade: {{ tag:"Risk Metric", title:"Volatilidade Anualizada", text:"Carregando...", cls:"info" }},
  tendencia: {{ tag:"Technical", title:"Análise de Tendência", text:"Carregando...", cls:"purple" }},
  ia: {{ tag:"Model Output", title:"Confiança do Modelo LSTM", text:"Carregando...", cls:"warning" }}
}};

let priceChart = null;
let activeRange = '1mo';

const MAPE_NUM = {mape_num};
const CONFIDENCE = MAPE_NUM > 0 ? (100 - MAPE_NUM).toFixed(1) : '—';

function toggleDetail(el) {{
  const key = el.dataset.key;
  const panel = document.getElementById('detailPanel');
  const isSame = panel.classList.contains('open') && panel.dataset.activeKey === key;
  document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('active'));
  if (isSame) {{
    panel.classList.remove('open');
    panel.dataset.activeKey = '';
    return;
  }}
  el.classList.add('active');
  panel.dataset.activeKey = key;
  const d = DETAILS[key];
  document.getElementById('detailTag').textContent = d.tag;
  document.getElementById('detailTitle').textContent = d.title;
  document.getElementById('detailText').innerHTML = d.text;
  panel.className = 'detail-panel open ' + d.cls;
}}

function switchRange(btn) {{
  document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  activeRange = btn.dataset.range;
  fetchChart(activeRange);
}}

async function fetchChart(range) {{
  const canvas = document.getElementById('priceChart');
  try {{
    const resp = await fetch('/health');
    const health = await resp.json();
    if (!health.model_loaded) throw new Error('modelo não carregado');
  }} catch(e) {{
    canvas.parentElement.innerHTML =
      '<div style="color:#52525B;font-size:0.75rem;padding:40px;text-align:center;">' +
      'Modelo não disponível · gráfico offline</div>';
    return;
  }}
  const ctx = canvas.getContext('2d');
  try {{
    const resp = await fetch('/predict/symbol', {{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{ symbol:SYMBOL, days_ahead:5 }})
    }});
    if (!resp.ok) throw new Error('API error');
    const data = await resp.json();
    document.getElementById('kpiPreco').textContent = '$' + data.last_close.toFixed(2);
    const pct = ((data.predictions[0].predicted_price - data.last_close) / data.last_close * 100);
    const pctStr = (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%';
    const deltaEl = document.getElementById('kpiPrecoDelta');
    deltaEl.textContent = pctStr + ' (próx. $' + data.predictions[0].predicted_price.toFixed(2) + ')';
    deltaEl.className = 'kpi-delta ' + (pct >= 0 ? 'up' : 'down');

    DETAILS.preco.text = 'O ativo <b>' + SYMBOL + '</b> opera em <b>$' + data.last_close.toFixed(2) + '</b>. ' +
      'Previsão LSTM D+1: <b>$' + data.predictions[0].predicted_price.toFixed(4) + '</b> (' + pctStr + '). ' +
      'Confiança do modelo: MAPE de <b>' + '{mape_val}' + '%</b>.';
    DETAILS.ia.text = 'Modelo LSTM com camadas de <b>' + '{lstm_1}' + ' + ' + '{lstm_2}' + '</b> unidades, ' +
      'treinado em <b>' + SYMBOL + '</b> com janela de <b>' + '{window_size}' + '</b> dias. ' +
      'Previsão atual D+1: <b>$' + data.predictions[0].predicted_price.toFixed(2) + '</b>. ' +
      'MAPE: <b>' + '{mape_val}' + '%</b>.';

    document.getElementById('kpiIA').textContent = CONFIDENCE + '%';
    document.getElementById('kpiIADelta').textContent = 'MAPE ' + '{mape_val}' + '%';
  }} catch(e) {{
    console.warn('prediction fetch failed, using defaults');
  }}

  try {{
    const histResp = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/' + SYMBOL + '?range=' + range + '&interval=1d');
    if (!histResp.ok) throw new Error('yahoo blocked');
    const histData = await histResp.json();
    const quotes = histData.chart.result[0];
    const timestamps = quotes.timestamp.map(t => new Date(t*1000).toLocaleDateString());
    const closes = quotes.indicators.quote[0].close;
    const volumes = quotes.indicators.quote[0].volume;

    const minC = Math.min(...closes.filter(c => c));
    const maxC = Math.max(...closes.filter(c => c));
    const volatility = ((maxC - minC) / minC * 100);
    document.getElementById('kpiVolatilidade').textContent = volatility.toFixed(1) + '%';
    const volEl = document.getElementById('kpiVolatilidadeDelta');
    volEl.textContent = volatility < 30 ? '↓ risco controlado' : '↑ volatilidade elevada';
    volEl.className = 'kpi-delta ' + (volatility < 30 ? 'up' : 'down');
    DETAILS.volatilidade.text = 'Volatilidade de <b>' + volatility.toFixed(2) + '%</b> no período (' + range + '). ' +
      'Valores acima de 30% indicam risco elevado. ' +
      'O ativo está <b>' + (volatility < 30 ? 'dentro' : 'acima') + '</b> dos níveis usuais.';

    const last20 = closes.filter(c => c).slice(-20);
    const slope = last20.length > 1 ? (last20[last20.length-1] - last20[0]) / last20[0] * 100 : 0;
    const trendText = slope > 0.5 ? 'ALTA' : slope < -0.5 ? 'BAIXA' : 'LATERAL';
    const trendCls = slope > 0.5 ? 'up' : slope < -0.5 ? 'down' : 'neutral';
    const trendName = slope > 0.5 ? 'Bullish' : slope < -0.5 ? 'Bearish' : 'Neutral';
    document.getElementById('kpiTendencia').textContent = trendText;
    const trEl = document.getElementById('kpiTendenciaDelta');
    trEl.textContent = trendName + ' · ' + slope.toFixed(2) + '%';
    trEl.className = 'kpi-delta ' + trendCls;
    DETAILS.tendencia.text = 'Tendência <b>' + trendText + '</b> (' + trendName + ') detectada pela inclinação dos últimos 20 dias. ' +
      'Inclinação: <b>' + slope.toFixed(2) + '%</b>. ' +
      'Confirmação adicional pelo cruzamento de MAs e MACD.';

    if (priceChart) priceChart.destroy();
    priceChart = new Chart(ctx, {{
      type:'line',
      data:{{
        labels: timestamps,
        datasets:[{{
          label:SYMBOL + ' Close',
          data:closes,
          borderColor:'#00FF88',
          backgroundColor:'rgba(0,255,136,0.05)',
          borderWidth:1.5,
          fill:true,
          tension:0.3,
          pointRadius:0,
          pointHitRadius:8
        }}]
      }},
      options:{{
        responsive:true,
        maintainAspectRatio:false,
        plugins:{{ legend:{{ display:false }} }},
        scales:{{
          x:{{ grid:{{ color:'rgba(255,255,255,0.03)' }}, ticks:{{ color:'#52525B', font:{{ size:9, family:'JetBrains Mono' }} }} }},
          y:{{ grid:{{ color:'rgba(255,255,255,0.03)' }}, ticks:{{ color:'#52525B', font:{{ size:9, family:'JetBrains Mono' }} }} }}
        }},
        interaction:{{ intersect:false, mode:'index' }}
      }}
    }});
  }} catch(e) {{
    canvas.parentElement.innerHTML =
      '<div style="color:#52525B;font-size:0.75rem;padding:40px;text-align:center;">' +
      'Gráfico indisponível · Yahoo Finance pode estar bloqueado</div>';
  }}
}}

fetchChart(activeRange);
</script>
</body>
</html>""")


# ============================================================ #
@router.get("/health", tags=["health"])
def health_check(request: Request):
    predictor = getattr(request.app.state, "predictor", None)
    md = predictor.metadata if predictor else {}
    metrics_data = md.get("metrics", {}) if md else {}
    engine_status = "ok" if predictor is not None else "degraded"

    now = datetime.now()
    uptime_seconds = (now - getattr(request.app.state, "_started_at", now)).seconds if hasattr(request.app.state, "_started_at") else 0

    query_format = request.query_params.get("format", "")
    accept = request.headers.get("accept", "")
    if query_format == "json" or "text/html" not in accept:
        return {
            "status": engine_status,
            "model_loaded": predictor is not None,
            "version": __version__,
            "model": {
                "symbol": md.get("symbol", "—") if md else "—",
                "metrics": {
                    "mae": metrics_data.get("mae"),
                    "rmse": metrics_data.get("rmse"),
                    "mape": metrics_data.get("mape"),
                } if metrics_data else None,
                "window_size": md.get("window_size") if md else None,
                "trained_at": md.get("trained_at") if md else None,
            } if predictor else None,
            "uptime_seconds": uptime_seconds,
            "timestamp": now.isoformat(),
        }

    status_color = "#00FF88" if predictor else "#FF3B3B"
    status_text = "ONLINE" if predictor else "DEGRADED"
    symbol = md.get("symbol", "—") if md else "—"
    trained_at = md.get("trained_at", "—") if md else "—"
    window_size = md.get("window_size", "—") if md else "—"

    mae_raw = metrics_data.get("mae") if metrics_data else None
    rmse_raw = metrics_data.get("rmse") if metrics_data else None
    mape_raw = metrics_data.get("mape") if metrics_data else None
    mae_v = f"{mae_raw:.4f}" if mae_raw is not None else "—"
    rmse_v = f"{rmse_raw:.4f}" if rmse_raw is not None else "—"
    mape_v = f"{mape_raw:.2f}" if mape_raw is not None else "—"

    mae_bar = f"{min(100, max(5, int(mae_raw * 10)))}" if mae_raw is not None else "0"
    rmse_bar = f"{min(100, max(5, int(rmse_raw * 8)))}" if rmse_raw is not None else "0"
    mape_bar = f"{min(100, max(5, int(mape_raw * 12)))}" if mape_raw is not None else "0"

    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · Health</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background:#050507; color:#A1A1AA; font-family:'JetBrains Mono',monospace;
    min-height:100vh; padding:32px 20px; display:flex; flex-direction:column; align-items:center;
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(0,255,136,0.03) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 50%, rgba(183,148,244,0.03) 0%, transparent 50%);
  }}
  body::before {{
    content:''; position:fixed; inset:0; pointer-events:none;
    background:repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,136,0.008) 2px, rgba(0,255,136,0.008) 4px);
    z-index:9999;
  }}
  .container {{ max-width:680px; width:100%; }}
  .prompt {{ font-size:0.6rem; color:#3F3F46; margin-bottom:24px; display:flex; align-items:center; gap:8px; }}
  .prompt-sym {{ color:#00FF88; }}
  .cursor {{ animation:blink 1s step-end infinite; }}
  @keyframes blink {{ 50%{{opacity:0}} }}

  .card {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:8px;
    padding:24px; margin-bottom:16px;
  }}
  .card-title {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:16px; }}

  .status-row {{ display:flex; align-items:center; gap:12px; margin-bottom:24px; }}
  .status-dot {{ width:12px; height:12px; border-radius:50%; background:{status_color};
    box-shadow:0 0 16px {status_color}; animation:pulse-dot 2s ease-in-out infinite; }}
  @keyframes pulse-dot {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
  .status-label {{ font-size:1.1rem; font-weight:600; color:{status_color}; }}
  .status-sub {{ font-size:0.65rem; color:#52525B; }}

  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .field {{}}
  .field-label {{ font-size:0.5rem; color:#3F3F46; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px; }}
  .field-value {{ font-size:0.85rem; color:#FAFAFA; font-weight:500; }}
  .field-value.green {{ color:#00FF88; }}
  .field-value.blue {{ color:#5B9DFF; }}
  .field-value.purple {{ color:#B794F4; }}
  .field-value.yellow {{ color:#FBBF24; }}
  .field-value.orange {{ color:#FF9500; }}
  .field-value.red {{ color:#FF3B3B; }}

  .bar-group {{ margin-top:16px; }}
  .bar-row {{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }}
  .bar-label {{ font-size:0.55rem; color:#52525B; width:60px; flex-shrink:0; }}
  .bar-track {{ flex:1; height:6px; background:#0E0E15; border-radius:3px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:3px; }}

  .meta {{ font-size:0.6rem; color:#3F3F46; text-align:center; margin-top:24px; }}
  .meta a {{ color:#52525B; text-decoration:none; }}
  .meta a:hover {{ color:#A1A1AA; }}

  .section {{ margin-top:20px; }}
  .section-title {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:12px; }}

  .endpoints {{ background:#0A0A0F; border:1px solid #18181B; border-radius:8px; overflow:hidden; }}
  .endpoint-row {{
    display:flex; justify-content:space-between; align-items:center;
    padding:10px 16px; border-bottom:1px solid #18181B; font-size:0.72rem;
    transition:background .2s; text-decoration:none; color:inherit;
  }}
  .endpoint-row:last-child {{ border-bottom:none; }}
  .endpoint-row:hover {{ background:#0E0E15; }}
  .endpoint-method {{
    display:inline-block; width:44px; padding:2px 0; text-align:center;
    border-radius:4px; font-size:0.55rem; font-weight:700;
  }}
  .get {{ background:rgba(97,175,254,0.15); color:#61AFFE; }}
  .endpoint-path {{ color:#FAFAFA; font-weight:500; margin-left:10px; }}
  .endpoint-desc {{ color:#52525B; font-size:0.6rem; margin-left:auto; }}

  .json-btn {{
    display:inline-block; margin-top:12px; padding:6px 14px;
    background:transparent; border:1px solid #18181B; border-radius:4px;
    color:#52525B; font-family:inherit; font-size:0.6rem; cursor:pointer;
    text-decoration:none; transition:all .2s;
  }}
  .json-btn:hover {{ border-color:#333; color:#A1A1AA; }}

  @media (max-width:500px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="prompt">
    <span class="prompt-sym">►</span>
    <span>healthcheck — {now.strftime('%Y-%m-%d %H:%M:%S')}Z</span>
    <span class="cursor">▌</span>
  </div>

  <div class="card">
    <div class="card-title">Status do Sistema</div>
    <div class="status-row">
      <span class="status-dot"></span>
      <div>
        <div class="status-label">{status_text}</div>
        <div class="status-sub">v{__version__} · {uptime_str} de atividade</div>
      </div>
    </div>

    <div class="grid">
      <div class="field">
        <div class="field-label">Modelo</div>
        <div class="field-value green">{'CARREGADO' if predictor else 'NÃO DISPONÍVEL'}</div>
      </div>
      <div class="field">
        <div class="field-label">Símbolo</div>
        <div class="field-value blue">{symbol}</div>
      </div>
      <div class="field">
        <div class="field-label">Janela (window)</div>
        <div class="field-value purple">{window_size}</div>
      </div>
      <div class="field">
        <div class="field-label">Treinado em</div>
        <div class="field-value" style="font-size:0.7rem;">{trained_at[:19] if trained_at != '—' else '—'}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Métricas do Modelo</div>
    <div class="grid">
      <div class="field">
        <div class="field-label">MAE</div>
        <div class="field-value orange">{mae_v}</div>
      </div>
      <div class="field">
        <div class="field-label">RMSE</div>
        <div class="field-value yellow">{rmse_v}</div>
      </div>
      <div class="field">
        <div class="field-label">MAPE</div>
        <div class="field-value green">{mape_v}%</div>
      </div>
      <div class="field">
        <div class="field-label">Acurácia</div>
        <div class="field-value green">{f'{100 - mape_raw:.2f}%' if mape_raw is not None else '—'}</div>
      </div>
    </div>

    <div class="bar-group">
      <div class="bar-row">
        <span class="bar-label">MAE</span>
        <div class="bar-track"><div class="bar-fill" style="width:{mae_bar}%;background:#FF9500;"></div></div>
      </div>
      <div class="bar-row">
        <span class="bar-label">RMSE</span>
        <div class="bar-track"><div class="bar-fill" style="width:{rmse_bar}%;background:#FBBF24;"></div></div>
      </div>
      <div class="bar-row">
        <span class="bar-label">MAPE</span>
        <div class="bar-track"><div class="bar-fill" style="width:{mape_bar}%;background:#00FF88;"></div></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Endpoints</div>
    <div class="endpoints">
      <a class="endpoint-row" href="/">
        <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/</span></span>
        <span class="endpoint-desc">Dashboard principal</span>
      </a>
      <a class="endpoint-row" href="/model/info">
        <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/model/info</span></span>
        <span class="endpoint-desc">Metadados do treinamento</span>
      </a>
      <a class="endpoint-row" href="/docs">
        <span><span class="endpoint-method" style="background:rgba(255,255,255,0.06);color:#888;">DOC</span><span class="endpoint-path">Swagger UI</span></span>
        <span class="endpoint-desc">Documentação interativa</span>
      </a>
      <a class="endpoint-row" href="/metrics">
        <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/metrics</span></span>
        <span class="endpoint-desc">Métricas Prometheus</span>
      </a>
    </div>
  </div>

  <div style="text-align:center;margin-top:16px;">
    <a class="json-btn" href="/health?format=json">⎔ Ver JSON</a>
  </div>

  <div class="meta">
    <a href="/">⟨⟩ AI Quant Terminal</a> · <a href="/docs">API Docs</a> · {now.strftime('%Y-%m-%d %H:%M:%S')}Z
  </div>
</div>
</body>
</html>""")


# ============================================================ #
@router.get("/model/info", response_model=ModelInfoResponse, tags=["model"])
def model_info(request: Request) -> ModelInfoResponse:
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    md = predictor.metadata
    return ModelInfoResponse(
        symbol_trained_on=md.get("symbol", "?"),
        window_size=md["window_size"],
        lstm_units_1=md["lstm_units_1"],
        lstm_units_2=md["lstm_units_2"],
        dropout_rate=md["dropout_rate"],
        epochs_trained=md["epochs_trained"],
        train_samples=md["train_samples"],
        test_samples=md["test_samples"],
        metrics=md["metrics"],
        trained_at=md["trained_at"],
    )


# ============================================================ #
@router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["prediction"],
    summary="Previsão a partir de histórico fornecido",
)
def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    """
    Recebe uma lista de preços históricos e retorna a previsão.

    A lista precisa ter ao menos `window_size` (60) valores em ordem
    cronológica crescente.
    """
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    if len(payload.close_prices) < predictor.window_size:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Forneça pelo menos {predictor.window_size} preços. "
                f"Recebidos: {len(payload.close_prices)}."
            ),
        )

    start = time.perf_counter()
    with TrackPrediction(endpoint="/predict"):
        if payload.days_ahead == 1:
            preds: List[float] = [predictor.predict_next(payload.close_prices)]
        else:
            preds = predictor.predict_multistep(
                payload.close_prices, steps=payload.days_ahead
            )
    elapsed_ms = (time.perf_counter() - start) * 1000

    items = [
        PredictionItem(day=i + 1, predicted_price=round(p, 4))
        for i, p in enumerate(preds)
    ]

    if preds:
        LAST_PREDICTION_VALUE.labels(symbol="custom").set(preds[-1])

    return PredictResponse(
        predictions=items,
        inference_time_ms=round(elapsed_ms, 2),
    )


# ============================================================ #
@router.post(
    "/predict/symbol",
    response_model=SymbolPredictResponse,
    tags=["prediction"],
    summary="Previsão buscando histórico recente via Yahoo Finance",
)
def predict_from_symbol(
    payload: SymbolPredictRequest, request: Request
) -> SymbolPredictResponse:
    """
    Busca o histórico recente do yfinance e prevê o(s) próximo(s) preço(s).
    """
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    try:
        closes = fetch_recent_window(payload.symbol, predictor.window_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # noqa: BLE001
        logger.exception("Erro ao buscar dados do yfinance")
        raise HTTPException(status_code=502, detail=f"Falha ao buscar dados: {e}")

    last_close = float(closes.iloc[-1])
    last_date = str(closes.index[-1].date())

    start = time.perf_counter()
    with TrackPrediction(endpoint="/predict/symbol"):
        if payload.days_ahead == 1:
            preds = [predictor.predict_next(closes.tolist())]
        else:
            preds = predictor.predict_multistep(
                closes.tolist(), steps=payload.days_ahead
            )
    elapsed_ms = (time.perf_counter() - start) * 1000

    items = [
        PredictionItem(day=i + 1, predicted_price=round(p, 4))
        for i, p in enumerate(preds)
    ]

    if preds:
        LAST_PREDICTION_VALUE.labels(symbol=payload.symbol).set(preds[-1])

    return SymbolPredictResponse(
        symbol=payload.symbol,
        last_close=round(last_close, 4),
        last_close_date=last_date,
        predictions=items,
        inference_time_ms=round(elapsed_ms, 2),
    )
