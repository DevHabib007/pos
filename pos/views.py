from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import Product, Customer, Sale, SaleItem, Payment
from .forms import ProductForm, CustomerForm, SaleForm, SaleItemFormSet, PaymentForm
from decimal import Decimal

def index(request):
    return render(request, "pos/index.html", {
        "product_count": Product.objects.count(),
        "customer_count": Customer.objects.count(),
        "sale_count": Sale.objects.count(),
    })

@permission_required('pos.add_product', raise_exception=True)
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,"Product created."); return redirect('product_list')
    return render(request,"pos/product_form.html",{"form":form,"title":"Add Product"})

@permission_required('pos.change_product', raise_exception=True)
def product_update(request, pk):
    p = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=p)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,"Product updated."); return redirect('product_list')
    return render(request,"pos/product_form.html",{"form":form,"title":"Edit Product"})

@permission_required('pos.delete_product', raise_exception=True)
def product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method=='POST':
        p.delete(); messages.success(request,"Product deleted."); return redirect('product_list')
    return render(request,"pos/confirm_delete.html",{"object":p,"cancel_url":reverse('product_list')})

@login_required
def product_list(request):
    products = Product.objects.order_by('-id')
    return render(request,"pos/product_list.html",{"products":products})

@login_required
def customer_list(request):
    customers = Customer.objects.order_by('name')
    return render(request,"pos/customer_list.html",{"customers":customers})

@permission_required('pos.add_customer', raise_exception=True)
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,"Customer created."); return redirect('customer_list')
    return render(request,"pos/customer_form.html",{"form":form,"title":"Add Customer"})

@login_required
def sale_list(request):
    sales = Sale.objects.order_by('-id')
    return render(request,"pos/sale_list.html",{"sales":sales})

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request,"pos/sale_detail.html",{"sale":sale})

@login_required
def sale_create(request):
    sale = Sale()
    if request.method=='POST':
        form = SaleForm(request.POST, instance=sale)
        formset = SaleItemFormSet(request.POST, instance=sale)
        payment_form = PaymentForm(request.POST)
        if form.is_valid() and formset.is_valid() and payment_form.is_valid():
            sale = form.save()
            formset.instance = sale; formset.save()
            payment = payment_form.save(commit=False); payment.sale = sale
            payment.amount = payment.amount or sale.total; payment.save()
            messages.success(request,"Sale recorded successfully."); return redirect('sale_detail', pk=sale.pk)
    else:
        form = SaleForm(instance=sale); formset = SaleItemFormSet(instance=sale); payment_form = PaymentForm(initial={'amount':0})
    return render(request,"pos/sale_create.html",{'form':form,'formset':formset,'payment_form':payment_form})

@login_required
def sale_receipt_print(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request,"pos/sale_receipt.html",{'sale':sale})

@login_required
@permission_required('pos.view_sale', raise_exception=True)
def report_sales(request):
    qs = Sale.objects.order_by('-created_at').prefetch_related('items')
    start = request.GET.get('start'); end = request.GET.get('end')
    if start: qs = qs.filter(created_at__gte=start)
    if end: qs = qs.filter(created_at__lte=end)
    total_sales = sum(s.total for s in qs)
    total_items = sum(s.total_items for s in qs)
    return render(request,"pos/report_sales.html",{'sales':qs,'total_sales':total_sales,'total_items':total_items,'start':start or '','end':end or ''})
