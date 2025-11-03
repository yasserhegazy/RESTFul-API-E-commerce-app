from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    # Products
    path('products/', views.ProductListCreateAPIView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('product/info/', views.ProductInfoAPIView.as_view(), name='product-info'),
    
    # Users
    path('users/', views.UserListView.as_view(), name='user-list'),
    
    # Orders (non-viewset endpoints)
    path('user-orders/', views.UserOrderListAPIView.as_view(), name='user-orders'),
]

# ViewSet router
router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('reviews', views.ReviewViewSet, basename='review')
router.register('cart', views.CartViewSet, basename='cart')
router.register('profiles', views.UserProfileViewSet, basename='profile')

urlpatterns += router.urls
