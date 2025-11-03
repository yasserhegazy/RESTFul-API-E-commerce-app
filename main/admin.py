from django.contrib import admin
from .models import Order, OrderItem, Product, User, UserProfile, Category, Review, Cart, CartItem


# Inline admin classes
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('item_subtotal', 'price_at_purchase')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


# ModelAdmin classes
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'shipping_city', 'shipping_country')
    search_fields = ('user__username', 'phone_number', 'shipping_city')
    list_filter = ('shipping_country',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent', 'created_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'reserved_stock', 'available_stock', 'is_active', 'average_rating')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_active', 'created_at')
    readonly_fields = ('average_rating', 'review_count', 'available_stock', 'created_at', 'updated_at')
    inlines = [ReviewInline]
    
    def available_stock(self, obj):
        return obj.available_stock
    available_stock.short_description = 'Available Stock'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('total_items', 'total_price', 'created_at', 'updated_at')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal', 'added_at')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('added_at',)
    readonly_fields = ('subtotal', 'added_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status', 'tracking_number', 'total_price', 'created_at')
    search_fields = ('order_id', 'user__username', 'tracking_number')
    list_filter = ('status', 'created_at')
    readonly_fields = ('order_id', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status', 'tracking_number', 'total_price')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_address_line1', 'shipping_address_line2',
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def total_price(self, obj):
        return f"${obj.total_price:.2f}"
    total_price.short_description = 'Total Price'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase', 'item_subtotal')
    search_fields = ('order__order_id', 'product__name')
    readonly_fields = ('item_subtotal',)
