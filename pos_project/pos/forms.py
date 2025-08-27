from django import forms
from django.forms import inlineformset_factory
from .models import Product, Customer, Sale, SaleItem, Payment
class ProductForm(forms.ModelForm):
    class Meta: model = Product; fields = ['name','sku','price','stock','is_active']
class CustomerForm(forms.ModelForm):
    class Meta: model = Customer; fields = ['name','email','phone','address']
class SaleForm(forms.ModelForm):
    class Meta: model = Sale; fields = ['customer','notes','discount_amount','tax_percent']
class PaymentForm(forms.ModelForm):
    class Meta: model = Payment; fields = ['amount','method']
SaleItemFormSet = inlineformset_factory(Sale, SaleItem, fields=['product','quantity','unit_price','discount_percent'], extra=1, can_delete=True)
