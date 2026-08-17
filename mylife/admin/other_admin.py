from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path

from mylife.models import (Currency, Person, EventType,
                           Event, Gender, CurrencyHistory)
from mylife.services import get_and_save_currency_exchange_rate
from mylife.views import get_exchange_rate

admin.site.site_header = "Life"
admin.site.site_title = "Life"
admin.site.index_title = "Life"


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

    def has_module_permission(self, request):
        return False
    

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('code',)
    ordering = ('code',)


@admin.register(CurrencyHistory)
class CurrencyHistoryAdmin(admin.ModelAdmin):
    list_display = ('currency', 'date', 'exchange_rate')
    search_fields = ('currency__code', 'date')
    ordering = ('-date',)
    list_filter = ('currency',)

    change_list_template = "admin/mylife/currencyhistory/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-rates/', self.admin_site.admin_view(self.get_rate), name='currencyhistory_fetch_rates'),
        ]
        return custom_urls + urls

    def get_rate(self, request):
        try:
            get_and_save_currency_exchange_rate()
            messages.success(request, "Currency exchange rates updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating currency exchange rates: {str(e)}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '../'))


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'merchant', 'gender')
    search_fields = ('first_name', 'last_name', 'merchant__name', 'gender__name')
    ordering = ('first_name', 'last_name')


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def has_module_permission(self, request):
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_time_date', 'event_type', 'name', 'location', 'passed_time')
    search_fields = ('event_time', 'event_type__name', 'name', 'location__city',
                     'location__state', 'location__country')
    autocomplete_fields = ('event_type', 'location', 'people')
    ordering = ('-event_time', )

    @admin.display(description='Event time', ordering='event_time')
    def event_time_date(self, obj):
        return obj.event_time.strftime('%Y-%m-%d')
