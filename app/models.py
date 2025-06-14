from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from datetime import datetime, timedelta


class Gender(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    unit_no = models.IntegerField(null=True, blank=True)
    building_no = models.IntegerField(null=True, blank=True)
    street_no = models.CharField(max_length=255, null=True, blank=True)
    street_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = "Location"

    def __str__(self):
        return (f'{self.name or ""} {self.street_no or ""} {self.street_name or ""} '
                f'{self.city}, {self.state or ""}, {self.country}')


class Merchant(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Location,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    website = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'location'],
                                    name='unique_merchant_name'),
        ]
        ordering = ['name']

    def __str__(self):
        return self.name


class TransactionType(models.Model):
    name = models.CharField(max_length=255)
    is_income = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_expense = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TransactionCategory(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Transaction Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def show_color(self):
        if self.color is not None or self.color != '':
            return format_html(
                f'<span style="color:{self.color}">&#x25A0;</span>'
            )
        else:
            return ''


class Transaction(models.Model):
    amount = models.FloatField()
    transaction_time = models.DateField()
    transaction_type = models.ForeignKey(TransactionType,
                                         on_delete=models.PROTECT)
    merchant = models.ForeignKey(Merchant,
                                 on_delete=models.PROTECT)
    category = models.ForeignKey(TransactionCategory,
                                 on_delete=models.PROTECT)

    def __str__(self):
        return (f"{self.transaction_time} "
                f"- {self.merchant.name} "
                f"- {self.transaction_type.name} "
                f"- {self.amount}")


class Report(models.Model):
    date = models.DateField()
    total_expense = models.FloatField(default=0, blank=True)
    total_income = models.FloatField(default=0, blank=True)


class ReportLine(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    category = models.ForeignKey(TransactionCategory, on_delete=models.PROTECT)
    amount = models.FloatField(default=0, blank=True)
    percentage = models.FloatField(default=0, blank=True)


class AccountType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_asset = models.BooleanField(default=False)
    is_liability = models.BooleanField(default=False)
    is_cash = models.BooleanField(default=False)
    is_investment = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Bank(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=255)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, null=True, blank=True)
    account_no = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Investment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    due_date = models.DateField(null=True, blank=True)
    amount = models.FloatField(default=0, blank=True)
    interest_rate = models.FloatField(default=0, blank=True)

    def __str__(self):
        return f'{self.due_date} - {self.amount}'


class History(models.Model):
    date = models.DateField(auto_now=True, unique=True)
    sum = models.FloatField(default=0, blank=True)
    wire_transfer_sum = models.FloatField(default=0, blank=True)
    investment_sum = models.FloatField(default=0, blank=True)
    existing_sum = models.FloatField(default=0, blank=True, help_text="Existing sum is total - car/house")

    class Meta:
        verbose_name_plural = "Histories"

    def __str__(self):
        return datetime.strftime(self.date, "%Y-%m-%d")

    def calculate_sum(self):
        account_histories = self.accounthistory_set.all()
        total = 0
        investment_total = 0
        car_house = 0
        for account_history in account_histories:
            total += account_history.account_amount
            if account_history.account.type.name.lower() == 'investment':
                investment_total += account_history.account_amount

            if (account_history.account.name.lower() == 'car'
                or account_history.account.name.lower() == 'house'):
                car_house += account_history.account_amount
        self.sum = round(total, 2)
        self.investment_sum = round(investment_total, 2)
        self.existing_sum = round(total - car_house, 2)
        return total

    def calculate_wire_transfer(self):
        wire_transfer = Transaction.objects.filter(
            transaction_type__name__iexact='wire transfer')
        total = 0
        for wire_transfer in wire_transfer:
            total += wire_transfer.amount
        self.wire_transfer_sum = round(total, 2)
        return total


class AccountHistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    history = models.ForeignKey(History, on_delete=models.CASCADE)
    account_amount = models.FloatField(default=0, blank=True)

    class Meta:
        unique_together = ('account', 'history')

    def __str__(self):
        return self.account.name


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100,
                                 null=True,
                                 blank=True)
    merchant = models.ForeignKey(Merchant,
                                 on_delete=models.PROTECT,
                                 null=True,
                                 blank=True)
    gender = models.ForeignKey(Gender,
                               on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "People"

    def __str__(self):
        return self.first_name + " " + self.last_name


class EventType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_event_name'),
        ]

    def __str__(self):
        return self.name


class Event(models.Model):
    event_type = models.ForeignKey(EventType,
                                   on_delete=models.PROTECT)
    event_time = models.DateTimeField()
    location = models.ForeignKey(Location,
                                 on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True,
                             null=True)
    people = models.ManyToManyField(Person)

    def __str__(self):
        return self.name

    def passed_time(self):
        now = timezone.now()
        delta = now - self.event_time
        total_days = delta.days
        years = total_days // 365
        months = (total_days % 365) // 30
        days = (total_days % 365) % 30
        result = ""
        if years > 0:
            result += f"{years} years "
        if months > 0:
            result += f"{months} months "
        result += f"{days} days "
        return result.strip()


class UtilityType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name.title()


class UtilityTransaction(models.Model):
    amount = models.FloatField()
    usage = models.FloatField()
    start_time = models.DateField()
    end_time = models.DateField()
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    days = models.IntegerField(blank=True, null=True)
    usage_per_day = models.FloatField(blank=True, null=True)
    cost_per_day = models.FloatField(blank=True, null=True)
    cost_per_unit = models.FloatField(blank=True, null=True)
    type = models.ForeignKey(UtilityType, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        days = (self.end_time - self.start_time).days
        mid = self.start_time + timedelta(days=15)
        self.days = days
        self.year = mid.year
        self.month = mid.month
        self.usage_per_day = self.usage / days
        self.cost_per_day = self.amount / days
        self.cost_per_unit = self.amount / self.usage if self.usage > 0 else 0
        super().save(*args, **kwargs)
