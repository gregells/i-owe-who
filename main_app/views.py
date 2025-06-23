from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Ledger, Expense
from .forms import ExpenseForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def signup(request):
    error_message = ''
    if request.method == 'POST':
        # Create a 'user' form object using the data from the browser request:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Add the new user to the database:
            user = form.save()
            # Log the user in to save them from having to login after signup:
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form:
    form = UserCreationForm()
    context = { 'form': form, 'error_message': error_message }
    return render(request, 'registration/signup.html', context)


@login_required
def ledgers_index(request):
    # Get all ledgers where the current user is either the creator or a member:
    ledgers = Ledger.objects.filter(Q(creator=request.user) | Q(members=request.user))
    return render(request, 'ledgers/index.html', {
        'ledgers': ledgers
    })


@login_required
def ledgers_detail(request, ledger_id):
    ledger = Ledger.objects.get(id=ledger_id)
    # Redirect back to index page if user is not the creator or a member of this ledger:
    if request.user != ledger.creator and request.user not in ledger.members.all():
        return redirect('ledgers_index')
    
    # Create an ExpenseForm instance to be used in the template:
    expense_form = ExpenseForm()
    return render(request, 'ledgers/detail.html', {
        'ledger': ledger,
        'expense_form': expense_form
    })


class LedgerCreate(LoginRequiredMixin, CreateView):
    model = Ledger
    fields = ['name', 'description', 'currency', 'members']

    # Override the inherited method called when a valid form is submitted:
    def form_valid(self, form):
        # Assign the logged in user (self.request.user) as the ledgers creator:
        form.instance.creator = self.request.user
        # Pass control back to the superclass CreateView's form_valid() method to do its job:
        return super().form_valid(form)
    

class LedgerUpdate(LoginRequiredMixin, UpdateView):
    model = Ledger
    fields = ['name', 'description', 'currency']


class LedgerDelete(LoginRequiredMixin, DeleteView):
    model = Ledger
    success_url = '/ledgers'


@login_required
def add_expense(request, ledger_id):
    # Create an ExpenseForm instance using the data from the request:
    expense_form = ExpenseForm(request.POST)
    # Check if the form is valid:
    if expense_form.is_valid():
        # Don't save the form to the database until the ledger and user are set:
        # Note: saving the form with commit=False returns an in-memory model
        #   object that has not been saved to the database yet.
        new_expense = expense_form.save(commit=False)
        # Set the ledger and user for the new expense:
        new_expense.ledger_id = ledger_id
        new_expense.user_id = request.user.id
        # Now save the new expense to the database:
        new_expense.save()
        # Trigger a save on the ledger to update its updated_at field:
        ledger = Ledger.objects.get(id=ledger_id)
        ledger.save()
    return redirect('ledgers_detail', ledger_id=ledger_id)


@login_required
def expenses_detail(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    # Redirect back to index page if user is not the creator or a member of the ledger
    #   that the expense belongs to:
    if request.user != expense.ledger.creator and request.user not in expense.ledger.members.all():
        return redirect('ledgers_index')
    
    return render(request, 'expenses/detail.html', {
        'expense': expense
    })


class ExpenseUpdate(LoginRequiredMixin, UpdateView):
    model = Expense
    fields = ['name', 'amount', 'date']


class ExpenseDelete(LoginRequiredMixin, DeleteView):
    model = Expense
    success_url = '/ledgers'