from django.contrib import admin
from .models import Product, Customer, Sale, SaleItem, Payment
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','sku','price','stock','is_active')
    search_fields = ('name','sku')
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name','email','phone')
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id','customer','created_at','total','total_items')
    inlines = [SaleItemInline]
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('sale','amount','method','paid_at')
