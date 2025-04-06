from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.forms import BaseInlineFormSet

from app.models import AccountType, Account, AccountHistory, History


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_no', 'type')
    search_fields = ('name', 'account_no', 'type__name')
    autocomplete_fields = ('type',)
    ordering = ('name', )


class AccountHistoryInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk is None:
            all_accounts = Account.objects.all()
            initial_data = []
            for account in all_accounts:
                initial_data.append({'account': account})
            self.initial = initial_data
            self.extra = len(initial_data)

    def save_new(self, form, commit=True):
        # Assign the history instance to each new form entry
        obj = form.save(commit=False)
        obj.history = self.instance
        if commit:
            obj.save()
        return obj

    def save_existing(self, form, instance, commit=True):
        # Update existing entries (not needed in this case, but for completeness)
        obj = form.save(commit=False)
        obj.history = self.instance
        if commit:
            obj.save()
        return obj


class AccountHistoryInline(admin.TabularInline):
    model = AccountHistory
    extra = 0
    can_delete = False
    formset = AccountHistoryInlineFormSet


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    inlines = (AccountHistoryInline, )
    list_display = ('date', 'total', 'wire_transfer_total', 'investment_total', 'existing_total')

    def total(self, obj):
        return intcomma(obj.sum)
    total.short_description = 'Total'
    total.admin_order_field = 'sum'

    def wire_transfer_total(self, obj):
        return intcomma(obj.wire_transfer_sum)
    wire_transfer_total.admin_order_field = 'wire_transfer_sum'
    wire_transfer_total.short_description = 'Wire Transfer Total'

    def investment_total(self, obj):
        return intcomma(obj.investment_sum)
    investment_total.admin_order_field = 'investment_sum'
    investment_total.short_description = 'Investment Total'

    def existing_total(self, obj):
        return intcomma(obj.existing_sum)
    existing_total.admin_order_field = 'existing_sum'
    existing_total.short_description = 'Existing Total'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        formset.save()  # Save AccountHistory objects first
        if isinstance(formset, AccountHistoryInlineFormSet):
            form.instance.calculate_sum()
            form.instance.calculate_wire_transfer()
            form.instance.save()
