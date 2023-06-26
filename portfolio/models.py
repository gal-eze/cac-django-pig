from django.db import models
from home.models import AppUser


class Broker(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Security(models.Model):
    symbol = models.CharField(default="", max_length=25)
    description = models.CharField(max_length=100)
    sector = models.CharField(default="", max_length=100)
    last_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.symbol


class Portfolio(models.Model):
    customer = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    total_investment = models.FloatField(default=0)
    transactions = models.ManyToManyField(Security, through="Transaction")

    def get_transactions(self):
        return self.transaction_set.all()

    def update_investment(self):
        investment = 0
        transactions = Transaction.objects.filter(portfolio=self)
        for t in transactions:
            investment += t.investment_amount
        self.total_investment = investment
        self.save()

    def __str__(self):
        return f"Usuario: {self.customer.username} - Total Invertido: {self.total_investment} - Cantidad de Transacciones: {self.transactions.count()}"


class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    date = models.DateTimeField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    investment_amount = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.investment_amount = self.price * self.quantity
        print(self.price * self.quantity)
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"Ticker: {self.security.symbol} - Cantidad: {self.quantity} - Monto Invertido: {self.investment_amount}"

