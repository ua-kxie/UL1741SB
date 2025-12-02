import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

boolean_palette = {
    False: 'rgba(215, 25, 25, 0.05)',
    True: 'rgba(25, 215, 25, 0.05)',
}

dct_trace_order = {
    'P': 'y1',
    'Q': 'y2',
    'V': 'y3',
    'F': 'y4',
}


class Validator:
    def __init__(self, proc):
        self.proc = proc

        # {'start': ts, 'end': ts, 'label': string, 'passed': bool}
        self.epochs = []
        self.meas = []  # df ts-index P Q V F
        # one or multiple of P, Q, V, F. df ts-index min targ max
        self.crit = {c: [] for c in ['P', 'Q', 'V', 'F']}

    def record_epoch(self, df_meas, dct_crits, **kwargs):
        self.meas.append(df_meas)
        for c in dct_crits:
            self.crit[c].append(dct_crits[c])
        # unpack/pack to check fields are correct
        self.epochs.append({
            'start': kwargs['start'],
            'end': kwargs['end'],
            'label': kwargs['label'],
            'passed': kwargs['passed']
        })

    def _draw_pqvf(self, fig):
        df_meas = pd.concat(self.meas)
        dct_trace_template = {
            'P': "Value: %{y:.0f}",
            'Q': "Value: %{y:.0f}",
            'V': "Value: %{y:.1f}",
            'F': "Value: %{y:.2f}",
        }
        for trace in ['P', 'Q', 'V', 'F']:
            fig.add_trace(
                go.Scatter(
                    x=df_meas.index, y=df_meas[trace], name=trace, mode='lines', opacity=.5,
                    hovertemplate=dct_trace_template[trace],
                    yaxis=dct_trace_order[trace]
                ),
            )

    def _draw_crit(self, fig):
        dct_lst_df_crit = self.crit
        for trace, lst in dct_lst_df_crit.items():
            if len(lst) == 0:
                continue
            df = pd.concat(lst)
            # draw min
            row = dct_trace_order[trace]
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['targ'],
                    error_y=dict(
                        type='data', symmetric=False,
                        arrayminus=df['targ'] - df['min'],
                        array=df['max'] - df['targ'],
                    ),
                    name=f'{trace} target', mode='markers', opacity=.5, hoveron="points",
                    hovertemplate="Time: %{x|%H:%M:%S.%L}<br>Value: %{y:.0f}",
                    yaxis=dct_trace_order[trace]
                ),
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['min'],
                    name=f'{trace} max', mode='lines', opacity=.2, hoveron="points",
                    line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
                    yaxis=dct_trace_order[trace]
                ),
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['max'],
                    name=f'{trace} min', mode='lines', opacity=.2, hoveron="points", fill='tonexty',
                    fillcolor='rgba(0, 0, 0, 0.1)', line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
                    yaxis=dct_trace_order[trace]
                ),
            )

    def _draw_epochs(self, fig, domains):
        lst_epochs = self.epochs
        for epoch in lst_epochs:
            start = epoch['start']
            end = epoch['end']
            label = epoch['label']
            passed = epoch['passed']
            fillcolor = boolean_palette[passed]
            fig.add_shape(
                type="rect",
                x0=start, x1=end, y0=domains['y1d'][0], y1=domains['y1d'][1],
                line_width=0.2,
                fillcolor=fillcolor,
                yref="paper"
            )
            fig.add_shape(
                type="rect",
                x0=start, x1=end, y0=domains['y2d'][0], y1=domains['y2d'][1],
                line_width=0.2,
                fillcolor=fillcolor,
                yref="paper"
            )
            fig.add_shape(
                type="rect",
                x0=start, x1=end, y0=domains['y3d'][0], y1=domains['y3d'][1],
                line_width=0.2,
                fillcolor=fillcolor,
                yref="paper"
            )
            fig.add_shape(
                type="rect",
                x0=start, x1=end, y0=domains['y4d'][0], y1=domains['y4d'][1],
                line_width=0.2,
                fillcolor=fillcolor,
                yref="paper"
            )
            fig.add_annotation(
                x=start, y=domains['y1d'][1], yref="paper", text=label,
                textangle=90, showarrow=False, xanchor="left", yanchor="top"
            )

    def draw_new(self, outdir):
        pq_heights = [0.35, 0.35, 0.15, 0.15]
        p_heights = [0.55, 0.15, 0.15, 0.15]
        q_heights = [0.15, 0.55, 0.15, 0.15]
        if self.proc in ['cpf', 'crp', 'wv', 'vv', 'vv-vref']:
            heights = q_heights
        elif self.proc in ['lap', 'vw', 'vw-1pu', 'vw-pu66', 'vw-pu20', 'fwo', 'fwu']:
            heights = p_heights
        else:
            heights = pq_heights

        # get domain size
        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True, row_heights=heights)
        domains = dict(
            y1d=fig.layout.yaxis.domain,
            y2d=fig.layout.yaxis2.domain,
            y3d=fig.layout.yaxis3.domain,
            y4d=fig.layout.yaxis4.domain
        )

        # make subplots using go.Figure - make subplots don't work with hover subplots
        layout = dict(
            grid=dict(rows=4, columns=1),
            title=self.proc.upper(),
            plot_bgcolor='rgba(245, 245, 245)',
            hoversubplots="axis",
            hovermode="x",
            yaxis=dict(domain=domains['y1d'], anchor='x'),
            yaxis2=dict(domain=domains['y2d'], anchor='x'),
            yaxis3=dict(domain=domains['y3d'], anchor='x'),
            yaxis4=dict(domain=domains['y4d'], anchor='x'),
            xaxis=dict(title="Time", ticks='outside', anchor='y4',
                       hoverformat='%H:%M:%S.%L', tickformat='%H:%M:%S'),
        )
        fig = go.Figure(layout=layout)

        # self.epochs = []  # {'start': ts, 'end': ts, 'label': string, 'passed': bool}
        # self.meas = []  # df ts-index P Q V F
        # self.crit = {}  # one or multiple of P, Q, V, F. df ts-index min targ max
        self._draw_pqvf(fig)
        self._draw_crit(fig)
        self._draw_epochs(fig, domains)

        plotly.offline.plot(fig, filename=f'{outdir}{self.proc}.html')
