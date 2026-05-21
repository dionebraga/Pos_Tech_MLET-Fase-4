---
title: LSTM Stock Prediction API
emoji: 📈
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
license: mit
---

<div align="center">

# Tech Challenge Fase 4
## Previsão de Preços de Ações com LSTM

**PosTech · Machine Learning Engineering · FIAP**

[![API Status](https://img.shields.io/badge/API-Online-00FF88?style=for-the-badge&logo=fastapi)](https://lstm-stock-api.onrender.com/health)
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-5B9DFF?style=for-the-badge&logo=streamlit)](https://lstm-stock-dashboard.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-B794F4?style=for-the-badge&logo=python)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-A1A1AA?style=for-the-badge)](LICENSE)

</div>

---

## 🌐 Links de Acesso Rápido

| Recurso | URL |
|---------|-----|
| 🖥️ **Dashboard Interativo** | [lstm-stock-dashboard.onrender.com](https://lstm-stock-dashboard.onrender.com) |
| ⚡ **API REST** | [lstm-stock-api.onrender.com](https://lstm-stock-api.onrender.com) |
| 📖 **Swagger UI** | [lstm-stock-api.onrender.com/docs](https://lstm-stock-api.onrender.com/docs) |
| 🔍 **Health Check** | [lstm-stock-api.onrender.com/health](https://lstm-stock-api.onrender.com/health) |
| 🧠 **Model Info** | [lstm-stock-api.onrender.com/model/info](https://lstm-stock-api.onrender.com/model/info) |
| 📦 **Repositório GitHub** | [github.com/dionebraga/Pos_Tech_MLET-Fase-4](https://github.com/dionebraga/Pos_Tech_MLET-Fase-4) |
| 🎬 **Vídeo Demonstrativo** | [Google Drive — Pasta do Projeto](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing) |

> ⚠️ O Render utiliza plano Free. Se o serviço estiver dormindo, a primeira requisição pode levar ~30s para acordar.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Stack Tecnológica](#-stack-tecnológica)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Métricas do Modelo](#-métricas-do-modelo)
- [Uso da API](#-uso-da-api)
- [Setup Local](#-setup-local)
- [Treinamento do Modelo](#-treinamento-do-modelo)
- [Docker](#-docker)
- [Monitoramento](#-monitoramento)
- [Deploy em Nuvem](#-deploy-em-nuvem)
- [Vídeo Demonstrativo](#-vídeo-demonstrativo)
- [Autor](#-autor)

---

## 💡 Sobre o Projeto

Projeto end-to-end de Deep Learning para **previsão do preço de fechamento de ações** utilizando redes neurais LSTM (Long Short-Term Memory).

O sistema é composto por dois serviços independentes em produção:

- **API REST** (FastAPI) — recebe um símbolo ou histórico de preços e retorna previsões do modelo LSTM treinado, com métricas de inferência e monitoramento Prometheus.
- **Dashboard Interativo** (Streamlit) — terminal de trading com dados reais em tempo real, gráficos de candlestick, análise técnica (RSI, MACD, Bollinger Bands, Fibonacci), simulação Monte Carlo, heatmap sazonal e previsões LSTM integradas.

**Todos os dados exibidos são reais** — obtidos diretamente do Yahoo Finance via proxy da API. Não há fallback sintético nem valores fabricados.

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
│   + Grafana     │      │ /predict /health │      │   scaler.pkl    │
└─────────────────┘      └────────┬─────────┘      └─────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │  Streamlit Dashboard     │
                   │  (Trading Terminal)      │
                   │  lstm-stock-dashboard    │
                   │  .onrender.com           │
                   └──────────────────────────┘
```

### Fluxo de dados

1. **Coleta** — yfinance busca dados históricos OHLCV do Yahoo Finance
2. **Pré-processamento** — MinMaxScaler + janelas deslizantes de 60 dias
3. **Treinamento** — LSTM 64+64 unidades com Dropout e Early Stopping
4. **Inferência** — API recebe preços e devolve predições D+1 a D+N
5. **Visualização** — Dashboard consome a API e renderiza análises em tempo real

---

## 🛠 Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Coleta de dados** | yfinance + curl_cffi | ≥ 0.2.50 |
| **Processamento** | NumPy, Pandas, scikit-learn | latest |
| **Deep Learning** | TensorFlow / Keras | 2.x |
| **API** | FastAPI + Uvicorn | latest |
| **Validação** | Pydantic v2 | v2 |
| **Dashboard** | Streamlit | latest |
| **Visualizações** | Plotly | latest |
| **Containerização** | Docker + Docker Compose | — |
| **Monitoramento** | Prometheus + Grafana | — |
| **Deploy** | Render (Free Tier) | — |
| **Armazenamento do modelo** | Hugging Face Hub (artefatos: `.keras`, `.pkl`) | — |
| **Testes** | pytest | latest |

---

## 📁 Estrutura do Projeto

```
tech-challenge-fase4/
├── README.md
├── Dockerfile                        # Container da API
├── Dockerfile.dashboard              # Container do Dashboard
├── docker-compose.yml
├── render.yaml                       # Configuração de deploy (Render)
├── requirements.txt                  # Dependências completas
├── requirements-api.txt              # Dependências mínimas para API
├── dashboard.py                      # Streamlit — Trading Terminal
│
├── src/                              # Código-fonte principal
│   ├── __init__.py
│   ├── config.py                     # Configurações centralizadas
│   ├── data_loader.py                # Coleta via yfinance
│   ├── preprocessor.py               # Normalização e janelamento
│   ├── model.py                      # Arquitetura LSTM
│   ├── train.py                      # Pipeline de treinamento
│   ├── evaluate.py                   # Métricas (MAE, RMSE, MAPE)
│   ├── predict.py                    # Inferência
│   └── api/
│       ├── main.py                   # FastAPI app
│       ├── schemas.py                # Modelos Pydantic
│       ├── routes.py                 # Endpoints + proxy Yahoo Finance
│       └── monitoring.py             # Métricas Prometheus
│
├── notebooks/
│   └── 01_exploracao_e_treino.ipynb  # Notebook completo EDA + treino
│
├── models/                           # Artefatos serializados
│   ├── lstm_model.keras              # Modelo treinado (baixado do HF Hub)
│   ├── scaler.pkl                    # MinMaxScaler serializado
│   └── metadata.json                 # Métricas e hiperparâmetros
│
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/dashboards/
│       └── api_dashboard.json
│
├── scripts/
│   ├── download_model.py             # Baixa modelo do HF Hub
│   ├── run_training.sh
│   └── run_api.sh
│
└── tests/
    ├── test_data_loader.py
    ├── test_preprocessor.py
    └── test_api.py
```

---

## 📈 Métricas do Modelo

Modelo treinado em **AAPL** (2018-01-01 a 2024-07-20) — LSTM 64+64 · Janela 60 dias · Dropout 0.2

| Métrica | Valor | Descrição |
|---------|-------|-----------|
| **MAE** | ~4.90 USD | Erro absoluto médio |
| **RMSE** | ~6.48 USD | Raiz do erro quadrático médio |
| **MAPE** | ~2.60% | Erro percentual absoluto médio |
| **Acurácia** | ~97.4% | 100 − MAPE |

> Métricas em tempo real disponíveis em [/model/info](https://lstm-stock-api.onrender.com/model/info)

---

## 🚀 Uso da API

### Endpoints disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | [`/`](https://lstm-stock-api.onrender.com/) | Dashboard da API |
| `GET` | [`/health`](https://lstm-stock-api.onrender.com/health) | Status do sistema e modelo |
| `GET` | [`/model/info`](https://lstm-stock-api.onrender.com/model/info) | Arquitetura, métricas e metadados |
| `POST` | `/predict` | Previsão a partir de histórico fornecido |
| `POST` | `/predict/symbol` | Previsão buscando dados do yfinance automaticamente |
| `GET` | [`/metrics`](https://lstm-stock-api.onrender.com/metrics) | Métricas Prometheus |
| `GET` | [`/docs`](https://lstm-stock-api.onrender.com/docs) | Swagger UI interativo |

### Previsão por símbolo (mais simples)

```bash
curl -X POST "https://lstm-stock-api.onrender.com/predict/symbol" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "days_ahead": 5}'
```

Resposta:
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
curl -X POST "https://lstm-stock-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{"close_prices": [170.1, 171.5, 172.3, ...], "days_ahead": 3}'
```

> Mínimo de **60 valores** de fechamento em ordem cronológica crescente.

### Health check

```bash
curl https://lstm-stock-api.onrender.com/health?format=json
```

---

## ⚙️ Setup Local

### Requisitos

- Python 3.10+
- pip
- Docker (opcional)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/dionebraga/Pos_Tech_MLET-Fase-4.git
cd tech-challenge-fase4

# 2. Crie e ative um virtualenv
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Instale dependências
pip install -r requirements.txt
```

### Rodando a API localmente

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
# Acesse: http://localhost:8000/docs
```

### Rodando o Dashboard localmente

```bash
# Configure a URL da API
export API_URL=http://localhost:8000   # Linux/Mac
# $env:API_URL="http://localhost:8000" # Windows PowerShell

streamlit run dashboard.py
# Acesse: http://localhost:8501
```

---

## 🧠 Treinamento do Modelo

```bash
# Treino padrão (AAPL, 2018-2024)
python -m src.train

# Customizando símbolo e período
python -m src.train --symbol PETR4.SA --start 2019-01-01 --end 2024-12-31 --epochs 50
```

O pipeline de treinamento:
1. Baixa dados históricos via yfinance (OHLCV)
2. Aplica **MinMaxScaler** nos preços de fechamento
3. Cria **janelas deslizantes de 60 dias** (input → D+1 output)
4. Treina LSTM 64+64 com **Early Stopping** (patience=10)
5. Avalia com MAE, RMSE e MAPE no conjunto de teste
6. Serializa `models/lstm_model.keras` + `models/scaler.pkl` + `models/metadata.json`

### Arquitetura LSTM

```
Input (60, 1)
    ↓
LSTM(64, return_sequences=True)
    ↓
Dropout(0.2)
    ↓
LSTM(64, return_sequences=False)
    ↓
Dropout(0.2)
    ↓
Dense(1) → preço D+1
```

---

## 🐳 Docker

### API apenas

```bash
docker build -t lstm-stock-api .
docker run -p 8000:8000 lstm-stock-api
```

### Dashboard apenas

```bash
docker build -f Dockerfile.dashboard -t lstm-stock-dashboard .
docker run -p 8501:8501 -e API_URL=http://host.docker.internal:8000 lstm-stock-dashboard
```

### Stack completa (API + Dashboard + Prometheus + Grafana)

```bash
docker-compose up -d
```

| Serviço | URL Local |
|---------|-----------|
| API | http://localhost:8000 |
| Dashboard | http://localhost:8501 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |

---

## 📊 Monitoramento

A API expõe métricas Prometheus em [`/metrics`](https://lstm-stock-api.onrender.com/metrics):

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `http_requests_total` | Counter | Total de requisições por endpoint/status |
| `http_request_duration_seconds` | Histogram | Latência das requisições |
| `predictions_total` | Counter | Total de previsões realizadas |
| `prediction_duration_seconds` | Histogram | Tempo de inferência do modelo |
| `last_prediction_value` | Gauge | Último preço previsto por símbolo |
| `process_resident_memory_bytes` | Gauge | Uso de RAM |
| `process_cpu_seconds_total` | Counter | Uso de CPU |

Dashboard Grafana pré-configurado em `monitoring/grafana/dashboards/api_dashboard.json`.

---

## ☁️ Deploy em Nuvem

O projeto utiliza **Render** com dois serviços independentes definidos em `render.yaml`:

| Serviço | Nome | URL de Produção |
|---------|------|-----------------|
| API FastAPI | `lstm-stock-api` | [lstm-stock-api.onrender.com](https://lstm-stock-api.onrender.com) |
| Dashboard Streamlit | `lstm-stock-dashboard` | [lstm-stock-dashboard.onrender.com](https://lstm-stock-dashboard.onrender.com) |

### Como fazer deploy

1. Faça fork / conecte o repositório ao [Render](https://render.com)
2. Crie um **Blueprint** apontando para o `render.yaml`
3. Render detecta automaticamente os dois Dockerfiles
4. Configure a variável `API_URL` no serviço do Dashboard
5. Health Check Path configurado: `/health` (API) e `/_stcore/health` (Dashboard)

---

## 🎬 Vídeo Demonstrativo

[![Assistir vídeo](https://img.shields.io/badge/Google%20Drive-Assistir%20Vídeo-4285F4?style=for-the-badge&logo=googledrive)](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)

O vídeo apresenta:
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

📦 [Repositório GitHub](https://github.com/dionebraga/Pos_Tech_MLET-Fase-4) &nbsp;·&nbsp;
🖥️ [Dashboard](https://lstm-stock-dashboard.onrender.com) &nbsp;·&nbsp;
⚡ [API](https://lstm-stock-api.onrender.com) &nbsp;·&nbsp;
📖 [Swagger](https://lstm-stock-api.onrender.com/docs) &nbsp;·&nbsp;
🎬 [Vídeo](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)

</div>
