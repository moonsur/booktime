from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from . import models

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

class ContactForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100)
    message = forms.CharField(max_length=600, widget=forms.Textarea)

    def send_email(self):
        logger.info("This email send from customer")
        message = "From: {0} \n {1}".format(
            self.cleaned_data['name'],
            self.cleaned_data['message']
        )
        send_mail(
            "From website",
            message,
            "site@booktime.com",
            ['monsur.domtech@gmail.com',],
            fail_silently=False
        )




User = get_user_model()

class UserRegistrationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        #model = User
        fields = ('email',)
        field_classes = {'email': UsernameField}


    def send_mail(self):
        logger.info("This email sent during signup")
        message = f"You have signed up with the email {self.cleaned_data['email']}, Welcome to Booktime."
        email = self.cleaned_data['email']
        send_mail(
            "From Booktime",
            message,
            "site@booktime.com",
            [email,],
            fail_silently=False
        )

from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email  = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            self.user = authenticate(self.request, email = email, password = password)

        if self.user is None:
            raise forms.ValidationError('User or Password is not valid.')
        else:
            logger.info(f'You have logged in with the email {email}')


        return self.cleaned_data   

    def get_user(self):
        return self.user

from . import widget

BasketLineFormset = inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=('quantity',),
    extra=0,
    widgets={'quantity':widget.PlusMinusNumberInput()}
)            


class AdressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset
