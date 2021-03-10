from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate
import logging
from django.views.generic.list import ListView
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView
from main import forms, models


class ContactUsView(FormView):
    template_name = 'contact_form.html'
    form_class = forms.ContactForm
    success_url = '/'

    def form_valid(self, form):
        print("form valid- "+"1")
        form.send_mail()
        print("form valid- "+"2")
        return super().form_valid(form)


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 2

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != 'all':
            self.tag = get_object_or_404(
                models.ProductTag, slug=tag
            )
        if self.tag:
            products = models.Product.objects.active().filter(
                tags=self.tag
            )
        else:
            products = models.Product.objects.active()

        return products.order_by('name')


logger = logging.getLogger(__name__)


class SignupView(FormView):
    print("start signup view")
    template_name = "main/signup.html"
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        print("redirect"+redirect_to)
        return redirect_to

    def form_valid(self, form):
        print("sign up form valid- "+"1")
        response = super().form_valid(form)
        form.save()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(
            "New signup for email=% with SignupView", email
        )
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, "You have singed up successfully")
        print("sign up form valid- "+"2")
        return response


"""
    def form_invalid(self, form):
        print("form is invalid")
        return render(self.request, 'main/signup.html', {'form': form})
"""
