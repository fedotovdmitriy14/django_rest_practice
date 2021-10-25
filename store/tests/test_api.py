import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase
from store.models import Book
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.book1 = Book.objects.create(name='test_book1', price=25, author_name='Author 1')
        self.book2 = Book.objects.create(name='test_book2', price=45, author_name='Author 5')
        self.book3 = Book.objects.create(name='test_book Author 1', price=65, author_name='Author 2')
        self.user = User.objects.create(username='test_username')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})                    # тест для поиска
        serializer_data = BookSerializer([self.book1, self.book3], many=True).data      # в сериалайзер приходят только два объекта
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serializer_data = BookSerializer([self.book3, self.book2, self.book1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(Book.objects.count(), 3)
        url = reverse('book-list')
        data = {
            "name": "Python 3",
            "price": 900,
            "author_name": "O'Reilly"
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Book.objects.count(), 4)

    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 1000,
            "author_name": self.book1.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Нужно обновить книгу, так как она не сохраняется в БД класса
        # self.book1 = Book.objects.get(id=self.book1.id)
        self.book1.refresh_from_db()
        self.assertEqual(1000, self.book1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_detail(self):
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        data = {
            'id': 8,
            'name': 'test_book1',
            'price': '25.00',
            'author_name': 'Author 1'
        }

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data, response.data)



