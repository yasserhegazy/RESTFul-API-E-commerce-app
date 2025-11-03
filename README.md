# Django E-Commerce REST API

An e-commerce REST API built with Django REST Framework.

## Features

- User authentication with JWT tokens
- Product catalog with categories
- Shopping cart functionality
- Order management system
- Product reviews and ratings
- Inventory tracking
- Email notifications
- Admin interface

## Tech Stack

- Django 5.0+ 
- Django REST Framework
- SQLite / PostgreSQL
- Redis
- Celery
- JWT Authentication

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yasserhegazy/RESTFul-API-E-commerce-app.git
   cd RESTFul-API-E-commerce-app
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Start the server
   ```bash
   python manage.py runserver
   ```

API documentation: `http://localhost:8000/api/schema/swagger-ui/`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/products/` | List and create products |
| `/api/categories/` | Manage categories |
| `/api/cart/` | Shopping cart operations |
| `/api/orders/` | Order management |
| `/api/reviews/` | Product reviews |
| `/api/profiles/` | User profiles |
| `/api/token/` | Authentication |

## Project Structure

```
API/
├── main/                   # Main app
│   ├── models.py          # Database models
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   └── tasks.py           # Background tasks
├── API/                   # Settings
│   ├── settings.py        # Configuration
│   └── urls.py            # Main URLs
└── requirements.txt       # Dependencies
```

## Contact

- GitHub: [@yasserhegazy](https://github.com/yasserhegazy)
- Repository: [RESTFul-API-E-commerce-app](https://github.com/yasserhegazy/RESTFul-API-E-commerce-app)


