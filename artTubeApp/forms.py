from django import forms
from .models import Category
from django.core.exceptions import ValidationError
from magic import from_buffer

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

class account_validate_emailMFA(forms.Form):
    email_code = forms.PasswordInput()

class account_validate_questionsSetup(forms.Form):
    q1 = forms.CharField(max_length=100)
    q_answer1 = forms.CharField(max_length=1000)
    q2 = forms.CharField(max_length=100)
    q_answer2 = forms.CharField(max_length=1000)

class account_validate_questionsMFA(forms.Form):
    q_answer1 = forms.CharField(max_length=1000)
    q_answer2 = forms.CharField(max_length=1000)

class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class sub_request_form(forms.Form):
    img = forms.ImageField()
    title = forms.CharField(max_length=100)
    desc = forms.CharField(max_length=1000, required=False)
    category = CategoryChoiceField(
        queryset=Category.objects.all(),
        empty_label="Intended Category...",
        label = "Category"
    )

    def clean_img(self):
        img = self.cleaned_data.get('img')
        if not img:
            return img
        if img:
            try:
                mime = from_buffer(img.read(2048), mime=True)
                img.seek(0)
            except Exception as e:
                raise ValidationError(f"File inspection failed: {str(e)}")

            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if mime not in allowed_types:
                raise ValidationError(f"Invalid file type: {mime}")
        return img