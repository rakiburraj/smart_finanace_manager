from django import forms
from django.contrib.auth import get_user_model
from .models import IndividualTransaction, IndividualBudget

User = get_user_model()

INCOME_CATEGORIES = [
    ('salary','Salary'), ('freelance','Freelance'),
    ('business','Business'), ('investment','Investment'), ('other','Other'),
]

EXPENSE_CATEGORIES = [
    ('food','Food'), ('transport','Transport'), ('shopping','Shopping'),
    ('health','Health'), ('education','Education'),
    ('rent','Rent'), ('entertainment','Entertainment'), ('other','Other'),
]


class TransactionForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[])

    class Meta:
        model = IndividualTransaction
        fields = ['type', 'amount', 'category', 'description', 'date']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        txn_type = self.data.get('type') or (self.instance.type if self.instance.pk else 'income')

        self.fields['category'].choices = (
            EXPENSE_CATEGORIES if txn_type == 'expense' else INCOME_CATEGORIES
        )


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
