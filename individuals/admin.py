from django.contrib import admin
from .models import IndividualBudget,IndividualTransaction

admin.site.register(IndividualBudget)
admin.site.register(IndividualTransaction)
