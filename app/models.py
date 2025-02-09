from django.db import models
from django.utils import timezone
from django.utils.html import format_html


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

    def __str__(self):
        return self.name


class TransactionType(models.Model):
    name = models.CharField(max_length=255)
    is_income = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TransactionCategory(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Transaction Categories"

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


class AccountType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=255)
    account_no = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey(AccountType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class History(models.Model):
    date = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "Histories"

    def __str__(self):
        return self.date


class AccountHistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    history = models.ForeignKey(History, on_delete=models.CASCADE)
    account_amount = models.FloatField(default=0)

    class Meta:
        unique_together = ('account', 'history')


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
