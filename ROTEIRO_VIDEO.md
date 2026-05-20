# 🎬 Roteiro do Vídeo de Demonstração

Duração sugerida: **5 a 8 minutos**.

---

## ⏱ Estrutura

### 1. Introdução (30s)
- "Olá, sou a Dione Braga, aluna da Pós Tech ML Engineering"
- "Este é o Tech Challenge da Fase 4: previsão de preço de ações com LSTM"
- "Vou demonstrar a pipeline completa: do treinamento ao deploy com monitoramento"

### 2. Visão geral da arquitetura (1 min)
Mostrar no README a seção de arquitetura. Explicar:
- Coleta via yfinance
- Pré-processamento e janelamento
- Modelo LSTM (2 camadas + Dropout)
- API FastAPI
- Containerização com Docker
- Monitoramento com Prometheus + Grafana

### 3. Estrutura do projeto (45s)
Abrir o VS Code e mostrar:
- `src/` (config, data_loader, preprocessor, model, train, predict)
- `src/api/` (main, routes, schemas, monitoring)
- `notebooks/` (notebook de exploração)
- `tests/`
- `Dockerfile` e `docker-compose.yml`

### 4. Notebook de treino (1 min)
Abrir `notebooks/01_exploracao_e_treino.ipynb` e mostrar:
- Dados baixados do yfinance
- Gráfico do preço histórico
- Loss curve do treinamento
- Comparação real vs previsto
- Métricas finais (MAE, RMSE, MAPE)

### 5. Demonstração da API (2 min)
Subir a API:
```bash
uvicorn src.api.main:app --reload
```

Abrir `http://localhost:8000/docs` e demonstrar:

#### a) GET /health
Mostrar status e modelo carregado.

#### b) GET /model/info
Mostrar metadados do modelo (símbolo, métricas, hiperparâmetros).

#### c) POST /predict/symbol
Testar com `AAPL` e `days_ahead=5`.
Apontar o tempo de inferência na resposta.

#### d) POST /predict
Testar com lista de preços fornecida.

### 6. Monitoramento (1 min)
Subir o stack completo:
```bash
docker-compose up -d
```

Mostrar:
- **Prometheus** (`localhost:9090`) — query `predictions_total`
- **Grafana** (`localhost:3000`) — dashboard com latência, RPS, CPU/RAM
- Fazer 5-10 chamadas à API e ver as métricas atualizando em tempo real

### 7. Deploy em nuvem (30s)
Abrir o link da API publicada (Render/Railway). Fazer uma chamada via Postman ou curl.

### 8. Encerramento (15s)
- "Código completo no GitHub: [link]"
- "Obrigada pela atenção!"

---

## 🎯 Dicas

- **Grave em 1080p** com OBS Studio ou similar
- **Use webcam pequena no canto** para humanizar
- **Aumente o zoom do terminal** (180% no mínimo)
- **Tema claro** funciona melhor que escuro em vídeo
- Pratique antes — o vídeo deve fluir sem "uhmms" longos

## 📋 Checklist antes de gravar

- [ ] Modelo treinado e em `models/`
- [ ] API rodando localmente sem erros
- [ ] Docker Compose subindo Prometheus + Grafana
- [ ] Dashboard do Grafana com dados aparecendo
- [ ] Deploy em nuvem ativo
- [ ] Repositório Git público e atualizado
- [ ] README.md sem links quebrados
