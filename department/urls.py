from django.urls import path
from . import views

app_name = 'department'

urlpatterns = [
    
    path('head/', views.head_dashboard, name='head_dashboard'),
    path('create/', views.create_department, name='create_department'),
    path('assign/<int:dept_id>/', views.assign_rep, name='assign_rep'),
    path('remove-rep/<int:dept_id>/', views.remove_rep, name='remove_rep'),
    path('budget/<int:dept_id>/', views.update_budget, name='update_budget'),
    path('detail/<int:dept_id>/', views.dept_detail, name='dept_detail'),
    path('budget-respond/<int:req_id>/<str:action>/', views.respond_budget, name='respond_budget'),
    
    path('rep/', views.rep_dashboard, name='rep_dashboard'),
    path('rep/add/', views.add_dept_transaction, name='add_dept_transaction'),
    path('rep/request-budget/', views.request_budget, name='request_budget'),
    path('rep/delete/<int:pk>/', views.delete_dept_transaction, name='delete_dept_transaction'),
    path('report/monthly/<int:dept_id>/', views.monthly_report, name='monthly_report'),
    path('report/yearly/<int:dept_id>/', views.yearly_report, name='yearly_report'),
    path('company/monthly/', views.company_monthly_report, name='company_monthly_report'),
path('company/yearly/', views.company_yearly_report, name='company_yearly_report'),
    
]