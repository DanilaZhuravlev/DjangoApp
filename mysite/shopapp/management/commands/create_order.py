from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Order, Product
from django.db import transaction


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Create Order with products')
        user = User.objects.get(username='admin')
        products: Sequence[Product] = Product.objects.only('id').all()
        order, created = Order.objects.get_or_create(
            delivery_address="ST.P",
            promocode="Promo3",
            user=user,
        )
        for product in products:
            order.product.add(product)
        self.stdout.write(f'Created Order {order}')
