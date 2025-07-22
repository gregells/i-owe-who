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
        queryset = user.profile.friends.all()
        if creator:
            queryset = queryset.exclude(id=creator.id)
        self.fields['members'].queryset = queryset


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date']