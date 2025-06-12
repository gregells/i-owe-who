from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.views.generic.edit import CreateView
from .models import Ledger

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


def ledgers_index(request):
    # Get all ledgers where the current user is either the creator or a member:
    ledgers = Ledger.objects.filter(Q(creator=request.user) | Q(members=request.user))
    return render(request, 'ledgers/index.html', {
        'ledgers': ledgers
    })


def ledgers_detail(request, ledger_id):
    ledger = Ledger.objects.get(id=ledger_id)
    # Redirect back to index page if user is not the creator or a member of this ledger:
    if request.user != ledger.creator and request.user not in ledger.members.all():
        return redirect('ledgers_index')
    return render(request, 'ledgers/detail.html', {
        'ledger': ledger
    })


class LedgerCreate(CreateView):
    model = Ledger
    # fields = '__all__'
    fields = ['name', 'description', 'currency']

    # Override the inherited method called when a valid form is submitted:
    def form_valid(self, form):
        # Assign the logged in user (self.request.user) as the ledgers creator and member:
        form.instance.creator = self.request.user
        # Pass control back to the superclass CreateView's form_valid() method to do its job:
        return super().form_valid(form)