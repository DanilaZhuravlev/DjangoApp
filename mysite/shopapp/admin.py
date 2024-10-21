from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm
import csv


class OrderInline(admin.TabularInline):
    model = Order.product.through

class ProductInline(admin.StackedInline):
    model = ProductImage



@admin.action(description='Archive products')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(archived=True)


@admin.action(description='Unarchive products')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(archived=False)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin,ExportAsCSVMixin):
    change_list_template = 'shopapp/products_changelist.html'
    actions = [
        mark_archived,
        mark_unarchived,
        'export_csv',
    ]
    inlines = [OrderInline, ProductInline,]
    list_display = ('pk', 'name', 'description_short', 'price', 'discount', 'archived')
    list_display_links = 'pk', 'name',
    ordering = ('name','pk')
    search_fields = ('name', 'description', 'price')
    fieldsets = [
        (None, {'fields': ['name', 'description']}),
        ('Price Options', {'fields': ['price', 'discount'],
                           'classes': ('wide', 'collapse', )}),
        ('Extra Options', {'fields': ['archived',],
                          'classes': ('collapse', ),
                           'description': 'Extra options. Field "archived" is for soft delete'}),
        ('Images', {'fields': ['preview', ],}),
    ]

    def description_short(self, obj: Product) -> str:
        if  len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {'form': form}
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            file=form.files['csv_file'].file,
            encoding=request.encoding,
        )
        self.message_user(request, 'Data from CSV imported successfully.')
        return redirect('..')


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-products-csv/',
                self.import_csv,
                name='import_products_csv',
            )
        ]
        return new_urls + urls


class ProductInline(admin.StackedInline):
    model = Order.product.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/orders_changelist.html'
    inlines = [ProductInline]
    list_display = ('delivery_address', 'promocode', 'created_at', 'user_verbose')

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('product')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.import_csv, name='orders_import'),
        ]
        return custom_urls + urls

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {'form': form}
            return render(request, 'admin/csv_form.html', context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'admin/csv_form.html', context, status=400)

        csv_file = request.FILES["csv_file"]
        file_data = csv_file.read().decode("utf-8").splitlines()
        reader = csv.reader(file_data)

        for row in reader:
            Order.objects.create(
                user_id=row[0],
                delivery_address=row[1],
                phone_number=row[2],
                promocode=row[3],
            )

        self.message_user(request, "Orders imported successfully.")
        return redirect('admin:shopapp_order_changelist')