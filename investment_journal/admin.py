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


class StockTransactionInline(admin.TabularInline):
    model = StockTransaction
    fields = readonly_fields = ('date', 'qty', 'price', 'cost', 'fear_level', 'note',)
    extra = 0
    can_delete = False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'total_qty', 'sector', 'total_cost', 'total_market_value', 'earnings', 'earning_rate')
    readonly_fields = ('total_qty', 'total_market_value', 'total_cost', 'earnings', 'earning_rate')
    list_filter = ('sector',)
    ordering = ('symbol',)
    search_fields = ('symbol',)
    inlines = (StockTransactionInline,)



@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'qty', 'price', 'cost', 'fear_level')
    autocomplete_fields = ('stock',)
    list_filter = ('stock',)

