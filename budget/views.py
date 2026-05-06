from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from department.models import Department
from .models import MonthlyBudgetHistory

@login_required
def budget_history(request):
    departments = Department.objects.filter(finance_head=request.user)
    history = MonthlyBudgetHistory.objects.filter(
        department__in=departments
    ).select_related('department')
    return render(request, 'budget/history.html', {'history': history})