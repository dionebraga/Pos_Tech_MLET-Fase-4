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
import requests as http_requests

from src.data_loader import fetch_recent_window

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================ #
@router.get("/api/chart/{symbol}", tags=["chart"])
def chart_proxy(symbol: str, range: str = "3mo", interval: str = "1d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range}&interval={interval}"
    try:
        resp = http_requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/", include_in_schema=False)
def _build_dashboard(request: Request) -> HTMLResponse:
    predictor = getattr(request.app.state, "predictor", None)
    md = predictor.metadata if predictor else {}
    metrics = md.get("metrics", {}) if md else {}
    status_color = "#00FF88" if predictor else "#FF3B3B"
    status_text = "ONLINE" if predictor else "DEGRADED"

    mae_val = f"{metrics['mae']:.4f}" if metrics and "mae" in metrics else "—"
    rmse_val = f"{metrics['rmse']:.4f}" if metrics and "rmse" in metrics else "—"
    mape_val = f"{metrics['mape']:.2f}%" if metrics and "mape" in metrics else "—"
    mape_num = metrics.get("mape", 0) if metrics else 0
    acc_val = f"{100 - mape_num:.1f}%" if mape_num > 0 else "—"
    symbol = str(md.get("symbol", "—")) if md else "—"
    window_size = str(md.get("window_size", "—")) if md else "—"
    lstm_1 = str(md.get("lstm_units_1", "?")) if md else "?"
    lstm_2 = str(md.get("lstm_units_2", "?")) if md else "?"
    trained_at = str(md.get("trained_at", "—"))[:10] if md and md.get("trained_at") else "—"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · LSTM Stock Prediction API</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--green:#00FF88;--blue:#5B9DFF;--purple:#B794F4;--amber:#FF9500;--red:#FF3B3B;--bg:#050507;--bg2:#0A0A0F;--bg3:#0E0E15;--border:#18181B;--border2:#27272A;--t1:#FAFAFA;--t2:#A1A1AA;--t3:#71717A;--t4:#52525B;--t5:#3F3F46}}
body{{background:var(--bg);color:var(--t2);font-family:'JetBrains Mono',monospace;min-height:100vh;padding:0;background-image:radial-gradient(ellipse at 15% 40%,rgba(0,255,136,0.04) 0%,transparent 55%),radial-gradient(ellipse at 85% 60%,rgba(91,157,255,0.04) 0%,transparent 55%)}}
body::before{{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,0.006) 2px,rgba(0,255,136,0.006) 4px);z-index:0}}
.wrap{{max-width:900px;margin:0 auto;padding:40px 20px 60px;position:relative;z-index:1}}
/* ── TOPBAR ── */
.topbar{{display:flex;align-items:center;justify-content:space-between;margin-bottom:48px;flex-wrap:wrap;gap:12px}}
.brand{{display:flex;align-items:center;gap:12px}}
.brand-icon{{width:36px;height:36px;border:1px solid var(--green);border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--green);font-size:1rem;font-weight:700;box-shadow:0 0 18px rgba(0,255,136,0.12)}}
.brand-name{{font-size:1.15rem;font-weight:700;color:var(--t1);letter-spacing:-0.3px}}
.brand-name span{{color:var(--green)}}
.brand-sub{{font-size:0.52rem;color:var(--t5);letter-spacing:0.12em;text-transform:uppercase;margin-top:2px}}
.status-pill{{display:flex;align-items:center;gap:8px;padding:6px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:20px;font-size:0.6rem}}
.status-dot{{width:7px;height:7px;border-radius:50%;background:{status_color};box-shadow:0 0 8px {status_color};animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.status-label{{color:{status_color};font-weight:600}}
/* ── HERO ── */
.hero{{text-align:center;margin-bottom:48px;padding:40px 20px}}
.hero-eyebrow{{font-size:0.6rem;color:var(--t5);letter-spacing:0.18em;text-transform:uppercase;margin-bottom:14px}}
.hero-title{{font-size:2rem;font-weight:700;color:var(--t1);letter-spacing:-0.04em;line-height:1.15;margin-bottom:12px}}
.hero-title span{{color:var(--green)}}
.hero-desc{{font-size:0.8rem;color:var(--t3);line-height:1.75;max-width:560px;margin:0 auto 24px}}
.hero-links{{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap}}
.btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:6px;font-family:inherit;font-size:0.65rem;font-weight:600;text-decoration:none;transition:all .2s;cursor:pointer;border:none}}
.btn-primary{{background:var(--green);color:#050507}}
.btn-primary:hover{{background:#00e67a;box-shadow:0 0 20px rgba(0,255,136,0.3)}}
.btn-ghost{{background:transparent;color:var(--t3);border:1px solid var(--border2)}}
.btn-ghost:hover{{border-color:var(--t5);color:var(--t1)}}
/* ── METRICS ROW ── */
.metrics-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:32px}}
.metric-card{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:14px;position:relative;overflow:hidden}}
.metric-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px}}
.metric-card.g::before{{background:var(--green)}}
.metric-card.b::before{{background:var(--blue)}}
.metric-card.p::before{{background:var(--purple)}}
.metric-card.a::before{{background:var(--amber)}}
.metric-label{{font-size:0.48rem;color:var(--t5);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px}}
.metric-value{{font-size:1rem;font-weight:600;color:var(--t1)}}
.metric-sub{{font-size:0.48rem;color:var(--t4);margin-top:3px}}
/* ── SECTION ── */
.section{{margin-bottom:28px}}
.section-header{{display:flex;align-items:center;gap:10px;margin-bottom:14px}}
.section-title{{font-size:0.6rem;color:var(--t5);text-transform:uppercase;letter-spacing:0.15em;font-weight:500}}
.section-line{{flex:1;height:1px;background:var(--border)}}
/* ── ENDPOINTS ── */
.endpoints{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
.ep-group-label{{font-size:0.48rem;color:var(--t5);text-transform:uppercase;letter-spacing:0.14em;padding:10px 16px 6px;background:var(--bg3);border-bottom:1px solid var(--border)}}
.ep-row{{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid var(--border);text-decoration:none;color:inherit;transition:background .15s}}
.ep-row:last-child{{border-bottom:none}}
.ep-row:hover{{background:var(--bg3)}}
.ep-method{{display:inline-flex;align-items:center;justify-content:center;width:46px;padding:3px 0;border-radius:4px;font-size:0.5rem;font-weight:700;flex-shrink:0}}
.get{{background:rgba(91,157,255,0.12);color:#61AFFE}}
.post{{background:rgba(73,204,144,0.12);color:#49CC90}}
.ep-path{{color:var(--t1);font-weight:600;font-size:0.7rem;flex:1}}
.ep-desc{{color:var(--t4);font-size:0.6rem;text-align:right}}
.ep-badge{{display:inline-block;padding:1px 7px;border-radius:3px;font-size:0.45rem;font-weight:600;margin-left:6px}}
.ep-badge.new{{background:rgba(0,255,136,0.1);color:var(--green)}}
/* ── CODE BLOCK ── */
.code-block{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;overflow:hidden;margin-top:8px}}
.code-header{{display:flex;align-items:center;justify-content:space-between;padding:8px 14px;border-bottom:1px solid var(--border);font-size:0.52rem;color:var(--t4)}}
.code-lang{{color:var(--green)}}
pre{{padding:16px;font-size:0.62rem;line-height:1.7;overflow-x:auto;color:var(--t2)}}
pre .kw{{color:var(--blue)}}
pre .str{{color:var(--green)}}
pre .cm{{color:var(--t5)}}
/* ── ARCH ── */
.arch{{display:flex;align-items:center;justify-content:center;gap:0;flex-wrap:wrap;padding:20px}}
.arch-block{{background:var(--bg3);border:1px solid var(--border2);border-radius:6px;padding:8px 14px;font-size:0.6rem;color:var(--t2);text-align:center}}
.arch-block .ab-title{{color:var(--t1);font-weight:600;font-size:0.65rem;margin-bottom:2px}}
.arch-block .ab-sub{{color:var(--t5);font-size:0.48rem}}
.arch-arrow{{color:var(--t5);font-size:0.8rem;padding:0 6px}}
/* ── FOOTER ── */
.page-footer{{margin-top:48px;padding-top:20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;font-size:0.55rem;color:var(--t5)}}
.page-footer a{{color:var(--t4);text-decoration:none}}
.page-footer a:hover{{color:var(--t2)}}
@media(max-width:640px){{.metrics-row{{grid-template-columns:1fr 1fr}}.hero-title{{font-size:1.4rem}}.topbar{{flex-direction:column;align-items:flex-start}}}}
</style>
</head>
<body>
<div class="wrap">

  <!-- TOPBAR -->
  <div class="topbar">
    <div class="brand">
      <div class="brand-icon">◆</div>
      <div>
        <div class="brand-name">AI <span>Quant</span></div>
        <div class="brand-sub">LSTM Stock Prediction API · v{__version__}</div>
      </div>
    </div>
    <div class="status-pill">
      <span class="status-dot"></span>
      <span class="status-label">{status_text}</span>
      <span style="color:var(--t5)">·</span>
      <span style="color:var(--t4)">modelo {symbol}</span>
    </div>
  </div>

  <!-- HERO -->
  <div class="hero">
    <div class="hero-eyebrow">Tech Challenge Fase 4 · PosTech MLET FIAP</div>
    <div class="hero-title">Previsão de Ações com<br><span>LSTM</span> e FastAPI</div>
    <div class="hero-desc">
      API RESTful para predição de preços de fechamento de ações usando redes neurais
      Long Short-Term Memory (LSTM). Envie um histórico de preços e receba previsões
      para os próximos dias com intervalo de confiança.
    </div>
    <div class="hero-links">
      <a class="btn btn-primary" href="/docs">◈ Swagger UI</a>
      <a class="btn btn-ghost" href="/health">⊙ Health Check</a>
      <a class="btn btn-ghost" href="/model/info">⊛ Model Info</a>
      <a class="btn btn-ghost" href="https://github.com/dionebraga/Pos_Tech_MLET-Fase-4" target="_blank">↗ GitHub</a>
    </div>
  </div>

  <!-- MODEL METRICS -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">Performance do Modelo</div>
      <div class="section-line"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-card g">
        <div class="metric-label">Símbolo</div>
        <div class="metric-value" style="color:var(--green)">{symbol}</div>
        <div class="metric-sub">treinado em {trained_at}</div>
      </div>
      <div class="metric-card a">
        <div class="metric-label">MAE</div>
        <div class="metric-value" style="color:var(--amber)">{mae_val}</div>
        <div class="metric-sub">Mean Absolute Error</div>
      </div>
      <div class="metric-card b">
        <div class="metric-label">RMSE</div>
        <div class="metric-value" style="color:var(--blue)">{rmse_val}</div>
        <div class="metric-sub">Root Mean Sq. Error</div>
      </div>
      <div class="metric-card p">
        <div class="metric-label">Acurácia</div>
        <div class="metric-value" style="color:var(--purple)">{acc_val}</div>
        <div class="metric-sub">MAPE {mape_val}</div>
      </div>
    </div>
  </div>

  <!-- ARCHITECTURE -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">Arquitetura</div>
      <div class="section-line"></div>
    </div>
    <div class="arch">
      <div class="arch-block"><div class="ab-title">Yahoo Finance</div><div class="ab-sub">Dados históricos</div></div>
      <div class="arch-arrow">→</div>
      <div class="arch-block"><div class="ab-title">MinMaxScaler</div><div class="ab-sub">Normalização</div></div>
      <div class="arch-arrow">→</div>
      <div class="arch-block"><div class="ab-title">Windowing</div><div class="ab-sub">Janela {window_size}d</div></div>
      <div class="arch-arrow">→</div>
      <div class="arch-block" style="border-color:rgba(0,255,136,0.3)"><div class="ab-title" style="color:var(--green)">LSTM {lstm_1}+{lstm_2}</div><div class="ab-sub">Dropout · Dense</div></div>
      <div class="arch-arrow">→</div>
      <div class="arch-block"><div class="ab-title">FastAPI</div><div class="ab-sub">REST endpoints</div></div>
      <div class="arch-arrow">→</div>
      <div class="arch-block"><div class="ab-title">Prometheus</div><div class="ab-sub">Monitoramento</div></div>
    </div>
  </div>

  <!-- ENDPOINTS -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">Endpoints</div>
      <div class="section-line"></div>
    </div>
    <div class="endpoints">
      <div class="ep-group-label">Predição</div>
      <a class="ep-row" href="/docs#/prediction/predict_predict_post">
        <span class="ep-method post">POST</span>
        <span class="ep-path">/predict</span>
        <span class="ep-desc">Previsão via histórico de preços fornecido</span>
      </a>
      <a class="ep-row" href="/docs#/prediction/predict_symbol_predict_symbol_post">
        <span class="ep-method post">POST</span>
        <span class="ep-path">/predict/symbol</span>
        <span class="ep-desc">Previsão automática via ticker (yfinance)</span>
      </a>
      <div class="ep-group-label">Modelo</div>
      <a class="ep-row" href="/model/info">
        <span class="ep-method get">GET</span>
        <span class="ep-path">/model/info</span>
        <span class="ep-desc">Metadados, arquitetura e métricas do modelo</span>
      </a>
      <div class="ep-group-label">Infraestrutura</div>
      <a class="ep-row" href="/health">
        <span class="ep-method get">GET</span>
        <span class="ep-path">/health</span>
        <span class="ep-desc">Status do sistema e uptime</span>
      </a>
      <a class="ep-row" href="/metrics">
        <span class="ep-method get">GET</span>
        <span class="ep-path">/metrics</span>
        <span class="ep-desc">Métricas Prometheus (requisições, latência, inferência)</span>
      </a>
      <a class="ep-row" href="/docs">
        <span class="ep-method get" style="background:rgba(255,255,255,0.06);color:#888">DOC</span>
        <span class="ep-path">/docs</span>
        <span class="ep-desc">Swagger UI — documentação interativa completa</span>
      </a>
    </div>
  </div>

  <!-- QUICK EXAMPLE -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">Exemplo Rápido</div>
      <div class="section-line"></div>
    </div>
    <div class="code-block">
      <div class="code-header">
        <span class="code-lang">bash · curl</span>
        <span>POST /predict/symbol</span>
      </div>
      <pre><span class="cm"># Previsão dos próximos 5 dias para AAPL</span>
<span class="kw">curl</span> -X POST <span class="str">"{request.url.scheme}://{request.url.netloc}/predict/symbol"</span> \\
  -H <span class="str">"Content-Type: application/json"</span> \\
  -d <span class="str">'{{"symbol": "AAPL", "days_ahead": 5}}'</span></pre>
    </div>
    <div class="code-block" style="margin-top:8px">
      <div class="code-header">
        <span class="code-lang">bash · curl</span>
        <span>POST /predict</span>
      </div>
      <pre><span class="cm"># Previsão via histórico customizado (mínimo {window_size} valores)</span>
<span class="kw">curl</span> -X POST <span class="str">"{request.url.scheme}://{request.url.netloc}/predict"</span> \\
  -H <span class="str">"Content-Type: application/json"</span> \\
  -d <span class="str">'{{"close_prices": [150.0, 151.2, ...], "days_ahead": 3}}'</span></pre>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="page-footer">
    <span>Dione Braga Ferreira · PosTech MLET FIAP · 2024</span>
    <span style="color:var(--t5)">{now_str}</span>
    <span>
      <a href="/health">health</a> ·
      <a href="/model/info">model</a> ·
      <a href="/docs">docs</a> ·
      <a href="https://github.com/dionebraga/Pos_Tech_MLET-Fase-4" target="_blank">github</a>
    </span>
  </div>

</div>
</body>
</html>"""
    return HTMLResponse(html)


# ============================================================ #
@router.get("/healthz", tags=["health"])
def healthz():
    """Render's routing layer probes this endpoint for readiness."""
    return {"status": "ok"}


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
@router.get("/model/info", tags=["model"])
def model_info(request: Request):
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    md = predictor.metadata
    query_format = request.query_params.get("format", "")
    accept = request.headers.get("accept", "")

    want_json = query_format == "json" or "application/json" in accept
    if not want_json:
        metrics = md.get("metrics", {})
        mae = metrics.get("mae", "—")
        rmse = metrics.get("rmse", "—")
        mape = metrics.get("mape", "—")
        trained_at_str = str(md.get("trained_at", "—"))[:19]
        lstm_str = f"{md.get('lstm_units_1', '?')}+{md.get('lstm_units_2', '?')}"

        mae_v = f"{mae:.4f}" if isinstance(mae, (int, float)) else "—"
        rmse_v = f"{rmse:.4f}" if isinstance(rmse, (int, float)) else "—"
        mape_v = f"{mape:.2f}%" if isinstance(mape, (int, float)) else "—"
        acc_str = f"{100 - mape:.2f}%" if isinstance(mape, (int, float)) else "—"
        mae_bar = min(100, max(4, int(mae * 10))) if isinstance(mae, (int, float)) else 0
        rmse_bar = min(100, max(4, int(rmse * 8))) if isinstance(rmse, (int, float)) else 0
        mape_bar = min(100, max(4, int(mape * 12))) if isinstance(mape, (int, float)) else 0
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · Model Info</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--green:#00FF88;--blue:#5B9DFF;--purple:#B794F4;--amber:#FF9500;--bg:#050507;--bg2:#0A0A0F;--bg3:#0E0E15;--border:#18181B;--border2:#27272A;--t1:#FAFAFA;--t2:#A1A1AA;--t3:#71717A;--t4:#52525B;--t5:#3F3F46}}
body{{background:var(--bg);color:var(--t2);font-family:'JetBrains Mono',monospace;min-height:100vh;padding:40px 20px 60px;background-image:radial-gradient(ellipse at 20% 50%,rgba(0,255,136,0.04) 0%,transparent 55%),radial-gradient(ellipse at 80% 50%,rgba(183,148,244,0.04) 0%,transparent 55%)}}
body::before{{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,0.006) 2px,rgba(0,255,136,0.006) 4px);z-index:0}}
.wrap{{max-width:720px;margin:0 auto;position:relative;z-index:1}}
.breadcrumb{{font-size:0.55rem;color:var(--t5);margin-bottom:28px;display:flex;align-items:center;gap:6px}}
.breadcrumb a{{color:var(--t4);text-decoration:none}}
.breadcrumb a:hover{{color:var(--t2)}}
.cursor{{animation:blink 1s step-end infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.page-header{{margin-bottom:28px}}
.page-eyebrow{{font-size:0.52rem;color:var(--t5);text-transform:uppercase;letter-spacing:0.14em;margin-bottom:8px}}
.page-title{{font-size:1.5rem;font-weight:700;color:var(--t1);letter-spacing:-0.03em;margin-bottom:6px}}
.page-title span{{color:var(--green)}}
.page-sub{{font-size:0.7rem;color:var(--t3);line-height:1.6}}
.card{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:24px;margin-bottom:14px;position:relative;overflow:hidden}}
.card-accent{{border-top:2px solid var(--green)}}
.card-accent-p{{border-top:2px solid var(--purple)}}
.card-accent-a{{border-top:2px solid var(--amber)}}
.card-label{{font-size:0.52rem;color:var(--t5);text-transform:uppercase;letter-spacing:0.14em;margin-bottom:18px;display:flex;align-items:center;gap:8px}}
.card-label::after{{content:'';flex:1;height:1px;background:var(--border)}}
.arch{{display:flex;flex-direction:column;gap:0}}
.arch-layer{{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--bg3)}}
.arch-layer:last-child{{border-bottom:none}}
.arch-idx{{font-size:0.48rem;color:var(--t5);width:20px;flex-shrink:0}}
.arch-badge{{display:inline-flex;align-items:center;padding:4px 10px;border-radius:5px;font-size:0.6rem;font-weight:600;flex-shrink:0;min-width:68px;justify-content:center}}
.arch-desc{{font-size:0.6rem;color:var(--t3);line-height:1.5}}
.arch-desc b{{color:var(--t2)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.field-label{{font-size:0.48rem;color:var(--t5);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:5px}}
.field-value{{font-size:0.88rem;color:var(--t1);font-weight:500}}
.metric-row{{margin-bottom:16px}}
.metric-head{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}}
.metric-name{{font-size:0.52rem;color:var(--t4);text-transform:uppercase;letter-spacing:0.1em}}
.metric-val{{font-size:0.78rem;font-weight:600}}
.bar-track{{height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:3px}}
.acc-badge{{display:inline-flex;align-items:center;gap:12px;padding:12px 18px;background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.2);border-radius:8px;margin-top:16px}}
.acc-val{{font-size:1.4rem;font-weight:700;color:var(--green)}}
.acc-label{{font-size:0.5rem;color:var(--t4);text-transform:uppercase;letter-spacing:0.1em;line-height:1.6}}
.cta-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}}
.btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:6px;font-family:inherit;font-size:0.62rem;font-weight:600;text-decoration:none;transition:all .2s;cursor:pointer;border:none}}
.btn-ghost{{background:transparent;color:var(--t3);border:1px solid var(--border2)}}
.btn-ghost:hover{{border-color:var(--t4);color:var(--t1)}}
.btn-green{{background:rgba(0,255,136,0.08);color:var(--green);border:1px solid rgba(0,255,136,0.25)}}
.btn-green:hover{{background:rgba(0,255,136,0.14)}}
.page-footer{{margin-top:28px;font-size:0.52rem;color:var(--t5);text-align:center;line-height:1.8}}
.page-footer a{{color:var(--t4);text-decoration:none}}
.page-footer a:hover{{color:var(--t2)}}
@media(max-width:500px){{.grid2{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="breadcrumb">
    <span>►</span>
    <a href="/">AI Quant API</a>
    <span>/</span>
    <span style="color:var(--t3)">model/info</span>
    <span style="margin-left:auto">{now_str}<span class="cursor">▌</span></span>
  </div>
  <div class="page-header">
    <div class="page-eyebrow">Model · LSTM · Tech Challenge Fase 4</div>
    <div class="page-title">Modelo <span>LSTM</span> — Metadados</div>
    <div class="page-sub">Rede neural para previsão de fechamento · Arquitetura {lstm_str} · Window {md.get("window_size","?")}d</div>
  </div>
  <div class="card card-accent">
    <div class="card-label">Arquitetura da Rede</div>
    <div class="arch">
      <div class="arch-layer">
        <span class="arch-idx">IN</span>
        <span class="arch-badge" style="background:rgba(91,157,255,0.12);color:#5B9DFF">Input</span>
        <span class="arch-desc">Shape <b>({md.get("window_size","?")}, 1)</b> — janela temporal normalizada (MinMaxScaler)</span>
      </div>
      <div class="arch-layer">
        <span class="arch-idx">L1</span>
        <span class="arch-badge" style="background:rgba(0,255,136,0.1);color:#00FF88">LSTM</span>
        <span class="arch-desc"><b>{md.get("lstm_units_1","?")} unidades</b> · return_sequences=True · padrões de curto prazo</span>
      </div>
      <div class="arch-layer">
        <span class="arch-idx">L2</span>
        <span class="arch-badge" style="background:rgba(0,255,136,0.1);color:#00FF88">LSTM</span>
        <span class="arch-desc"><b>{md.get("lstm_units_2","?")} unidades</b> · return_sequences=False · padrões de longo prazo</span>
      </div>
      <div class="arch-layer">
        <span class="arch-idx">D</span>
        <span class="arch-badge" style="background:rgba(255,149,0,0.1);color:#FF9500">Dropout</span>
        <span class="arch-desc">Taxa <b>{md.get("dropout_rate","?")}</b> — regularização contra overfitting</span>
      </div>
      <div class="arch-layer">
        <span class="arch-idx">OUT</span>
        <span class="arch-badge" style="background:rgba(183,148,244,0.1);color:#B794F4">Dense</span>
        <span class="arch-desc"><b>1 neurônio</b> — previsão do próximo preço de fechamento (D+1)</span>
      </div>
    </div>
  </div>
  <div class="card card-accent-a">
    <div class="card-label">Performance do Modelo</div>
    <div class="metric-row">
      <div class="metric-head">
        <span class="metric-name">MAE — Mean Absolute Error</span>
        <span class="metric-val" style="color:var(--amber)">{mae_v}</span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:{mae_bar}%;background:var(--amber)"></div></div>
    </div>
    <div class="metric-row">
      <div class="metric-head">
        <span class="metric-name">RMSE — Root Mean Square Error</span>
        <span class="metric-val" style="color:#FBBF24">{rmse_v}</span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:{rmse_bar}%;background:#FBBF24"></div></div>
    </div>
    <div class="metric-row">
      <div class="metric-head">
        <span class="metric-name">MAPE — Mean Absolute Percentage Error</span>
        <span class="metric-val" style="color:var(--blue)">{mape_v}</span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:{mape_bar}%;background:var(--blue)"></div></div>
    </div>
    <div class="acc-badge">
      <div class="acc-val">{acc_str}</div>
      <div class="acc-label">Acurácia<br>do Modelo LSTM</div>
    </div>
  </div>
  <div class="card card-accent-p">
    <div class="card-label">Detalhes do Treinamento</div>
    <div class="grid2">
      <div><div class="field-label">Símbolo</div><div class="field-value" style="color:var(--green)">{md.get("symbol","?")}</div></div>
      <div><div class="field-label">Treinado em</div><div class="field-value" style="font-size:0.75rem">{trained_at_str}</div></div>
      <div><div class="field-label">Window Size</div><div class="field-value" style="color:var(--blue)">{md.get("window_size","?")} dias</div></div>
      <div><div class="field-label">Epochs</div><div class="field-value">{md.get("epochs_trained","?")}</div></div>
      <div><div class="field-label">Amostras Treino</div><div class="field-value">{md.get("train_samples","?")}</div></div>
      <div><div class="field-label">Amostras Teste</div><div class="field-value">{md.get("test_samples","?")}</div></div>
    </div>
  </div>
  <div class="cta-row">
    <a class="btn btn-green" href="/model/info?format=json">⎔ Ver JSON</a>
    <a class="btn btn-ghost" href="/docs">◈ Swagger UI</a>
    <a class="btn btn-ghost" href="/health">⊙ Health</a>
    <a class="btn btn-ghost" href="/">← Voltar</a>
  </div>
  <div class="page-footer">
    <a href="/">AI Quant Terminal</a> · <a href="/docs">API Docs</a> · <a href="/health">Health</a> · {now_str}
  </div>
</div>
</body>
</html>""")

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
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        logger.exception("Erro ao buscar dados do yfinance")
        raise HTTPException(status_code=502, detail=f"Falha ao buscar dados: {e}") from e

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
