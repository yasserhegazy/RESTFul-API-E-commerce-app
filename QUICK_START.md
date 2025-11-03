# 🚀 Quick Start Guide

Follow these steps to get your enhanced E-Commerce API up and running!

## ⚠️ Important: Database Migration Required

**Your database schema has changed significantly. You have two options:**

### Option 1: Fresh Start (Recommended)
Delete your old database and start fresh with the new schema.

```powershell
# Stop the server if running (Ctrl+C)

# Delete the old database
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue

# Delete old migration files (keep __init__.py)
Remove-Item main\migrations\0*.py

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load sample data with all new features
python manage.py seed_data
```

### Option 2: Migrate Existing Data
If you want to keep existing data, follow Django's migration process carefully.

```powershell
python manage.py makemigrations
python manage.py migrate
```

**Note:** You may encounter errors due to new required fields. You'll need to provide default values or modify migrations manually.

## 📦 Step-by-Step Setup

### 1. Install Missing Dependencies

```powershell
pip install python-decouple
```

This is the only new package needed for environment variable management.

### 2. Verify Environment File

The `.env` file has been created for you. Review it:
```powershell
notepad .env
```

Default settings are ready for development. No changes needed unless you want to customize.

### 3. Database Setup

Choose **Option 1 (Fresh Start)** from above, then:

```powershell
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create sample data
python manage.py seed_data
```

You'll see output like:
```
Creating admin user...
Creating sample users...
Creating categories...
Creating products...
...
Data seeding completed successfully!

Login credentials:
  Admin: username=admin, password=test
  User1: username=john_doe, password=password123
  User2: username=jane_smith, password=password123
```

### 4. Start Redis Server

**Windows (if installed):**
```powershell
# If you have Redis installed via WSL
wsl redis-server

# Or if installed natively
redis-server
```

**Don't have Redis?** The API will work without it, but caching and Celery tasks won't function.

To install Redis on Windows:
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Or use WSL: `wsl --install` then `sudo apt-get install redis-server`

### 5. Start Celery Worker (Optional but Recommended)

Open a **new PowerShell terminal** in your project directory:

```powershell
# Activate virtual environment
venv\Scripts\activate

# Start Celery worker
celery -A main.celery worker -l info --pool=solo
```

**Note:** Use `--pool=solo` on Windows. For Linux/Mac, omit this flag.

You should see:
```
[tasks]
  . main.tasks.check_low_stock_products
  . main.tasks.send_order_confirmation_email
  . main.tasks.send_order_status_update_email
```

### 6. Start Django Development Server

In your **original terminal**:

```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

## ✅ Verify Installation

### 1. Check API Documentation
Open your browser and visit:
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **Admin Panel**: http://localhost:8000/admin/

### 2. Login to Admin
- URL: http://localhost:8000/admin/
- Username: `admin`
- Password: `test`

You should see all the new models:
- Users
- User Profiles
- Categories
- Products
- Reviews
- Carts
- Cart Items
- Orders
- Order Items

### 3. Test API Endpoints

**Get all products:**
```powershell
curl http://localhost:8000/api/products/
```

**Get JWT token:**
```powershell
curl -X POST http://localhost:8000/api/token/ -H "Content-Type: application/json" -d '{\"username\":\"admin\",\"password\":\"test\"}'
```

**Test with the provided api.http file:**
Open `api.http` in VS Code with the REST Client extension, or use your favorite API client (Postman, Insomnia).

## 🎯 What to Test

### 1. Products & Categories
- Browse products: http://localhost:8000/api/products/
- Filter by category: http://localhost:8000/api/products/?category=electronics
- Search products: http://localhost:8000/api/products/?search=laptop

### 2. User Authentication
- Get token at: http://localhost:8000/api/token/
- Use the Swagger UI for easy testing

### 3. Shopping Cart
1. Login as john_doe (password: password123)
2. GET http://localhost:8000/api/cart/me/
3. Add items, update quantities, check the cart

### 4. Reviews
1. Login as any user
2. POST to /api/reviews/ with product ID and rating
3. View reviews for a product

### 5. Orders
1. Add items to cart
2. Create an order from cart
3. Check order status and tracking

## 🐛 Troubleshooting

### Migration Errors
```powershell
# If you see "no such table" errors
python manage.py migrate --run-syncdb
```

### Redis Connection Error
```
Error: Redis connection refused
```
**Solution:** Start Redis server or disable caching temporarily in settings.py

### Celery Not Working
```
Error: Can't connect to Redis
```
**Solution:** 
1. Start Redis first
2. Then start Celery with `--pool=solo` on Windows

### Import Error for decouple
```
ModuleNotFoundError: No module named 'decouple'
```
**Solution:**
```powershell
pip install python-decouple
```

### Static Files Not Found
```powershell
python manage.py collectstatic --noinput
```

## 📊 Check What's Been Added

### New API Endpoints
Visit the Swagger UI to see all available endpoints:
http://localhost:8000/api/schema/swagger-ui/

### Database Contents
```powershell
python manage.py shell
```
```python
from main.models import *

# Check counts
print(f"Users: {User.objects.count()}")
print(f"Categories: {Category.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Reviews: {Review.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"Carts: {Cart.objects.count()}")
```

## 🎨 Explore the Admin Interface

1. Go to http://localhost:8000/admin/
2. Login with admin/test
3. Explore all the new models
4. Notice the enhanced admin interfaces with:
   - Inline editing
   - Search functionality
   - Filters
   - Computed fields (like total_price, available_stock)

## 📝 Next Steps

1. **Read the documentation:**
   - README.md - Project overview
   - API_USAGE.md - API examples
   - CONTRIBUTING.md - Development guide

2. **Customize:**
   - Update .env with your settings
   - Add your own products and categories
   - Configure email settings for production

3. **Test:**
   - Try all API endpoints
   - Test with different user roles
   - Verify stock management
   - Check order workflow

4. **Deploy:**
   - Follow the production checklist in README.md
   - Set up PostgreSQL
   - Configure proper email backend
   - Deploy to your hosting platform

## 🎉 You're All Set!

Your E-Commerce API is now running with:
- ✅ User profiles with addresses
- ✅ Product categories and reviews
- ✅ Shopping cart functionality
- ✅ Advanced inventory management
- ✅ Order tracking system
- ✅ Email notifications (via Celery)
- ✅ Comprehensive API documentation

**Ready to showcase on your CV and GitHub!** 🚀

## 💡 Quick Tips

- Use **Swagger UI** for easy API testing
- Check **Django Admin** to manage data visually
- Monitor **Celery terminal** to see background tasks
- Read **API_USAGE.md** for detailed examples
- Check **PROJECT_SUMMARY.md** for all changes

## 🆘 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the error message carefully
3. Check if all services are running (Django, Redis, Celery)
4. Verify migrations are applied
5. Look at the comprehensive documentation files

Happy coding! 🎊
