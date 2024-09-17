from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ContractManageForm(forms.Form):
    select = forms.fields.ChoiceField(
        required=True,
        widget=forms.widgets.Select
    )

