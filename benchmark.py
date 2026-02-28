import timeit

setup = """
import logic
import pandas as pd
import numpy as np
dates = pd.date_range("2020-01-01", periods=1825)
closes = {'SPY': pd.Series(np.random.rand(1825) * 400, index=dates)}
"""

stmt_baseline = """
latest_hist = logic.calc_ppo(closes['SPY'])[2].iloc[-1]
latest_ppo = logic.calc_ppo(closes['SPY'])[0].iloc[-1]
"""

stmt_optimized = """
ppo_data, _, hist_data = logic.calc_ppo(closes['SPY'])
latest_hist = hist_data.iloc[-1]
latest_ppo = ppo_data.iloc[-1]
"""

baseline_time = timeit.timeit(stmt_baseline, setup=setup, number=1000)
optimized_time = timeit.timeit(stmt_optimized, setup=setup, number=1000)

print(f"Baseline Time (1000 runs): {baseline_time:.4f} seconds")
print(f"Optimized Time (1000 runs): {optimized_time:.4f} seconds")
print(f"Improvement: {(baseline_time - optimized_time) / baseline_time * 100:.2f}%")
