from decimal import Decimal

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
    total_bought = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    average_cost = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    earned = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    total_sold = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    currency = models.ForeignKey('mylife.Currency', on_delete=models.PROTECT, blank=True, null=True)

    class Media:
        js = ('js/investment_journal.js',)

    def __str__(self):
        return self.symbol
    
    def save(self, *args, **kwargs):
        if self.id is None:
            # If the stock is new, we don't have any transactions yet, so we can skip calculations
            super().save(*args, **kwargs)
            return
        
        # 1. Fetch all transactions ordered chronologically by date
        transactions = self.stocktransaction_set.all().order_by('date', 'id')

        # Initialize tracking variables
        running_qty = Decimal('0.00')
        running_total_cost_pool = Decimal('0.00')
        running_avg_cost = Decimal('0.00')
        total_realized_earnings = Decimal('0.00')
        
        total_bought_accumulator = Decimal('0.00')
        total_sold_accumulator = Decimal('0.00')

        # 2. Compute ACB and Realized Return via a rolling timeline loop
        for tx in transactions:
            qty = Decimal(str(tx.qty))
            price = Decimal(str(tx.price))
            commission = Decimal(str(tx.commission))
            
            # Use tx.cost if available, otherwise calculate it safely
            # Note: total transaction outlay (including commission)
            tx_cost = tx.cost if tx.cost else (qty * price + commission)

            if tx.transaction_type.is_buy:
                running_qty += qty
                running_total_cost_pool += tx_cost
                total_bought_accumulator += tx_cost
                
                # Recalculate average cost on Buy
                if running_qty > 0:
                    running_avg_cost = running_total_cost_pool / running_qty

            elif tx.transaction_type.is_sell:
                # Net proceeds from a sale is Gross Sale minus Selling Commission
                net_sale_proceeds = (qty * price) - commission
                total_sold_accumulator += net_sale_proceeds

                # Cost basis of the shares being sold (based on current average cost)
                cost_basis_of_sold_shares = qty * running_avg_cost

                # Realized earnings = Net proceeds - Cost basis
                realized_gain_loss = net_sale_proceeds - cost_basis_of_sold_shares
                total_realized_earnings += realized_gain_loss

                # Reduce tracking metrics
                running_qty -= qty
                running_total_cost_pool -= cost_basis_of_sold_shares

                # If fully liquidated, reset cost pool to prevent floating point residue
                if running_qty <= 0:
                    running_qty = Decimal('0.00')
                    running_total_cost_pool = Decimal('0.00')
                    running_avg_cost = Decimal('0.00')

        # 3. Assign calculated values to model fields
        self.total_qty = running_qty
        self.average_cost = running_avg_cost
        self.earned = total_realized_earnings
        self.total_market_value = self.total_qty * self.current_price
        
        # Keep track of absolute gross money flows if desired
        self.total_bought = total_bought_accumulator
        self.total_sold = total_sold_accumulator

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
        self.stock.save() 
