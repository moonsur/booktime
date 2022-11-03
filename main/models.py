from asyncio import exceptions
from turtle import Turtle
from django.db import models
from django.core.exceptions import ValidationError
import logging
from django.contrib.auth.models import AbstractUser, BaseUserManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeneralSettings(models.Model):
    site_name = models.CharField(max_length=20)
    logo = models.ImageField(upload_to = 'logo', null = True, blank=True)
    logo_alt_text = models.CharField(max_length=20, blank=True)
    show_products_per_page = models.IntegerField(default=6) 


    def __str__(self):
        return "Click here to edit General Settings"

    def clean(self):
        if (GeneralSettings.objects.count() >= 1 and self.pk is None):
            raise ValidationError("Can only create single entity.")

    class Meta:
        verbose_name = 'General Settings'
        verbose_name_plural = 'General Settings'

class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug = slug)

class ProductTag(models.Model):
    #products = models.ManyToManyField(Product, blank=True)
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=35)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    objects = ProductTagManager()

    def __str__(self):
        return self.name    

    def natural_key(self):
        return (self.slug,)        

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=50)
    author = models.CharField(max_length=60, default='Unknown')
    best_seller = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(ProductTag, blank=True)

    objects = ActiveManager()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product-images')
    thumbnail = models.ImageField(upload_to='image-thumbnail', null=True)


    def __str__(self):
        return "Image of - "+self.product.name


class AboutUs(models.Model):
    content = models.TextField()

    def __str__(self):
        return "Click here to edit About Us"

    def clean(self):
        if (AboutUs.objects.count() >= 1 and self.pk is None):
            raise ValidationError("Can only create single entity.")

    class Meta:
        verbose_name = 'About Us'
        verbose_name_plural = 'About Us'





class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email address must have provided.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using =self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)        
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email,password, **extra_fields)   

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)        
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Super user must have is_staff role.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super user must have is_superuser role.')

        return self._create_user(email,password, **extra_fields)   


class User(AbstractUser): 
    #logger.info('model User')   
    username = None
    email = models.EmailField("Email Address", unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS= []

    objects = UserManager()

         


    
class Address(models.Model):
    SUPPORTED_COUNTRIES = (
        ('UK', 'United Kingdom'),
        ('USA', 'United State of America'),
        ('BD', 'Bangladesh'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address1 = models.CharField('Address Line 1',max_length=120)
    address2 = models.CharField('Address Line 2',max_length=120, blank=True)
    zip_code = models.CharField('Zip/Postal Code',max_length=12)
    city = models.CharField(max_length=40)
    country = models.CharField(max_length=3, choices=SUPPORTED_COUNTRIES)

    def __str__(self):
        return ', '.join(
            [self.name, self.address1, self.address2, self.zip_code, self.city, self.country]
        )

class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = (
        (OPEN, 'Open'),
        (SUBMITTED, 'Submitted'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())  

    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise exceptions.BasketException(f"Order can't created without User!")

        logger.info(
            f'Order creating for basket id = {self.id}, shipping address id = {shipping_address.id}, billing address id = {billing_address.id}'
        )  

        order_data ={
            "user": self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_zip_code": billing_address.zip_code, 
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name, 
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_zip_code": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country,
        }
        order = Order.objects.create(**order_data)
        c = 0
        for line in self.basketline_set.all():
            for _ in range(line.quantity):
                order_line_data ={
                    'order': order,
                    'product': line.product,
                }        
                #order_line = OrderLine.objects.create(**order_line_data)
                OrderLine.objects.create(**order_line_data)
                c +=1

        logger.info(f'Order created with id = {order.id} and order line count = {c}') 
        self.status = self.SUBMITTED
        self.save()
        return order 

    def __str__(self):
        return f"Basket ID - {self.id}"          


from django.core.validators import MinValueValidator

class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product =models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.product.name


class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW,"New"), (PAID,"Paid"),(DONE,"Done"),)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)

    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField('Address Line 1',max_length=120)
    billing_address2 = models.CharField('Address Line 2',max_length=120, blank=True)
    billing_zip_code = models.CharField('Zip/Postal Code',max_length=12)
    billing_city = models.CharField(max_length=40)
    billing_country = models.CharField(max_length=3)   

    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField('Address Line 1',max_length=120)
    shipping_address2 = models.CharField('Address Line 2',max_length=120, blank=True)
    shipping_zip_code = models.CharField('Zip/Postal Code',max_length=12)
    shipping_city = models.CharField(max_length=40)
    shipping_country = models.CharField(max_length=3)

    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)


class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCEL = 40
    STATUSES = ((NEW,"New"),(PROCESSING,"Processing"), (SENT,"Sent"), (CANCEL,"Cancel"))

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)


class SingleFirstSlideModel(models.Model):
    first_slide = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.first_slide:
            # select all other active items
            qs = type(self).objects.filter(first_slide=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(first_slide=False) 

        super(SingleFirstSlideModel, self).save(*args, **kwargs)

class HomeSlider(SingleFirstSlideModel):
    image = models.ImageField(upload_to='home-sliders') 
    alt_text = models.CharField(max_length=20)
    quoted_by = models.CharField(max_length=30)  
    caption_text = models.CharField(max_length=260)  
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.alt_text
    
