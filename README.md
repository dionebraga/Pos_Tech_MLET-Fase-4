<div align="center">

<br/>

```
██╗     ███████╗████████╗███╗   ███╗    ███████╗████████╗ ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝╚══██╔══╝████╗ ████║    ██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝
██║     ███████╗   ██║   ██╔████╔██║    ███████╗   ██║   ██║   ██║██║     █████╔╝
██║     ╚════██║   ██║   ██║╚██╔╝██║    ╚════██║   ██║   ██║   ██║██║     ██╔═██╗
███████╗███████║   ██║   ██║ ╚═╝ ██║    ███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝   ╚═╝   ╚═╝     ╚═╝    ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝
```

**Previsão de Preços de Ações com Deep Learning · End-to-End**

*PosTech · Machine Learning Engineering · FIAP · Tech Challenge Fase 4*

<br/>

[![API](https://img.shields.io/badge/API-●%20Online-00FF88?style=for-the-badge&logo=fastapi&logoColor=black)](https://pos-tech-mlet-fase-4.onrender.com/health)
[![Dashboard](https://img.shields.io/badge/Dashboard-●%20Live-5B9DFF?style=for-the-badge&logo=streamlit&logoColor=white)](https://lstm-stock-dashboard.onrender.com)
[![Swagger](https://img.shields.io/badge/Swagger-●%20Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://pos-tech-mlet-fase-4.onrender.com/docs)
[![Video](https://img.shields.io/badge/Vídeo-●%20Demo-FF0000?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)

<br/>

[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow_2.17-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Keras](https://img.shields.io/badge/Keras_3.x-D00000?style=flat-square&logo=keras&logoColor=white)](https://keras.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit_1.41-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![License](https://img.shields.io/badge/License-MIT-A1A1AA?style=flat-square)](LICENSE)

<br/>

| [🖥️ **Dashboard**](https://lstm-stock-dashboard.onrender.com) | [⚡ **API REST**](https://pos-tech-mlet-fase-4.onrender.com) | [📖 **Swagger UI**](https://pos-tech-mlet-fase-4.onrender.com/docs) | [🎬 **Vídeo Demo**](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing) |
|:---:|:---:|:---:|:---:|

</div>

<br/>

<div align="center">

| | |
|:---:|:---|
| 📡 | **100% dados reais** — Yahoo Finance · AAPL · Jan 2018 – Abr 2026 · 2 093 pregões |
| 🧠 | LSTM 2×64 · Dropout 0.2 · 29 épocas · MAPE **2.48 %** · Acurácia **97.52 %** |
| ☁️ | API + Dashboard + Prometheus + Grafana em produção no **Render** |
| ⚡ | Inferência ~87 ms · Pydantic v2 · Health check · Swagger UI · Docker Compose |

</div>

<br/>

<div align="center">

<!--  M É T R I C A S  -->

<table>
<tr>
<td align="center" width="160">
  <img src="https://img.shields.io/badge/MAE-5.78_USD-00FF88?style=for-the-badge" /><br/>
  <sub><b>Erro Absoluto Médio</b></sub>
</td>
<td align="center" width="160">
  <img src="https://img.shields.io/badge/RMSE-7.46_USD-5B9DFF?style=for-the-badge" /><br/>
  <sub><b>Raiz do Erro Quadrático</b></sub>
</td>
<td align="center" width="160">
  <img src="https://img.shields.io/badge/MAPE-2.48%25-B794F4?style=for-the-badge" /><br/>
  <sub><b>Erro Percentual Médio</b></sub>
</td>
<td align="center" width="160">
  <img src="https://img.shields.io/badge/Acurácia-97.52%25-FF6F00?style=for-the-badge" /><br/>
  <sub><b>100 − MAPE</b></sub>
</td>
<td align="center" width="160">
  <img src="https://img.shields.io/badge/Inferência-~87ms-FFD700?style=for-the-badge" /><br/>
  <sub><b>Latência da API</b></sub>
</td>
</tr>
</table>

*AAPL · Jan 2018 – Abr 2026 · LSTM 64+64 · Janela 60 dias · 29 épocas (EarlyStopping)*

</div>

---

## ✨ Destaques do Projeto

<br/>

<table>
<tr>

<td align="center" valign="top" width="25%">
<br/>
<b>🧠 Deep Learning Real</b>
<br/><br/>
LSTM 2×64 · Split 80/20 temporal sem <i>data leakage</i> · EarlyStopping · ReduceLROnPlateau · ModelCheckpoint · MAPE <b>2.48%</b>
<br/><br/>
<sub><code>TensorFlow 2.17</code> · <code>Keras 3.x</code> · <code>scikit-learn</code></sub>
<br/>
</td>

<td align="center" valign="top" width="25%">
<br/>
<b>🚀 Pronto para Produção</b>
<br/><br/>
Docker Compose · deploy automático no Render · lifespan handler · Pydantic v2 · logging estruturado · retry em cold start · <b>0 downtime</b>
<br/><br/>
<sub><code>FastAPI</code> · <code>Uvicorn</code> · <code>Docker</code> · <code>Render</code></sub>
<br/>
</td>

<td align="center" valign="top" width="25%">
<br/>
<b>📊 Observabilidade Total</b>
<br/><br/>
Middleware HTTP · RPS · latência p50/p95/p99 · inferência LSTM · RAM · CPU — <b>8 painéis</b> Grafana auto-provisioned
<br/><br/>
<sub><code>Prometheus</code> · <code>Grafana</code> · <code>prometheus-client</code></sub>
<br/>
</td>

<td align="center" valign="top" width="25%">
<br/>
<b>🖥️ Terminal de Trading</b>
<br/><br/>
<b>7 módulos</b>: Candlestick · RSI 14 · MACD · Bollinger Bands · Fibonacci · Monte Carlo · Forecast LSTM D+1 → D+5
<br/><br/>
<sub><code>Streamlit</code> · <code>Plotly</code> · <code>yfinance ≥1.x</code></sub>
<br/>
</td>

</tr>
</table>

---

## 🚀 Quick Start

<table>
<tr>
<td align="center" valign="top" width="30%">
<br/>
<b>❶ Clone o repositório</b>
<br/><br/>
<code>git clone https://github.com/dionebraga/Pos_Tech_MLET-Fase-4.git</code><br/>
<code>cd tech-challenge-fase4</code>
<br/><br/>
<sub>Pré-requisito: Git · Docker Desktop</sub>
<br/>
</td>
<td align="center" valign="middle" width="5%"><br/><b>→</b></td>
<td align="center" valign="top" width="34%">
<br/>
<b>❷ Suba a stack completa</b>
<br/><br/>
<code>docker-compose up -d</code>
<br/><br/>
<sub>Sobe 4 containers em paralelo:</sub><br/>
<sub><code>api</code> · <code>dashboard</code> · <code>prometheus</code> · <code>grafana</code></sub>
<br/>
</td>
<td align="center" valign="middle" width="5%"><br/><b>→</b></td>
<td align="center" valign="top" width="26%">
<br/>
<b>❸ Tudo no ar!</b>
<br/><br/>
<a href="http://localhost:8000/docs"><code>:8000/docs</code></a> — Swagger<br/>
<a href="http://localhost:8501"><code>:8501</code></a> — Dashboard<br/>
<a href="http://localhost:9090"><code>:9090</code></a> — Prometheus<br/>
<a href="http://localhost:3000"><code>:3000</code></a> — Grafana
<br/><br/>
<sub><i>Cold start Render: ~30 s</i></sub>
<br/>
</td>
</tr>
</table>

```bash
git clone https://github.com/dionebraga/Pos_Tech_MLET-Fase-4.git
cd tech-challenge-fase4
docker-compose up -d
```

<br/>

<table>
<tr>
<th align="center">Serviço</th>
<th align="center">🖥️ Local</th>
<th align="center">☁️ Produção</th>
</tr>
<tr>
<td>⚡ <b>API FastAPI</b></td>
<td><a href="http://localhost:8000">localhost:8000</a></td>
<td><a href="https://pos-tech-mlet-fase-4.onrender.com">pos-tech-mlet-fase-4.onrender.com</a></td>
</tr>
<tr>
<td>📖 <b>Swagger UI</b></td>
<td><a href="http://localhost:8000/docs">localhost:8000/docs</a></td>
<td><a href="https://pos-tech-mlet-fase-4.onrender.com/docs">.../docs</a></td>
</tr>
<tr>
<td>🖥️ <b>Dashboard</b></td>
<td><a href="http://localhost:8501">localhost:8501</a></td>
<td><a href="https://lstm-stock-dashboard.onrender.com">lstm-stock-dashboard.onrender.com</a></td>
</tr>
<tr>
<td>📊 <b>Prometheus</b></td>
<td><a href="http://localhost:9090">localhost:9090</a></td>
<td><em>local only</em></td>
</tr>
<tr>
<td>📈 <b>Grafana</b></td>
<td><a href="http://localhost:3000">localhost:3000</a> · <code>admin / admin</code></td>
<td><em>local only</em></td>
</tr>
</table>

> ⚠️ **Render Free Tier** — primeira requisição pode levar ~30 s (cold start do container).

---

## 🗺️ Índice

```mermaid
mindmap
  root((📈 LSTM<br/>Stock))
    Projeto
      ✨ Destaques
      🏗️ Arquitetura
      🔄 Fluxo de Requisição
      📸 Demonstração
    Modelo
      📈 Métricas
      🧠 Treinamento
      Arquitetura LSTM
      Células LSTM
      Janela 60d
      Geração D+5
      Regularização
    Desenvolvimento
      ⚡ Uso da API
      ⚙️ Setup Local
      🧪 Testes
      🐳 Docker
    Operações
      🛠️ Stack
      📁 Estrutura
      📊 Monitoramento
      ☁️ Deploy
```

---

## 🏗 Arquitetura

```mermaid
flowchart TD
    subgraph DADOS["  📦 1 · Dados  "]
        YF["☁️ Yahoo Finance\nyfinance ≥ 1.x · AAPL OHLCV\n2 093 linhas · 2018-01-02 → 2026-04-30"]
        CSV["💾 AAPL_2018_2026.csv\ncache local · fallback offline"]
    end

    subgraph TREINO["  🧠 2 · Treino  "]
        DP["⚙️ Pré-Processamento\nMinMaxScaler [0,1] · fit só no treino\nSliding Window 60d · Split 80/20 temporal"]
        ML["🔵 LSTM  2 × 64  +  Dropout 0.2\nTensorFlow 2.17 · Keras 3.x · Adam\nMSE loss · EarlyStopping patience=10\n29 épocas · melhor checkpoint época 19"]
        ART["💾 Artefatos Serializados\nlstm_model.keras · scaler.pkl\nmetadata.json  MAE 5.78 · MAPE 2.48%"]
    end

    subgraph SERVE["  ⚡ 3 · Serviço  "]
        API["🚀 FastAPI · Uvicorn\nPOST /predict  ·  /predict/symbol\nGET  /health  ·  /model/info\nGET  /metrics  ·  /docs  ·  /api/chart/{symbol}"]
    end

    subgraph OBS["  📊 4 · Observabilidade  "]
        PROM["📊 Prometheus\nscrape /metrics · intervalo 15s\ntime-series DB local"]
        GRAF["📈 Grafana\n8 painéis · auto-provisioned\nRPS · Latência · RAM · CPU · Inferência"]
    end

    subgraph UI["  🖥️ 5 · Interface  "]
        DASH["🖥️ Streamlit Dashboard\nCandlestick · RSI · MACD · Bollinger\nMonte Carlo · Fibonacci\nForecast LSTM D+1 → D+5"]
    end

    YF      -->|"OHLCV histórico"| DP
    CSV     -.->|"fallback offline"| DP
    DP      -->|"X (n,60,1) · y (n,1)"| ML
    ML      -->|"MAE 5.78 · RMSE 7.46 · MAPE 2.48%"| ART
    ART     -->|"model.load() no startup"| API
    API     -->|"HTTP middleware · scrape 15s"| PROM
    PROM    -->|"datasource PromQL"| GRAF
    API     -->|"REST JSON · ~87 ms"| DASH

    style YF   fill:#0d1117,color:#58a6ff,stroke:#388bfd,stroke-width:2px
    style CSV  fill:#0d1117,color:#8b949e,stroke:#30363d,stroke-width:1px,stroke-dasharray:4
    style DP   fill:#0d1117,color:#79c0ff,stroke:#388bfd,stroke-width:2px
    style ML   fill:#0d1117,color:#ffa657,stroke:#e3b341,stroke-width:3px
    style ART  fill:#0d1117,color:#d2a8ff,stroke:#a371f7,stroke-width:2px
    style API  fill:#0d1117,color:#56d364,stroke:#3fb950,stroke-width:3px
    style PROM fill:#0d1117,color:#ff7b72,stroke:#f85149,stroke-width:2px
    style GRAF fill:#0d1117,color:#ffa657,stroke:#e3b341,stroke-width:2px
    style DASH fill:#0d1117,color:#79c0ff,stroke:#388bfd,stroke-width:2px
```

---

## 🔄 Fluxo de Requisição

```mermaid
sequenceDiagram
    autonumber
    actor U as 👤 Cliente
    participant A as ⚡ FastAPI
    participant Y as ☁️ Yahoo Finance
    participant M as 🧠 LSTM Model
    participant P as 📊 Prometheus

    U  ->>  A : POST /predict/symbol<br/>{ "symbol": "AAPL", "days_ahead": 5 }
    Note over A: middleware: start = perf_counter()

    A  ->>  Y : yfinance.Ticker("AAPL").history(last 120d)
    Y -->>  A : DataFrame OHLCV · 60+ pregões
    Note over A: closes.iloc[-60:] → janela_60d<br/>scaler.transform(janela_60d) → [0, 1]

    rect rgb(30, 41, 59)
        Note over A, M: Loop auto-regressivo — 5 iterações
        loop D+1 até D+5
            A  ->>  M : model.predict(shape=(1,60,1))
            M -->>  A : escalar normalizado ∈ [0, 1]
            Note over A: inverse_transform → preço USD<br/>desliza janela: descarta t-59, injeta D+n
        end
    end

    A  ->>  P : http_requests_total{handler="/predict/symbol"}.inc()<br/>prediction_duration_seconds.observe(Δt)
    Note over A: middleware: latência total registrada

    A -->>  U : 200 OK · application/json<br/>{ "predictions": [...5 dias...], "inference_time_ms": 87.3 }
```

---

## 📸 Demonstração

<table>
<tr>

<td valign="top" width="33%">

### 🖥️ Trading Terminal

[![Abrir ao Vivo](https://img.shields.io/badge/▶%20Abrir%20ao%20Vivo-5B9DFF?style=for-the-badge&logo=streamlit&logoColor=white)](https://lstm-stock-dashboard.onrender.com)

Terminal de trading com dados reais do Yahoo Finance. 7 módulos interativos com atualização automática.

| # | Módulo | O que mostra |
|---|--------|-------------|
| 1 | 📈 **Preço** | Candlestick OHLCV diário |
| 2 | 📉 **Momentum** | RSI 14 · MACD linha/sinal |
| 3 | 〰️ **Volatilidade** | Bollinger Bands (2σ) |
| 4 | 🌀 **Suporte** | Níveis Fibonacci retracement |
| 5 | 🎲 **Cenários** | Monte Carlo 1 000 simulações |
| 6 | 🗓️ **Sazonalidade** | Heatmap retorno mensal |
| 7 | 🧠 **IA** | Forecast LSTM D+1 → D+5 |

</td>

<td valign="top" width="33%">

### 📊 Grafana Monitoring

[![Iniciar Local](https://img.shields.io/badge/▶%20docker--compose%20up%20-d-F46800?style=for-the-badge&logo=grafana&logoColor=white)](http://localhost:3000)

8 painéis provisionados automaticamente via JSON. Sem configuração manual.

| # | Painel | Métrica PromQL |
|---|--------|----------------|
| 1 | 🟢 **Status** | `max(model_loaded)` |
| 2 | 📈 **RPS** | `rate(http_requests_total[1m])` |
| 3 | ⏱️ **Latência** | `histogram_quantile(0.99,…)` |
| 4 | 🧠 **Inferência** | `avg(prediction_duration_seconds)` |
| 5 | 💾 **RAM** | `process_resident_memory_bytes` |
| 6 | 🖥️ **CPU** | `rate(process_cpu_seconds_total[1m])` |
| 7 | 🔢 **Previsões** | `predictions_total` |
| 8 | 💵 **Último preço** | `last_prediction_value` |

</td>

<td valign="top" width="34%">

### ⚡ Swagger UI

[![Abrir Swagger](https://img.shields.io/badge/▶%20Abrir%20Swagger%20UI-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://pos-tech-mlet-fase-4.onrender.com/docs)

Documentação interativa OpenAPI 3.1. Teste todos os endpoints diretamente no browser.

| Método | Endpoint | Ação |
|--------|----------|------|
| `GET` | `/health` | Status e modelo |
| `GET` | `/model/info` | Hiperparâmetros |
| `POST` | `/predict` | Previsão por array |
| `POST` | `/predict/symbol` | Previsão por ticker |
| `GET` | `/api/chart/{s}` | OHLCV Yahoo proxy |
| `GET` | `/metrics` | Scrape Prometheus |

</td>

</tr>
</table>

---

## 📈 Métricas do Modelo

```
  AAPL · Jan 2018 – Abr 2026 · LSTM 64+64 · 29 épocas · janela 60 dias
  ────────────────────────────────────────────────────────────────────
  MAE    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░   5.78 USD  ✅  bench < 6.0
  RMSE   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░   7.46 USD  ✅  bench < 8.0
  MAPE   ▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░   2.48  %   ✅  bench < 5.0
  Acc    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░  97.52  %   ✅  bench > 95
  ────────────────────────────────────────────────────────────────────
  Escala: MAE/RMSE/MAPE em 0–10 · Acurácia em 0–100 · ▓ = preenchido
```

<div align="center">

| Métrica | Valor | Benchmark | |
|---------|:-----:|:---------:|:---:|
| **MAE** | **5.78 USD** | < 6 USD | ✅ |
| **RMSE** | **7.46 USD** | < 8 USD | ✅ |
| **MAPE** | **2.48%** | < 5% | ✅ |
| **Acurácia** | **97.52%** | > 95% | ✅ |

</div>

<details>
<summary><b>📉 Curva de aprendizado completa + split do dataset</b></summary>

```
 Época  loss (MSE)   val_loss    Δ
──────┬────────────┬────────────┬────────────────
  01  │  0.004800  │  0.004500  │ ↓ aprendendo
  05  │  0.002700  │  0.002900  │ ↓ convergindo
  10  │  0.001700  │  0.002000  │ ↓ refinando
  15  │  0.001400  │  0.001800  │ ↓
  18  │  0.001300  │  0.001700  │ ↓
  19  │  0.001250  │  0.001650  │ ✅ melhor checkpoint salvo
  24  │  0.001200  │  0.001700  │ ↑ leve overfitting
  29  │      EarlyStopping (patience=10) disparado
──────┴────────────┴────────────┴────────────────

  Split   Amostras   Período      Proporção
─────────┬──────────┬─────────────┬──────────
 Treino  │  1 626   │  2018–2023  │   80 %
 Teste   │    407   │  2023–2026  │   20 %
 Total   │  2 093   │  2018–2026  │  100 %
```

</details>

Métricas ao vivo: [`/model/info`](https://pos-tech-mlet-fase-4.onrender.com/model/info)

---

## ⚡ Uso da API

<table>
<tr><th>Método</th><th>Endpoint</th><th>Descrição</th></tr>
<tr><td><img src="https://img.shields.io/badge/GET-61AFFE?style=flat-square"/></td>
    <td><a href="https://pos-tech-mlet-fase-4.onrender.com/"><code>/</code></a></td>
    <td>Dashboard HTML embutido</td></tr>
<tr><td><img src="https://img.shields.io/badge/GET-61AFFE?style=flat-square"/></td>
    <td><a href="https://pos-tech-mlet-fase-4.onrender.com/health"><code>/health</code></a></td>
    <td>Status detalhado do sistema e modelo</td></tr>
<tr><td><img src="https://img.shields.io/badge/GET-61AFFE?style=flat-square"/></td>
    <td><a href="https://pos-tech-mlet-fase-4.onrender.com/model/info"><code>/model/info</code></a></td>
    <td>Arquitetura, hiperparâmetros e métricas</td></tr>
<tr><td><img src="https://img.shields.io/badge/POST-49CC90?style=flat-square"/></td>
    <td><code>/predict</code></td>
    <td>Previsão via array de preços fornecido</td></tr>
<tr><td><img src="https://img.shields.io/badge/POST-49CC90?style=flat-square"/></td>
    <td><code>/predict/symbol</code></td>
    <td>Previsão via símbolo — busca automática no Yahoo Finance</td></tr>
<tr><td><img src="https://img.shields.io/badge/GET-61AFFE?style=flat-square"/></td>
    <td><a href="https://pos-tech-mlet-fase-4.onrender.com/api/chart/AAPL"><code>/api/chart/{symbol}</code></a></td>
    <td>Proxy OHLCV do Yahoo Finance</td></tr>
<tr><td><img src="https://img.shields.io/badge/GET-61AFFE?style=flat-square"/></td>
    <td><a href="https://pos-tech-mlet-fase-4.onrender.com/metrics"><code>/metrics</code></a></td>
    <td>Métricas Prometheus (scrape endpoint)</td></tr>
<tr><td><img src="https://img.shields.io/badge/GET-61AFFE?style=flat-square"/></td>
    <td><a href="https://pos-tech-mlet-fase-4.onrender.com/docs"><code>/docs</code></a></td>
    <td>Swagger UI interativo (OpenAPI 3.1)</td></tr>
</table>

<details>
<summary><b>🐚 cURL — Previsão por símbolo</b></summary>

```bash
curl -X POST "https://pos-tech-mlet-fase-4.onrender.com/predict/symbol" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "days_ahead": 5}'
```

```json
{
  "symbol": "AAPL",
  "last_close": 178.45,
  "last_close_date": "2026-04-30",
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

</details>

<details>
<summary><b>🐍 Python</b></summary>

```python
import requests

r = requests.post(
    "https://pos-tech-mlet-fase-4.onrender.com/predict/symbol",
    json={"symbol": "AAPL", "days_ahead": 5},
)
data = r.json()
for p in data["predictions"]:
    print(f"D+{p['day']}: $ {p['predicted_price']:.2f}")
# D+1: $ 179.12
# D+2: $ 180.05
# D+3: $ 180.88
```

</details>

<details>
<summary><b>🌐 JavaScript / fetch</b></summary>

```javascript
const res = await fetch("https://pos-tech-mlet-fase-4.onrender.com/predict/symbol", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ symbol: "AAPL", days_ahead: 5 }),
});
const { predictions, inference_time_ms } = await res.json();
console.log(`D+1: $${predictions[0].predicted_price} · ${inference_time_ms}ms`);
```

</details>

<details>
<summary><b>💚 Health check</b></summary>

```bash
curl https://pos-tech-mlet-fase-4.onrender.com/health
```

```json
{ "status": "ok", "model_loaded": true, "uptime_seconds": 3842,
  "symbol": "AAPL", "window_size": 60 }
```

</details>

---

## 🛠 Stack Tecnológica

<div align="center">

**🧠 Core ML & Data**

![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow_2.17-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Keras](https://img.shields.io/badge/Keras_3.x-D00000?style=for-the-badge&logo=keras&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)

**🚀 API & Dashboard**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![yfinance](https://img.shields.io/badge/yfinance_≥1.x-6002EE?style=for-the-badge&logo=yahoo&logoColor=white)

**☁️ Infra, Observabilidade & Deploy**

![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

</div>

---

## 📁 Estrutura do Projeto

<details>
<summary><b>📂 Ver árvore de arquivos completa</b></summary>

```
tech-challenge-fase4/
│
├── 🐳 Dockerfile                      # Container da API (produção)
├── 🐳 Dockerfile.dashboard            # Container do Dashboard
├── 🐳 docker-compose.yml              # Stack completa — 4 serviços
├── ☁️  render.yaml                     # Blueprint Render — 2 serviços
├── 📦 requirements.txt                # Dependências completas
├── 📦 requirements-api.txt            # Subset mínimo para API
├── 📦 requirements-dashboard.txt      # Subset para Dashboard
├── 🖥️  dashboard.py                    # Streamlit — Trading Terminal
│
├── src/
│   ├── config.py                      # Pydantic Settings · env vars
│   ├── data_loader.py                 # yfinance 1.x · OHLCV
│   ├── preprocessor.py               # MinMaxScaler · sliding windows
│   ├── model.py                       # Arquitetura LSTM (Keras)
│   ├── train.py                       # Pipeline de treinamento
│   ├── evaluate.py                    # MAE · RMSE · MAPE
│   ├── predict.py                     # StockPredictor · inferência
│   └── api/
│       ├── main.py                    # FastAPI app + lifespan + HTTP middleware
│       ├── schemas.py                 # Pydantic v2 · request/response
│       ├── routes.py                  # Endpoints + proxy Yahoo Finance
│       └── monitoring.py             # Prometheus counters/histograms/gauges
│
├── notebooks/
│   └── 01_exploracao_e_treino.ipynb   # EDA completo + treino passo a passo
│
├── models/                            # Artefatos serializados
│   ├── lstm_model.keras
│   ├── scaler.pkl
│   └── metadata.json
│
├── monitoring/
│   ├── prometheus.yml                 # Scrape targets: prod + local
│   └── grafana/
│       ├── dashboards/api_dashboard.json
│       └── provisioning/             # Auto-provisioning
│
├── data/
│   └── AAPL_2018_2026.csv            # Cache histórico · 2 093 linhas
│
└── tests/
    ├── test_api.py                    # Integração · endpoints
    ├── test_data_loader.py            # Unit · data loader
    └── test_preprocessor.py          # Unit · preprocessor
```

</details>

---

## ⚙️ Setup Local

<details>
<summary><b>🐍 Apenas a API (sem Docker)</b></summary>

```bash
git clone https://github.com/dionebraga/Pos_Tech_MLET-Fase-4.git
cd tech-challenge-fase4

python -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows PowerShell

pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs
```

</details>

<details>
<summary><b>🖥️ Dashboard local</b></summary>

```bash
export API_URL=http://localhost:8000          # Linux / macOS
# $env:API_URL="http://localhost:8000"        # Windows PowerShell

streamlit run dashboard.py   # → http://localhost:8501
```

</details>

<details>
<summary><b>🐳 Stack completa com Docker Compose</b></summary>

```bash
docker-compose up -d                   # Sobe tudo
docker-compose logs -f api             # Logs da API
docker-compose restart grafana         # Recarregar dashboards
docker-compose down                    # Para tudo
```

</details>

---

## 🧠 Treinamento do Modelo

<table>
<tr>
<td><b>Símbolo</b></td><td><b>Início</b></td><td><b>Fim</b></td><td><b>Épocas máx.</b></td><td><b>Resultado</b></td>
</tr>
<tr>
<td><code>AAPL</code></td><td><code>2018-01-01</code></td><td><code>2026-05-01</code></td><td><code>50</code></td><td>29 épocas · MAPE 2.48%</td>
</tr>
<tr>
<td><code>PETR4.SA</code></td><td><code>2019-01-01</code></td><td><code>2026-05-01</code></td><td><code>50</code></td><td><i>personalizável</i></td>
</tr>
</table>

```bash
# Treino padrão — AAPL 2018–2026
python -m src.train

# Treino personalizado — qualquer ticker Yahoo Finance
python -m src.train --symbol PETR4.SA --start 2019-01-01 --end 2026-05-01 --epochs 50

# Helpers
python -m src.evaluate   # MAE · RMSE · MAPE no conjunto de teste
python -m src.predict    # previsão D+1 para o ticker atual
```

### Arquitetura da Rede Neural

```mermaid
flowchart TD
    I["📥 Input Layer\nbatch × 60 × 1\n60 fechamentos normalizados ∈ [0, 1]"]

    subgraph LSTM1["  Bloco 1 — Padrões de Curto Prazo  "]
        L1["🔵 LSTM · 64 unidades\nreturn_sequences = True\n─────────────────────\noutput: batch × 60 × 64\n→ mantém toda a sequência temporal"]
        D1["⬜ Dropout  p = 0.2\ndesativa 20% dos neurônios por época\n→ previne co-adaptação"]
    end

    subgraph LSTM2["  Bloco 2 — Síntese de Longo Prazo  "]
        L2["🔵 LSTM · 64 unidades\nreturn_sequences = False\n─────────────────────\noutput: batch × 64\n→ colapsa sequência em vetor de contexto"]
        D2["⬜ Dropout  p = 0.2\n→ regularização final antes da saída"]
    end

    O["🟢 Dense(1) · ativação linear\nbatch × 1  →  escalar normalizado [0, 1]\n→  inverse_transform  →  preço D+1 (USD)"]

    I --> L1 --> D1 --> L2 --> D2 --> O

    style I  fill:#0d1117,color:#58a6ff,stroke:#388bfd,stroke-width:2px
    style L1 fill:#0d1117,color:#ffa657,stroke:#e3b341,stroke-width:2px
    style D1 fill:#0d1117,color:#8b949e,stroke:#30363d,stroke-width:1px,stroke-dasharray:4
    style L2 fill:#0d1117,color:#ffa657,stroke:#e3b341,stroke-width:2px
    style D2 fill:#0d1117,color:#8b949e,stroke:#30363d,stroke-width:1px,stroke-dasharray:4
    style O  fill:#0d1117,color:#56d364,stroke:#3fb950,stroke-width:2px
```

### Pipeline de Treinamento

<table>
<tr>
<td align="center" width="14%"><b>1️⃣</b><br/><b>Download</b><br/><sub>yfinance OHLCV<br/>2 093 linhas</sub></td>
<td align="center" width="2%">→</td>
<td align="center" width="14%"><b>2️⃣</b><br/><b>Normalização</b><br/><sub>MinMaxScaler<br/>fit só no treino</sub></td>
<td align="center" width="2%">→</td>
<td align="center" width="14%"><b>3️⃣</b><br/><b>Janelamento</b><br/><sub>60d → D+1<br/>sliding window</sub></td>
<td align="center" width="2%">→</td>
<td align="center" width="14%"><b>4️⃣</b><br/><b>Split Temporal</b><br/><sub>80% treino<br/>20% teste</sub></td>
<td align="center" width="2%">→</td>
<td align="center" width="14%"><b>5️⃣</b><br/><b>Treino</b><br/><sub>Adam lr=0.001<br/>MSE · EarlyStopping</sub></td>
<td align="center" width="2%">→</td>
<td align="center" width="14%"><b>6️⃣</b><br/><b>Avaliação</b><br/><sub>MAE · RMSE<br/>MAPE · Acurácia</sub></td>
<td align="center" width="2%">→</td>
<td align="center" width="14%"><b>7️⃣</b><br/><b>Salvar</b><br/><sub>model.keras<br/>scaler.pkl</sub></td>
</tr>
</table>

### Células LSTM — Memória com 3 Portões

> Cada pregão atualiza 3 portões que decidem o que lembrar, aprender e revelar — resolvendo o problema do gradiente que vanish em RNNs simples.

```mermaid
flowchart TD
    subgraph IN["  Entradas · pregão t  "]
        direction LR
        X["📊 x_t\npreço normalizado ∈ [0, 1]"]
        H["🔁 h_{t-1}\nestado oculto anterior"]
    end

    FG["🔴 Forget Gate  f_t\nf_t = σ( Wf · [h_{t-1}, x_t] + bf )\n'quanto do Cell State anterior preservar'"]

    IG["🟡 Input Gate  i_t + Candidato g_t\ni_t = σ( Wi · [h,x] + bi )\ng_t = tanh( Wc · [h,x] + bc )\n'quanto da nova informação absorver'"]

    CS["🔵 Cell State  C_t\nC_t = f_t ⊗ C_{t-1}  +  i_t ⊗ g_t\n─────────────────────────────────\n'memória de longo prazo — persiste através dos 60 pregões'"]

    OG["🟢 Output Gate  o_t\no_t = σ( Wo · [h,x] + bo )\nh_t = o_t ⊗ tanh( C_t )\n'quanto do Cell State revelar como saída'"]

    OUT["🔮 h_t  →  Dense(1)  →  inverse_transform\npreço previsto D+1 (USD)"]

    IN --> FG --> CS
    IN --> IG --> CS
    IN --> OG
    CS --> OG --> OUT

    style X   fill:#0d1117,color:#58a6ff,stroke:#388bfd,stroke-width:2px
    style H   fill:#0d1117,color:#8b949e,stroke:#30363d,stroke-width:2px
    style FG  fill:#0d1117,color:#ff7b72,stroke:#f85149,stroke-width:2px
    style IG  fill:#0d1117,color:#e3b341,stroke:#d29922,stroke-width:2px
    style CS  fill:#0d1117,color:#79c0ff,stroke:#388bfd,stroke-width:3px
    style OG  fill:#0d1117,color:#56d364,stroke:#3fb950,stroke-width:2px
    style OUT fill:#0d1117,color:#d2a8ff,stroke:#a371f7,stroke-width:2px
```

### Janela Deslizante — 60 Pregões como Sequência

> A mesma lógica de tokenização de texto: cada dia é um token, a janela de 60 dias é a sequência de entrada.

<table>
<thead>
<tr>
<th colspan="9" align="center">Janela Deslizante — 60 Pregões de Fechamento (AAPL)</th>
</tr>
<tr>
<th align="center"><sub>Pregão</sub></th>
<th align="center"><sub>t−59</sub></th>
<th align="center"><sub>t−58</sub></th>
<th align="center"><sub>···</sub></th>
<th align="center"><sub>t−2</sub></th>
<th align="center"><sub>t−1</sub></th>
<th align="center"><sub><b>t (hoje)</b></sub></th>
<th align="center"><sub>→</sub></th>
<th align="center"><sub><b>D+1</b></sub></th>
</tr>
</thead>
<tbody>
<tr>
<td align="center"><sub>Preço USD</sub></td>
<td align="center">$168.20</td>
<td align="center">$170.15</td>
<td align="center">···</td>
<td align="center">$194.50</td>
<td align="center">$195.80</td>
<td align="center"><b>$196.40</b></td>
<td align="center" rowspan="2"><b>🧠 LSTM<br/>64+64<br/>↓<br/>Dense(1)<br/>↓<br/>inverse<br/>transform</b></td>
<td align="center" rowspan="2"><b>$197.83</b><br/><sub>+0.73%</sub></td>
</tr>
<tr>
<td align="center"><sub>Normalizado</sub></td>
<td align="center"><sub>0.412</sub></td>
<td align="center"><sub>0.451</sub></td>
<td align="center"><sub>···</sub></td>
<td align="center"><sub>0.912</sub></td>
<td align="center"><sub>0.921</sub></td>
<td align="center"><b><sub>0.931</sub></b></td>
</tr>
<tr>
<td colspan="9" align="center"><sub>MinMaxScaler fit apenas no conjunto de treino · shape de entrada: <code>(1, 60, 1)</code></sub></td>
</tr>
</tbody>
</table>

### Geração Auto-Regressiva D+1 → D+5

> A mesma ideia de geração de texto em LLMs: cada previsão alimenta a janela seguinte — o modelo "escreve" o futuro um dia de cada vez.

<table>
<tr>
<td align="center" width="16%"><b>📦 Janela Inicial</b><br/><sub>t-59 … t<br/>60 dias reais</sub></td>
<td align="center" width="4%">→</td>
<td align="center" width="16%"><b>🧠 LSTM</b><br/>Iteração 1<br/><b>D+1 · $197.83</b></td>
<td align="center" width="4%">→</td>
<td align="center" width="16%"><b>🧠 LSTM</b><br/>Iteração 2<br/><b>D+2 · $198.51</b></td>
<td align="center" width="4%">→</td>
<td align="center" width="16%"><b>🧠 LSTM</b><br/>Iteração 3<br/><b>D+3 · $199.10</b></td>
<td align="center" width="4%">→</td>
<td align="center" width="20%"><b>🧠 LSTM</b><br/>Iterações 4–5<br/><b>D+4–5 · $199–200</b></td>
</tr>
<tr>
<td colspan="9" align="center"><sub><i>Cada previsão descarta o dia mais antigo da janela e injeta o novo fechamento previsto</i></sub></td>
</tr>
</table>

### Regularização — Por Que o Modelo Generaliza

> Três mecanismos trabalhando juntos para que o modelo não decore os 2 093 dias de treino — e acerte os 407 dias que nunca viu.

```mermaid
flowchart TD
    subgraph LOOP["  Loop de Treino · 29 épocas  "]
        EP["📊 Época N"] --> FW["Forward Pass\ncalcula MSE loss"]
        FW --> BW["Backprop\nAdam atualiza pesos"]
        BW --> EP
    end

    subgraph REG["  Regularização  "]
        direction LR
        DR["⬜ Dropout 20%\ndesativa neurônios aleatórios\na cada época\n→ ensemble implícito"]
        ES["⏹️ EarlyStopping\npatience: 10\nparou na época 29\nmelhor: época 19"]
        RL["📉 ReduceLROnPlateau\nfactor: 0.5 · patience: 5\n0.001 → 0.0005"]
        CP["💾 ModelCheckpoint\nsalva pesos da época 19\n→ generalização máxima"]
    end

    LOOP --> DR
    LOOP --> ES
    LOOP --> RL
    ES --> CP
    RL --> CP

    style DR fill:#0d1117,color:#8b949e,stroke:#30363d
    style ES fill:#0d1117,color:#ff7b72,stroke:#f85149,stroke-width:2px
    style RL fill:#0d1117,color:#e3b341,stroke:#d29922,stroke-width:2px
    style CP fill:#0d1117,color:#56d364,stroke:#3fb950,stroke-width:2px
```

---

## 🐳 Docker

```bash
docker build -t lstm-stock-api .
docker run -p 8000:8000 lstm-stock-api

docker build -f Dockerfile.dashboard -t lstm-stock-dashboard .
docker run -p 8501:8501 -e API_URL=http://host.docker.internal:8000 lstm-stock-dashboard

docker-compose up -d   # stack completa (recomendado)
```

---

## 📊 Monitoramento

<table>
<tr>
<th>Métrica</th>
<th align="center">Tipo</th>
<th>Labels</th>
<th>Descrição</th>
</tr>
<tr>
<td><code>http_requests_total</code></td>
<td align="center"><img src="https://img.shields.io/badge/Counter-00C853?style=flat-square&logoColor=white"/></td>
<td><sub><code>method</code> · <code>handler</code> · <code>status</code></sub></td>
<td>Total de requisições HTTP recebidas</td>
</tr>
<tr>
<td><code>http_request_duration_seconds</code></td>
<td align="center"><img src="https://img.shields.io/badge/Histogram-5B9DFF?style=flat-square&logoColor=white"/></td>
<td><sub><code>method</code> · <code>handler</code></sub></td>
<td>Latência end-to-end de cada request</td>
</tr>
<tr>
<td><code>predictions_total</code></td>
<td align="center"><img src="https://img.shields.io/badge/Counter-00C853?style=flat-square&logoColor=white"/></td>
<td><sub><code>endpoint</code> · <code>status</code></sub></td>
<td>Previsões LSTM executadas</td>
</tr>
<tr>
<td><code>prediction_duration_seconds</code></td>
<td align="center"><img src="https://img.shields.io/badge/Histogram-5B9DFF?style=flat-square&logoColor=white"/></td>
<td><sub><code>endpoint</code></sub></td>
<td>Tempo de inferência do modelo LSTM (~87 ms)</td>
</tr>
<tr>
<td><code>last_prediction_value</code></td>
<td align="center"><img src="https://img.shields.io/badge/Gauge-FFD700?style=flat-square&logoColor=black"/></td>
<td><sub><code>symbol</code></sub></td>
<td>Último preço previsto por ticker (USD)</td>
</tr>
<tr>
<td><code>model_loaded</code></td>
<td align="center"><img src="https://img.shields.io/badge/Gauge-FFD700?style=flat-square&logoColor=black"/></td>
<td><sub>—</sub></td>
<td><code>1</code> = modelo ativo · <code>0</code> = degradado</td>
</tr>
<tr>
<td><code>process_resident_memory_bytes</code></td>
<td align="center"><img src="https://img.shields.io/badge/Gauge-FFD700?style=flat-square&logoColor=black"/></td>
<td><sub>—</sub></td>
<td>RAM do processo em bytes</td>
</tr>
<tr>
<td><code>process_cpu_seconds_total</code></td>
<td align="center"><img src="https://img.shields.io/badge/Counter-00C853?style=flat-square&logoColor=white"/></td>
<td><sub>—</sub></td>
<td>CPU acumulado em segundos</td>
</tr>
</table>

<details>
<summary><b>📟 Queries Prometheus úteis</b></summary>

```promql
sum by (handler) (rate(http_requests_total[1m]))
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
rate(prediction_duration_seconds_sum[2m]) / rate(prediction_duration_seconds_count[2m]) * 1000
max by (symbol) (last_prediction_value)
max(model_loaded)
rate(prediction_errors_total[5m])
```

</details>

---

## ☁️ Deploy em Nuvem

<table>
<tr>
<th align="center">Serviço</th>
<th align="center">Container</th>
<th align="center">Status</th>
<th align="center">URL de Produção</th>
</tr>
<tr>
<td>⚡ <b>API FastAPI</b></td>
<td><code>Dockerfile</code></td>
<td align="center"><img src="https://img.shields.io/badge/●%20Online-00FF88?style=flat-square&logoColor=black"/></td>
<td><a href="https://pos-tech-mlet-fase-4.onrender.com">pos-tech-mlet-fase-4.onrender.com</a></td>
</tr>
<tr>
<td>🖥️ <b>Dashboard Streamlit</b></td>
<td><code>Dockerfile.dashboard</code></td>
<td align="center"><img src="https://img.shields.io/badge/●%20Live-5B9DFF?style=flat-square&logoColor=white"/></td>
<td><a href="https://lstm-stock-dashboard.onrender.com">lstm-stock-dashboard.onrender.com</a></td>
</tr>
</table>

<details>
<summary><b>☁️ Como fazer deploy no Render</b></summary>

1. Fork o repositório
2. [render.com](https://render.com) → **New Blueprint** → aponte para `render.yaml`
3. Defina `API_URL=https://pos-tech-mlet-fase-4.onrender.com` no Dashboard service
4. Render detecta os Dockerfiles e faz deploy automaticamente

</details>

---

## 🧪 Testes

<div align="center">

![Tests](https://img.shields.io/badge/12%20testes-passing-00C853?style=for-the-badge&logo=pytest&logoColor=white)
![Suites](https://img.shields.io/badge/3%20suites-API%20·%20DataLoader%20·%20Preprocessor-5B9DFF?style=for-the-badge)

</div>

```bash
pytest tests/ -v --tb=short                               # execução rápida
pytest tests/ -v --cov=src --cov-report=term-missing      # com cobertura
```

<details>
<summary><b>📋 Resultado esperado</b></summary>

```
tests/test_api.py::test_root_endpoint             PASSED
tests/test_api.py::test_health_endpoint           PASSED
tests/test_api.py::test_metrics_endpoint          PASSED
tests/test_api.py::test_predict_validates_input   PASSED
tests/test_api.py::test_predict_negative_prices   PASSED
tests/test_api.py::test_predict_days_ahead_range  PASSED
tests/test_data_loader.py::test_fetch_returns_df  PASSED
tests/test_data_loader.py::test_empty_raises      PASSED
tests/test_preprocessor.py::test_scaler_0_1       PASSED
tests/test_preprocessor.py::test_inverse_recover  PASSED
tests/test_preprocessor.py::test_windows_shapes   PASSED
tests/test_preprocessor.py::test_split_order      PASSED

12 passed in 3.42s
```

</details>

---

## 🎬 Vídeo Demonstrativo

<div align="center">

[![Assistir Demo](https://img.shields.io/badge/Google%20Drive-▶%20Assistir%20Demonstração%20Completa-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)

| Cobertura do vídeo | |
|---|:---:|
| Arquitetura end-to-end | ✅ |
| Dashboard ao vivo — 7 módulos | ✅ |
| Swagger UI — teste de endpoints | ✅ |
| Métricas LSTM e curva de treino | ✅ |
| Prometheus + Grafana — 8 painéis | ✅ |

</div>

---

## 👤 Autor

<table>
<tr>
<td valign="top" width="50%">

**Dione Braga Ferreira**

Pós-Graduação em Machine Learning Engineering<br/>
FIAP · Tech Challenge Fase 4 · 2026

[![GitHub](https://img.shields.io/badge/GitHub-dionebraga-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/dionebraga)
[![Email](https://img.shields.io/badge/Email-dionebraga.work%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:dionebraga.work@gmail.com)

</td>
<td valign="top" width="50%">

| Entregável | Status |
|---|:---:|
| Modelo LSTM treinado | ✅ |
| API REST em produção | ✅ |
| Dashboard interativo | ✅ |
| Monitoramento Prometheus/Grafana | ✅ |
| Testes automatizados (12) | ✅ |
| Vídeo demonstrativo | ✅ |

</td>
</tr>
</table>

---

<div align="center">

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-Repositório-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dionebraga/Pos_Tech_MLET-Fase-4)
[![Dashboard](https://img.shields.io/badge/Dashboard-●%20Live-5B9DFF?style=for-the-badge&logo=streamlit&logoColor=white)](https://lstm-stock-dashboard.onrender.com)
[![API](https://img.shields.io/badge/API-●%20Online-00FF88?style=for-the-badge&logo=fastapi&logoColor=black)](https://pos-tech-mlet-fase-4.onrender.com)
[![Swagger](https://img.shields.io/badge/Swagger-●%20Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://pos-tech-mlet-fase-4.onrender.com/docs)
[![Vídeo](https://img.shields.io/badge/Vídeo-●%20Demo-FF0000?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/drive/folders/13oh-1vmyH5aKzemD9ClMUIB7JU9LFkaa?usp=sharing)

<br/>

```
  2 093 pregões · LSTM 64+64 · 29 épocas · MAPE 2.48% · 97.52% acurácia · ~87ms inferência
```

*TensorFlow · Keras · FastAPI · Streamlit · Prometheus · Grafana · Docker · Render*

**© 2026 Dione Braga Ferreira** · [MIT License](LICENSE)

<br/>

</div>
