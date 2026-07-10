from datetime import datetime

from django.contrib import admin
from django.conf import settings
from import_export import fields, resources
from import_export.widgets import DateWidget, ForeignKeyWidget

from investment_journal.models import (
    Stock,
    StockTransaction,
    Sector,
    News
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
    fields = readonly_fields = ('date', 'qty', 'price', 'cost', 'fear_level', 'note',)
    extra = 0
    can_delete = False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'total_qty', 'sector', 'average_cost', 'current_price', 'total_market_value', 'earnings',
                    'earning_rate', 'realized_return',)
    readonly_fields = ('total_qty', 'total_market_value', 'total_cost', 'earnings', 'earning_rate', 'realized_return',)
    list_filter = ('sector',)
    ordering = ('symbol',)
    search_fields = ('symbol',)
    inlines = (StockTransactionInline,)

    class Media:
        js = (
            'js/investment_journal.js',
        )


class MultiFormatDateWidget(DateWidget):
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
    transaction_time = fields.Field(
        column_name='transaction_time',
        attribute='transaction_time',
        widget=MultiFormatDateWidget()
    )
    
    currency = fields.Field(
        column_name='currency',
        attribute='currency',
        widget=ForeignKeyWidget(Currency, 'code')
    )


    class Meta:
        model = StockTransaction
        fields = ('amount', 'transaction_time',
                  'transaction_type', 'merchant', 'category',)
        import_id_fields = []
        skip_unchanged = True
        report_skipped = True

    def parse_merchant_name(self, name):
        for merchant in settings.MERCHANTS:
            if merchant.lower() in name.lower():
                return merchant.title()
        return name

    def before_import_row(self, row, **kwargs):
        transaction_type_name = row.get('transaction_type', None)
        merchant_name = row.get('merchant', None)
        category_name = row.get('category', None)



@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'qty', 'price', 'cost', 'transaction_type', 'fear_level')
    autocomplete_fields = ('stock',)
    list_filter = ('stock',)
