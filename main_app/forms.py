from django.forms import ModelForm
from .models import Ledger, Expense

class LedgerForm(ModelForm):
    class Meta:
        model = Ledger
        fields = ['name', 'description', 'currency', 'members']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)
        # Use the user's friends as the queryset for members:
        self.fields['members'].queryset = user.profile.friends.all()


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date']