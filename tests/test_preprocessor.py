"""Testes unitários do preprocessor."""
import numpy as np
import pytest

from src.preprocessor import (
    create_windows,
    fit_scaler,
    inverse_transform,
    train_test_split_time,
    transform_with_scaler,
)


def test_fit_scaler_normalizes_to_0_1():
    values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    scaler = fit_scaler(values)
    transformed = transform_with_scaler(values, scaler)
    assert transformed.min() == pytest.approx(0.0)
    assert transformed.max() == pytest.approx(1.0)


def test_inverse_transform_recovers_original():
    values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    scaler = fit_scaler(values)
    transformed = transform_with_scaler(values, scaler)
    recovered = inverse_transform(transformed.flatten(), scaler)
    np.testing.assert_allclose(recovered, values, rtol=1e-6)


def test_create_windows_shapes():
    series = np.arange(100, dtype=np.float32)
    X, y = create_windows(series, window_size=10)
    assert X.shape == (90, 10, 1)
    assert y.shape == (90,)
    # Primeira janela deve ser [0..9], target = 10
    np.testing.assert_array_equal(X[0].flatten(), np.arange(10))
    assert y[0] == 10


def test_create_windows_raises_on_short_series():
    series = np.arange(5, dtype=np.float32)
    with pytest.raises(ValueError):
        create_windows(series, window_size=10)


def test_train_test_split_preserves_order():
    X = np.arange(100).reshape(-1, 1, 1)
    y = np.arange(100)
    X_train, X_test, y_train, y_test = train_test_split_time(X, y, train_ratio=0.8)
    assert len(X_train) == 80
    assert len(X_test) == 20
    # Ordem deve ser preservada (split temporal)
    assert y_train[0] == 0
    assert y_test[0] == 80
