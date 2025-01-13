from django.contrib import admin


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'street_no', 'street_name', 'city', 'state', 'country')
    search_fields = ('name', 'unit_no', 'building_no', 'street_no',
                     'street_name', 'city', 'state', 'zip_code', 'country')
