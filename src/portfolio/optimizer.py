import numpy as np

def optimize_portfolio(prices):

    returns = prices.pct_change().dropna()

    mean_returns = returns.mean()

    cov_matrix = returns.cov()

    weights = np.random.random(len(mean_returns))

    weights /= np.sum(weights)

    portfolio_return = np.sum(mean_returns * weights)

    portfolio_volatility = np.sqrt(
        np.dot(weights.T, np.dot(cov_matrix, weights))
    )

    sharpe = portfolio_return / portfolio_volatility

    return {
        "weights": weights,
        "return": portfolio_return,
        "volatility": portfolio_volatility,
        "sharpe": sharpe
    }