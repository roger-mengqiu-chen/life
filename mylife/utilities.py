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
