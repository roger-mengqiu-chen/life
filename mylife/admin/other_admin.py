from django.contrib import admin

from mylife.models import (Person, EventType,
                           Event, Gender)

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
    

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'merchant', 'gender')
    search_fields = ('first_name', 'last_name', 'merchant__name', 'gender__name')
    ordering = ('first_name', 'last_name')


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_time', 'event_type', 'name', 'location', 'passed_time')
    search_fields = ('event_time', 'event_type__name', 'name', 'location__city',
                     'location__state', 'location__country')
    autocomplete_fields = ('event_type', 'location', 'people')
    ordering = ('-event_time', )
