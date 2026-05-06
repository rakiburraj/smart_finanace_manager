from django.contrib import admin
from .models import MonthlyBudgetHistory


@admin.register(MonthlyBudgetHistory)
class MonthlyBudgetHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'department',
        'year',
        'month',
        'allocated',
        'total_expense',
        'total_income',
        'saved',
        'carried_over',
        'created_at'
    )

    list_filter = ('year', 'month', 'department')
    search_fields = ('department__name',)
    ordering = ('-year', '-month')