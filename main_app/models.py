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
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    invites_sent = models.ManyToManyField(User, blank=True, related_name='invites_rec')

    def __str__(self):
        return f"{self.user.username}'s Profile"


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
    members = models.ManyToManyField(User, blank=True, related_name='ledgers_joined')
    
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('ledgers_detail', kwargs={'ledger_id': self.id})
    
    def get_total_spent(self):
        return self.expense_set.aggregate(models.Sum('amount', default=0))['amount__sum']
    
    def get_individual_spent(self):
        # Create a list of users from: creator, members, and distinct users from expenses:
        users = ([self.creator] + 
                [member for member in self.members.all()] + 
                [User.objects.get(id=user['user']) for user in self.expense_set.order_by().values('user').distinct()])
        # Convert list to a set to avoid duplicates:
        users_set = set(users)
        
        # Initialize the list of individual amounts spent:
        individual_spent = []
        
        # Calculate the total amount spent by each user:
        for user in users_set:
            individual_spent.append({
                'name': user.username,
                'total': self.expense_set.filter(user=user).aggregate(models.Sum('amount', default=0))['amount__sum']
            })

        return individual_spent


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


class Photo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=200)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for {self.expense.name} - @{self.url}"