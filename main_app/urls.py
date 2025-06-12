from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('ledgers/', views.ledgers_index, name='ledgers_index'),
    path('ledgers/<int:ledger_id>/', views.ledgers_detail, name='ledgers_detail'),
    path('ledgers/create/', views.LedgerCreate.as_view(), name='ledgers_create'),
]