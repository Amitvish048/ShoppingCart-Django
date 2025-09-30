from django import forms
from .models import Account


class RegistrationFrom(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter a Password'

        
        }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter a Password'
        
        }))

    class Meta:
        model = Account
        fields = ['first_name','last_name','email','phone_number','password']

    def __init__(self, *args, **kwargs):
        super(RegistrationFrom, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationFrom, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match !."
            )
        
        