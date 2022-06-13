from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import get_user_model
from . import models

logger = logging.getLogger(__name__)

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


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        print("start send mail ")
        logger.info(
            "Sending signup email for email=%s", self.cleaned_data["email"],
        )
        message = "Welcome {}".format(self.cleaned_data["email"])
        print("1")
        send_mail(
            "Welcome to Booktime",
            message,
            "site@booktime.domain",
            [self.cleaned_data["email"]],
            fail_silently=False,

        )
        print("2")