from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


@shared_task
def send_order_confirmation_email(order_id, user_email):
    """Send order confirmation email to customer."""
    subject = f'Order Confirmation - Order #{order_id}'
    message = f'''
    Thank you for your order!
    
    Order ID: {order_id}
    
    We have received your order and are processing it now.
    You will receive another email once your order has been shipped.
    
    Track your order status by logging into your account.
    
    Thank you for shopping with us!
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"Email sent successfully to {user_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@shared_task
def send_order_status_update_email(order_id, user_email, status):
    """Send email when order status is updated."""
    subject = f'Order Update - Order #{order_id}'
    
    status_messages = {
        'Confirmed': 'Your order has been confirmed and is being prepared.',
        'Processing': 'Your order is currently being processed.',
        'Shipped': 'Great news! Your order has been shipped.',
        'Delivered': 'Your order has been delivered. Thank you for shopping with us!',
        'Cancelled': 'Your order has been cancelled. If you have any questions, please contact us.',
    }
    
    message = f'''
    Order #{order_id} Status Update
    
    Status: {status}
    
    {status_messages.get(status, 'Your order status has been updated.')}
    
    Track your order by logging into your account.
    
    Thank you!
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"Status update email sent to {user_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@shared_task
def check_low_stock_products():
    """Periodic task to check for low stock products and alert admins."""
    from main.models import Product
    
    low_stock_products = Product.objects.filter(
        stock__lt=10,
        stock__gt=0,
        is_active=True
    )
    
    if low_stock_products.exists():
        product_list = '\n'.join([
            f"- {p.name}: {p.available_stock} units remaining"
            for p in low_stock_products
        ])
        
        message = f'''
        Low Stock Alert
        
        The following products are running low on stock:
        
        {product_list}
        
        Please restock these items soon.
        '''
        
        # Send to admin email (you should configure this)
        admin_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            send_mail(
                'Low Stock Alert',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=False,
            )
            return f"Low stock alert sent for {low_stock_products.count()} products"
        except Exception as e:
            return f"Failed to send alert: {str(e)}"
    
    return "No low stock products found"
