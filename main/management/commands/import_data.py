from django.core.management.base import BaseCommand
from collections import Counter
import csv
from os import path
from django.core.files.images import ImageFile
from django.template.defaultfilters import slugify
from main import models

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=open)
        parser.add_argument('image_dir', type=str)

    def handle(self, *args, **options):
        self.stdout.write('Import Products in Booktime..')
        c = Counter()
        reader = csv.DictReader(options.pop('csvfile'))
        for row in reader:
            product, created = models.Product.objects.get_or_create(
                name = row['name'],
                price = row['price']
            ) 
            product.description = row['description']
            product.slug = slugify(row['name'])
            product.author = row['author']
            for product_tag in row['tags'].split('|'):
                tag, tag_created = models.ProductTag.objects.get_or_create(
                    name = product_tag,
                    slug = slugify(product_tag)
                )
                product.tags.add(tag)
                c['tags'] += 1
                if tag_created:
                    c['tags_created'] +=1
            with open(              
                path.join(options['image_dir'], row['image_filename']), "rb"
            ) as f:
                image = models.ProductImage(
                    product =product,
                    image = ImageFile(f, row['image_filename'])
                )
                image.save()
            product.save()
            c['images'] += 1
            c['products'] += 1
            if created:
                c['products_created'] += 1

        self.stdout.write(f'Products Processed = {c["products"]} and Created = {c["products_created"]}') 
        self.stdout.write(f'Tags processed = {c["tags"]} and Created = {c["tags_created"]}') 
        self.stdout.write(f'Image created = {c["images"]}')      

