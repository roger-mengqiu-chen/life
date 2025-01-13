from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from app.models import (Location, Merchant,
                        TransactionType, Transaction,
                        TransactionCategory, Person, EventType, Event)

admin.site.site_header = "Life"
admin.site.site_title = "Life"
admin.site.index_title = "Life"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'street_no', 'street_name', 'city', 'state', 'country')
    search_fields = ('name', 'unit_no', 'building_no', 'street_no', 'street_name',
                     'city', 'state', 'zip_code', 'country')


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'website', 'phone', 'email', 'location')


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = ('transaction_time', 'amount', 'transaction_type',
                    'merchant', 'category')
    search_fields = ('transaction_time', 'amount',
                     'merchant', 'category')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'merchant', 'gender')
    search_fields = ('first_name', 'last_name', 'merchant__name', 'gender')


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_time', 'event_type', 'name', 'location')
    search_fields = ('event_time', 'event_type', 'name', 'location__city',
                     'location__state', 'location__country')
