# Tech Challenge Fase 4 — Previsão de Preços de Ações com LSTM

Projeto end-to-end de Deep Learning para previsão do preço de fechamento de ações utilizando redes neurais **LSTM (Long Short-Term Memory)**, com pipeline completa: coleta, treinamento, API REST, containerização, deploy e monitoramento.

---

## 📋 Índice

- [Arquitetura](#arquitetura)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Setup Local](#setup-local)
- [Treinamento do Modelo](#treinamento-do-modelo)
- [Uso da API](#uso-da-api)
- [Docker](#docker)
- [Monitoramento](#monitoramento)
- [Deploy em Nuvem](#deploy-em-nuvem)
- [Métricas do Modelo](#métricas-do-modelo)

---

## 🏗 Arquitetura

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Yahoo Finance  │─────▶│  Data Pipeline   │─────▶│  LSTM Training  │
│   (yfinance)    │      │ (Scaler+Windows) │      │  (TensorFlow)   │
└─────────────────┘      └──────────────────┘      └────────┬────────┘
                                                            │
                                                            ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Prometheus    │◀─────│   FastAPI App    │◀─────│  model.keras +  │
│   + Grafana     │      │   (/predict)     │      │   scaler.pkl    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                         │
        └────────────┬────────────┘
                     ▼
                 Docker
                Container
```

## 🛠 Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| **Coleta de dados** | yfinance |
| **Processamento** | NumPy, Pandas, scikit-learn |
| **Deep Learning** | TensorFlow / Keras |
| **API** | FastAPI + Uvicorn |
| **Validação** | Pydantic v2 |
| **Containerização** | Docker + Docker Compose |
| **Monitoramento** | Prometheus + Grafana |
| **Testes** | pytest |

---

## 📁 Estrutura do Projeto

```
tech-challenge-fase4/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
│
├── src/                          # Código-fonte principal
│   ├── __init__.py
│   ├── config.py                 # Configurações centralizadas
│   ├── data_loader.py            # Coleta via yfinance
│   ├── preprocessor.py           # Normalização e janelamento
│   ├── model.py                  # Arquitetura LSTM
│   ├── train.py                  # Pipeline de treinamento
│   ├── evaluate.py               # Métricas (MAE, RMSE, MAPE)
│   ├── predict.py                # Inferência
│   └── api/
│       ├── __init__.py
│       ├── main.py               # FastAPI app
│       ├── schemas.py            # Modelos Pydantic
│       ├── routes.py             # Endpoints
│       └── monitoring.py         # Métricas Prometheus
│
├── notebooks/
│   └── 01_exploracao_e_treino.ipynb   # Notebook completo
│
├── models/                       # Artefatos serializados
│   ├── lstm_model.keras
│   ├── scaler.pkl
│   └── metadata.json
│
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       └── dashboards/
│           └── api_dashboard.json
│
├── scripts/
│   ├── run_training.sh
│   └── run_api.sh
│
└── tests/
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_preprocessor.py
    └── test_api.py
```

---

## ⚙️ Setup Local

### Requisitos
- Python 3.10+
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone <seu-repo>
cd tech-challenge-fase4

# 2. Crie um virtualenv
python -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate       # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Copie variáveis de ambiente
cp .env.example .env
```

---

## 🧠 Treinamento do Modelo

```bash
# Treina o modelo com a configuração default (AAPL, 2018-2024)
python -m src.train

# Customizando
python -m src.train --symbol PETR4.SA --start 2019-01-01 --end 2024-12-31 --epochs 50
```

O script:
1. Baixa dados via yfinance
2. Aplica MinMaxScaler
3. Cria janelas deslizantes de 60 dias
4. Treina LSTM com Early Stopping
5. Avalia com MAE, RMSE e MAPE
6. Salva `models/lstm_model.keras` + `models/scaler.pkl` + `models/metadata.json`

---

## 🚀 Uso da API

### Iniciar localmente

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação Swagger disponível em: **http://localhost:8000/docs**

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Info básica |
| `GET` | `/health` | Health check |
| `GET` | `/model/info` | Metadados do modelo |
| `POST` | `/predict` | Previsão a partir de histórico fornecido |
| `POST` | `/predict/symbol` | Previsão buscando dados do yfinance |
| `GET` | `/metrics` | Métricas Prometheus |

### Exemplo: prever a partir do símbolo

```bash
curl -X POST "http://localhost:8000/predict/symbol" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "days_ahead": 5}'
```

Resposta:
```json
{
  "symbol": "AAPL",
  "last_close": 178.45,
  "predictions": [
    {"day": 1, "predicted_price": 179.12},
    {"day": 2, "predicted_price": 180.05},
    {"day": 3, "predicted_price": 180.88},
    {"day": 4, "predicted_price": 181.42},
    {"day": 5, "predicted_price": 181.95}
  ],
  "inference_time_ms": 87.3
}
```

### Exemplo: prever a partir de histórico

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"close_prices": [170.1, 171.5, 172.3, ...]}'
```
*(precisa enviar pelo menos 60 valores)*

---

## 🐳 Docker

### Build & Run da API

```bash
docker build -t lstm-stock-api .
docker run -p 8000:8000 lstm-stock-api
```

### Stack completa (API + Prometheus + Grafana)

```bash
docker-compose up -d
```

| Serviço | URL |
|---------|-----|
| API | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |

---

## 📊 Monitoramento

A API expõe métricas Prometheus em `/metrics`:

- `http_requests_total` — total de requisições por endpoint/status
- `http_request_duration_seconds` — latência (histograma)
- `predictions_total` — total de previsões realizadas
- `prediction_duration_seconds` — tempo de inferência
- `process_resident_memory_bytes` — uso de RAM
- `process_cpu_seconds_total` — uso de CPU

Dashboard Grafana pré-configurado em `monitoring/grafana/dashboards/`.

---

## ☁️ Deploy em Nuvem

### Render (gratuito, recomendado)

1. Crie um Web Service apontando para o repositório.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. Adicione as variáveis de ambiente do `.env`.

### Railway / Fly.io

Funciona via Dockerfile out-of-the-box.

---

## 📈 Métricas do Modelo

Resultados de referência (AAPL, 2018-01-01 a 2024-07-20):

| Métrica | Valor |
|---------|-------|
| MAE | ~4.90 USD |
| RMSE | ~6.48 USD |
| MAPE | ~2.60% |

*Os valores podem variar conforme empresa, período e seed.*

---

## 🎬 Vídeo Demonstrativo

[Adicionar link do vídeo aqui]

## 👤 Autor

Dione Braga — Pós-Tech Machine Learning Engineering — Fase 4
