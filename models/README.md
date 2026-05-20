# Modelos Treinados

Esta pasta deve conter os artefatos serializados após o treinamento:

- `lstm_model.keras` — modelo LSTM treinado
- `scaler.pkl` — MinMaxScaler ajustado
- `metadata.json` — hiperparâmetros + métricas + data do treino

## Como gerar

Execute o script de treinamento na raiz do projeto:

```bash
python -m src.train
```

ou via shell helper:

```bash
./scripts/run_training.sh AAPL
```

> **Atenção:** estes arquivos são gerados automaticamente e podem ser
> ignorados pelo Git em projetos com modelos grandes (use Git LFS se quiser
> versioná-los).
