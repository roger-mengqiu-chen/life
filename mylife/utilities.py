from datetime import datetime, timedelta

import pandas
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json


def load_pie_chart(df):
    pie = go.Pie(
        labels=df['label'],
        values=df['value'],
        hoverinfo='label+percent+value',
        textinfo='label+percent+value',
        textposition='inside',
    )

    fig = go.Figure(data=[pie])
    fig.update_layout(
        showlegend=True,
        width=700,
        height=600,
    )
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json


def load_line_chart(df):
    first_year_start = df['date'].min()
    first_year_end = datetime.strptime(first_year_start, '%Y-%m-%d').date() + pandas.DateOffset(years=1)
    first_year_end = first_year_end.strftime('%Y-%m-%d')
    fig = go.Figure(
        [go.Scatter(
            x=df['date'],
            y=df['value'],
        )]
    )

    fig.update_layout(
        autosize=True,
        yaxis=dict(
            tickformat=',.2f',
            fixedrange=False,
            autorange=True,
        ),
        xaxis=dict(
            range=[first_year_start, first_year_end],
            rangeslider=dict(
                visible=True,
            ),
            type='date'
        )
    )
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json


def load_bar_chart(df):
    first_year_start = df['date'].min()
    first_year_end = datetime.strptime(first_year_start, '%Y-%m-%d').date() + pandas.DateOffset(years=1)
    first_year_end = first_year_end.strftime('%Y-%m-%d')
    fig = px.bar(
        df,
        x='date',
        y='value',
        color='account',
        barmode='stack',
    )

    fig.update_layout(
        yaxis=dict(
            tickformat=',',
        ),
        xaxis=dict(
            tickformat='%b %Y',
            dtick='M1',
            range=[first_year_start, first_year_end],
            rangeslider=dict(
                visible=True,
            )
        )
    )

    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json
