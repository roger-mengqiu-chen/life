import pandas
import requests
from django.conf import settings
from django.db import connection

from .models import Transaction, History, Currency, CurrencyHistory


def get_trans_df(request):
    dict_query = request.GET.dict()
    dict_query.pop('p', None)
    dict_query.pop('o', None)
    dict_query.pop('all', None)

    dict_query['transaction_time__gte'] = (
        dict_query.pop('transaction_time__range__gte', None))
    dict_query['transaction_time__lte'] = (
        dict_query.pop('transaction_time__range__lte', None))
    kwargs = {}
    for k, v in dict_query.items():
        if v is not None and v != '':
            kwargs[k] = v

    last_month_expense = list(Transaction.objects.filter(**kwargs).exclude(
        transaction_type__is_transfer=True
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
    return category_sum


def calculate_income(df):
    result_df = df[df['transaction_type'].str.lower() == 'income']
    result_df = result_df.drop(columns=['transaction_type'])
    category_sum = result_df.groupby('category')['amount'].sum()
    category_sum = category_sum.reset_index()
    return category_sum


def get_histories():
    values = History.objects.all().values('date', 'existing_sum', 'investment_sum')
    df = pandas.DataFrame(values)
    df['date'] = df.apply(
        lambda x: x['date'].strftime('%Y-%m-%d'), axis=1
    )
    df.rename(columns={'existing_sum': 'net_worth'}, inplace=True)

    networth_df = df[['date', 'net_worth']]
    networth_df.rename(columns={'net_worth': 'value'}, inplace=True)
    investment_df = df[['date', 'investment_sum']]
    investment_df.rename(columns={'investment_sum': 'value'}, inplace=True)
    return networth_df, investment_df


def get_investment_by_account_due_date():
    query = '''
            SELECT ma.name AS account__name, due_date, amount, exchange_rate
            FROM mylife_investment mi
                     LEFT JOIN mylife_currency mc ON mi.currency_id = mc.id
                     LEFT JOIN mylife_account ma ON mi.account_id = ma.id
                     LEFT JOIN (WITH RankedRates AS (SELECT currency_id,
                                                            exchange_rate,
                                    date
                                   , ROW_NUMBER() OVER (
                                    PARTITION BY currency_id
                                    ORDER BY date DESC
                                    ) AS RowNum
                                FROM
                                    mylife_currencyhistory mc2)
            SELECT currency_id,
                   exchange_rate, date
            FROM
                RankedRates
            WHERE
                RowNum = 1
                ) t1
            ON mc.id = t1.currency_id \
            '''
    values = connection.cursor().execute(query).fetchall()
    df = pandas.DataFrame(values, columns=['account__name', 'due_date', 'amount', 'exchange_rate'])
    df = df[df['due_date'].isna() == False]
    df['date'] = df.apply(
        lambda x: x['due_date'].strftime('%Y-%m-01'), axis=1
    )
    df['amount'] = df['amount'] / df['exchange_rate']
    df.drop(columns=['due_date'], inplace=True)
    df.rename(columns={'account__name': 'account',
                       'amount': 'value'},
              inplace=True)
    return df


def get_utility_df_for_queryset(queryset):
    values = queryset.values('year', 'month', 'days', 'amount', 'usage')
    df = pandas.DataFrame(values)
    df['date'] = df.apply(
        lambda x: f'{int(x["year"])}-{int(x["month"])}-01', axis=1
    )
    df.drop(columns=['year', 'month'], inplace=True)
    usage_df = df[['date', 'usage']]
    usage_df.rename(columns={'usage': 'value'}, inplace=True)
    cost_df = df[['date', 'amount']]
    cost_df.rename(columns={'amount': 'value'}, inplace=True)

    return usage_df, cost_df


def get_and_save_currency_exchange_rate():
    url = f'https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/USD'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['result'] == 'success':
            rates = data['conversion_rates']
            date = data['time_last_update_unix']
            currencies = Currency.objects.all()
            for currency in currencies:
                if currency.code in rates:
                    currency.exchange_rate = rates[currency.code]
                    CurrencyHistory.objects.update_or_create(
                        currency=currency,
                        date=pandas.Timestamp(date, unit='s').date(),
                        defaults={'exchange_rate': rates[currency.code]}
                    )
