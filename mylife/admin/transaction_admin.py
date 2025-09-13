from datetime import datetime

from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from rangefilter.filters import DateRangeFilter
from django.contrib.humanize.templatetags.humanize import intcomma
from django.forms import ModelForm, TextInput
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from mylife.models import TransactionType, TransactionCategory, Merchant, Transaction, Location, UtilityType, \
    UtilityTransaction
from mylife.services import get_trans_df, calculate_expense, calculate_income, get_utility_df_for_queryset


def bulk_edit_category(modeladmin, request, queryset):
    if 'apply' in request.POST:
        new_value = request.POST.get('new_value')

        # Check if a new value was provided
        if not new_value:
            modeladmin.message_user(request, "Error: A new value must be provided.", level='ERROR')
            return

        # Update the selected records
        updated_count = queryset.update(category=new_value)

        # Display a success message
        modeladmin.message_user(request, f"{updated_count} records were successfully updated.")
        return

    categories = TransactionCategory.objects.all()
    context = {
        'categories': categories,
        'queryset': queryset,
        'model_meta': modeladmin.model._meta,
    }
    return render(request, 'admin/bulk_edit_template.html', context)


# Add a description for the action in the Django admin interface
bulk_edit_category.short_description = "Bulk edit category"


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
    ordering = ('-transaction_time', )
    list_filter = (('transaction_time', DateRangeFilter), 'transaction_type', 'category', 'merchant', )
    change_list_template = 'admin/mylife/transaction/change_list.html'
    actions = [bulk_edit_category]

    def displayed_amount(self, obj):
        return intcomma(obj.amount)
    displayed_amount.short_description = 'Amount'
    displayed_amount.admin_order_field = 'amount'

    def display_time(self, obj):
        return obj.transaction_time.strftime('%Y-%m-%d')
    display_time.short_description = 'Date'
    display_time.admin_order_field = 'transaction_time'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        df = get_trans_df(request)
        expense = calculate_expense(df)
        income = calculate_income(df)
        extra_context['expense'] = expense
        extra_context['income'] = income

        return super(TransactionAdmin, self).changelist_view(request, extra_context)


@admin.register(UtilityType)
class UtilityTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

    def has_module_permission(self, request):
        return False


@admin.register(UtilityTransaction)
class UtilityTransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'usage', 'year', 'month', 'days')
    ordering = ('-start_time',)
    list_filter = ('type',)
    change_list_template = 'admin/mylife/utility_transaction/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qd = request.GET.copy()
        query_dict = {}
        for k, v in qd.items() :
            query_dict[k] = v[0]
        queryset = UtilityTransaction.objects.filter(**query_dict)
        df = get_utility_df_for_queryset(queryset)
        extra_context['transactions'] = df

        return super(UtilityTransactionAdmin, self).changelist_view(request, extra_context)
