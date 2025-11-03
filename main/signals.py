from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from main.models import Product, User, UserProfile, Order
from django.core.cache import cache


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """Invalidates the cache for products."""
    print("Invalidating products cache")
    # Using pattern matching for Redis cache
    try:
        cache.delete_many(cache.keys("*product_list*"))
    except:
        # Fallback if pattern matching is not available
        pass


@receiver(post_save, sender=Order)
def send_low_stock_alerts(sender, instance, created, **kwargs):
    """Check for low stock after order is created."""
    if created:
        for item in instance.items.all():
            if item.product.is_low_stock:
                print(f"LOW STOCK ALERT: {item.product.name} has only {item.product.available_stock} units left!")
                # Here you could send an email to admins or trigger a notification

    