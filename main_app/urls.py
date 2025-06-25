from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/myprofile/', views.my_profile, name='my_profile'),
    path('ledgers/', views.ledgers_index, name='ledgers_index'),
    path('ledgers/<int:ledger_id>/', views.ledgers_detail, name='ledgers_detail'),
    path('ledgers/create/', views.LedgerCreate.as_view(), name='ledgers_create'),
    path('ledgers/<int:pk>/update/', views.LedgerUpdate.as_view(), name='ledgers_update'),
    path('ledgers/<int:pk>/delete/', views.LedgerDelete.as_view(), name='ledgers_delete'),
    path('ledgers/<int:ledger_id>/add_expense/', views.add_expense, name='add_expense'),
    path('expenses/<int:expense_id>/', views.expenses_detail, name='expenses_detail'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdate.as_view(), name='expenses_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDelete.as_view(), name='expenses_delete'),
]