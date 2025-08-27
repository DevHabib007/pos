from django.db import models
from django.utils import timezone
from decimal import Decimal

class Customer(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"{self.name} ({self.sku})"

class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=255, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return sum(item.line_total_before_tax for item in self.items.all())

    @property
    def total_discount(self):
        item_discounts = sum((item.unit_price * item.quantity - item.line_total_before_tax) for item in self.items.all())
        return Decimal(item_discounts) + (self.discount_amount or Decimal('0'))

    @property
    def tax_amount(self):
        base = self.subtotal - (self.discount_amount or Decimal('0'))
        return (base * (self.tax_percent or Decimal('0'))) / Decimal('100')

    @property
    def total(self):
        return (self.subtotal - (self.discount_amount or Decimal('0'))) + self.tax_amount

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self): return f"Sale #{self.id} - {self.created_at:%Y-%m-%d %H:%M}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def line_total_before_tax(self):
        discount = (self.unit_price * self.quantity) * (self.discount_percent or 0) / 100
        return (self.unit_price * self.quantity) - discount

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
        if self.product and self.quantity:
            self.product.stock = max(0, self.product.stock - self.quantity)
            self.product.save(update_fields=['stock'])

    def __str__(self): return f"{self.product} x {self.quantity}"

class Payment(models.Model):
    METHODS = [('cash','Cash'),('card','Card'),('mobile','Mobile Payment')]
    sale = models.OneToOneField(Sale, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHODS, default='cash')
    paid_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return f"Payment for Sale #{self.sale_id} - {self.amount}"
