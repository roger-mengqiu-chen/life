from django.db import models


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
        return (f'{self.street_no} {self.street_name} {self.city} '
                f'{self.state} {self.country}')


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

    def __str__(self):
        return self.name


class Transaction(models.Model):
    amount = models.FloatField()
    transaction_time = models.DateTimeField()
    transaction_type = models.ForeignKey(TransactionType,
                                         on_delete=models.PROTECT)
    merchant = models.ForeignKey(Merchant,
                                 on_delete=models.PROTECT)
    category = models.ForeignKey(TransactionCategory,
                                 on_delete=models.PROTECT)


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
