from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm
from shopapp.models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'discount', 'preview',]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'delivery_address', 'phone_number', 'promocode', 'product', ]


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()