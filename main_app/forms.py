from django.forms import ModelForm
from .models import Ledger, Expense

class LedgerForm(ModelForm):
    class Meta:
        model = Ledger
        fields = ['name', 'description', 'currency', 'members']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['members'].queryset = self.fields['members'].queryset.exclude(id=user.id)


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date']