from datetime import datetime

from django.conf import settings
from django.contrib import admin
from import_export import fields, resources
from import_export import widgets
from import_export.admin import ImportExportModelAdmin

from investment_journal.models import (
    Stock,
    StockTransaction,
    Sector,
    News,
    StockTransactionType
)
from mylife.models import Currency


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'sector')
    ordering = ('date', 'title')
    search_fields = ('title',)


class StockTransactionInline(admin.TabularInline):
    model = StockTransaction
    fields = readonly_fields = (
        'date', 'qty', 'price', 'transaction_type', 'cost', 'fear_level',
    )
    ordering = ('-date',)
    extra = 0
    can_delete = False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'symbol', 'total_qty', 'sector', 'currency',
        'current_price', 'total_market_value', 'total_bought', 'average_cost',
        'earned', 'total_sold',
    )
    readonly_fields = (
        'total_qty', 'total_market_value', 'total_bought', 'average_cost',
        'earned', 'total_sold',
    )
    list_filter = ('sector',)
    ordering = ('symbol',)
    search_fields = ('symbol',)
    inlines = (StockTransactionInline,)
    change_list_template = 'admin/investment_journal/stock/change_list.html'


class MultiFormatDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None

        formats = settings.TRANSACTION_TIME_FORMAT

        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except (ValueError, TypeError):
                continue

        return super().clean(value, row, **kwargs)


class StockTransactionSource(resources.ModelResource):
    date = fields.Field(
        column_name='Transaction Date',
        attribute='date',
        widget=MultiFormatDateWidget()
    )

    qty = fields.Field(
        column_name='Quantity',
        attribute='qty',
        widget=widgets.DecimalWidget()
    )

    price = fields.Field(
        column_name='Price',
        attribute='price',
        widget=widgets.DecimalWidget()
    )

    commission = fields.Field(
        column_name='Commission',
        attribute='commission',
        widget=widgets.DecimalWidget()
    )

    exchange_rate = fields.Field(
        column_name='Exchange Rate',
        attribute='exchange_rate',
        widget=widgets.DecimalWidget()
    )

    stock = fields.Field(
        column_name='Symbol',
        attribute='stock',
        widget=widgets.ForeignKeyWidget(Stock, 'symbol')
    )

    transaction_type = fields.Field(
        column_name='Transaction Type',
        attribute='transaction_type',
        widget=widgets.ForeignKeyWidget(StockTransactionType, 'name')
    )

    currency = fields.Field(
        column_name='Currency of Amount',
        attribute='currency',
        widget=widgets.ForeignKeyWidget(Currency, 'code')
    )

    class Meta:
        model = StockTransaction
        # Include all the fields you want imported
        fields = ('date', 'stock', 'qty', 'price', 'commission', 'exchange_rate',
                  'currency', 'transaction_type')
        import_id_fields = []
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        stock_identifier = row.get('Symbol')
        if not stock_identifier:
            raise ValueError("Stock identifier (Symbol) is missing in the import row.")

        stock_exists = Stock.objects.filter(symbol=stock_identifier).exists()
        if not stock_exists:
            raise ValueError(f'Stock with symbol "{stock_identifier}" does not exist. '
                             f' Please add it before importing transactions.')
        tx_type_name = row.get('Transaction Type')
        if tx_type_name:
            StockTransactionType.objects.get_or_create(
                name=tx_type_name,
                defaults={'is_buy': tx_type_name.lower() == 'buy',
                          'is_sell': tx_type_name.lower() == 'sell'}
            )

        exchange_rate_value = row.get('Exchange Rate')
        if exchange_rate_value is None or exchange_rate_value == '':
            exchange_rate_value = 1.0
            row['Exchange Rate'] = exchange_rate_value

    def after_import_row(self, row, row_result, **kwargs):
        stock_identifier = row.get('Symbol')
        if stock_identifier:
            stock = Stock.objects.get(symbol=stock_identifier)
            stock.save()  # This will trigger the recalculation of totals and averages


@admin.register(StockTransactionType)
class StockTransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_buy', 'is_sell')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(StockTransaction)
class StockTransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('stock', 'date', 'qty', 'price', 'cost', 'transaction_type',
                    'fear_level')
    autocomplete_fields = ('stock',)
    list_filter = ('stock',)
    resource_class = StockTransactionSource
