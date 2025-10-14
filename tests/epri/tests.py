from pyUL1741SB.UL1741SB import UL1741SB
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import pandas as pd
import plotly
pd.options.plotting.backend = "plotly"
import plotly.graph_objs as go
from plotly.subplots import make_subplots

std = UL1741SB()
eut = EpriEut()
env = EpriEnv(eut)

def test_cpf():
    std.cpf_proc(env=env, eut=eut)
    results = env.results['cpf'].iloc[:, :-1]
    df = pd.concat(env.results['cpf'].loc[:, 'data'].values)
    plotly.offline.plot(df.plot(), filename='tests/epri/results/cpf.html')
    assert env.results['cpf'].loc[:, 'ss_valid'].all()
    assert env.results['cpf'].loc[:, 'olrt_valid'].all()

def test_crp():
    std.crp_proc(env=env, eut=eut)
    results = env.results['crp'].iloc[:, :-1]
    df = pd.concat(env.results['crp'].loc[:, 'data'].values)
    plotly.offline.plot(df.plot(), filename='tests/epri/results/crp.html')
    assert env.results['crp'].loc[:, 'ss_valid'].all()
    assert env.results['crp'].loc[:, 'olrt_valid'].all()

def test_vv():
    std.vv_proc(env=env, eut=eut)
    results = env.results['vv'].iloc[:, :-1]
    df = pd.concat(env.results['vv'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['V'], name='V'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/vv.html')
    assert env.results['vv'].loc[:, 'ss_valid'].all()
    assert env.results['vv'].loc[:, 'olrt_valid'].all()

def test_vv_vref():
    std.vv_vref_proc(env=env, eut=eut)
    results = env.results['vv-vref'].iloc[:, :-1]
    df = pd.concat(env.results['vv-vref'].loc[:, 'data'].values)

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/vv-vref.html')
    assert env.results['vv-vref'].loc[:, 'valid'].all()

def test_wv():
    std.wv_proc(env=env, eut=eut)
    results = env.results['wv'].iloc[:, :-1]
    df = pd.concat(env.results['wv'].loc[:, 'data'].values)
    plotly.offline.plot(df.plot(), filename='tests/epri/results/wv.html')
    assert env.results['wv'].loc[:, 'ss_valid'].all()
    assert env.results['wv'].loc[:, 'olrt_valid'].all()

def test_vw():
    # TODO should meet criteria with 1.5 * tMRA accounted for for olrt validation
    std.vw_proc(env=env, eut=eut)
    results = env.results['vw'].iloc[:, :-1]
    df = pd.concat(env.results['vw'].loc[:, 'data'].values)
    plotly.offline.plot(df.plot(), filename='tests/epri/results/vw.html')
    assert env.results['vw'].loc[:, 'ss_valid'].all()
    assert env.results['vw'].loc[:, 'olrt_valid'].all()

def test_fwo():
    std.fwo_proc(env=env, eut=eut)
    results = env.results['fwo'].iloc[:, :-1]
    df = pd.concat(env.results['fwo'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['F'], name='F'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/fwo.html')
    assert env.results['fwo'].loc[:, 'ss_valid'].all()
    assert env.results['fwo'].loc[:, 'olrt_valid'].all()

def test_fwu():
    std.fwu_proc(env=env, eut=eut)
    results = env.results['fwu'].iloc[:, :-1]
    df = pd.concat(env.results['fwu'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['F'], name='F'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/fwu.html')
    assert env.results['fwu'].loc[:, 'ss_valid'].all()
    assert env.results['fwu'].loc[:, 'olrt_valid'].all()

def test_pri():
    std.pri_proc(env=env, eut=eut)
    results = env.results['pri'].iloc[:, :-1]
    df = pd.concat(env.results['pri'].loc[:, 'data'].values)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['V'], name='V'), row=2, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['F'], name='F'), row=3, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/pri.html')
    assert env.results['pri'].loc[:, 'p_valid'].all()
    assert env.results['pri'].loc[:, 'q_valid'].all()

def test_lap():
    std.lap_proc(env=env, eut=eut)
    results = env.results['lap'].iloc[:, :-1]
    df = pd.concat(env.results['lap'].loc[:, 'data'].values)
    plotly.offline.plot(df.plot(), filename='tests/epri/results/lap.html')
    assert env.results['lap'].loc[:, 'ss_valid'].all()

def test_es_ramp():
    std.es_ramp_proc(env=env, eut=eut)
    results = env.results['es-ramp'].iloc[:, :-1]
    df = pd.concat(env.results['es-ramp'].loc[:, 'data'].values)

    fig = make_subplots(rows=4, cols=1)
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Trace(x=df.index, y=df[col], name=col), row=i+1, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/es-ramp.html')
    assert env.results['es-ramp'].loc[:, 'valid'].all()

def test_uvt():
    std.uvt_proc(env=env, eut=eut)
    results = env.results['uvt'].iloc[:, :-1]
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_ovt():
    std.ovt_proc(env=env, eut=eut)
    results = env.results['ovt'].iloc[:, :-1]
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_uft():
    std.uft_proc(env=env, eut=eut)
    results = env.results['uft'].iloc[:, :-1]
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_oft():
    std.oft_proc(env=env, eut=eut)
    results = env.results['oft'].iloc[:, :-1]
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_lvrt():
    std.lvrt_proc(env=env, eut=eut)
    results = env.results['lvrt'].iloc[:, :-1]
    df = pd.concat(env.results['lvrt'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['V'], name='V'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/lvrt.html')
    assert env.results['lvrt'].loc[:, 'valid'].all()

def test_hvrt():
    std.hvrt_proc(env=env, eut=eut)
    results = env.results['hvrt'].iloc[:, :-1]
    df = pd.concat(env.results['hvrt'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['V'], name='V'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/hvrt.html')
    assert env.results['hvrt'].loc[:, 'valid'].all()

def test_lfrt():
    std.lfrt_proc(env=env, eut=eut)
    results = env.results['lfrt'].iloc[:, :-1]
    df = pd.concat(env.results['lfrt'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['F'], name='F'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/lfrt.html')
    assert env.results['lfrt'].loc[:, 'valid'].all()

def test_hfrt():
    std.hfrt_proc(env=env, eut=eut)
    results = env.results['hfrt'].iloc[:, :-1]
    df = pd.concat(env.results['hfrt'].loc[:, 'data'].values)

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Trace(x=df.index, y=df['P'], name='P'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['Q'], name='Q'), row=1, col=1)
    fig.add_trace(go.Trace(x=df.index, y=df['F'], name='F'), row=2, col=1)
    plotly.offline.plot(fig, filename='tests/epri/results/hfrt.html')
    assert env.results['hfrt'].loc[:, 'valid'].all()
