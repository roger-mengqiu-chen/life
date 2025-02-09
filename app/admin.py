from django.conf import settings
from django.contrib import admin
from django.forms import ModelForm, TextInput, BaseInlineFormSet
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from datetime import datetime
from django.contrib.humanize.templatetags.humanize import intcomma

from app.models import (Location, Merchant,
                        TransactionType, Transaction,
                        TransactionCategory, Person, EventType,
                        Event, Gender, Account, AccountType,
                        AccountHistory, History)
from app.services import get_last_month_trans_df, calculate_expense, calculate_income

admin.site.site_header = "Life"
admin.site.site_title = "Life"
admin.site.index_title = "Life"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'street_no', 'street_name', 'city', 'state', 'country')
    search_fields = ('name', 'unit_no', 'building_no', 'street_no', 'street_name',
                     'city', 'state', 'zip_code', 'country')
    ordering = ('street_no', 'street_name', 'city', 'state', 'zip_code')


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'website', 'phone', 'email', 'location__name')
    ordering = ('name',)


class CategoryForm(ModelForm):
    class Meta:
        model = TransactionCategory
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ('name', 'show_color')
    search_fields = ('name',)


class TransactionSource(resources.ModelResource):
    merchant = fields.Field(
        column_name='merchant',
        attribute='merchant',
        widget=ForeignKeyWidget(Merchant, 'name')
    )

    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(TransactionCategory, 'name')
    )

    transaction_type = fields.Field(
        column_name='transaction_type',
        attribute='transaction_type',
        widget=ForeignKeyWidget(TransactionType, 'name'))

    class Meta:
        model = Transaction
        fields = ('amount', 'transaction_time',
                  'transaction_type', 'merchant', 'category', )
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
        transaction_time_str = row.get('transaction_time', None)
        merchant_name = row.get('merchant', None)
        category_name = row.get('category', None)

        if transaction_time_str:
            for fmt in settings.TRANSACTION_TIME_FORMAT:
                try:
                    transaction_time = datetime.strptime(transaction_time_str, fmt)
                    row['transaction_time'] = transaction_time
                except ValueError:
                    pass

        if transaction_type_name:
            transaction_type_name = transaction_type_name.title()
            row['transaction_type'], _ = (
                TransactionType.objects.get_or_create(name=transaction_type_name)
            )

        if merchant_name:
            merchant_name = self.parse_merchant_name(merchant_name)
            row['merchant'], _ = Merchant.objects.get_or_create(name=merchant_name)

        if category_name:
            category_name = category_name.title()
            row['category'], _ = (
                TransactionCategory.objects.get_or_create(name=category_name)
            )


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('display_time', 'displayed_amount', 'transaction_type',
                    'merchant', 'category')
    search_fields = ('transaction_time', 'amount',
                     'merchant__name', 'category__name')
    autocomplete_fields = ('transaction_type', 'category', 'merchant')
    resource_class = TransactionSource
    ordering = ('transaction_time', )
    change_list_template = 'admin/app/transaction/change_list.html'

    def displayed_amount(self, obj):
        return intcomma(obj.amount)
    displayed_amount.short_description = 'Amount'
    displayed_amount.admin_order_field = 'amount'

    def display_time(self, obj):
        return obj.transaction_time.strftime('%Y-%m-%d')
    display_time.short_description = 'Date'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        df = get_last_month_trans_df()
        expense = calculate_expense(df)
        income = calculate_income(df)
        extra_context['expense'] = expense
        extra_context['income'] = income

        return super(TransactionAdmin, self).changelist_view(request, extra_context)


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
            self.instance.save()
            all_accounts = Account.objects.all()
            for account in all_accounts:
                AccountHistory.objects.create(account=account, history=self.instance)


class AccountHistoryInline(admin.StackedInline):
    model = AccountHistory
    extra = 0
    can_delete = False
    formset = AccountHistoryInlineFormSet


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    inlines = (AccountHistoryInline, )
    list_display = ('date', 'total', 'wire_transfer_total', 'investment_total')

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

    def save_model(self, request, obj, form, change):
        obj.calculate_sum()
        obj.calculate_wire_transfer()
        obj.save()


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


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
    autocomplete_fields = ('event_type', 'location')
    ordering = ('-event_time', )
