from django.contrib import admin
from .models import (
    Department,
    DepartmentRep,
    DepartmentTransaction,
    BudgetRequest
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'finance_head',
        'monthly_budget',
        'carried_over',
        'total_budget_display',
        'created_at'
    )
    search_fields = ('name',)
    list_filter = ('created_at',)

    def total_budget_display(self, obj):
        return obj.total_budget()
    total_budget_display.short_description = 'Total Budget'



@admin.register(DepartmentRep)
class DepartmentRepAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'plain_password')
    search_fields = ('user__username', 'department__name')



@admin.register(DepartmentTransaction)
class DepartmentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'department',
        'type',
        'amount',
        'added_by',
        'date',
        'created_at'
    )
    list_filter = ('type', 'department', 'date')
    search_fields = ('department__name', 'description')
    date_hierarchy = 'date'



@admin.register(BudgetRequest)
class BudgetRequestAdmin(admin.ModelAdmin):
    list_display = (
        'department',
        'requested_by',
        'requested_amount',
        'status',
        'request_date',
        'responded_by',
        'response_date'
    )
    list_filter = ('status', 'department', 'request_date')
    search_fields = ('department__name', 'requested_by__username', 'reason')
    readonly_fields = ('request_date', 'response_date')

    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    reject_requests.short_description = "Reject selected requests"