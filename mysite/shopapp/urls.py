from django.views.decorators.cache import cache_page
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.sitemaps.views import sitemap
from .views import (
    ShopIndexView,
    GroupsListView, ProductsListView, OrdersListView, create_product,
    create_order, ProductsDetailsView, OrderDetailView, ProductCreateView,
    ProductUpdateView, ProductDeleteView, OrderUpdateView, OrderDeleteView,
    ProductsDataExportView, OrdersDataExportView, ProductViewSet, OrderViewSet, LatestProductsFeed, UserOrdersListView,
    UserOrdersExportView,
)
from .sitemap import ProductSitemap, OrderSitemap

app_name = 'shopapp'

sitemaps = {
    'products': ProductSitemap,
    'orders': OrderSitemap,
}

routers = DefaultRouter()
routers.register('products', ProductViewSet)
routers.register('orders', OrderViewSet)

urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),
    path('api/', include(routers.urls)),
    path('groups/', GroupsListView.as_view(), name='groups_list'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/export/', ProductsDataExportView.as_view(), name='products_export'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductsDetailsView.as_view(), name='products_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='products_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='products_delete'),
    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_details'),
    path('orders/create/', create_order, name='order_create'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='orders_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='orders_delete'),
    path('orders/export/', OrdersDataExportView.as_view(), name='orders_export'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('products/latest/feed/', LatestProductsFeed(), name='products_latest_feed'),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='users_orders_list'),
    path('users/<int:user_id>/orders/export/', UserOrdersExportView.as_view(), name='user_orders_export'),
]
