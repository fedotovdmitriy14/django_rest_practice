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

