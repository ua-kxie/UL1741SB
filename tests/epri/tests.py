import pytest

from pyUL1741SB import UL1741SB
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import pandas as pd
import plotly
pd.options.plotting.backend = "plotly"
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import datetime as dt
import numpy as np


palette = {
    False: 'rgba(155, 55, 55, 0.05)',
    True: 'rgba(55, 155, 55, 0.05)',
}

def drawfig(fig, df, titletext, dct_traces, labelfcn, pfcols, dct_yranges, epoch=False):
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    df_data = pd.concat(df.loc[:, 'data'].values)
    df_results = df.iloc[:, :-1]

    ts_vrange_min = pd.concat([
        df_results.loc[:, ['t_init', 'y_init']].rename(columns={"t_init": "t", "y_init": "y"}),
        df_results.loc[:, ['t_olrt', 'y_olrt_min']].rename(columns={"t_olrt": "t", "y_olrt_min": "y"}),
        df_results.loc[:, ['t_ss0', 'y_ss_min']].rename(columns={"t_ss0": "t", "y_ss_min": "y"}),
        df_results.loc[:, ['t_ss1', 'y_ss_min']].rename(columns={"t_ss1": "t", "y_ss_min": "y"}),
    ]).set_index('t').sort_index()
    ts_vrange_max = pd.concat([
        df_results.loc[:, ['t_init', 'y_init']].rename(columns={"t_init": "t", "y_init": "y"}),
        df_results.loc[:, ['t_olrt', 'y_olrt_max']].rename(columns={"t_olrt": "t", "y_olrt_max": "y"}),
        df_results.loc[:, ['t_ss0', 'y_ss_max']].rename(columns={"t_ss0": "t", "y_ss_max": "y"}),
        df_results.loc[:, ['t_ss1', 'y_ss_max']].rename(columns={"t_ss1": "t", "y_ss_max": "y"}),
    ]).set_index('t').sort_index()
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ts_vrange_min.index, ts_vrange_max.index[::-1]]), y=pd.concat([ts_vrange_min['y'], ts_vrange_max['y'][::-1]]),
            name='test', mode='lines', opacity=.2, fill='toself', hoveron='points',
            hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y}<extra></extra>"
        ),
        row=1, col=1,
    )
    # plot traces
    for k, v in dct_traces.items():
        fig.add_trace(
            go.Scatter(
                x=df_data.index, y=df_data[k], name=k, mode='lines', opacity=.5,
                hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y}<extra></extra>"
            ),
            row=v, col=1
        )
    # mark epochs
    if epoch:
        for i, row in df.iterrows():
            start = row['data'].index[0]
            end = row['data'].index[-1]
            label = labelfcn(row)
            fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0.2, annotation_textangle=90,
                          annotation_position='top left', fillcolor=palette[all(row[pfcol] for pfcol in pfcols)])
    fig.update_xaxes(tickformat="%H:%M:%S.%2f")
    fig.update_layout(
        title=dict(text=titletext),
        plot_bgcolor='rgba(245, 245, 245)'
    )
    plotly.offline.plot(fig, filename=f'tests/epri/results/test.html')
    return fig

class EpriStd(UL1741SB):
    def __init__(self, env, eut):
        super().__init__(env, eut)

        self.mra_scale = 1.5  # 1.5 in standard
        self.trip_rpt = 5  # 5 in standard

    def conn_to_grid(self):
        # vdc to nom
        # vgrid to std
        pass

    def trip_rst(self):
        # return to continuous op after tripping
        # set VDC, (Vg) to 0
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_eut.dc_config(Vdc=0)
        # wait 1 second
        self.c_env.sleep(dt.timedelta(seconds=1))
        # set VDC to nominal
        self.c_eut.dc_config(Vdc=self.c_eut.Vin_nom)
        self.c_env.log(msg='waiting for re-energization...')
        while self.c_env.meas_single('P').iloc[0, 0] < self.c_eut.Prated * 0.5:
            self.c_env.sleep(dt.timedelta(seconds=1))
        return None

@pytest.fixture
def std():
    eut = EpriEut()
    env = EpriEnv(eut)
    std = EpriStd(env, eut)
    return std

def rtest_pri_corruption(std):
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
    fig = drawfig(fig, std.c_env.results[proc], '', dct_traces, labelfcn, pfcols, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def rtest_uvt_nrst(std):
    std.lap_proc()
    ts = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d %H:%M:%S")
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
    dct_traces = {'Q': 1, 'P': 1, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'CPF y(x) = Q(P)'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=True)

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
    dct_traces = {'Q': 1, 'P': 1, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'CRP y(x) = Q'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=True)
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
    dct_traces = {'Q': 1, 'V': 2, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'VV y(x) = Q(V)'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=False)
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
    title = 'VV-vref'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
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
    dct_traces = {'Q': 1, 'P': 1, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'WV y(x) = P(Q)'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=False)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vw(std):
    std.vw_proc()
    proc = 'vw'
    lst_labels = ['pwr', 'crv', 'step']
    pfcols = ['ss_valid', 'olrt_valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'V': 2, 'P': 1, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'VW y(x) = P(V)'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=False)
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
    dct_traces = {'P': 1, 'F': 2, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'FWO y(x) = W(F)'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=False)
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
    dct_traces = {'P': 1, 'F': 2, 'y_ss_target': 1}
    dct_yranges = {'y_ss_range': ('y_min', 'y_max', 1)}
    title = 'FWU y(x) = W(F)'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=False)
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
    dct_traces = {'P': 1, 'Q': 1, 'V': 2, 'F': 3, 'p_ss_target': 1, 'q_ss_target': 1}
    dct_yranges = {'p_ss_target': ('p_min', 'p_max', 1), 'q_ss_target': ('q_min', 'q_max', 1)}
    title = 'PRI'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=True)
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
    dct_traces = {'P': 1, 'y_ss_target': 1}
    dct_yranges = {'y_ss_target': ('y_min', 'y_max', 1)}
    title = 'PRI'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges, epoch=True)
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
    title = 'ES-ramp'

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], title, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_uvt(std):
    std.uvt_proc()
    proc = 'uvt'
    lst_labels = ['region', 'time', 'mag', 'iter']
    pfcols = ['ceased']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_ovt(std):
    std.ovt_proc()
    proc = 'ovt'
    lst_labels = ['region', 'time', 'mag', 'iter']
    pfcols = ['ceased']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_uft(std):
    std.uft_proc()
    proc = 'uft'
    lst_labels = ['region', 'time', 'mag', 'iter']
    pfcols = ['ceased']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'F': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_oft(std):
    std.oft_proc()
    proc = 'oft'
    lst_labels = ['region', 'time', 'mag', 'iter']
    pfcols = ['ceased']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'F': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_lvrt(std):
    std.lvrt_proc()
    proc = 'lvrt'
    lst_labels = ['pwr_pu', 'cond']
    pfcols = ['valid']
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    dct_traces = {'P': 1, 'Q': 1, 'V': 2}

    results = std.c_env.results[proc].iloc[:, :-1]
    labelfcn = lambda row: eval(f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
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
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
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
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
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
    fig = drawfig(fig, std.c_env.results[proc], proc, dct_traces, labelfcn, pfcols, dct_yranges={}, epoch=True)
    plotly.offline.plot(fig, filename=f'tests/epri/results/{proc}.html')
    results.to_csv(f'tests/epri/results/{proc}.csv')

    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()
