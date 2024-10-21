from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_two_numbers(self):
        result = add_two_numbers(1, 2)
        self.assertEqual(result, 3)


class ProductCreateViewTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin_create', password='12345678')
        self.client.login(username='admin_create', password='12345678')
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'price': '123',
                'description': 'A good table',
                'discount': '10',
            }
        )
        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(username='admin_details', password='12345678')
        cls.product = Product.objects.create(
            name='Best Product',
            created_by=cls.admin_user
        )

    def setUp(self):
        self.client.login(username='admin_details', password='12345678')

    def test_get_product_and_check_content(self):
        response = self.client.get(reverse('shopapp:products_details', kwargs={'pk': self.product.pk}))
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'groups-fixture.json',
        'users-fixture.json',
        'products-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).order_by('pk'),
            values=sorted(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(username='admin_orders', password='12345678')
        cls.product = Product.objects.create(
            name='Best Product',
            created_by=cls.admin_user,
        )

    def setUp(self):
        self.client.login(username='admin_orders', password='12345678')

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


@user_passes_test(lambda u: u.is_staff)
def orders_export_view(request):
    orders = Order.objects.all()
    orders_data = [
        {
            'id': order.id,
            'address': order.delivery_address,
            'promocode': order.promocode,
            'user_id': order.user.id,
            'product_ids': [product.id for product in order.product.all()],
        }
        for order in orders
    ]
    return JsonResponse({'orders': orders_data})


class OrdersExportViewTestCase(TestCase):
    fixtures = ['users-fixture.json', 'groups-fixture.json', 'products-fixture.json', 'orders-fixture.json']

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(username='admin_export', password='password')

    @classmethod
    def tearDownClass(cls):
        cls.admin_user.delete()

    def setUp(self):
        self.client.login(username='admin_export', password='password')

    def test_orders_export(self):
        response = self.client.get(reverse('shopapp:orders_export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.all()
        expected_data = [
            {
                'id': order.id,
                'address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.id,
                'product_ids': [product.id for product in order.product.all()],
            }
            for order in orders
        ]
        self.assertEqual(response.json()['orders'], expected_data)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser_detail', password='password')
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)

        cls.product = Product.objects.create(name='Test Product', price=100, created_by=cls.user)
        cls.order = Order.objects.create(delivery_address='Test address', promocode='PROMO123', user=cls.user)
        cls.order.product.add(cls.product)

    @classmethod
    def tearDownClass(cls):
        cls.order.delete()
        cls.product.delete()
        cls.user.delete()

    def setUp(self):
        self.client.login(username='testuser_detail', password='password')

    def test_order_details(self):
        response = self.client.get(reverse('shopapp:order_details', kwargs={'pk': self.order.pk}))
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context['order'].pk, self.order.pk)
