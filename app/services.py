from datetime import datetime, timedelta
import pandas

from .models import Transaction, History, Investment


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
    df = pandas.DataFrame(last_month_expense, columns=['category', 'color',
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
    df.rename(columns={'existing_sum': 'net_worth'}, inplace=True)

    networth_df = df[['date', 'net_worth']]
    investment_df = df[['date', 'investment_sum']]
    return networth_df.to_dict(orient='records'), investment_df.to_dict(orient='records')


def get_investment_by_account_due_date():
    values = Investment.objects.all().values('account__name', 'due_date', 'amount')
    df = pandas.DataFrame(values)
    df['year'] = df.apply(
        lambda x: x['due_date'].strftime('%Y'), axis=1
    )
    df['month'] = df.apply(
        lambda x: x['due_date'].strftime('%m'), axis=1
    )
    df.drop(columns=['due_date'], inplace=True)
    df.rename(columns={'account__name': 'account'}, inplace=True)
    return df.to_dict(orient='records')


def get_utility_df_for_queryset(queryset):
    values = queryset.values('year', 'month', 'days', 'cost_per_unit', 'usage')
    df = pandas.DataFrame(values)
    df['date'] = df.apply(
        lambda x: f'{int(x["year"])}-{int(x["month"])}', axis=1
    )
    df.drop(columns=['year', 'month'], inplace=True)
    return df.to_dict(orient='records')
