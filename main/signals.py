from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import get_object_or_404
from .models import ProductImage, Basket


THUMBNAIL_SIZE = (300, 300)
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(
        "Generating thumbnail for product %d",
        instance.product.id,
    )
    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)
    # set save=False, otherwise it will run in an infinite loop
    instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
    )
    temp_thumb.close()



@receiver(user_logged_in)
def marge_basket_if_exist(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, 'basket', None)
    if anonymous_basket:
        try:
            loggedin_basket = Basket.objects.get(user = user, status = Basket.OPEN)  
            for line in anonymous_basket.basketline_set.all():
                try:
                    logedin_line = loggedin_basket.basketline_set.get(product = line.product)               
                except:
                    logedin_line = None
                    
                if logedin_line:                                       
                    line.basket = loggedin_basket                   
                    line.quantity = logedin_line.quantity + line.quantity
                    line.save()
                    logedin_line.delete()
                else:                      
                    line.basket = loggedin_basket
                    line.save()
            anonymous_basket.delete()
            request.basket = loggedin_basket
            request.session['basket_id'] = loggedin_basket.id
            logger.info(f'Merge basket to id = {loggedin_basket.id}')    

        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info(f'User assign to basket id - {anonymous_basket.id}')    
    else:
        try:
            loggedin_basket = Basket.objects.get(user = user, status = Basket.OPEN)         
            if loggedin_basket:
                request.basket = loggedin_basket
                request.session['basket_id'] = loggedin_basket.id  
        except Basket.DoesNotExist:
                request.session['basket_id'] = None
                request.basket = None
                       