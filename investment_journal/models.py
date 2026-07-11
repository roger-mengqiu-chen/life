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
    earned = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    profit_rate = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    sold = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    currency = models.ForeignKey('mylife.Currency', on_delete=models.PROTECT, blank=True, null=True)

    class Media:
        js = ('js/investment_journal.js',)

    def __str__(self):
        return self.symbol
    
    def save(self, *args, **kwargs):
        transactions = self.stocktransaction_set.all()
        sell_transactions = transactions.filter(transaction_type__is_sell=True)
        buy_transactions = transactions.filter(transaction_type__is_buy=True)
        self.total_qty = (
            buy_transactions.aggregate(total=models.Sum('qty'))['total'] or 0 
            - sell_transactions.aggregate(total=models.Sum('qty'))['total'] or 0
        )

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


class StockTransactionType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_buy = models.BooleanField(default=True)
    is_sell = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class StockTransaction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    commission = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    cost = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    exchange_rate = models.DecimalField(default=1, max_digits=20, decimal_places=6)
    currency = models.ForeignKey('mylife.Currency', on_delete=models.PROTECT, blank=True, null=True)
    fear_level = models.IntegerField(default=0, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    news = models.ManyToManyField(News, blank=True)
    transaction_type = models.ForeignKey(
        StockTransactionType, on_delete=models.PROTECT, blank=True, null=True)    

    def __str__(self):
        return f'{self.stock}: {self.qty} {self.date}'

    def save(self, *args, **kwargs):
        self.cost = self.qty * self.price + self.commission
        super().save(*args, **kwargs)
