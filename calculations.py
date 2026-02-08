import pandas as pd

def calculate_ppo(price):
    """
    Calculates the Percentage Price Oscillator (PPO).

    Args:
        price (pd.Series): A pandas Series of prices.

    Returns:
        tuple: A tuple containing (ppo_line, signal_line, hist).
    """
    ema12 = price.ewm(span=12, adjust=False).mean()
    ema26 = price.ewm(span=26, adjust=False).mean()
    ppo_line = ((ema12 - ema26) / ema26) * 100
    signal_line = ppo_line.ewm(span=9, adjust=False).mean()
    hist = ppo_line - signal_line
    return ppo_line, signal_line, hist
