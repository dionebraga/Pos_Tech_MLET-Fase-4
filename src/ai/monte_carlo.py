import numpy as np

def monte_carlo_simulation(
    prices,
    simulations=100,
    days=30
):

    returns = np.diff(prices) / prices[:-1]

    mu = returns.mean()

    sigma = returns.std()

    last_price = prices[-1]

    simulations_data = []

    for _ in range(simulations):

        sim_prices = [last_price]

        for _ in range(days):

            next_price = sim_prices[-1] * (
                1 + np.random.normal(mu, sigma)
            )

            sim_prices.append(next_price)

        simulations_data.append(sim_prices)

    return simulations_data