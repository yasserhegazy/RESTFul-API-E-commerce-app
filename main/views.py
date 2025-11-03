from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
# The method reverse is used to get the URL of a view by its name
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import filters, generics, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import InStockFilterBackend, OrderFilter, ProductFilter
from .models import Order, OrderItem, Product, User, UserProfile, Category, Review, Cart, CartItem
from .serializers import (
    OrderSerializer, ProductSerializer, OrderCreateSerializer, UserSerializer,
    UserProfileSerializer, CategorySerializer, ReviewSerializer, CartSerializer,
    CartItemSerializer, ProductInfoSerializer
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers 
from rest_framework.throttling import ScopedRateThrottle
from main.tasks import send_order_confirmation_email
from django.db import transaction


# User Profile ViewSet
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        serializer = self.get_serializer(profile, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


# Review ViewSet
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'product')
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]


# Cart ViewSet
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related('items__product')
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity
            cart_item.quantity += quantity
            
            # Validate stock
            if cart_item.quantity > product.available_stock:
                return Response(
                    {'error': f'Only {product.available_stock} items available in stock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """Update cart item quantity"""
        cart = get_object_or_404(Cart, user=request.user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        
        if not product_id or quantity is None:
            return Response(
                {'error': 'product and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        
        if quantity <= 0:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
        
        # Validate stock
        if quantity > cart_item.product.available_stock:
            return Response(
                {'error': f'Only {cart_item.product.available_stock} items available in stock.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = get_object_or_404(Cart, user=request.user)
        product_id = request.data.get('product')
        
        if not product_id:
            return Response(
                {'error': 'product is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)


class ProductListCreateAPIView(generics.ListCreateAPIView):
    throttle_scope = 'products'
    throttle_classes = [ScopedRateThrottle]
    queryset = Product.objects.select_related('category').filter(is_active=True).order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    search_fields = ('=name', 'description', 'price')
    ordering_fields = ('name', 'price', 'stock', 'created_at', 'average_rating')
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    pagination_class.page_query_param = 'pagenum'
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 50
    
    @method_decorator(cache_page(60*15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = super().get_queryset()
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('reviews')
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'PATCH','DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer 


class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.filter(is_active=True)
        serializer = ProductInfoSerializer(data={
            'products': products,
            'count': products.count(),
            'max_price': products.aggregate(Max('price'))['price__max']
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    throttle_scope = 'orders'
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'status']
    
    @method_decorator(cache_page(60*15, key_prefix='order_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Get or create user profile for shipping address default
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        
        # Use shipping address from request or fallback to profile
        shipping_data = {
            'shipping_address_line1': serializer.validated_data.get('shipping_address_line1', profile.shipping_address_line1),
            'shipping_address_line2': serializer.validated_data.get('shipping_address_line2', profile.shipping_address_line2),
            'shipping_city': serializer.validated_data.get('shipping_city', profile.shipping_city),
            'shipping_state': serializer.validated_data.get('shipping_state', profile.shipping_state),
            'shipping_postal_code': serializer.validated_data.get('shipping_postal_code', profile.shipping_postal_code),
            'shipping_country': serializer.validated_data.get('shipping_country', profile.shipping_country),
        }
        
        order = serializer.save(user=self.request.user, **shipping_data)
        
        # Clear user's cart after order
        try:
            cart = Cart.objects.get(user=self.request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        
        # Trigger the Celery task to send the order confirmation email
        send_order_confirmation_email.delay(str(order.order_id), self.request.user.email)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            return qs.filter(user=self.request.user)
        return qs
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status with validation"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status transitions
        valid_transitions = {
            Order.StatusChoices.PENDING: [Order.StatusChoices.CONFIRMED, Order.StatusChoices.CANCELLED],
            Order.StatusChoices.CONFIRMED: [Order.StatusChoices.PROCESSING, Order.StatusChoices.CANCELLED],
            Order.StatusChoices.PROCESSING: [Order.StatusChoices.SHIPPED, Order.StatusChoices.CANCELLED],
            Order.StatusChoices.SHIPPED: [Order.StatusChoices.DELIVERED],
            Order.StatusChoices.DELIVERED: [],
            Order.StatusChoices.CANCELLED: [],
        }
        
        if new_status not in valid_transitions.get(order.status, []):
            return Response(
                {'error': f'Cannot transition from {order.status} to {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Handle stock when order is cancelled
        if new_status == Order.StatusChoices.CANCELLED and old_status != Order.StatusChoices.CANCELLED:
            with transaction.atomic():
                for item in order.items.all():
                    # Return reserved stock
                    item.product.reserved_stock -= item.quantity
                    item.product.save()
        
        # Deduct from actual stock when delivered
        if new_status == Order.StatusChoices.DELIVERED:
            with transaction.atomic():
                for item in order.items.all():
                    # Deduct from actual stock and reserved stock
                    item.product.stock -= item.quantity
                    item.product.reserved_stock -= item.quantity
                    item.product.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None
    permission_classes = [IsAdminUser]
