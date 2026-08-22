import dash
import plotly.graph_objs as go
from dash import dcc, html, dash_table, Input, Output
from django.db.models import Sum
from django_plotly_dash import DjangoDash

from mylife.models import TransactionCategory


def get_category_data():
    """Fetch and calculate category data with percentages"""
    try:
        categories_data = TransactionCategory.objects.filter(transaction__transaction_type__is_expense=True).annotate(
            total=Sum('transaction__amount')
        ).values('name', 'total').order_by('-total')

        # Calculate total and build data with percentages
        total_sum = sum(item['total'] or 0 for item in categories_data)
        data = []
        for item in categories_data:
            category_total = item['total'] or 0
            percentage = (category_total / total_sum * 100) if total_sum > 0 else 0
            data.append({
                'Category': item['name'],
                'Total': round(category_total, 2),
                'Percentage': f"{percentage:.2f}%"
            })
        return data
    except Exception as e:
        print(f"Error loading category data: {e}")
        return []


app = DjangoDash('SimpleExample')

app.layout = html.Div([
    html.Div([
        html.Button('Clear Selection', id='clear-selection-btn', n_clicks=0, style={'marginBottom': '12px'}),
        html.Div([
            html.Div([
                dash_table.DataTable(
                    id='category-table',
                    columns=[
                        {'name': 'Category', 'id': 'Category'},
                        {'name': 'Total', 'id': 'Total', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                        {'name': 'Percentage', 'id': 'Percentage'}
                    ],
                    style_table={'width': '100%', 'minWidth': '100%'},
                    style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'sans-serif'},
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    page_action='none',
                    row_selectable='multi',
                    selected_rows=[],
                ),
            ], style={
                'height': '500px',
                'overflowY': 'auto',
                'flex': '1',
                'border': '1px solid #eee',
                'backgroundColor': '#fff',
                'paddingRight': '8px',
            }),
            dcc.Graph(id='category-pie', style={'flex': '2', 'height': '100%'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'alignItems': 'flex-start',
                  'gap': '24px'}),
    ], style={'flex': '1', 'minHeight': '0', 'display': 'flex', 'flexDirection': 'column', 'overflowY': 'auto'}),
    dcc.Store(id='store'),
], style={'display': 'flex', 'flexDirection': 'column', 'height': '100%', 'width': '100%', 'overflowY': 'auto'})


# Callback to update table and pie chart
@app.callback(
    [
        Output('category-table', 'data'),
        Output('category-pie', 'figure')
    ],
    [
        Input('store', 'data'),
        Input('category-table', 'selected_rows')
    ],
    prevent_initial_call=False
)
def update_table_and_pie(data, selected_rows):
    category_data = get_category_data()
    # If any rows are selected, filter to those rows
    if selected_rows and len(selected_rows) > 0:
        filtered_data = [category_data[i] for i in selected_rows]
    else:
        filtered_data = category_data
    # Prepare pie chart
    if filtered_data:
        fig = go.Figure(data=[go.Pie(
            labels=[item['Category'] for item in filtered_data],
            values=[item['Total'] for item in filtered_data],
            textinfo='label+percent',
            hoverinfo='label+value+percent',
            textposition='inside',
        )])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=500)
    else:
        fig = go.Figure()
    return category_data, fig


# Callback to clear selection
@app.callback(
    Output('category-table', 'selected_rows'),
    Input('clear-selection-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_selection(n_clicks):
    if n_clicks:
        return []
    return dash.no_update
