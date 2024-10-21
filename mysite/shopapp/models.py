from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def product_preview_directory_path(instance:'Product', filename: str):
    return 'products/product_{pk}/preview/{filename}'.format(pk=instance.pk, filename=filename)


class Product(models.Model):
    """
    Модель Product представляет товар, который можно продавать в интернет-магазине
    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='products')
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)


    # class Meta:
    #     ordering = ['-price']
    #
    # @property
    # # def description_short(self):
    # #     if len(self.description) < 48:
    # #         return self.description
    # #     return self.description[:48] + '...'

    def __str__(self):
        return f'Product: (pk={self.pk}, name={self.name!r})'

    def get_absolute_url(self):
        return reverse('shopapp:products_details', kwargs={'pk': self.pk})

def product_images_directory_path(instance:'Product', filename: str):
    return 'products/product_{pk}/images/{filename}'.format(pk=instance.product.pk, filename=filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=255, null=False, blank=True)




class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20,null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ManyToManyField(Product,related_name='orders')
    phone_number = models.CharField(max_length=20,null=False, blank=True)
    receipt = models.FileField(null=True, upload_to='orders/receipts')

    def get_absolute_url(self):
        return reverse('shopapp:order_details', kwargs={'pk': self.pk})

    def __str__(self):
        return f'Order {self.pk} by {self.user}'