from datetime import datetime, timedelta
import pandas

from .models import Transaction


def get_last_month_trans_df():
    today = datetime.today()
    this_month = today.replace(day=1).date()
    last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1).date()
    last_month_expense = list(Transaction.objects.filter(
        transaction_time__gte=last_month,
        transaction_time__lte=this_month,
    ).exclude(
        transaction_type__name__iexact='wire transfer'
    ).values_list(
        'category__name',
        'category__color',
        'amount',
        'transaction_type__name'
    ))
    df = pandas.DataFrame(last_month_expense, columns=['category', 'colocr',
                                                       'amount', 'transaction_type'])
    return df


def calculate_expense(df):
    result_df = df[df['transaction_type'].str.lower() == 'expense']
    result_df = result_df.drop(columns=['transaction_type'])
    category_sum = result_df.groupby('category')['amount'].sum()
    category_sum = category_sum.reset_index()
    return category_sum.to_dict(orient='records')


def calculate_income(df):
    result_df = df[df['transaction_type'].str.lower() == 'income']
    result_df = result_df.drop(columns=['transaction_type'])
    category_sum = result_df.groupby('category')['amount'].sum()
    category_sum = category_sum.reset_index()
    return category_sum.to_dict(orient='records')
