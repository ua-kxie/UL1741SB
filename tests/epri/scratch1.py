from pyUL1741SB.UL1741SB import UL1741SB
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import pandas as pd
import plotly
pd.options.plotting.backend = "plotly"
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import itertools

std = UL1741SB()
eut = EpriEut()
env = EpriEnv(eut)

palette = itertools.cycle([
    'rgba(255, 0, 0, 0.2)',
    'rgba(0, 255, 0, 0.2)',
    'rgba(0, 0, 255, 0.2)',
])

std.cpf_proc(env=env, eut=eut)
results = env.results['cpf'].iloc[:, :-1]
df = pd.concat(env.results['cpf'].loc[:, 'data'].values)

fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
dct_traces = {'Q': 1, 'P': 1, 'target': 1}
for k, v in dct_traces.items():
    fig.add_trace(go.Scatter(x=df.index, y=df[k], name=k, mode='lines'), row=v, col=1)
for i, row in env.results['cpf'].iterrows():
    start = row['data'].index[0]
    end = row['data'].index[-1]
    label = f"vin: {row['Vin']}; PF: {row['PF']}; step: {row['Step']}"
    fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0, annotation_textangle=90,
                  annotation_position='top right', fillcolor=next(palette))
plotly.offline.plot(fig, filename='results/cpf.html')

assert env.results['cpf'].loc[:, 'ss_valid'].all()
assert env.results['cpf'].loc[:, 'olrt_valid'].all()