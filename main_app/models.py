from django.db import models
from django.contrib.auth.models import User

CURRENCIES = (
    ('AUD', 'Australian Dollar'),
    ('CAD', 'Canadian Dollar'),
    ('EUR', 'Euro'),
    ('GBP', 'British Pound'),
    ('JPY', 'Japanese Yen'),
    ('NZD', 'New Zealand Dollar'),
    ('USD', 'United States Dollar'),
    ('OTH', 'Other Currency'),
)

# Create your models here.
class Ledger(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES,
        default=CURRENCIES[0][0]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledgers_created')
    members = models.ManyToManyField(User, related_name='ledgers_joined')

    def __str__(self):
        return self.name