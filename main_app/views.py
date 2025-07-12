import uuid
import os
import boto3
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Profile, Ledger, Expense, Photo
from .forms import LedgerForm, ExpenseForm

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
            # Create a profile for the new user:
            Profile.objects.create(user=user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with a form:
    # No existing form for GET requests, so create one:
    if request.method == 'GET':
        form = UserCreationForm()
    context = { 'form': form, 'error_message': error_message }
    return render(request, 'registration/signup.html', context)


@login_required
def my_profile(request):
    return render(request, 'profiles/my_profile.html')


@login_required
def send_friend_request(request):
    receiver_username = request.POST.get('username')
    receiver = User.objects.filter(username=receiver_username).first()

    if receiver:
        # Case 1: user sends a request to themselves:
        if request.user == receiver:
            return render(request, 'profiles/my_profile.html', {
                'toast_message': 'Cannot send a friend request to yourself.',
            })
        # Case 2: receiver is already a friend:
        elif receiver in request.user.profile.friends.all():
            return render(request, 'profiles/my_profile.html', {
                'toast_message': 'You are already friends with',
                'username': receiver_username,
            })
        # Case 3: request already sent to receiver:
        elif receiver in request.user.profile.invites_sent.all():
            return render(request, 'profiles/my_profile.html', {
                'toast_message': 'You have already sent a friend request to',
                'username': receiver_username,
            })
        # Case 4: request already received from receiver:
        elif request.user in receiver.profile.invites_sent.all():
            return render(request, 'profiles/my_profile.html', {
                'toast_message': 'You have already received a friend request from',
                'username': receiver_username,
            })
        # Case 5: request is valid and can be sent:
        else:
            # Add the receiver to the sender's invites_sent list:
            request.user.profile.invites_sent.add(receiver)
            return render(request, 'profiles/my_profile.html', {
                'toast_message': 'Friend request sent to',
                'username': receiver_username,
            })
    else:
        # Case 6: the receiver does not exist:
        return render(request, 'profiles/my_profile.html', {
            'toast_message': 'Could not find user',
            'username': receiver_username,
        })


@login_required
def accept_friend_request(request, user_id):
    new_friend = User.objects.get(id=user_id)
    # Add new friend's user.id to logged in user's friends list:
    request.user.profile.friends.add(new_friend)
    # Add logged in user's user.id to new friend's friends list:
    new_friend.profile.friends.add(request.user)
    # Remove logged in user's user.id from new friend's invites_sent list:
    new_friend.profile.invites_sent.remove(request.user)

    return render(request, 'profiles/my_profile.html', {
        'toast_message': 'You are now friends with',
        'username': new_friend.username,
    })


@login_required
def cancel_friend_request(request, user_id):
    invitee = User.objects.get(id=user_id)
    # Remove invitee's user.id from logged in user's invites_sent list:
    request.user.profile.invites_sent.remove(invitee)
    
    return render(request, 'profiles/my_profile.html', {
        'toast_message': 'Retracted friend request to',
        'username': invitee.username,
    })


@login_required
def remove_friend(request, user_id):
    old_friend = User.objects.get(id=user_id)
    # Remove old_friend's user.id from logged in user's friends list:
    request.user.profile.friends.remove(old_friend)
    # Remove logged in user's user.id from old_friend's friends list:
    old_friend.profile.friends.remove(request.user)
    
    return render(request, 'profiles/my_profile.html', {
        'toast_message': 'You are no longer friends with',
        'username': old_friend.username,
    })


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
    form_class = LedgerForm

    # Override the inherited method called when a valid form is submitted:
    def form_valid(self, form):
        # Assign the logged in user (self.request.user) as the ledgers creator:
        form.instance.creator = self.request.user
        # Pass control back to the superclass CreateView's form_valid() method to do its job:
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class LedgerUpdate(LoginRequiredMixin, UpdateView):
    model = Ledger
    form_class = LedgerForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the logged in user to the form:
        kwargs['user'] = self.request.user
        # Pass the ledger's creator to the form:
        ledger = self.get_object()
        kwargs['creator'] = ledger.creator
        return kwargs


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

    def form_valid(self, form):
        # Get the expense object being updated:
        expense = self.get_object()
        # Trigger a save on the ledger to update its updated_at field:
        expense.ledger.save()
        # Now call the superclass form_valid method to save the changes:
        return super().form_valid(form)


class ExpenseDelete(LoginRequiredMixin, DeleteView):
    model = Expense
    
    def get_success_url(self):
        return self.object.ledger.get_absolute_url()
    
    def form_valid(self, form):
        # Get the expense object to be deleted:
        expense = self.get_object()
        # Delete all photos associated with this expense from Amazon S3:
        s3 = boto3.client('s3')
        bucket = os.environ['S3_BUCKET']
        for photo in expense.photo_set.all():
            key = photo.url.split('/')[-1]
            # Use a try-except block to handle any errors that may occur:
            try:
                # Delete the photo from S3 and our database:
                s3.delete_object(Bucket=bucket, Key=key)
                photo.delete()
            except Exception as e:
                print('An error occurred deleting file from S3')
                print(e)
        # Trigger a save on the ledger to update its updated_at field:
        expense.ledger.save()
        # Now call the superclass form_valid method to delete the expense:
        return super().form_valid(form)


@login_required
def add_photo(request, expense_id):
    # photo-file will be the 'name' attribute on the <input type="file"> field:
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # Need a unique "key" for the photo in S3, with extension:
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # Use a try-except block to handle any errors that may occur:
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # Build the URL for the uploaded photo:
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            # Create a new Photo object and save it to the database:
            # Note: can use expense_id or expense object:
            Photo.objects.create(url=url, expense_id=expense_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('expenses_detail', expense_id=expense_id)


@login_required
def delete_photo(request, expense_id, photo_id):
    s3 = boto3.client('s3')
    # Get the photo to be deleted from the database:
    photo = Photo.objects.get(id=photo_id)
    key = photo.url.split('/')[-1]
    # Use a try-except block to handle any errors that may occur:
    try:
        bucket = os.environ['S3_BUCKET']
        # Delete the photo from S3 and our database:
        s3.delete_object(Bucket=bucket, Key=key)
        photo.delete()
    except Exception as e:
        print('An error occurred deleting file from S3')
        print(e)
    return redirect('expenses_detail', expense_id=expense_id)