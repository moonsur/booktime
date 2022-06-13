from dataclasses import fields
from django.contrib import admin
from . import models
from django.utils.html import format_html

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','slug','price', 'in_stock', 'active')
    list_editable = ('in_stock','active')
    list_filter = ('active', 'in_stock', 'date_updated')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('tags',)

admin.site.register(models.Product, ProductAdmin)

class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'active')
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    #autocomplete_fields = ('products',)

admin.site.register(models.ProductTag, ProductTagAdmin)

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'image_thumbnail')
    readonly_fields = ('thumbnail',)
    search_fields = ('product_name',)

    def product_name(self, obj):
        return obj.product.name

    def image_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src = "%s"/>' % obj.thumbnail.url
            )
        else:
            return "-"

    image_thumbnail.short_description = "Thumbnail"


admin.site.register(models.ProductImage, ProductImageAdmin)

class AboutUsAdmin(admin.ModelAdmin):
    #list_display= ('content',)

    def has_add_permission(self, request, obj=None):
        if (models.AboutUs.objects.count() >= 1):
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False       


admin.site.register(models.AboutUs, AboutUsAdmin)

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    fieldsets =(
        (
            None, {"fields": ("email", "password")},
        ),
        (
            "Personal Information:",
            {"fields": ("first_name","last_name")},
        ),
        (
            "Permission:",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (
            "Important Dates:",
            {"fields": ("last_login", "date_joined")},
        ),
    )

    add_fieldsets =(
        (
            None, {
                "classes": ("wide",), "fields": ("email", "password1", "password2")
            },
        ),
    )

    list_display = ("email","first_name", "last_name", "is_staff", "is_superuser")
    search_fields =("email","first_name", "last_name",)
    ordering = ("email",)




class BasketLineInline(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ('product',)

@admin.register(models.Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status')
    list_editable = ('status',)   
    list_filter = ('status',)
    inlines = (BasketLineInline,) 