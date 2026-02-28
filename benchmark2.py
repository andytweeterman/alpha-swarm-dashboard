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

def original():
    c_d = c_data[c_data.index >= start_filter]
    a = l_cone[l_cone.index >= start_filter]
    b = u_cone[u_cone.index >= start_filter]
    c = ppo[ppo.index >= c_d.index[0]]
    d = sig[sig.index >= c_d.index[0]]
    e = hist[hist.index >= c_d.index[0]]
    f = ['#00ff00' if v >= 0 else '#ff0000' for v in hist[hist.index >= c_d.index[0]]]

def optimized():
    c_d = c_data[c_data.index >= start_filter]
    sub_l_cone = l_cone.loc[c_d.index]
    sub_u_cone = u_cone.loc[c_d.index]
    sub_ppo = ppo.loc[c_d.index]
    sub_sig = sig.loc[c_d.index]
    sub_hist = hist.loc[c_d.index]
    f = ['#00ff00' if v >= 0 else '#ff0000' for v in sub_hist]

def optimized2():
    mask = c_data.index >= start_filter
    c_d = c_data.loc[mask]
    sub_l_cone = l_cone.loc[mask]
    sub_u_cone = u_cone.loc[mask]
    sub_ppo = ppo.loc[mask]
    sub_sig = sig.loc[mask]
    sub_hist = hist.loc[mask]
    f = ['#00ff00' if v >= 0 else '#ff0000' for v in sub_hist]

print("Original:", timeit.timeit(original, number=1000))
print("Optimized (loc[index]):", timeit.timeit(optimized, number=1000))
print("Optimized2 (loc[mask]):", timeit.timeit(optimized2, number=1000))
