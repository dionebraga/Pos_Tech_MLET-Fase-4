"""
Arquitetura do modelo LSTM para previsão de séries temporais.

Modelo: 2 camadas LSTM empilhadas + Dropout + Dense de saída.
Esta arquitetura é amplamente usada para previsão de preços de ações
e oferece bom equilíbrio entre capacidade e tempo de treinamento.
"""
import logging
from typing import Tuple

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers

logger = logging.getLogger(__name__)


def build_lstm_model(
    window_size: int = 60,
    n_features: int = 1,
    lstm_units_1: int = 64,
    lstm_units_2: int = 64,
    dropout_rate: float = 0.2,
    learning_rate: float = 0.001,
) -> tf.keras.Model:
    """
    Constrói uma LSTM empilhada para previsão de 1 passo à frente.

    Arquitetura:
        Input (window_size, n_features)
        ↓
        LSTM(units_1, return_sequences=True)
        ↓
        Dropout
        ↓
        LSTM(units_2)
        ↓
        Dropout
        ↓
        Dense(32, relu)
        ↓
        Dense(1)  # preço previsto (escalado)

    Returns:
        Modelo Keras compilado com Adam + MSE.
    """
    model = models.Sequential(name="lstm_stock_predictor")

    model.add(layers.Input(shape=(window_size, n_features)))

    # Primeira camada LSTM — retorna sequência para empilhar
    model.add(
        layers.LSTM(
            lstm_units_1,
            return_sequences=True,
            name="lstm_1",
        )
    )
    model.add(layers.Dropout(dropout_rate, name="dropout_1"))

    # Segunda camada LSTM — retorna apenas o último estado
    model.add(layers.LSTM(lstm_units_2, name="lstm_2"))
    model.add(layers.Dropout(dropout_rate, name="dropout_2"))

    # Cabeça de regressão
    model.add(layers.Dense(32, activation="relu", name="dense_hidden"))
    model.add(layers.Dense(1, name="output"))

    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="mean_squared_error",
        metrics=["mae"],
    )

    logger.info("Modelo LSTM criado:")
    model.summary(print_fn=lambda s: logger.info(s))
    return model


def get_callbacks(patience: int = 10) -> Tuple[tf.keras.callbacks.Callback, ...]:
    """Callbacks padrão: Early Stopping + Reduce LR."""
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=patience,
        restore_best_weights=True,
        verbose=1,
    )
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1,
    )
    return early_stop, reduce_lr
