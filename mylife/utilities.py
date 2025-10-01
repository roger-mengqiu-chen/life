import plotly
import plotly.graph_objects as go
import json


def load_pie_chart(df):
    pie = go.Pie(
        labels=df['label'],
        values=df['value'],
        hoverinfo='label+percent+value',
        textinfo='label+percent',
        textposition='inside',
    )

    fig = go.Figure(data=[pie])
    fig.update_layout(
        showlegend=True,
        width=700,
        height=600,
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def load_line_chart(df):
    fig = go.Figure(
        [go.Scatter(
            x=df['date'],
            y=df['value'],
        )]
    )
    fig.update_yaxes(
        tickformat=',.2f',
    )

    fig.update_layout(
        width=1500,
        height=700
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
