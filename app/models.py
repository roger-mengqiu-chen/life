from django.db import models


class Gender(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=255)
    unit_no = models.IntegerField(null=True, blank=True)
    building_no = models.IntegerField(null=True, blank=True)
    street_no = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)


class Merchant(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'location'], name='unique_merchant_name'),
        ]


class TransactionType(models.Model):
    name = models.CharField(max_length=255)
    is_income = models.BooleanField(default=False)


class TransactionCategory(models.Model):
    name = models.CharField(max_length=255)


class Transaction(models.Model):
    amount = models.FloatField()
    transaction_time = models.DateTimeField()
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT)
    category = models.ForeignKey(TransactionCategory, on_delete=models.PROTECT)


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT)


class EventType(models.Model):
    name = models.CharField(max_length=255)


class Event(models.Model):
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    people = models.ManyToManyField(Person)
