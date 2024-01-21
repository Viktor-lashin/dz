from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(attrs={"class": "col-9 log-field form-control form-control-sm"})
    )
    password = forms.CharField(
        min_length=4,
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "col-9 log-field form-control form-control-sm"})
    )


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(attrs={"class": "col-9 log-field form-control form-control-sm"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "col-9 log-field"})
    )
    first_name = forms.CharField(
        label="NickName",
        widget=forms.TextInput(attrs={"class": "col-9 log-field form-control form-control-sm"})
    )
    password = forms.CharField(
        min_length=4,
        label='Password',
        widget=forms.PasswordInput(attrs={"class": "col-9 log-field form-control form-control-sm"})
    )
    password_check = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput(attrs={"class": "col-9 log-field form-control form-control-sm"})
    )

    image = forms.ImageField(required=False, label="Upload avatar",
                             widget=forms.FileInput(attrs={"class": "col-9 choose_file"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password_check(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password_check']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password_check']

    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        self.cleaned_data.pop('image')
        return User.objects.create_user(**self.cleaned_data)


class SettingsForm(forms.Form):
    username = forms.CharField(label="Login", widget=forms.TextInput(attrs={"class": "col-9 log-field"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "col-9 log-field"}))
    first_name = forms.CharField(label="NickName", widget=forms.TextInput(attrs={"class": "col-9 log-field"}))

    image = forms.ImageField(required=False, label="Upload avatar", widget=forms.FileInput(attrs={"class": "col-9"}))


class QuestionForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "col-9 question-field"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "col-9 question-field"}))
    tags = forms.CharField(widget=forms.TextInput(attrs={"class": "col-9 question-field"}))


class AddAnswerForm(forms.Form):
    answer = forms.CharField(
        widget=forms.Textarea(attrs={"class": "col-9 question-field", "placeholder": "Enter your answer here"}))
