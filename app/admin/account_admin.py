from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.forms import BaseInlineFormSet

from app.models import AccountType, Account, AccountHistory, History, Bank, Investment
from app.services import get_histories, get_investment_by_account_due_date


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_no','bank', 'type', 'is_active')
    search_fields = ('name', 'account_no', 'bank', 'type__name')
    autocomplete_fields = ('type',)
    ordering = ('name', )


class AccountHistoryInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk is None:
            all_accounts = Account.objects.filter(is_active=True).order_by('name')
            initial_data = []
            for account in all_accounts:
                initial_data.append({'account': account})
            self.initial = initial_data
            self.extra = len(initial_data)
        else:
            all_accounts = self.instance.accounthistory_set.all().order_by('account__name')
            initial_data = []
            for account in all_accounts:
                initial_data.append({'account': account.account, 'account_amount': account.account_amount})
            self.initial = initial_data

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
    list_display = ('date', 'existing_total', 'investment_total', 'total', 'wire_transfer_total',)
    ordering = ('-date', )
    change_list_template = 'admin/app/history/change_list.html'

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
    existing_total.short_description = 'Net Worth'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        formset.save()  # Save AccountHistory objects first
        if isinstance(formset, AccountHistoryInlineFormSet):
            form.instance.calculate_sum()
            form.instance.calculate_wire_transfer()
            form.instance.save()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        net_worth, investment = get_histories()
        extra_context['net_worth'] = net_worth
        extra_context['investment'] = investment

        return super(HistoryAdmin, self).changelist_view(request, extra_context)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('account', 'due_date', 'amount', 'interest_rate')
    search_fields = ('account__name', 'due_date')
    list_filter = ('account',)
    autocomplete_fields = ('account',)
    ordering = ('account', 'due_date')
    change_list_template = 'admin/app/investment/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        investment = get_investment_by_account_due_date()
        extra_context['investment'] = investment

        return super(InvestmentAdmin, self).changelist_view(request, extra_context)
