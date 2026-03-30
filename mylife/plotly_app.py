import dash
from dash import dcc, html, dash_table, Input, Output
from django_plotly_dash import DjangoDash
from django.db.models import Sum
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
        dash_table.DataTable(
            id='category-table',
            columns=[
                {'name': 'Category', 'id': 'Category'},
                {'name': 'Total', 'id': 'Total'},
                {'name': 'Percentage', 'id': 'Percentage'}
            ],
            style_table={'width': '100%'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            page_action='none',
        ),
    ], style={'flex': '1', 'minHeight': '0', 'display': 'flex', 'flexDirection': 'column', 'overflowY': 'auto'}),
    dcc.Store(id='store'),
], style={'display': 'flex', 'flexDirection': 'column', 'height': '100%', 'width': '100%', 'overflowY': 'auto'})

@app.callback(
    Output('category-table', 'data'),
    Input('store', 'data'),
    prevent_initial_call=False
)
def update_table(data):
    return get_category_data()
