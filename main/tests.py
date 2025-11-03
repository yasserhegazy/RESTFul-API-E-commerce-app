from django.test import TestCase
# The method reverse is used to get the URL of a view by its name
from django.urls import reverse
from rest_framework import status

from .models import Order, OrderItem, Product, User

from rest_framework.test import APITestCase
# Create your tests here.
class UserOrderTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='test')
        user2 = User.objects.create_user(username='user2', password='test')
        Order.objects.create(user=user1)
        Order.objects.create(user=user1)
        Order.objects.create(user=user2)
        Order.objects.create(user=user2)
        
    def test_user_order_enepoint_retrieves_only_auth_user_orders(self):
        user = User.objects.get(username='user1')
        self.client.force_login(user)
        response = self.client.get(reverse('user-orders'))
        assert response.status_code == 200
        orders = response.json()
        self.assertTrue(all(order['user'] == user.id for order in orders))
    
    def test_user_order_list_unauthenticated(self):
        response = self.client.get(reverse('user-orders'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Assuming permission is set to IsAuthenticated

        
class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.normal_user = User.objects.create_user(username='user', password='userpass')
        self.product = Product.objects.create(name='Test Product', description='Description 1', price=10.00, stock=5)
        
        
        self.url = reverse('product-detail', kwargs={'pk': self.product.pk})  # Assuming the view is named 'product-detail'
        
    def test_get_product(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.product.name)
        
    def test_unauthorized_update_product(self):
        data = {"name": "Updated Product"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 401)  # Assuming only admin can create products
    
    def test_only_admins_can_delete_product(self):
        # Attempt to delete as normal user
        self.client.login(username='user', password='userpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Forbidden for normal users
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        self.client.logout()
        
        # Attempt to delete as admin user
        self.client.login(username='admin', password='adminpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)  # No content on successful deletion
