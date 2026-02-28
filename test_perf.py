import timeit
import pandas as pd
import numpy as np

# Setup realistic dummy data
n_rows = 5000
dates = pd.date_range(start='2000-01-01', periods=n_rows)
full_data = pd.DataFrame({
    'Open': np.random.randn(n_rows),
    'High': np.random.randn(n_rows),
    'Low': np.random.randn(n_rows),
    'Close': np.random.randn(n_rows)
}, index=dates)
full_data.columns = pd.MultiIndex.from_product([full_data.columns, ['SPY']])

spy = full_data['Close']['SPY']
l_cone = spy.rolling(20).mean() - 2 * spy.rolling(20).std()
u_cone = spy.rolling(20).mean() + 2 * spy.rolling(20).std()
ppo = spy.rolling(12).mean() - spy.rolling(26).mean()
sig = ppo.rolling(9).mean()
hist = ppo - sig

start_filter = '2010-01-01'

def original():
    c_data = full_data[full_data.index >= start_filter]

    y_l_cone = l_cone[l_cone.index >= start_filter]
    y_u_cone = u_cone[u_cone.index >= start_filter]

    sub_ppo = ppo[ppo.index >= c_data.index[0]]
    y_sig = sig[sig.index >= c_data.index[0]]
    y_hist = hist[hist.index >= c_data.index[0]]

    colors = ['#00ff00' if v >= 0 else '#ff0000' for v in hist[hist.index >= c_data.index[0]]]

def optimized():
    c_data = full_data[full_data.index >= start_filter]

    # Pre-slice everything using loc and c_data.index which is guaranteed to match
    sub_idx = c_data.index
    sub_l_cone = l_cone.loc[sub_idx]
    sub_u_cone = u_cone.loc[sub_idx]

    sub_ppo = ppo.loc[sub_idx]
    sub_sig = sig.loc[sub_idx]
    sub_hist = hist.loc[sub_idx]

    colors = ['#00ff00' if v >= 0 else '#ff0000' for v in sub_hist]

print("Original:", timeit.timeit(original, number=1000))
print("Optimized:", timeit.timeit(optimized, number=1000))
