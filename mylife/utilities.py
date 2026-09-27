import json
from datetime import datetime
from html import escape

import pandas
import plotly
import plotly.express as px
import plotly.graph_objects as go


def load_event_map(events):
    """Map filtered events, combining hover details at shared coordinates."""
    locations = {}
    for event in events:
        lat, lng = event.location.lat, event.location.lng
        if lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
            continue
        title = escape(event.name or str(event.event_time.date()))
        notes = escape(event.notes or '').replace('\n', '<br>')
        details = f'<b>{title}</b>'
        if notes:
            details += f'<br>{notes}'
        locations.setdefault((float(lat), float(lng)), []).append(details)

    if not locations:
        return None

    latitudes, longitudes = zip(*locations)
    fig = go.Figure(go.Scattermap(
        lat=latitudes,
        lon=longitudes,
        mode='markers',
        marker=dict(size=12, color='#417690'),
        text=['<br><br>'.join(details) for details in locations.values()],
        hovertemplate='%{text}<extra></extra>',
    ))
    fig.update_layout(
        map=dict(
            style='open-street-map',
            # Exact -180/180 endpoints wrap to the same longitude in Plotly.js
            # 3.1.0, collapsing the bounds and leaving the entire map blank.
            bounds=dict(west=-179.999, east=179.999, south=-85, north=85),
            center=dict(lat=(min(latitudes) + max(latitudes)) / 2,
                        lon=(min(longitudes) + max(longitudes)) / 2),
            zoom=1,
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        template=None,
    )
    return fig.to_dict()


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
        height=600,

        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        )
    )
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json


def load_line_chart(df):
    year_end = df['date'].max()
    start = (datetime.strptime(year_end, '%Y-%m-%d').date()
             - pandas.DateOffset(years=1))
    end = datetime.strptime(year_end, '%Y-%m-%d').date()

    fig = go.Figure(
        [go.Scatter(
            x=df['date'],
            y=df['value'],
        )]
    )

    fig.update_layout(
        yaxis=dict(
            tickformat=',.2f',
            fixedrange=False,
            autorange=True,
        ),
        xaxis=dict(
            range=[start, end],
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
    first_year_end = (datetime.strptime(first_year_start, '%Y-%m-%d').date()
                      + pandas.DateOffset(years=1))
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
            tickformat=',.2f',
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
