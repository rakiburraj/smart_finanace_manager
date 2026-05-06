from django import forms
from django.contrib.auth import get_user_model
from .models import IndividualTransaction, IndividualBudget

User = get_user_model()




class TransactionForm(forms.ModelForm):
   

    class Meta:
        model = IndividualTransaction
        fields = ['type', 'amount', 'description', 'date']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        txn_type = self.data.get('type') or (self.instance.type if self.instance.pk else 'income')

        

class BudgetForm(forms.ModelForm):
    class Meta:
        model = IndividualBudget
        fields = ['monthly_budget']


class IndividualUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'profession', 'monthly_income',
            'monthly_expense', 'income_source',
            'profile_pic'
        ]
