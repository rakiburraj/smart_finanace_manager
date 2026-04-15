from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta
import json

from .models import IndividualTransaction, IndividualBudget
from .forms import TransactionForm, BudgetForm, IndividualUpdateForm

def get_budget_alert(spent, budget):
    if budget <= 0:
        return None
    pct = (spent / budget) * 100
    if pct >= 100:
        return {'level': 'danger',  'pct': round(pct), 'msg': 'Budget fully used! You have exceeded your monthly budget.'}
    elif pct >= 95:
        return {'level': 'danger',  'pct': round(pct), 'msg': '95% of budget used! Almost at the limit.'}
    elif pct >= 90:
        return {'level': 'warning', 'pct': round(pct), 'msg': '90% of budget used! Be careful with spending.'}
    elif pct >= 75:
        return {'level': 'warning', 'pct': round(pct), 'msg': '75% of budget used! You are spending fast.'}
    elif pct >= 50:
        return {'level': 'info',    'pct': round(pct), 'msg': '50% of budget used. Stay on track!'}
    return None

@login_required
def dashboard(request):
    user  = request.user
    today = date.today()

    # All transactions
    all_txns = IndividualTransaction.objects.filter(user=user)

    # This month
    month_txns   = all_txns.filter(date__year=today.year, date__month=today.month)
    month_income  = month_txns.filter(type='income').aggregate(Sum('amount'))['amount__sum']  or 0
    month_expense = month_txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Today
    today_txns    = all_txns.filter(date=today)
    today_income  = today_txns.filter(type='income').aggregate(Sum('amount'))['amount__sum']  or 0
    today_expense = today_txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # This year
    year_txns    = all_txns.filter(date__year=today.year)
    year_income  = year_txns.filter(type='income').aggregate(Sum('amount'))['amount__sum']  or 0
    year_expense = year_txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Budget
    budget_obj, _ = IndividualBudget.objects.get_or_create(user=user)
    budget        = float(budget_obj.monthly_budget)
    alert         = get_budget_alert(float(month_expense), budget)
    pct_used      = round((float(month_expense) / budget * 100)) if budget > 0 else 0
    pct_used      = min(pct_used, 100)

    # Last 7 days chart data
    labels, income_data, expense_data = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        income_data.append(float(all_txns.filter(date=d, type='income').aggregate(Sum('amount'))['amount__sum'] or 0))
        expense_data.append(float(all_txns.filter(date=d, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0))

    # Monthly chart (last 6 months)
    m_labels, m_income, m_expense = [], [], []
    for i in range(5, -1, -1):
        if today.month - i <= 0:
            yr, mo = today.year - 1, today.month - i + 12
        else:
            yr, mo = today.year, today.month - i
        m_labels.append(date(yr, mo, 1).strftime('%b %Y'))
        m_income.append(float(all_txns.filter(date__year=yr, date__month=mo, type='income').aggregate(Sum('amount'))['amount__sum'] or 0))
        m_expense.append(float(all_txns.filter(date__year=yr, date__month=mo, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0))

    return render(request, 'individuals/dashboard.html', {
        'month_income': month_income,   'month_expense': month_expense,
        'today_income': today_income,   'today_expense': today_expense,
        'year_income':  year_income,    'year_expense':  year_expense,
        'balance': month_income - month_expense,
        'budget': budget, 'pct_used': pct_used, 'alert': alert,
        'recent_txns': all_txns[:8],
        'labels':       json.dumps(labels),
        'income_data':  json.dumps(income_data),
        'expense_data': json.dumps(expense_data),
        'm_labels':     json.dumps(m_labels),
        'm_income':     json.dumps(m_income),
        'm_expense':    json.dumps(m_expense),
    })
