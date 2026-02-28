import timeit
import pandas as pd
import numpy as np

# Setup realistic dummy data
n_rows = 1000
dates = pd.date_range(start='2020-01-01', periods=n_rows)
c_data = pd.DataFrame({'Open': np.random.randn(n_rows), 'High': np.random.randn(n_rows), 'Low': np.random.randn(n_rows), 'Close': np.random.randn(n_rows)}, index=dates)

# Simulated logic output
l_cone = pd.Series(np.random.randn(n_rows), index=dates)
u_cone = pd.Series(np.random.randn(n_rows), index=dates)
ppo = pd.Series(np.random.randn(n_rows), index=dates)
sig = pd.Series(np.random.randn(n_rows), index=dates)
hist = pd.Series(np.random.randn(n_rows), index=dates)

start_filter = '2022-01-01'
c_data = c_data[c_data.index >= start_filter]

def original():
    a = l_cone[l_cone.index >= start_filter]
    b = u_cone[u_cone.index >= start_filter]
    c = ppo[ppo.index >= c_data.index[0]]
    d = sig[sig.index >= c_data.index[0]]
    e = hist[hist.index >= c_data.index[0]]
    f = ['#00ff00' if v >= 0 else '#ff0000' for v in hist[hist.index >= c_data.index[0]]]

def optimized():
    sub_l_cone = l_cone[c_data.index]
    sub_u_cone = u_cone[c_data.index]
    sub_ppo = ppo[c_data.index]
    sub_sig = sig[c_data.index]
    sub_hist = hist[c_data.index]
    f = ['#00ff00' if v >= 0 else '#ff0000' for v in sub_hist]

print("Original:", timeit.timeit(original, number=1000))
print("Optimized:", timeit.timeit(optimized, number=1000))
