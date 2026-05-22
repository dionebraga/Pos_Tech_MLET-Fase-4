"""
src/api/main.py

FastAPI application entry point.
Carrega o modelo LSTM na inicialização, registra as rotas e expõe métricas
Prometheus para monitoramento em produção.
"""
import logging
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from starlette.routing import Match

from src import __version__
from src.api.routes import router
from src.api.monitoring import MODEL_LOADED, HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION, initialize_metrics
from src.config import settings
from src.predict import StockPredictor

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: carrega / descarrega o modelo
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executado no startup (yield) e no shutdown."""
    app.state._started_at = datetime.now()
    initialize_metrics()
    try:
        predictor = StockPredictor(
            model_path=settings.MODEL_PATH,
            scaler_path=settings.SCALER_PATH,
            metadata_path=settings.METADATA_PATH,
        )
        app.state.predictor = predictor
        MODEL_LOADED.set(1)
        logger.info(
            "Modelo carregado — symbol=%s, window=%d, metrics=%s",
            predictor.metadata.get("symbol", "?"),
            predictor.window_size,
            predictor.metadata.get("metrics", {}),
        )
    except FileNotFoundError:
        logger.warning(
            "Modelo não encontrado em %s — API rodando em modo degradado. "
            "Execute `python -m src.train` primeiro.",
            settings.MODEL_PATH,
        )
        app.state.predictor = None
        MODEL_LOADED.set(0)
    except Exception as exc:
        logger.exception("Falha ao carregar modelo: %s", exc)
        app.state.predictor = None
        MODEL_LOADED.set(0)

    yield  # API está pronta para atender requisições

    # Cleanup (se necessário no futuro)
    logger.info("API encerrando.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Tech Challenge Fase 4 - LSTM API",
    description="Previsão de preços de ações com LSTM · FastAPI · TensorFlow",
    summary="Stock price prediction API powered by LSTM deep learning",
    version=__version__,
    docs_url="/docs",
    lifespan=lifespan,
    contact={
        "name": "Dione Braga Ferreira",
        "url": "https://github.com/dionebraga/Pos_Tech_MLET-Fase-4",
    },
    license_info={
        "name": "MIT",
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
        "syntaxHighlight.theme": "monokai",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_http_middleware(request: Request, call_next):
    start = time.perf_counter()

    # Resolve o nome da rota (ex: /predict/symbol) em vez do path com params
    handler = request.url.path
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            handler = route.path
            break

    response = await call_next(request)
    duration = time.perf_counter() - start

    # Ignora o scrape do próprio Prometheus para não poluir as métricas
    if handler != "/metrics":
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            handler=handler,
            status=response.status_code,
        ).inc()
        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            handler=handler,
        ).observe(duration)

    return response


app.include_router(router)

# Expõe métricas Prometheus no /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)