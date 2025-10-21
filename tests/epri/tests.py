import pytest

from pyUL1741SB import UL1741SB
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import pandas as pd
import plotly
pd.options.plotting.backend = "plotly"
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import datetime


palette = {
    False: 'rgba(155, 55, 55, 0.05)',
    True: 'rgba(55, 155, 55, 0.05)',
}

def drawfig(fig, df, dct_traces, labelfcn, pfcols, epoch=False):
    df_data = pd.concat(df.loc[:, 'data'].values)
    for k, v in dct_traces.items():
        fig.add_trace(go.Scatter(x=df_data.index, y=df_data[k], name=k, mode='lines', opacity=.5), row=v, col=1)
    if epoch:
        for i, row in df.iterrows():
            start = row['data'].index[0]
            end = row['data'].index[-1]
            label = labelfcn(row)
            fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0.2, annotation_textangle=90,
                          annotation_position='top left', fillcolor=palette[all(row[pfcol] for pfcol in pfcols)])
    fig.update_xaxes(tickformat="%H:%M:%S.%2f")
    return fig

@pytest.fixture
def std():
    eut = EpriEut()
    env = EpriEnv(eut)
    std = UL1741SB(env, eut)
    return std

def test_pri_corruption(std):
    std.vv_vref_proc()
    std.vw_proc()
    std.pri_proc()
    proc = 'pri'
    lst_labels = ['vars_ctrl', 'step']
    pfcols = ['p_valid', 'q_valid']
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2, 'F': 3, 'p_target': 1, 'q_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_uvt_nrst(std):
    std.lap_proc()
    ts = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    print('\n')
    print(ts)
    std.uvt_proc()
    proc = 'uvt'
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_cpf(std):
    std.cpf_proc()
    proc = 'cpf'
    lst_labels = ['Vin', 'PF', 'Step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    dct_traces = {'Q': 1, 'P': 1, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_crp(std):
    std.crp_proc()
    proc = 'crp'
    lst_labels = ['Qset', 'Vin', 'Step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    dct_traces = {'Q': 1, 'P': 1, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vv(std):
    std.vv_proc()
    proc = 'vv'
    lst_labels = ['crv', 'step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'Q': 1, 'V': 2, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=False)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vv_vref(std):
    std.vv_vref_proc()
    proc = 'vv-vref'
    lst_labels = ['Tref', 'step']
    pfcols = ['valid']
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    dct_traces = {'Q': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_wv(std):
    std.wv_proc()
    proc = 'wv'
    lst_labels = ['crv', 'dir', 'step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    dct_traces = {'Q': 1, 'P': 1, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=False)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vw(std):
    # TODO should meet criteria with 1.5 * tMRA accounted for for olrt validation
    std.vw_proc()
    proc = 'vw'
    lst_labels = ['pwr', 'crv', 'step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'V': 1, 'P': 2, 'y_target': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=False)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_fwo(std):
    std.fwo_proc()
    proc = 'fwo'
    lst_labels = ['crv', 'pwr_pu', 'step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'F': 2, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=False)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_fwu(std):
    std.fwu_proc()
    proc = 'fwu'
    lst_labels = ['crv', 'pwr_pu', 'step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'F': 2, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=False)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_pri(std):
    std.pri_proc()
    proc = 'pri'
    lst_labels = ['vars_ctrl', 'step']
    pfcols = ['p_valid', 'q_valid']
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2, 'F': 3, 'p_target': 1, 'q_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_lap(std):
    std.lap_proc()
    proc = 'lap'
    lst_labels = ['iter', 'aplim_pu', 'step']
    pfcols = ['ss_valid']
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'y_target': 1}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_es_ramp(std):
    std.es_ramp_proc()
    proc = 'es-ramp'
    lst_labels = ['case', 'step']
    pfcols = ['valid']
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'F': 2, 'V': 3}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_uvt(std):
    std.uvt_proc()
    proc = 'uvt'
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_ovt(std):
    std.ovt_proc()
    proc = 'ovt'
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_uft(std):
    std.uft_proc()
    proc = 'uft'
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_oft(std):
    std.oft_proc()
    proc = 'oft'
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')
    assert results.loc[:, 'ceased'].all()
    # assert results.loc[:, 'tripped'].all()

def test_lvrt(std):
    std.lvrt_proc()
    proc = 'lvrt'
    lst_labels = ['pwr_pu', 'cond']
    pfcols = ['valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_hvrt(std):
    std.hvrt_proc()
    proc = 'hvrt'
    lst_labels = ['pwr_pu', 'cond']
    pfcols = ['valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_lfrt(std):
    std.lfrt_proc()
    proc = 'lfrt'
    lst_labels = ['iter', 'step']
    pfcols = ['valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'F': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_hfrt(std):
    std.hfrt_proc()
    proc = 'hfrt'
    lst_labels = ['iter', 'step']
    pfcols = ['valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'F': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()
