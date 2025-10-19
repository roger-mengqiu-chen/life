from django.contrib import admin

from investment_journal.models import (
    Stock,
    StockTransaction,
    Sector,
    News
)


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

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'total_qty', 'sector', 'total_market_value', 'earnings')
    list_filter = ('sector',)
    ordering = ('symbol',)
    search_fields = ('symbol',)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'qty', 'date', 'price', 'fear_level')
    autocomplete_fields = ('stock',)
