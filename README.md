<div align="center">

# 📈 LSTM Stock Prediction API

### Previsão de Preços de Ações com Deep Learning

*PosTech · Machine Learning Engineering · FIAP · Tech Challenge Fase 4*

<br/>

[![API Status](https://img.shields.io/badge/API-Online-00FF88?style=for-the-badge&logo=fastapi&logoColor=black)](https://pos-tech-mlet-fase-4.onrender.com/health)
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-5B9DFF?style=for-the-badge&logo=streamlit&logoColor=white)](https://lstm-stock-dashboard.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-B794F4?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.17-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-A1A1AA?style=for-the-badge)](LICENSE)

<br/>

**[🖥️ Dashboard](https://lstm-stock-dashboard.onrender.com)** &nbsp;·&nbsp;
**[⚡ API](https://pos-tech-mlet-fase-4.onrender.com)** &nbsp;·&nbsp;
**[📖 Swagger](https://pos-tech-mlet-fase-4.onrender.com/docs)** &nbsp;·&nbsp;
**[🎬 Vídeo Demo](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)**

</div>

---

## 💡 Sobre

Sistema **end-to-end de Deep Learning** para previsão do preço de fechamento de ações. Um modelo LSTM treinado em dados históricos do Yahoo Finance, servido por uma API REST de alta performance com dashboard interativo de análise técnica.

> **Todos os dados são reais** — obtidos diretamente do Yahoo Finance via proxy integrado à API. Nenhum fallback sintético ou dado fabricado.

<br/>

<table>
<tr>
<td valign="top" width="50%">

### ⚡ API REST (FastAPI)
- Previsão D+1 a D+N com LSTM treinado
- Busca automática de dados via Yahoo Finance
- Monitoramento Prometheus nativo em `/metrics`
- Swagger UI interativo em `/docs`
- Health check detalhado em `/health`

</td>
<td valign="top" width="50%">

### 🖥️ Dashboard (Streamlit)
- Gráficos de candlestick com dados em tempo real
- Indicadores: RSI, MACD, Bollinger Bands, Fibonacci
- Simulação Monte Carlo de preços futuros
- Heatmap sazonal de retornos mensais
- Previsões LSTM integradas ao terminal

</td>
</tr>
</table>

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/dionebraga/Pos_Tech_MLET-Fase-4.git && cd tech-challenge-fase4

# Suba toda a stack (API + Dashboard + Prometheus + Grafana)
docker-compose up -d
```

| Serviço | URL Local | Produção |
|---------|-----------|----------|
| 🔌 API FastAPI | [localhost:8000](http://localhost:8000) | [pos-tech-mlet-fase-4.onrender.com](https://pos-tech-mlet-fase-4.onrender.com) |
| 📖 Swagger UI | [localhost:8000/docs](http://localhost:8000/docs) | [.../docs](https://pos-tech-mlet-fase-4.onrender.com/docs) |
| 🖥️ Dashboard | [localhost:8501](http://localhost:8501) | [lstm-stock-dashboard.onrender.com](https://lstm-stock-dashboard.onrender.com) |
| 📊 Prometheus | [localhost:9090](http://localhost:9090) | — local only |
| 📈 Grafana | [localhost:3000](http://localhost:3000) `admin/admin` | — local only |

> ⚠️ Render usa plano Free — a primeira requisição pode levar ~30s (cold start).

---

## 📋 Índice

- [Arquitetura](#-arquitetura)
- [Métricas do Modelo](#-métricas-do-modelo)
- [Uso da API](#-uso-da-api)
- [Stack Tecnológica](#-stack-tecnológica)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Setup Local](#-setup-local)
- [Treinamento do Modelo](#-treinamento-do-modelo)
- [Monitoramento](#-monitoramento)
- [Deploy em Nuvem](#-deploy-em-nuvem)
- [Vídeo Demonstrativo](#-vídeo-demonstrativo)

---

## 🏗 Arquitetura

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Yahoo Finance  │─────▶│  Data Pipeline   │─────▶│  LSTM Training  │
│   (yfinance)    │      │ (Scaler+Windows) │      │  (TensorFlow)   │
└─────────────────┘      └──────────────────┘      └────────┬────────┘
                                                             │ model.keras
                                                             ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Prometheus    │◀─────│   FastAPI App    │◀─────│  Predictor      │
│   + Grafana     │      │ /predict /health │      │  + MinMaxScaler │
└─────────────────┘      └────────┬─────────┘      └─────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │   Streamlit Dashboard    │
                   │   (Trading Terminal)     │
                   └──────────────────────────┘
```

### Fluxo de dados

| Etapa | Descrição |
|-------|-----------|
| 1. **Coleta** | yfinance busca OHLCV histórico do Yahoo Finance |
| 2. **Pré-processamento** | MinMaxScaler + janelas deslizantes de 60 dias |
| 3. **Treinamento** | LSTM 64+64 com Dropout e Early Stopping |
| 4. **Inferência** | API recebe preços e devolve predições D+1 a D+N |
| 5. **Visualização** | Dashboard consome a API e renderiza análises em tempo real |

---

## 📈 Métricas do Modelo

> Treinado em **AAPL** (Jan/2018 – Jul/2024) · LSTM 64+64 · Janela 60 dias · Dropout 0.2

<div align="center">

| Métrica | Valor | |
|---------|-------|-|
| **MAE** | ~4.90 USD | Erro absoluto médio |
| **RMSE** | ~6.48 USD | Raiz do erro quadrático médio |
| **MAPE** | ~2.60% | Erro percentual absoluto médio |
| **Acurácia** | ~97.4% | `100 − MAPE` |

</div>

Métricas em tempo real: [`/model/info`](https://pos-tech-mlet-fase-4.onrender.com/model/info)

---

## 🚀 Uso da API

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | [`/`](https://pos-tech-mlet-fase-4.onrender.com/) | Dashboard da API |
| `GET` | [`/health`](https://pos-tech-mlet-fase-4.onrender.com/health) | Status do sistema e modelo |
| `GET` | [`/model/info`](https://pos-tech-mlet-fase-4.onrender.com/model/info) | Arquitetura, métricas e metadados |
| `POST` | `/predict` | Previsão a partir de histórico fornecido |
| `POST` | `/predict/symbol` | Previsão buscando dados do Yahoo Finance automaticamente |
| `GET` | [`/metrics`](https://pos-tech-mlet-fase-4.onrender.com/metrics) | Métricas Prometheus |
| `GET` | [`/docs`](https://pos-tech-mlet-fase-4.onrender.com/docs) | Swagger UI interativo |

### Previsão por símbolo

```bash
curl -X POST "https://pos-tech-mlet-fase-4.onrender.com/predict/symbol" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "days_ahead": 5}'
```

```json
{
  "symbol": "AAPL",
  "last_close": 178.45,
  "last_close_date": "2024-07-19",
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

### Previsão por histórico customizado

```bash
curl -X POST "https://pos-tech-mlet-fase-4.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{"close_prices": [170.1, 171.5, 172.3, ...], "days_ahead": 3}'
```

> Mínimo de **60 valores** de fechamento em ordem cronológica crescente.

---

## 🛠 Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Coleta de dados | yfinance | ≥ 1.x |
| Processamento | NumPy · Pandas · scikit-learn | latest |
| Deep Learning | TensorFlow / Keras | 2.17 / 3.x |
| API | FastAPI + Uvicorn | latest |
| Validação | Pydantic v2 | v2 |
| Dashboard | Streamlit | latest |
| Visualizações | Plotly | latest |
| Containerização | Docker + Docker Compose | — |
| Monitoramento | Prometheus + Grafana | — |
| Deploy | Render (Free Tier) | — |
| Testes | pytest | latest |

---

## 📁 Estrutura do Projeto

```
tech-challenge-fase4/
├── 📄 README.md
├── 🐳 Dockerfile                        # Container da API
├── 🐳 Dockerfile.dashboard              # Container do Dashboard
├── 🐳 docker-compose.yml
├── ☁️  render.yaml                       # Blueprint de deploy (Render)
├── 📦 requirements.txt
├── 📦 requirements-api.txt
├── 🖥️  dashboard.py                      # Streamlit — Trading Terminal
│
├── src/
│   ├── config.py                        # Configurações centralizadas
│   ├── data_loader.py                   # Coleta via yfinance
│   ├── preprocessor.py                  # Normalização e janelamento
│   ├── model.py                         # Arquitetura LSTM
│   ├── train.py                         # Pipeline de treinamento
│   ├── evaluate.py                      # Métricas (MAE, RMSE, MAPE)
│   ├── predict.py                       # Inferência
│   └── api/
│       ├── main.py                      # FastAPI app
│       ├── schemas.py                   # Modelos Pydantic
│       ├── routes.py                    # Endpoints + proxy Yahoo Finance
│       └── monitoring.py               # Métricas Prometheus
│
├── notebooks/
│   └── 01_exploracao_e_treino.ipynb     # EDA + treinamento completo
│
├── models/
│   ├── lstm_model.keras                 # Modelo treinado
│   ├── scaler.pkl                       # MinMaxScaler serializado
│   └── metadata.json                    # Métricas e hiperparâmetros
│
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/dashboards/
│       └── api_dashboard.json           # Dashboard pré-configurado
│
└── tests/
    ├── test_data_loader.py
    ├── test_preprocessor.py
    └── test_api.py
```

---

## ⚙️ Setup Local

### Pré-requisitos

- Python 3.10+
- Docker (para stack completa)

### Apenas a API (sem Docker)

```bash
# 1. Clone e entre no diretório
git clone https://github.com/dionebraga/Pos_Tech_MLET-Fase-4.git
cd tech-challenge-fase4

# 2. Crie o virtualenv
python -m venv venv
source venv/bin/activate        # Linux / Mac
# venv\Scripts\activate         # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Suba a API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs
```

### Dashboard local

```bash
# Aponte para a API
export API_URL=http://localhost:8000        # Linux/Mac
# $env:API_URL="http://localhost:8000"      # Windows PowerShell

streamlit run dashboard.py
# → http://localhost:8501
```

---

## 🧠 Treinamento do Modelo

```bash
# Treino padrão (AAPL, 2018–2024)
python -m src.train

# Customizando símbolo e período
python -m src.train --symbol PETR4.SA --start 2019-01-01 --end 2024-12-31 --epochs 50
```

### Arquitetura LSTM

```
Input (60, 1)
    ↓
LSTM(64, return_sequences=True)  →  Dropout(0.2)
    ↓
LSTM(64, return_sequences=False) →  Dropout(0.2)
    ↓
Dense(1)  →  preço D+1 (USD)
```

### Pipeline de treinamento

1. Baixa dados OHLCV históricos via yfinance
2. Aplica **MinMaxScaler** nos preços de fechamento
3. Cria **janelas deslizantes de 60 dias** (input → D+1 output)
4. Treina com **Early Stopping** (`patience=10`)
5. Avalia MAE, RMSE e MAPE no conjunto de teste
6. Serializa `models/lstm_model.keras` + `models/scaler.pkl` + `models/metadata.json`

---

## 🐳 Docker

```bash
# Apenas a API
docker build -t lstm-stock-api .
docker run -p 8000:8000 lstm-stock-api

# Apenas o Dashboard
docker build -f Dockerfile.dashboard -t lstm-stock-dashboard .
docker run -p 8501:8501 -e API_URL=http://host.docker.internal:8000 lstm-stock-dashboard

# Stack completa
docker-compose up -d
```

---

## 📊 Monitoramento

A API expõe métricas Prometheus em [`/metrics`](https://pos-tech-mlet-fase-4.onrender.com/metrics):

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `http_requests_total` | Counter | Requisições por endpoint/status |
| `http_request_duration_seconds` | Histogram | Latência HTTP |
| `predictions_total` | Counter | Total de previsões |
| `prediction_duration_seconds` | Histogram | Tempo de inferência do modelo |
| `last_prediction_value` | Gauge | Último preço previsto por símbolo |
| `model_loaded` | Gauge | 1 = modelo ativo, 0 = offline |
| `process_resident_memory_bytes` | Gauge | Uso de RAM |

Dashboard Grafana pré-configurado: `monitoring/grafana/dashboards/api_dashboard.json`

---

## ☁️ Deploy em Nuvem

O projeto usa **Render** com dois serviços definidos em `render.yaml`:

| Serviço | Nome no Render | URL de Produção |
|---------|----------------|-----------------|
| API FastAPI | `pos-tech-mlet-fase-4` | [pos-tech-mlet-fase-4.onrender.com](https://pos-tech-mlet-fase-4.onrender.com) |
| Dashboard Streamlit | `lstm-stock-dashboard` | [lstm-stock-dashboard.onrender.com](https://lstm-stock-dashboard.onrender.com) |

### Passos para deploy

1. Faça fork do repositório
2. Conecte ao [Render](https://render.com) e crie um **Blueprint** via `render.yaml`
3. Configure a variável `API_URL` no serviço do Dashboard
4. Render detecta automaticamente os Dockerfiles e inicia o deploy

---

## 🎬 Vídeo Demonstrativo

[![Assistir vídeo](https://img.shields.io/badge/Google%20Drive-Assistir%20Vídeo-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)

O vídeo cobre:
- Visão geral da arquitetura do projeto
- Demonstração do dashboard interativo em tempo real
- Funcionamento dos endpoints da API via Swagger
- Resultados do modelo LSTM e métricas de desempenho

---

## 👤 Autor

**Dione Braga Ferreira**
Pós-Graduação em Machine Learning Engineering — FIAP
Tech Challenge Fase 4 · 2024

---

<div align="center">

**[📦 Repositório](https://github.com/dionebraga/Pos_Tech_MLET-Fase-4)** &nbsp;·&nbsp;
**[🖥️ Dashboard](https://lstm-stock-dashboard.onrender.com)** &nbsp;·&nbsp;
**[⚡ API](https://pos-tech-mlet-fase-4.onrender.com)** &nbsp;·&nbsp;
**[📖 Swagger](https://pos-tech-mlet-fase-4.onrender.com/docs)** &nbsp;·&nbsp;
**[🎬 Vídeo](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)**

<br/>

*Feito com ❤️ + TensorFlow + FastAPI*

</div>
