from django.db import models


class Sector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Stock(models.Model):
    symbol = models.CharField(max_length=50, unique=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    average_cost = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_qty = models.DecimalField(default=0, max_digits=20, blank=True, decimal_places=2)
    total_market_value = models.DecimalField(default=0, max_digits=20, blank=True, decimal_places=2)
    total_cost = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    earnings = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    earning_rate = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    realized_return = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Media:
        js = ('js/investment_journal.js',)

    def __str__(self):
        return self.symbol

    def save(self, *args, **kwargs):
        if self.pk:
            transactions = self.stocktransaction_set.all()
            sold_transactions = transactions.filter(cost__lt=0)

            if sold_transactions.exists():
                self.realized_return = -transactions.filter(cost__lt=0).aggregate(models.Sum('cost'))['cost__sum']
                sold_qty = sold_transactions.aggregate(models.Sum('qty'))['qty__sum']
            else:
                self.realized_return = 0
                sold_qty = 0

            self.total_qty = transactions.filter(cost__gt=0).aggregate(models.Sum('qty'))['qty__sum'] + sold_qty
            self.total_market_value = self.current_price * self.total_qty
            self.total_cost = self.average_cost * self.total_qty

            self.earnings = (self.current_price - self.average_cost) * self.total_qty
            self.earning_rate = (self.current_price - self.average_cost) / self.average_cost * 100
        super().save(*args, **kwargs)


class News(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.title}"

    class Meta:
        verbose_name_plural = "News"


class StockTransaction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    cost = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    fear_level = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    news = models.ManyToManyField(News, blank=True, null=True)

    def __str__(self):
        return f'{self.stock}: {self.qty} {self.date}'

    def save(self, *args, **kwargs):
        self.cost = self.qty * self.price
        super().save(*args, **kwargs)
