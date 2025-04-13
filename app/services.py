from datetime import datetime, timedelta
import pandas

from .models import Transaction, History


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


def get_histories():
    values = History.objects.all().values('date', 'existing_sum', 'investment_sum')
    df = pandas.DataFrame(values)
    df['date'] = df.apply(
        lambda x: x['date'].strftime('%Y-%m-%d'), axis=1
    )
    
    networth_df = df[['date', 'existing_sum']]
    networth_df.rename(columns={'existing_sum': 'net_worth'}, inplace=True)
    investment_df = df[['date', 'investment_sum']]
    return networth_df.to_dict(orient='records'), investment_df.to_dict(orient='records')
