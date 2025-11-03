import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum
from django.utils.text import slugify

from main.models import (
    Order, OrderItem, Product, User, UserProfile, 
    Category, Review, Cart, CartItem
)


class Command(BaseCommand):
    help = 'Creates application data with sample products, categories, reviews, and orders'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed data...'))
        
        # Get or create superuser
        user = User.objects.filter(username='admin').first()
        if not user:
            self.stdout.write('Creating admin user...')
            user = User.objects.create_superuser(username='admin', password='test', email='admin@example.com')
        
        # Create sample regular users
        self.stdout.write('Creating sample users...')
        user1, _ = User.objects.get_or_create(
            username='john_doe',
            defaults={'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'}
        )
        user1.set_password('password123')
        user1.save()
        
        user2, _ = User.objects.get_or_create(
            username='jane_smith',
            defaults={'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'}
        )
        user2.set_password('password123')
        user2.save()
        
        # Create user profiles with addresses
        self.stdout.write('Creating user profiles...')
        UserProfile.objects.get_or_create(
            user=user1,
            defaults={
                'phone_number': '+1234567890',
                'shipping_address_line1': '123 Main St',
                'shipping_city': 'New York',
                'shipping_state': 'NY',
                'shipping_postal_code': '10001',
                'shipping_country': 'USA',
                'billing_address_line1': '123 Main St',
                'billing_city': 'New York',
                'billing_state': 'NY',
                'billing_postal_code': '10001',
                'billing_country': 'USA',
            }
        )
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories_data = [
            ('Electronics', 'Electronic devices and gadgets'),
            ('Books', 'Books and literature'),
            ('Music', 'Music albums and instruments'),
            ('Home & Kitchen', 'Home appliances and kitchen items'),
            ('Fashion', 'Clothing and accessories'),
        ]
        
        categories = []
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'slug': slugify(name)}
            )
            categories.append(cat)
        
        # Create products with categories
        self.stdout.write('Creating products...')
        products_data = [
            ("A Scanner Darkly", categories[1], Decimal('12.99'), 15),
            ("Coffee Machine", categories[3], Decimal('70.99'), 8),
            ("Velvet Underground & Nico", categories[2], Decimal('15.99'), 11),
            ("Enter the Wu-Tang (36 Chambers)", categories[2], Decimal('17.99'), 6),
            ("Digital Camera", categories[0], Decimal('350.99'), 4),
            ("Smart Watch", categories[0], Decimal('500.05'), 3),
            ("Laptop", categories[0], Decimal('1200.00'), 5),
            ("Headphones", categories[0], Decimal('89.99'), 20),
            ("Python Programming Book", categories[1], Decimal('45.00'), 12),
            ("Blender", categories[3], Decimal('65.00'), 7),
        ]
        
        products = []
        for name, category, price, stock in products_data:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': lorem_ipsum.paragraph(),
                    'price': price,
                    'stock': stock,
                    'category': category,
                    'is_active': True
                }
            )
            products.append(product)
        
        # Create reviews
        self.stdout.write('Creating product reviews...')
        review_texts = [
            ("Great product!", "Really satisfied with this purchase. Highly recommend!"),
            ("Good value", "Good quality for the price."),
            ("Excellent", "Exceeded my expectations. Will buy again."),
            ("Not bad", "It's okay, does the job."),
            ("Amazing quality", "The best purchase I've made this year!"),
        ]
        
        for product in random.sample(products, min(5, len(products))):
            for user_reviewer in [user1, user2]:
                if random.choice([True, False]):
                    title, comment = random.choice(review_texts)
                    Review.objects.get_or_create(
                        product=product,
                        user=user_reviewer,
                        defaults={
                            'rating': random.randint(3, 5),
                            'title': title,
                            'comment': comment
                        }
                    )
        
        # Create some dummy orders
        self.stdout.write('Creating sample orders...')
        for user_customer in [user, user1, user2]:
            for _ in range(random.randint(1, 3)):
                profile, _ = UserProfile.objects.get_or_create(user=user_customer)
                
                order = Order.objects.create(
                    user=user_customer,
                    status=random.choice(['Pending', 'Confirmed', 'Shipped', 'Delivered']),
                    shipping_address_line1=profile.shipping_address_line1 or '123 Default St',
                    shipping_city=profile.shipping_city or 'Default City',
                    shipping_state=profile.shipping_state or 'State',
                    shipping_postal_code=profile.shipping_postal_code or '00000',
                    shipping_country=profile.shipping_country or 'USA'
                )
                
                # Add order items
                for product in random.sample(products, random.randint(1, 3)):
                    quantity = random.randint(1, 2)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_at_purchase=product.price
                    )
                    # Reserve stock
                    product.reserved_stock += quantity
                    product.save()
        
        # Create a cart for user1 with some items
        self.stdout.write('Creating sample cart...')
        cart, _ = Cart.objects.get_or_create(user=user1)
        for product in random.sample(products, 2):
            CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': random.randint(1, 2)}
            )
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(f'  - {User.objects.count()} users')
        self.stdout.write(f'  - {Category.objects.count()} categories')
        self.stdout.write(f'  - {Product.objects.count()} products')
        self.stdout.write(f'  - {Review.objects.count()} reviews')
        self.stdout.write(f'  - {Order.objects.count()} orders')
        self.stdout.write(f'  - {Cart.objects.count()} carts')
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Admin: username=admin, password=test')
        self.stdout.write('  User1: username=john_doe, password=password123')
        self.stdout.write('  User2: username=jane_smith, password=password123')
