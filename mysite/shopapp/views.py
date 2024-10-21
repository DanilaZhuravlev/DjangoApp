"""В этом модуле лежат различные представления для интернет-магазина. По товарам заказам, и т д."""

import logging
from csv import DictWriter

from django.contrib.auth.models import Group, User
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404, reverse
from django.views.decorators.cache import cache_page

from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from .forms import ProductForm
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .common import save_csv_products




log=logging.getLogger(__name__)

class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest):
        products = [
            ("orange", 1),
            ('banana', 2),
            ('apple', 3),
        ]

        context = {
            'products': products,
            'items': 2,
        }
        print('shop index context', context)
        return render(request, 'shopapp/shop-index.html', context=context)

@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.
    Полный CRUD для сущностей товара

    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter, DjangoFilterBackend, OrderingFilter,
    ]
    search_fields = ['name', 'description']
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name',
                        'description',
                        'price',
                        'discount',
                        'archived',
                        ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]
    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print('Hello products list')
        return super().list(*args, **kwargs)


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    @extend_schema(
        summary='Get one product by id',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description='Empty response, product by id not found'),
        }

    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=['get'],detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = ['name', 'description', 'price', 'discount']
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(methods=['post'],detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self,request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = ['user',
                        'product',
                        'phone_number',
                        ]
    ordering_fields = ['user',
                       'product',
                       'phone_number',
                       ]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)




class GroupsListView(View):
    def get(self, request: HttpRequest):
        context = {
            'form': GroupForm(),
            'groups': Group.objects.all()

        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductsDetailsView(DetailView):
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    template_name = 'shopapp/products-details.html'
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


def create_product(request: HttpRequest):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            url = reverse('shopapp:products_list')
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        'form': form
    }

    return render(request, 'shopapp/create-product.html', context=context)


def create_order(request: HttpRequest):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            url = reverse('shopapp:orders_list')
            return redirect(url)
    else:
        form = OrderForm()

    context = {
        'form': form
    }

    return render(request, 'shopapp/create-order.html', context=context)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'price', 'description', 'discount', 'preview']
    success_url = reverse_lazy('shopapp:products_list')

    permission_required = 'shopapp.add_product'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class OrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/order_list.html'
    model = Order
    context_object_name = 'orders'
    success_url = reverse_lazy('shopapp:products_list')


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user.is_superuser or (user == product.created_by and user.has_perm('shopapp.change_product'))

    def get_success_url(self):
        return reverse('shopapp:products_details', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.FILES.getlist('images'):
            for image in self.request.FILES.getlist('images'):
                ProductImage.objects.create(product=self.object, image=image)
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderDetailView(PermissionRequiredMixin, DetailView):
    model = Order
    template_name = 'shopapp/order_detail.html'
    permission_required = 'shopapp.view_order'


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'user', 'delivery_address', 'product', 'phone_number'
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [{
                'pk': product.pk,
                'name': product.name,
                'price': product.price,
                'archived': product.archived,
            }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({'products': products_data})


class OrdersDataExportView(View):
    def get(self, request, *args, **kwargs):
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
        return JsonResponse({'orders': expected_data})

class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        self.owner = get_object_or_404(User, id=user_id)
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class UserOrdersExportView(View):
    def get(self, request, user_id):
        cache_key = f'user_orders_{user_id}'

        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data, safe=False)

        user = get_object_or_404(User, pk=user_id)
        orders = Order.objects.filter(user=user).order_by('id')

        orders_data = [
            {
                'id': order.id,
                'product_name': order.product.name,
                'delivery_address': order.delivery_address,
            }
            for order in orders
        ]

        cache.set(cache_key, orders_data, timeout=300)

        return JsonResponse(orders_data, safe=False)

class LatestProductsFeed(Feed):
    title = "Latest Products"
    link = "/products/latest/feed/"
    description = "Updates on the latest products."

    def items(self):
        return Product.objects.filter(archived=False).order_by('-created_at')[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse('shopapp:products_details', kwargs={'pk': item.pk})


