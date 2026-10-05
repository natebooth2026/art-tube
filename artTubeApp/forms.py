from django import forms
from .models import Category, User

class account_creation(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=50)
    pwd = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_pwd = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('pwd')
        confirm = cleaned_data.get('confirm_pwd')

        if pwd and confirm and pwd != confirm:
            self.add_error('confirm_pwd', 'Password doesn\'t match.')

        return cleaned_data

class account_validate(forms.Form):
    email = forms.EmailField()
    pwd = forms.CharField(widget=forms.PasswordInput(), label="Password")

class Sub_Request_Form(forms.Form):
    img = forms.FileField()
    title = forms.CharField(max_length=100)
    desc = forms.CharField(max_length=1000)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Intended Category...",
        label = "Category"
    )