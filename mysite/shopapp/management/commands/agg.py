from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Product
from django.db.models import aggregates, Avg, Max, Min, Count, Sum


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Create Order with products')
        result = Product.objects.aggregate(
            Avg('price'),
            Max('price'),
            Min('price'),
            Count('id'),
        )
        print(result)
        self.stdout.write('Done')
