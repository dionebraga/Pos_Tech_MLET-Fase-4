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
<title>AI Quant · Trading Terminal</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
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
  .container {{ max-width:1100px; width:100%; margin:0 auto; }}
  .terminal-bar {{
    font-size:0.6rem; color:#3F3F46; margin-bottom:16px;
    display:flex; align-items:center; gap:8px;
  }}
  .prompt {{ color:#00FF88; }}
  .cursor {{ animation:blink 1s step-end infinite; }}
  @keyframes blink {{ 50%{{opacity:0}} }}

  .top-row {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; flex-wrap:wrap; gap:12px; }}
  .brand {{ display:flex; align-items:center; gap:16px; }}
  .brand-icon {{ width:36px; height:36px; border:1px solid #00FF88; border-radius:6px; display:flex; align-items:center; justify-content:center; color:#00FF88; font-weight:700; font-size:1rem; box-shadow:0 0 16px rgba(0,255,136,0.1); }}
  .brand-name {{ font-size:1.2rem; font-weight:700; color:#FAFAFA; letter-spacing:-0.3px; }}
  .brand-name span {{ color:#00FF88; }}
  .brand-tag {{ font-size:0.5rem; color:#52525B; text-transform:uppercase; letter-spacing:0.15em; }}
  .status-pill {{
    display:flex; align-items:center; gap:8px; padding:6px 14px;
    background:#0A0A0F; border:1px solid #18181B; border-radius:20px; font-size:0.65rem;
  }}
  .pill-dot {{ width:7px; height:7px; border-radius:50%; background:{status_color}; box-shadow:0 0 8px {status_color}; animation:pulse-dot 2s ease-in-out infinite; }}
  @keyframes pulse-dot {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}

  .model-meta {{ font-size:0.55rem; color:#3F3F46; text-align:right; line-height:1.6; }}

  /* ━━ Earth Pulse ━━ */
  .earth-section {{ display:flex; align-items:center; justify-content:center; gap:36px; margin-bottom:28px; flex-wrap:wrap; }}
  .earth-pulse {{ position:relative; width:100px; height:100px; flex-shrink:0; }}
  .earth-globe {{
    width:100px; height:100px; border-radius:50%;
    background:radial-gradient(circle at 35% 35%, #1a3a4a, #0a1a2a 50%, #050a12);
    box-shadow:inset -15px -8px 25px rgba(0,0,0,0.6), 0 0 30px rgba(0,255,136,0.1);
    position:relative; overflow:hidden;
  }}
  .earth-globe::before {{
    content:''; position:absolute; inset:0; border-radius:50%;
    background:linear-gradient(90deg, transparent 30%, rgba(0,255,136,0.05) 50%, transparent 70%);
    animation:spin 8s linear infinite;
  }}
  @keyframes spin {{ 0%{{transform:translateX(-30%)}} 100%{{transform:translateX(30%)}} }}
  .ring {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:100px; height:100px; border-radius:50%; border:1px solid rgba(0,255,136,0.1); animation:expand 3s ease-out infinite; }}
  .ring:nth-child(2) {{ animation-delay:1s; }}
  .ring:nth-child(3) {{ animation-delay:2s; }}
  @keyframes expand {{ 0%{{width:100px;height:100px;opacity:1}} 100%{{width:220px;height:220px;opacity:0}} }}
  .stat-hub {{ display:flex; gap:20px; flex-wrap:wrap; }}
  .stat-item {{ text-align:center; }}
  .stat-num {{ font-size:1.1rem; font-weight:600; }}
  .stat-lbl {{ font-size:0.5rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-top:2px; }}

  /* ━━ KPI Cards ━━ */
  .kpi-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:8px; }}
  .kpi {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:8px;
    padding:14px; cursor:pointer; transition:all .25s; position:relative; overflow:hidden;
  }}
  .kpi::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px; background:transparent; transition:background .25s; }}
  .kpi:hover {{ border-color:#27272A; background:#0E0E15; }}
  .kpi.on {{ border-color:#333; }}
  .kpi.green.on::before {{ background:#00FF88; }}
  .kpi.blue.on::before {{ background:#5B9DFF; }}
  .kpi.purple.on::before {{ background:#B794F4; }}
  .kpi.amber.on::before {{ background:#FF9500; }}
  .kpi-head {{ display:flex; justify-content:space-between; align-items:center; }}
  .kpi-lbl {{ font-size:0.5rem; color:#52525B; text-transform:uppercase; letter-spacing:0.1em; }}
  .kpi-ico {{ font-size:0.65rem; color:#3F3F46; }}
  .kpi-val {{ font-size:1.1rem; font-weight:600; color:#FAFAFA; margin:3px 0; }}
  .kpi-dlt {{ font-size:0.55rem; }}
  .kpi-dlt.up {{ color:#00FF88; }}
  .kpi-dlt.down {{ color:#FF3B3B; }}
  .kpi-dlt.neutral {{ color:#FBBF24; }}

  .detail-box {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:8px;
    padding:18px; margin-bottom:20px; display:none; animation:slide .3s ease;
  }}
  .detail-box.show {{ display:block; }}
  @keyframes slide {{ 0%{{opacity:0;transform:translateY(-6px)}} 100%{{opacity:1;transform:translateY(0)}} }}
  .detail-tag {{ font-size:0.45rem; color:#52525B; text-transform:uppercase; letter-spacing:0.15em; }}
  .detail-title {{ font-size:0.95rem; font-weight:600; color:#FAFAFA; margin:4px 0 8px; }}
  .detail-text {{ font-size:0.72rem; color:#A1A1AA; line-height:1.6; }}
  .detail-text b {{ color:#FAFAFA; }}

  /* ━━ Main Layout ━━ */
  .main-grid {{ display:grid; grid-template-columns:1.8fr 1fr; gap:16px; margin-bottom:20px; }}
  .chart-card {{ background:#0A0A0F; border:1px solid #18181B; border-radius:8px; padding:14px; }}
  .chart-top {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }}
  .chart-title {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.1em; }}
  .range-group {{ display:flex; gap:6px; }}
  .range-btn {{
    padding:3px 10px; background:transparent; border:1px solid #18181B; border-radius:4px;
    color:#52525B; font-family:inherit; font-size:0.55rem; cursor:pointer; transition:all .2s;
  }}
  .range-btn:hover {{ border-color:#333; color:#A1A1AA; }}
  .range-btn.active {{ border-color:#00FF88; color:#00FF88; }}
  .chart-box {{ height:300px; }}
  .chart-box > div {{ width:100% !important; height:100% !important; }}

  /* ━━ Prediction Panel ━━ */
  .pred-card {{ background:#0A0A0F; border:1px solid #18181B; border-radius:8px; padding:14px; }}
  .pred-title {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:10px; }}
  .pred-row {{ display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #0E0E15; font-size:0.65rem; }}
  .pred-row:last-child {{ border-bottom:none; }}
  .pred-day {{ color:#3F3F46; }}
  .pred-val {{ color:#FAFAFA; font-weight:500; }}
  .pred-chg {{ font-size:0.6rem; }}
  .pred-chg.pos {{ color:#00FF88; }}
  .pred-chg.neg {{ color:#FF3B3B; }}
  .model-badge {{
    display:inline-block; padding:2px 8px; border:1px solid #00FF88; border-radius:4px;
    font-size:0.5rem; color:#00FF88; margin-top:10px;
  }}

  /* ━━ Market Info ━━ */
  .info-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; }}
  .info-cell {{}}
  .info-lbl {{ font-size:0.45rem; color:#3F3F46; text-transform:uppercase; letter-spacing:0.1em; }}
  .info-val {{ font-size:0.7rem; color:#FAFAFA; font-weight:500; }}

  .footer {{ text-align:center; margin-top:24px; font-size:0.55rem; color:#3F3F46; padding-bottom:20px; }}
  .footer a {{ color:#52525B; text-decoration:none; }}
  .footer a:hover {{ color:#A1A1AA; }}

  @media (max-width:768px) {{ .kpi-row {{ grid-template-columns:repeat(2,1fr); }} .main-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="terminal-bar">
    <span class="prompt">►</span>
    <span>AI Quant Terminal · v{__version__} · {datetime.now().strftime('%Y-%m-%d %H:%M')}Z</span>
    <span class="cursor">▌</span>
  </div>

  <div class="top-row">
    <div class="brand">
      <div class="brand-icon">◆</div>
      <div>
        <div class="brand-name">AI <span>Quant</span></div>
        <div class="brand-tag">LSTM Trading Terminal</div>
      </div>
    </div>
    <div class="status-pill">
      <span class="pill-dot"></span>
      <span style="color:{status_color};">{status_text}</span>
      <span style="color:#3F3F46;">·</span>
      <span style="color:#52525B;">{model_badge}</span>
    </div>
    <div class="model-meta">
      <div>MODEL {symbol}</div>
      <div>TRAIN {trained_at[:10] if trained_at != '—' else '—'}</div>
    </div>
  </div>

  <div class="earth-section">
    <div class="earth-pulse">
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="earth-globe"></div>
    </div>
    <div class="stat-hub">
      <div class="stat-item"><div class="stat-num" style="color:#00FF88;">{symbol}</div><div class="stat-lbl">Símbolo</div></div>
      <div class="stat-item"><div class="stat-num" style="color:#B794F4;">{mae_val}</div><div class="stat-lbl">MAE</div></div>
      <div class="stat-item"><div class="stat-num" style="color:#5B9DFF;">{rmse_val}</div><div class="stat-lbl">RMSE</div></div>
      <div class="stat-item"><div class="stat-num" style="color:#FBBF24;">{mape_val}%</div><div class="stat-lbl">MAPE</div></div>
      <div class="stat-item"><div class="stat-num" style="color:#FF9500;">{window_size}</div><div class="stat-lbl">Window</div></div>
    </div>
  </div>

  <div class="kpi-row">
    <div class="kpi green" data-k="preco" onclick="kpiClick(this)">
      <div class="kpi-head"><span class="kpi-lbl">Preço Atual</span><span class="kpi-ico">$</span></div>
      <div class="kpi-val" id="kPreco">—</div>
      <div class="kpi-dlt up" id="kPrecoD">—</div>
    </div>
    <div class="kpi blue" data-k="vol" onclick="kpiClick(this)">
      <div class="kpi-head"><span class="kpi-lbl">Volatilidade</span><span class="kpi-ico">σ</span></div>
      <div class="kpi-val" id="kVol">—</div>
      <div class="kpi-dlt" id="kVolD">—</div>
    </div>
    <div class="kpi purple" data-k="tend" onclick="kpiClick(this)">
      <div class="kpi-head"><span class="kpi-lbl">Tendência (20d)</span><span class="kpi-ico">Δ</span></div>
      <div class="kpi-val" id="kTend">—</div>
      <div class="kpi-dlt" id="kTendD">—</div>
    </div>
    <div class="kpi amber" data-k="ia" onclick="kpiClick(this)">
      <div class="kpi-head"><span class="kpi-lbl">Confiança IA</span><span class="kpi-ico">λ</span></div>
      <div class="kpi-val" id="kIA">—</div>
      <div class="kpi-dlt up" id="kIAD">—</div>
    </div>
  </div>

  <div class="detail-box" id="detailBox">
    <div class="detail-tag" id="dTag"></div>
    <div class="detail-title" id="dTitle"></div>
    <div class="detail-text" id="dText"></div>
  </div>

  <div class="main-grid">
    <div class="chart-card">
      <div class="chart-top">
        <div class="chart-title">CANDLE · {symbol}</div>
        <div class="range-group" id="rangeGroup">
          <button class="range-btn" data-r="1mo">1M</button>
          <button class="range-btn active" data-r="3mo">3M</button>
          <button class="range-btn" data-r="6mo">6M</button>
          <button class="range-btn" data-r="1y">1A</button>
        </div>
      </div>
      <div class="chart-box" id="chartBox"></div>
    </div>

    <div class="pred-card">
      <div class="pred-title">Previsão LSTM · Próximos Dias</div>
      <div id="predBody">
        <div style="text-align:center;padding:30px 0;color:#3F3F46;font-size:0.65rem;">carregando...</div>
      </div>
      <div class="model-badge">LSTM {lstm_1}+{lstm_2} · window {window_size}</div>
      <div class="info-grid">
        <div class="info-cell"><div class="info-lbl">MAE</div><div class="info-val" style="color:#FF9500;">{mae_val}</div></div>
        <div class="info-cell"><div class="info-lbl">RMSE</div><div class="info-val" style="color:#FBBF24;">{rmse_val}</div></div>
        <div class="info-cell"><div class="info-lbl">MAPE</div><div class="info-val" style="color:#00FF88;">{mape_val}%</div></div>
        <div class="info-cell"><div class="info-lbl">Acurácia</div><div class="info-val" style="color:#00FF88;">{f'{100 - mape_num:.1f}%' if mape_num > 0 else '—'}</div></div>
      </div>
    </div>
  </div>

  <div class="footer">
    Tech Challenge Fase 4 · PósTech MLET FIAP ·
    <a href="https://github.com/dionebraga/Pos_Tech_MLET-Fase-4" target="_blank">GitHub</a>
    <span> · </span>
    <a href="/health">System Health</a>
    <span> · </span>
    <a href="/docs">API Docs</a>
  </div>
</div>

<script>
const SYM = "{symbol}";
const MAPE = {mape_num};
const CONF = MAPE > 0 ? (100 - MAPE).toFixed(1) : '—';

const DD = {{
  preco: {{ t:"Asset Price", ti:"Análise de Preço", tx:"Carregando...", c:"green" }},
  vol: {{ t:"Risk Metric", ti:"Volatilidade Anualizada", tx:"Carregando...", c:"blue" }},
  tend: {{ t:"Technical", ti:"Análise de Tendência", tx:"Carregando...", c:"purple" }},
  ia: {{ t:"Model Output", ti:"Confiança do Modelo LSTM", tx:"Carregando...", c:"amber" }}
}};

let chart = null;
let activeRange = '3mo';

function kpiClick(el) {{
  const k = el.dataset.k;
  const box = document.getElementById('detailBox');
  const same = box.classList.contains('show') && box.dataset.k === k;
  document.querySelectorAll('.kpi').forEach(c => c.classList.remove('on'));
  if (same) {{ box.classList.remove('show'); box.dataset.k = ''; return; }}
  el.classList.add('on');
  box.dataset.k = k;
  const d = DD[k];
  document.getElementById('dTag').textContent = d.t;
  document.getElementById('dTitle').textContent = d.ti;
  document.getElementById('dText').innerHTML = d.tx;
  box.className = 'detail-box show';
}}

function initChart() {{
  chart = LightweightCharts.createChart(document.getElementById('chartBox'), {{
    layout: {{ background:{{type:'solid',color:'#0A0A0F'}}, textColor:'#52525B', fontFamily:'JetBrains Mono' }},
    grid: {{ vertLines:{{color:'#0E0E15'}}, horzLines:{{color:'#0E0E15'}} }},
    timeScale: {{ borderColor:'#18181B', timeVisible:false }},
    rightPriceScale: {{ borderColor:'#18181B' }},
    crosshair: {{ mode:LightweightCharts.CrosshairMode.Normal }},
    width:0, height:300,
  }});
  const candleSeries = chart.addCandlestickSeries({{
    upColor:'#00FF88', downColor:'#FF3B3B', borderUpColor:'#00FF88', borderDownColor:'#FF3B3B',
    wickUpColor:'#00FF88', wickDownColor:'#FF3B3B',
  }});
  const volSeries = chart.addHistogramSeries({{
    priceFormat:{{ type:'volume' }}, color:'rgba(0,255,136,0.08)',
  }});
  return {{ chart, candleSeries, volSeries }};
}}

async function loadChart(range) {{
  try {{
    const r = await fetch('/health');
    const h = await r.json();
    if (!h.model_loaded) throw Error('no model');
  }} catch(e) {{
    document.getElementById('chartBox').innerHTML =
      '<div style="text-align:center;padding:40px;color:#52525B;font-size:0.7rem;">Modelo offline</div>';
    return;
  }}

  let predData = null;
  try {{
    const r = await fetch('/predict/symbol', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{ symbol:SYM, days_ahead:5 }})
    }});
    if (r.ok) predData = await r.json();
  }} catch(e) {{}}

  const box = document.getElementById('predBody');
  if (predData) {{
    document.getElementById('kPreco').textContent = '$' + predData.last_close.toFixed(2);
    const pct = ((predData.predictions[0].predicted_price - predData.last_close) / predData.last_close * 100);
    const ps = (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%';
    const el = document.getElementById('kPrecoD');
    el.textContent = ps + ' (D+1 $' + predData.predictions[0].predicted_price.toFixed(2) + ')';
    el.className = 'kpi-dlt ' + (pct >= 0 ? 'up' : 'down');
    DD.preco.tx = 'O ativo <b>' + SYM + '</b> opera em <b>$' + predData.last_close.toFixed(2) + '</b>. Previsão LSTM D+1: <b>$' + predData.predictions[0].predicted_price.toFixed(4) + '</b> (' + ps + '). MAPE: <b>{mape_val}%</b>.';
    DD.ia.tx = 'Modelo LSTM <b>{lstm_1}+{lstm_2}</b> treinado em <b>' + SYM + '</b> window=<b>{window_size}</b>. D+1: <b>$' + predData.predictions[0].predicted_price.toFixed(2) + '</b>. MAPE: <b>{mape_val}%</b>. Acurácia: <b>' + CONF + '%</b>.';
    document.getElementById('kIA').textContent = CONF + '%';
    document.getElementById('kIAD').textContent = 'MAPE {mape_val}%';

    box.innerHTML = predData.predictions.map((p,i) => {{
      const chg = i === 0 && predData.last_close ? ((p.predicted_price - predData.last_close) / predData.last_close * 100) : 0;
      const cls = chg >= 0 ? 'pos' : 'neg';
      const pref = chg >= 0 ? '+' : '';
      return '<div class="pred-row"><span class="pred-day">D+' + p.day + '</span><span class="pred-val">$' + p.predicted_price.toFixed(2) + '</span><span class="pred-chg ' + cls + '">' + pref + chg.toFixed(2) + '%</span></div>';
    }}).join('');
  }} else {{
    box.innerHTML = '<div style="text-align:center;padding:20px;color:#3F3F46;font-size:0.6rem;">Previsão indisponível</div>';
  }}

  try {{
    const url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + SYM + '?range=' + range + '&interval=1d';
    const hr = await fetch(url);
    if (!hr.ok) throw Error('yahoo blocked');
    const j = await hr.json();
    const q = j.chart.result[0];
    const t = q.timestamp;
    const o = q.indicators.quote[0].open;
    const hh = q.indicators.quote[0].high;
    const ll = q.indicators.quote[0].low;
    const cl = q.indicators.quote[0].close;
    const vo = q.indicators.quote[0].volume;

    const candles = [];
    const vols = [];
    let minP = Infinity, maxP = -Infinity;
    for (let i = 0; i < t.length; i++) {{
      if (o[i] == null || cl[i] == null) continue;
      candles.push({{ time: t[i], open: o[i], high: hh[i]||o[i], low: ll[i]||cl[i], close: cl[i] }});
      vols.push({{ time: t[i], value: vo[i]||0, color: cl[i] >= o[i] ? 'rgba(0,255,136,0.08)' : 'rgba(255,59,59,0.08)' }});
      if (o[i] < minP) minP = o[i];
      if (cl[i] > maxP) maxP = cl[i];
    }}

    const volatility = ((maxP - minP) / minP * 100);
    document.getElementById('kVol').textContent = volatility.toFixed(1) + '%';
    const ve = document.getElementById('kVolD');
    ve.textContent = volatility < 30 ? '✓ risco controlado' : '↑ volatilidade elevada';
    ve.className = 'kpi-dlt ' + (volatility < 30 ? 'up' : 'down');
    DD.vol.tx = 'Volatilidade <b>' + volatility.toFixed(2) + '%</b> no período (' + range + '). O ativo está <b>' + (volatility < 30 ? 'dentro' : 'acima') + '</b> dos níveis de risco usuais.';

    const last20 = cl.filter(c => c != null).slice(-20);
    const slope = last20.length > 1 ? (last20[last20.length-1] - last20[0]) / last20[0] * 100 : 0;
    const tTxt = slope > 0.5 ? 'ALTA' : slope < -0.5 ? 'BAIXA' : 'LATERAL';
    const tCls = slope > 0.5 ? 'up' : slope < -0.5 ? 'down' : 'neutral';
    const tNm = slope > 0.5 ? 'Bullish' : slope < -0.5 ? 'Bearish' : 'Neutral';
    document.getElementById('kTend').textContent = tTxt;
    const te = document.getElementById('kTendD');
    te.textContent = tNm + ' · ' + slope.toFixed(2) + '%';
    te.className = 'kpi-dlt ' + tCls;
    DD.tend.tx = 'Tendência <b>' + tTxt + '</b> (' + tNm + ') pelos últimos 20 dias. Inclinação: <b>' + slope.toFixed(2) + '%</b>.';

    if (chart) chart.chart.remove();
    const { chart: c, candleSeries: cs, volSeries: vs } = initChart();
    chart = {{ chart: c, candleSeries: cs, volSeries: vs }};
    cs.setData(candles);
    vs.setData(vols);
    c.timeScale().fitContent();
  }} catch(e) {{
    document.getElementById('chartBox').innerHTML =
      '<div style="text-align:center;padding:40px;color:#52525B;font-size:0.7rem;">Gráfico indisponível</div>';
  }}
}}

document.getElementById('rangeGroup').querySelectorAll('.range-btn').forEach(b => {{
  b.addEventListener('click', function() {{
    document.querySelectorAll('.range-btn').forEach(x => x.classList.remove('active'));
    this.classList.add('active');
    activeRange = this.dataset.r;
    loadChart(activeRange);
  }});
}});

loadChart(activeRange);
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
