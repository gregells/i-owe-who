from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/my_profile/', views.my_profile, name='my_profile'),
    path('accounts/send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('accounts/accept_friend_request/<int:user_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('accounts/cancel_friend_request/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('accounts/remove_friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('ledgers/', views.ledgers_index, name='ledgers_index'),
    path('ledgers/<int:ledger_id>/', views.ledgers_detail, name='ledgers_detail'),
    path('ledgers/create/', views.LedgerCreate.as_view(), name='ledgers_create'),
    path('ledgers/<int:pk>/update/', views.LedgerUpdate.as_view(), name='ledgers_update'),
    path('ledgers/<int:pk>/delete/', views.LedgerDelete.as_view(), name='ledgers_delete'),
    path('ledgers/<int:ledger_id>/add_expense/', views.add_expense, name='add_expense'),
    path('expenses/', views.expenses_index, name='expenses_index'),
    path('expenses/<int:expense_id>/', views.expenses_detail, name='expenses_detail'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdate.as_view(), name='expenses_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDelete.as_view(), name='expenses_delete'),
    path('expenses/<int:expense_id>/add_photo/', views.add_photo, name='add_photo'),
    path('expenses/<int:expense_id>/delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('expenses/search/', views.expenses_search, name='expenses_search'),
]