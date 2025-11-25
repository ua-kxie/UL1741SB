from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env

from pyUL1741SB.IEEE1547.VoltReg.cpf import CPF
from pyUL1741SB.IEEE1547.VoltReg.crp import CRP
from pyUL1741SB.IEEE1547.VoltReg.vv import VV
from pyUL1741SB.IEEE1547.VoltReg.vw import VW
from pyUL1741SB.IEEE1547.VoltReg.wv import WV
from pyUL1741SB.IEEE1547.FreqSupp import FreqSupp
from pyUL1741SB.IEEE1547.LimitAP import LAP
from pyUL1741SB.IEEE1547.RespPri import RespPri
from pyUL1741SB.IEEE1547.EnterService import ES
from pyUL1741SB.IEEE1547.VoltDistResp import VoltDist
from pyUL1741SB.IEEE1547.FreqDistResp import FreqDist
from pyUL1741SB.IEEE1547 import IEEE1547

from pyUL1741SB.eut import VoltShallTripTable
from pyUL1741SB.eut import FreqShallTripTable

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class UL1741SB(CPF, CRP, VV, VW, WV, FreqSupp, RespPri, LAP, ES, VoltDist, FreqDist, IEEE1547):
    pass


boolean_palette = {
    False: 'rgba(215, 25, 25, 0.05)',
    True: 'rgba(25, 215, 25, 0.05)',
}


class Post:
    def __init__(self, outdir):
        self.outdir = outdir

    def mintargmax(self, df_rslts, key):
        ini = f'{key}_init'
        olrtmin = f'{key}_olrt_min'
        ssmin = f'{key}_ss_min'
        olrtmax = f'{key}_olrt_max'
        ssmax = f'{key}_ss_max'
        olrt = f'{key}_olrt_target'
        ss = f'{key}_ss_target'
        dmin = pd.concat([
            df_rslts.loc[:, ['t_init', ini]].rename(
                columns={"t_init": "t", ini: "y"}),
            df_rslts.loc[:, ['t_olrt', olrtmin]].rename(
                columns={"t_olrt": "t", olrtmin: "y"}),
            df_rslts.loc[:, ['t_ss0', ssmin]].rename(
                columns={"t_ss0": "t", ssmin: "y"}),
            df_rslts.loc[:, ['t_ss1', ssmin]].rename(
                columns={"t_ss1": "t", ssmin: "y"}),
        ]).set_index('t').sort_index()
        targ = pd.concat([
            df_rslts.loc[:, ['t_init', ini]].rename(
                columns={"t_init": "t", ini: "y"}),
            df_rslts.loc[:, ['t_olrt', olrt]].rename(
                columns={"t_olrt": "t", olrt: "y"}),
            df_rslts.loc[:, ['t_ss0', ss]].rename(
                columns={"t_ss0": "t", ss: "y"}),
            df_rslts.loc[:, ['t_ss1', ss]].rename(
                columns={"t_ss1": "t", ss: "y"}),
        ]).set_index('t').sort_index()
        dmax = pd.concat([
            df_rslts.loc[:, ['t_init', ini]].rename(
                columns={"t_init": "t", ini: "y"}),
            df_rslts.loc[:, ['t_olrt', olrtmax]].rename(
                columns={"t_olrt": "t", olrtmax: "y"}),
            df_rslts.loc[:, ['t_ss0', ssmax]].rename(
                columns={"t_ss0": "t", ssmax: "y"}),
            df_rslts.loc[:, ['t_ss1', ssmax]].rename(
                columns={"t_ss1": "t", ssmax: "y"}),
        ]).set_index('t').sort_index()

        return dmin, targ, dmax

    def mintargmax_pri(self, df_rslts, key):
        ssmin = f'{key}_min'
        ssmax = f'{key}_max'
        ss = f'{key}_target'
        dmin = pd.concat([
            df_rslts.loc[:, ['t_ss0', ssmin]].rename(
                columns={"t_ss0": "t", ssmin: "y"}),
            df_rslts.loc[:, ['t_ss1', ssmin]].rename(
                columns={"t_ss1": "t", ssmin: "y"}),
            df_rslts.loc[:, ['t_ss2', ssmin]].rename(
                columns={"t_ss2": "t", ssmin: "y"}),
        ]).set_index('t').sort_index()
        targ = pd.concat([
            df_rslts.loc[:, ['t_ss0', ss]].rename(
                columns={"t_ss0": "t", ss: "y"}),
            df_rslts.loc[:, ['t_ss1', ss]].rename(
                columns={"t_ss1": "t", ss: "y"}),
            df_rslts.loc[:, ['t_ss2', ss]].rename(
                columns={"t_ss2": "t", ss: "y"}),
        ]).set_index('t').sort_index()
        dmax = pd.concat([
            df_rslts.loc[:, ['t_ss0', ssmax]].rename(
                columns={"t_ss0": "t", ssmax: "y"}),
            df_rslts.loc[:, ['t_ss1', ssmax]].rename(
                columns={"t_ss1": "t", ssmax: "y"}),
            df_rslts.loc[:, ['t_ss2', ssmax]].rename(
                columns={"t_ss2": "t", ssmax: "y"}),
        ]).set_index('t').sort_index()

        return dmin, targ, dmax

    def valid_range_by_key(self, fig, df_rslts, key, displayname):
        dmin, targ, dmax = self.mintargmax(df_rslts, key)
        fig.add_trace(
            go.Scatter(
                x=targ.index,
                y=targ['y'],
                error_y=dict(
                    type='data', symmetric=False,
                    arrayminus=targ['y'] - dmin['y'],
                    array=dmax['y'] - targ['y'],
                ),
                name=f'{displayname} target', mode='markers', opacity=.5, hoveron="points",
                hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y:.0f}"
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=dmax.index,
                y=dmax['y'],
                name=f'{displayname} max', mode='lines', opacity=.2, hoveron="points",
                line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=dmin.index,
                y=dmin['y'],
                name=f'{displayname} min', mode='lines', opacity=.2, hoveron="points", fill='tonexty',
                fillcolor='rgba(0, 0, 0, 0.1)', line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
            ),
            row=1, col=1,
        )

        return fig

    def valid_range_by_key_pri(self, fig, df_rslts, key, displayname, row):
        dmin, targ, dmax = self.mintargmax_pri(df_rslts, key)
        fig.add_trace(
            go.Scatter(
                x=targ.index,
                y=targ['y'],
                error_y=dict(
                    type='data', symmetric=False,
                    arrayminus=targ['y'] - dmin['y'],
                    array=dmax['y'] - targ['y'],
                ),
                name=f'{displayname} target', mode='markers', opacity=.5, hoveron="points+fills",
                hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y:.0f}"
            ),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=dmax.index,
                y=dmax['y'],
                name=f'{displayname} max', mode='lines', opacity=.2, hoveron="points",
                line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
            ),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=dmin.index,
                y=dmin['y'],
                name=f'{displayname} min', mode='lines', opacity=.2, hoveron="points", fill='tonexty',
                fillcolor='rgba(0, 0, 0, 0.1)', line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
            ),
            row=row, col=1,
        )
        return fig

    def common(self, name, fig, title):
        fig.update_xaxes(tickformat="%H:%M:%S.%2f")
        fig.update_layout(
            title=dict(text=title),
            plot_bgcolor='rgba(245, 245, 245)',
            hovermode="x"
        )
        plotly.offline.plot(fig, filename=f'{self.outdir}{name}.html')

    def draw_cpf_type(self, name, df, lst_traces, labelfcn, pfcols, titletext, yname):
        fig = make_subplots(rows=len(lst_traces), cols=1, shared_xaxes=True)
        df_data = pd.concat(df.loc[:, 'data'].values)
        df_rslts = df.iloc[:, :-1]

        fig = self.valid_range_by_key(fig, df_rslts, 'y', yname)
        # plot traces
        for i, traces in enumerate(lst_traces):
            for k in traces:
                fig.add_trace(
                    go.Scatter(
                        x=df_data.index, y=df_data[k], name=k, mode='lines', opacity=.5,
                        hovertemplate="Value: %{y:.2f}"
                    ),
                    row=i+1, col=1
                )
        # mark epochs
        for i, row in df.iterrows():
            start = row['data'].index[0]
            end = row['data'].index[-1]
            label = labelfcn(row)
            fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0.2, annotation_textangle=90,
                          annotation_position='top left',
                          fillcolor=boolean_palette[all(row[pfcol] for pfcol in pfcols)])

        self.common(name, fig, titletext)

    def draw_pri(self, name, df, lst_traces, labelfcn, pfcols, titletext):
        fig = make_subplots(rows=len(lst_traces), cols=1, shared_xaxes=True)
        df_data = pd.concat(df.loc[:, 'data'].values)
        df_rslts = df.iloc[:, :-1]

        # plot traces
        for i, traces in enumerate(lst_traces):
            for k in traces:
                if k == 'P':
                    fig = self.valid_range_by_key_pri(
                        fig, df_rslts, 'p', 'P', i + 1)
                if k == 'Q':
                    fig = self.valid_range_by_key_pri(
                        fig, df_rslts, 'q', 'Q', i + 1)
                fig.add_trace(
                    go.Scatter(
                        x=df_data.index, y=df_data[k], name=k, mode='lines', opacity=.5,
                        hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y:.0f}"
                    ),
                    row=i+1, col=1
                )
        # mark epochs
        for i, row in df.iterrows():
            start = row['data'].index[0]
            end = row['data'].index[-1]
            label = labelfcn(row)
            fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0.2, annotation_textangle=90,
                          annotation_position='top left',
                          fillcolor=boolean_palette[all(row[pfcol] for pfcol in pfcols)])

        self.common(name, fig, titletext)

    def draw_bare_type(self, name, df, lst_traces, titletext, yname):
        fig = make_subplots(rows=len(lst_traces), cols=1, shared_xaxes=True)
        df_data = pd.concat(df.loc[:, 'data'].values)
        df_rslts = df.iloc[:, :-1]

        fig = self.valid_range_by_key(fig, df_rslts, 'y', yname)
        # plot traces
        for i, traces in enumerate(lst_traces):
            for k in traces:
                fig.add_trace(
                    go.Scatter(
                        x=df_data.index, y=df_data[k], name=k, mode='lines', opacity=.5,
                        hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y:.0f}"
                    ),
                    row=i+1, col=1
                )

        self.common(name, fig, titletext)

    def draw_notarg_type(self, name, df, lst_traces, labelfcn, pfcols, titletext):
        fig = make_subplots(rows=len(lst_traces), cols=1, shared_xaxes=True)
        df_data = pd.concat(df.loc[:, 'data'].values)
        df_rslts = df.iloc[:, :-1]

        # plot traces
        for i, traces in enumerate(lst_traces):
            for k in traces:
                fig.add_trace(
                    go.Scatter(
                        x=df_data.index, y=df_data[k], name=k, mode='lines', opacity=.5,
                        hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y:.0f}"
                    ),
                    row=i+1, col=1
                )
        # mark epochs
        for i, row in df.iterrows():
            start = row['data'].index[0]
            end = row['data'].index[-1]
            label = labelfcn(row)
            fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0.2, annotation_textangle=90,
                          annotation_position='top left',
                          fillcolor=boolean_palette[all(row[pfcol] for pfcol in pfcols)])

        self.common(name, fig, titletext)

    def plot(self, proc, df, name):
        if proc == 'cpf':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['Vin', 'PF', 'Step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q']]
            title = 'CPF y(x) = Q(P)'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'Q')

        elif proc == 'crp':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['Qset', 'Vin', 'Step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q']]
            title = 'CRP y(x) = Q'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'Q')

        elif proc == 'vv':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['crv', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['Q'], ['V']]
            title = 'VV y(x) = Q(V)'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'Q')

        elif proc == 'vv-vref':
            pfcols = ['valid']
            lst_labels = ['Tref', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['Q']]
            title = 'VV-vref'
            self.draw_notarg_type(name, df, traces, labelfcn, pfcols, title)

        elif proc == 'wv':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['crv', 'dir', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q']]
            title = 'WV y(x) = Q(P)'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'Q')

        elif proc == 'vw-bare':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['pwr', 'crv', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P'], ['V']]
            title = 'VW y(x) = P(V)'
            self.draw_bare_type(name, df, traces, title, 'P')

        elif proc == 'vw':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['pwr', 'crv', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P'], ['V']]
            title = 'VW y(x) = P(V)'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'P')

        elif proc in ['fwo', 'fwu']:
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['crv', 'pwr_pu', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P'], ['F']]
            title = f'{proc.upper()} y(x) = P(F)'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'P')

        elif proc == 'pri':
            pfcols = ['p_valid', 'q_valid']
            lst_labels = ['vars_ctrl', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P'], ['Q'], ['V'], ['F']]
            title = 'PRI'
            self.draw_pri(name, df, traces, labelfcn, pfcols, title)

        elif proc == 'lap':
            pfcols = ['ss_valid', 'olrt_valid']
            lst_labels = ['iter', 'aplim_pu', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P']]
            title = 'LAP'
            self.draw_cpf_type(name, df, traces, labelfcn, pfcols, title, 'P')

        elif proc == 'es-ramp':
            pfcols = ['valid']
            lst_labels = ['case', 'step'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P'], ['F'], ['V']]
            title = 'ES (ramp)'
            self.draw_notarg_type(name, df, traces, labelfcn, pfcols, title)

        elif proc in ['uvt', 'ovt']:
            pfcols = ['ceased']
            lst_labels = ['region', 'time', 'mag', 'iter'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q'], ['V']]
            title = f'{proc.upper()}'
            self.draw_notarg_type(name, df, traces, labelfcn, pfcols, title)

        elif proc in ['uft', 'oft']:
            pfcols = ['ceased']
            lst_labels = ['region', 'time', 'mag', 'iter'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q'], ['F']]
            title = f'{proc.upper()}'
            self.draw_notarg_type(name, df, traces, labelfcn, pfcols, title)

        elif proc in ['lvrt', 'hvrt']:
            pfcols = ['valid']
            lst_labels = ['pwr_pu', 'cond'] + pfcols

            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q'], ['V']]
            title = f'{proc.upper()}'
            self.draw_notarg_type(name, df, traces, labelfcn, pfcols, title)

        elif proc in ['lfrt', 'hfrt']:
            pfcols = ['valid']
            lst_labels = ['iter', 'step'] + pfcols
            def labelfcn(row): return eval(
                f"""f'{''.join([f'{k}: {{row["{k}"]}}; ' for k in lst_labels])}'""")
            traces = [['P', 'Q'], ['F']]
            title = f'{proc.upper()}'
            self.draw_notarg_type(name, df, traces, labelfcn, pfcols, title)

        else:
            raise ValueError(f'Invalid proc: {proc} - typo or NotImplemented')

    def post(self, proc, df, name):
        self.plot(proc, df, name)
        results = df.iloc[:, :-1]
        results.to_csv(f'{self.outdir}{name}.csv')
