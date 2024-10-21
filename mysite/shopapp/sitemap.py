from django.contrib.sitemaps import Sitemap
from .models import Product, Order

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(archived=False)

    def lastmod(self, obj):
        return obj.created_at

class OrderSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Order.objects.all()

    def lastmod(self, obj):
        return obj.created_at