from rest_framework import serializers
from .models import Product, Order, OrderItem, User, UserProfile, Category, Review, Cart, CartItem
from django.db import transaction


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'phone_number',
            'shipping_address_line1',
            'shipping_address_line2',
            'shipping_city',
            'shipping_state',
            'shipping_postal_code',
            'shipping_country',
            'billing_address_line1',
            'billing_address_line2',
            'billing_city',
            'billing_state',
            'billing_postal_code',
            'billing_country',
        )


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'profile',
        )


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'description',
            'slug',
            'parent',
            'products_count',
            'created_at',
        )
    
    def get_products_count(self, obj):
        return obj.products.count()


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = (
            'id',
            'product',
            'user',
            'user_username',
            'rating',
            'title',
            'comment',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('user',)
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    available_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock',
            'available_stock',
            'category',
            'category_name',
            'image',
            'is_active',
            'average_rating',
            'review_count',
            'is_low_stock',
            'created_at',
            'updated_at',
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='product.price',
        read_only=True
    )
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = (
            'id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'subtotal',
            'added_at',
        )
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if product and quantity > product.available_stock:
            raise serializers.ValidationError(
                f"Only {product.available_stock} items available in stock."
            )
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = (
            'id',
            'user',
            'items',
            'total_price',
            'total_items',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('user',)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='price_at_purchase',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            'product',
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal'
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity')
        
        def validate_quantity(self, value):
            if value < 1:
                raise serializers.ValidationError("Quantity must be at least 1.")
            return value

    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many=True)
    
    # Shipping address fields (optional with defaults from user profile)
    shipping_address_line1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipping_state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipping_postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    shipping_country = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must have at least one item.")
        
        # Check stock availability
        for item in items:
            product = item['product']
            quantity = item['quantity']
            
            if quantity > product.available_stock:
                raise serializers.ValidationError(
                    f"Only {product.available_stock} units of {product.name} available."
                )
        
        return items

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(**validated_data)

            # Create order items and reserve stock
            for item in orderitem_data:
                product = item['product']
                quantity = item['quantity']
                
                # Reserve stock
                product.reserved_stock += quantity
                product.save()
                
                # Create order item with price snapshot
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )

        return order

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items', None)
        
        with transaction.atomic():
            # Update order fields
            instance = super().update(instance, validated_data)
            
            if orderitem_data is not None:
                # Return reserved stock from old items
                for old_item in instance.items.all():
                    old_item.product.reserved_stock -= old_item.quantity
                    old_item.product.save()
                
                # Clear existing items
                instance.items.all().delete()
                
                # Create new items and reserve stock
                for item in orderitem_data:
                    product = item['product']
                    quantity = item['quantity']
                    
                    # Validate stock again
                    if quantity > product.available_stock:
                        raise serializers.ValidationError(
                            f"Only {product.available_stock} units of {product.name} available."
                        )
                    
                    # Reserve stock
                    product.reserved_stock += quantity
                    product.save()
                    
                    OrderItem.objects.create(
                        order=instance,
                        product=product,
                        quantity=quantity,
                        price_at_purchase=product.price
                    )
            
        return instance
        
    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'status',
            'items',
            'shipping_address_line1',
            'shipping_address_line2',
            'shipping_city',
            'shipping_state',
            'shipping_postal_code',
            'shipping_country',
        )
        extra_kwargs = {
            'user': {'read_only': True}
        }


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')
    user_username = serializers.CharField(source='user.username', read_only=True)

    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'updated_at',
            'user',
            'user_username',
            'status',
            'tracking_number',
            'items',
            'total_price',
            'shipping_address_line1',
            'shipping_address_line2',
            'shipping_city',
            'shipping_state',
            'shipping_postal_code',
            'shipping_country',
        )


class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
