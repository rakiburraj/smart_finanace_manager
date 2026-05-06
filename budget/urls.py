from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('history/', views.budget_history, name='history'),
]