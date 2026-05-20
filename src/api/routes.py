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

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · LSTM API</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;500;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background:#050507; color:#A1A1AA; font-family:'JetBrains Mono',monospace;
    min-height:100vh; display:flex; flex-direction:column; align-items:center;
    justify-content:center; padding:40px 20px;
  }}
  .container {{ max-width:900px; width:100%; }}
  .header {{ text-align:center; margin-bottom:48px; }}
  .logo {{ font-size:2.8rem; font-weight:700; color:#FAFAFA; letter-spacing:-1px; }}
  .logo span {{ color:#B794F4; }}
  .tag {{ font-size:0.75rem; color:#52525B; letter-spacing:0.2em; text-transform:uppercase; margin-top:6px; }}
  .status-bar {{
    display:flex; align-items:center; justify-content:center; gap:10px;
    margin-top:18px; font-size:0.8rem;
  }}
  .status-dot {{ width:10px; height:10px; border-radius:50%; background:{status_color};
    box-shadow:0 0 12px {status_color}; animation:pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin-bottom:32px; }}
  .card {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:10px;
    padding:20px; transition:border-color .2s;
  }}
  .card:hover {{ border-color:#27272A; }}
  .card-label {{ font-size:0.6rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:6px; }}
  .card-value {{ font-size:1.4rem; font-weight:500; color:#FAFAFA; }}
  .card-desc {{ font-size:0.7rem; color:#71717A; margin-top:4px; }}
  .card .accent {{ color:#B794F4; }}
  .card .green {{ color:#00FF88; }}
  .card .red {{ color:#FF3B3B; }}
  .card .yellow {{ color:#FBBF24; }}
  .endpoints {{ background:#0A0A0F; border:1px solid #18181B; border-radius:10px; overflow:hidden; }}
  .endpoint-row {{
    display:flex; justify-content:space-between; align-items:center;
    padding:14px 20px; border-bottom:1px solid #18181B; font-size:0.82rem;
    transition:background .2s; text-decoration:none; color:inherit;
  }}
  .endpoint-row:last-child {{ border-bottom:none; }}
  .endpoint-row:hover {{ background:#0E0E15; }}
  .endpoint-method {{
    display:inline-block; width:52px; padding:2px 0; text-align:center;
    border-radius:4px; font-size:0.65rem; font-weight:700; letter-spacing:0.05em;
  }}
  .get {{ background:rgba(97,175,254,0.15); color:#61AFFE; }}
  .post {{ background:rgba(73,204,144,0.15); color:#49CC90; }}
  .endpoint-path {{ color:#FAFAFA; font-weight:500; margin-left:14px; }}
  .endpoint-desc {{ color:#52525B; font-size:0.7rem; margin-left:auto; }}
  .footer {{ text-align:center; margin-top:32px; font-size:0.65rem; color:#3F3F46; letter-spacing:0.05em; }}
  .footer a {{ color:#52525B; text-decoration:none; }}
  .footer a:hover {{ color:#A1A1AA; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">AI <span>Quant</span></div>
    <div class="tag">LSTM Stock Prediction API · v{__version__}</div>
    <div class="status-bar">
      <span class="status-dot"></span>
      <span style="color:{status_color};font-weight:500;">{status_text}</span>
      <span style="color:#52525B;">·</span>
      <span style="color:#52525B;font-size:0.7rem;">{model_badge}</span>
    </div>
  </div>

  <div class="cards">
    <div class="card">
      <div class="card-label">Status do Modelo</div>
      <div class="card-value {'green' if predictor else 'red'}">{'ATIVO' if predictor else 'INDISPONÍVEL'}</div>
      <div class="card-desc">{md.get('symbol','—') if md else 'Nenhum modelo carregado'}</div>
    </div>
    <div class="card">
      <div class="card-label">Métricas</div>
      <div class="card-value accent">
        {'MAE ' + str(metrics.get('mae','—'))[:5] if metrics else '—'}
      </div>
      <div class="card-desc">
        {('RMSE ' + str(metrics.get('rmse','—'))[:5]) if metrics else '—'}{(' · MAPE ' + str(metrics.get('mape','—'))[:5] + '%') if metrics else ''}
      </div>
    </div>
    <div class="card">
      <div class="card-label">Janela Temporal</div>
      <div class="card-value">{md.get('window_size','—') if md else '—'}</div>
      <div class="card-desc">dias para prever o próximo</div>
    </div>
    <div class="card">
      <div class="card-label">Arquitetura</div>
      <div class="card-value accent">LSTM</div>
      <div class="card-desc">{str(md.get('lstm_units_1','?')) + ' + ' + str(md.get('lstm_units_2','?')) + ' unidades' if md else '2 camadas'}</div>
    </div>
  </div>

  <div class="endpoints">
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method swagger">📘</span><span class="endpoint-path">Swagger UI</span></span>
      <span class="endpoint-desc">Documentação interativa →</span>
    </a>
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/health</span></span>
      <span class="endpoint-desc">Status da API e do modelo</span>
    </a>
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/model/info</span></span>
      <span class="endpoint-desc">Metadados do modelo treinado</span>
    </a>
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method post">POST</span><span class="endpoint-path">/predict</span></span>
      <span class="endpoint-desc">Prever enviando preços manualmente</span>
    </a>
    <a class="endpoint-row" href="/docs">
      <span><span class="endpoint-method post">POST</span><span class="endpoint-path">/predict/symbol</span></span>
      <span class="endpoint-desc">Prever buscando Yahoo Finance</span>
    </a>
    <a class="endpoint-row" href="/metrics">
      <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/metrics</span></span>
      <span class="endpoint-desc">Métricas Prometheus</span>
    </a>
  </div>

  <div class="footer">
    <span>Tech Challenge Fase 4 · PósTech MLET FIAP · </span>
    <a href="/docs">Documentação</a>
  </div>
</div>
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
