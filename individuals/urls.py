from django.urls import path
from . import views

app_name = 'individuals'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('budget/', views.set_budget, name='set_budget'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
   
    
]
