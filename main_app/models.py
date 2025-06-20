from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

CURRENCIES = (
    ('AUD', 'Australian Dollar - $'),
    ('CAD', 'Canadian Dollar - $'),
    ('EUR', 'Euro - €'),
    ('GBP', 'British Pound - £'),
    ('JPY', 'Japanese Yen - ¥'),
    ('NZD', 'New Zealand Dollar - $'),
    ('USD', 'United States Dollar - $'),
    ('OTH', 'Other Currency - $'),
)

# Create your models here.
class Ledger(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES,
        default=CURRENCIES[0][0]
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledgers_created')
    members = models.ManyToManyField(User, related_name='ledgers_joined')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('ledgers_detail', kwargs={'ledger_id': self.id})
    

class Expense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} {self.ledger.currency}"
    
    def get_absolute_url(self):
        return reverse('expenses_detail', kwargs={'expense_id': self.id})