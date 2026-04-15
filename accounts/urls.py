from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/individual/', views.individual_register, name='individual_register'),
    path('register/company/', views.company_register, name='company_register'),
    path('login/individual/', views.individual_login, name='individual_login'),
    path('login/finance-head/', views.finance_head_login, name='finance_head_login'),
    path('login/dept-rep/', views.dept_rep_login, name='dept_rep_login'),
    path('logout/', views.logout_view, name='logout'),
]