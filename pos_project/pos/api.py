from rest_framework import serializers, viewsets, routers, filters
from .models import Product, Customer, Sale, SaleItem, Payment
from django.urls import path, include
from rest_framework import permissions
from rest_framework.response import Response

class ProductSerializer(serializers.ModelSerializer):
    class Meta: model = Product; fields = '__all__'
class CustomerSerializer(serializers.ModelSerializer):
    class Meta: model = Customer; fields = '__all__'
class SaleItemSerializer(serializers.ModelSerializer):
    class Meta: model = SaleItem; fields = ['id','product','quantity','unit_price','discount_percent']
class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    class Meta: model = Sale; fields = ['id','customer','created_at','notes','discount_amount','tax_percent','items']
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sale = Sale.objects.create(**validated_data)
        for it in items_data:
            SaleItem.objects.create(sale=sale, **it)
        return sale
class PaymentSerializer(serializers.ModelSerializer):
    class Meta: model = Payment; fields = '__all__'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['sku','name']
    def list(self, request, *args, **kwargs):
        sku = request.GET.get('sku')
        qs = self.get_queryset()
        if sku:
            qs = qs.filter(sku=sku)
            serializer = self.get_serializer(qs, many=True)
            return Response({'results': serializer.data})
        return super().list(request, *args, **kwargs)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.prefetch_related('items').all()
    serializer_class = SaleSerializer
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [ path('api/', include(router.urls)), ]
