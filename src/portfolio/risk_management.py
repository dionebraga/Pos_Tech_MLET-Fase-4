import numpy as np

def calculate_var(returns):

    return np.percentile(
        returns,
        5
    )

def calculate_sharpe(returns):

    return (
        returns.mean()
        / returns.std()
    ) * np.sqrt(252)