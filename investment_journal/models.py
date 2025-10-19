from django.db import models


class Sector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Stock(models.Model):
    symbol = models.CharField(max_length=50, unique=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_qty = models.DecimalField(default=0, max_digits=20, blank=True, decimal_places=2)
    total_market_value = models.DecimalField(default=0, max_digits=20, blank=True, decimal_places=2)
    total_cost = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    earnings = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    def __str__(self):
        return self.symbol

    def save(self, *args, **kwargs):
        transactions = self.stocktransaction_set.all()
        self.total_qty = transactions.aggregate(models.Sum('qty'))['qty__sum']
        self.total_market_value = self.current_price * self.total_qty
        self.total_cost = transactions.aggregate(models.Sum('cost'))['price__sum']
        self.earnings = self.total_cost - self.total_market_value
        super().save(*args, **kwargs)


class News(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    content = models.TextField()

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
    note = models.TextField()
    news = models.ManyToManyField(News)

    def __str__(self):
        return f'{self.stock}: {self.qty} {self.date}'

    def save(self, *args, **kwargs):
        self.cost = self.qty * self.price
        super().save(*args, **kwargs)
