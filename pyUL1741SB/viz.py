import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots

boolean_palette = {
    False: 'rgba(215, 25, 25, 0.05)',
    True: 'rgba(25, 215, 25, 0.05)',
}

dct_trace_order = {
    'P': 1,
    'Q': 2,
    'V': 3,
    'F': 4,
}

def draw_pqvf(fig, df_meas):
    for trace in ['P', 'Q', 'V', 'F']:
        fig.add_trace(
            go.Scatter(
                x=df_meas.index, y=df_meas[trace], name=trace, mode='lines', opacity=.5,
                hovertemplate="Value: %{y:.1f}"
            ),
            row=dct_trace_order[trace], col=1
        )

def draw_crit(fig, dct_df_crit):
    for trace, df in dct_df_crit.items():
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
                hovertemplate="Time: %{x|%H:%M:%S.%2f}<br>Value: %{y:.0f}"
            ),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['min'],
                name=f'{trace} max', mode='lines', opacity=.2, hoveron="points",
                line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
            ),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['max'],
                name=f'{trace} min', mode='lines', opacity=.2, hoveron="points", fill='tonexty',
                fillcolor='rgba(0, 0, 0, 0.1)', line_color="rgba(0, 0, 0, 0.2)", hovertemplate="Value: %{y:.0f}",
            ),
            row=row, col=1,
        )

def draw_epochs(fig, lst_epochs):
    for epoch in lst_epochs:
        start = epoch['start']
        end = epoch['end']
        label = epoch['label']
        passed = epoch['passed']
        fig.add_vrect(x0=start, x1=end, annotation_text=label, line_width=0.2, annotation_textangle=90,
                      annotation_position='top left', fillcolor=boolean_palette[passed],
                      row=1, col=1)

def draw_new(name, df_meas, dct_df_crit, lst_epochs, outdir):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True)

    # self.epochs = []  # {'start': ts, 'end': ts, 'label': string, 'passed': bool}
    # self.meas = []  # df ts-index P Q V F
    # self.crit = {}  # one or multiple of P, Q, V, F. df ts-index min targ max
    draw_pqvf(fig, df_meas)
    draw_crit(fig, dct_df_crit)
    draw_epochs(fig, lst_epochs)

    fig.update_xaxes(tickformat="%H:%M:%S.%2f")
    fig.update_layout(
        title=dict(text=name),
        plot_bgcolor='rgba(245, 245, 245)',
        hovermode="x"
    )

    plotly.offline.plot(fig, filename=f'{outdir}{name}.html')

