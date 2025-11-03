import django_filters
from django_filters.rest_framework import FilterSet
from rest_framework import filters

from .models import Order, Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category_slug = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'category': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset


class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        in_stock_only = request.query_params.get('in_stock_only', None)
        if in_stock_only and in_stock_only.lower() == 'true':
            return queryset.filter(stock__gt=0)
        return queryset


class OrderFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at': ['exact'],
        }
