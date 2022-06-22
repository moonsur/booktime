from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView 
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from main import forms, models
import logging
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactUsForm(FormView):
    #logger.info('contact us view')
    template_name = "contact-us.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_email()
        #logger.info('22222222222222')
        return super().form_valid(form)

# This code is add for future referece purpose
def contact_us(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            form.send_mail()
            return HttpResponseRedirect('/')
    else:
        form = forms.ContactForm()
    return render(request, 'contact-us.html', {'form': form})

class ProductListView(ListView):
   # logger.info('Product List view')
    template_name = "main/product_list.html"
    paginate_by = 5

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != 'All':
            self.tag = get_object_or_404(models.ProductTag, slug= tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags = self.tag)
        else:
            products = models.Product.objects.active()        
        logger.info('End of Product List view')
        return products.order_by('name')


def about_us_View(request):
    aboutus = models.AboutUs.objects.first()
    return render(request, 'about-us.html', {'about':aboutus})




User = get_user_model()

class SignupView(FormView):
    template_name = "signup.html"
    #model = User
    form_class = forms.UserRegistrationForm
    #logger.info('signup view after form class asign')

    def get_success_url(self):
        redirect_to = self.request.GET.get('next','/')
        return redirect_to

    def form_valid(self, form):        
        response = super().form_valid(form)
        form.save()        
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        logger.info(f'Signup complete with email {email}')
        messages.info(self.request,"You signed up successfully")

        return response


class AddressListView(LoginRequiredMixin, ListView):
    template_name = 'main/address_list.html'
    model = models.Address
    context_object_name = 'address_list'

    def get_queryset(self):
        queryset = self.model.objects.filter(user = self.request.user)       
        return queryset

class AddressCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/address_create.html'
    model = models.Address

    fields = [
        'name',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country'
    ]
    success_url = reverse_lazy('address_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'main/address_update.html'
    model = models.Address
    #context_object_name = 'address_update' # not working in this view
    fields =[
        'name',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country'
    ]     
    success_url = reverse_lazy('address_list')
    def get_queryset(self):        
        queryset = self.model.objects.filter(id=self.kwargs['pk'])
        return queryset  

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'main/address_delete.html'
    model = models.Address
            
    success_url = reverse_lazy('address_list')
    def get_queryset(self):        
        queryset = self.model.objects.filter(id=self.kwargs['pk'])
        return queryset  



def add_to_basket(request):
    product = get_object_or_404(models.Product, pk=request.GET.get('product_id'))
    if request.basket:
        basket = request.basket
    else:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        basket = models.Basket.objects.create(user = user)

    basketline, created = models.BasketLine.objects.get_or_create(
        product = product,
        basket = basket
    ) 
    if not created:
        basketline.quantity += 1
        basketline.save()        

    request.session['basket_id'] = basket.id 

    return HttpResponseRedirect(reverse('product', args=(product.slug,)))

def manage_basket(request):
    if request.basket.is_empty() or not request.basket:       
        return render(request, 'main/basket.html', {'formset': None})    
   
    if request.method == 'POST':       
        formset = forms.BasketLineFormset(request.POST, instance=request.basket)         
        if formset.is_valid():            
            formset.save()            
    #else:        
        #formset = forms.BasketLineFormset(instance=request.basket)

    formset = forms.BasketLineFormset(instance=request.basket)
    return render(request, 'main/basket.html', {'formset': formset})               


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "main/address_select.html"
    form_class = forms.AdressSelectionForm
    #context_object_name = 'addressesobj'
    success_url = reverse_lazy('checkout_done') 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(form.cleaned_data['billing_address'], form.cleaned_data['shipping_address'])
        return super().form_valid(form)    

