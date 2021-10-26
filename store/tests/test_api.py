import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase
from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book1 = Book.objects.create(name='test_book1', price=25, author_name='Author 1', owner=self.user)
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
        self.assertEqual(self.user, Book.objects.last().owner)

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

    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book2.id,))
        data = {
            "name": self.book2.name,
            "price": 1000,
            "author_name": self.book2.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book2.refresh_from_db()
        self.assertEqual(45, self.book2.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)

        url = reverse('book-detail', args=(self.book2.id,))
        data = {
            "name": self.book2.name,
            "price": 1000,
            "author_name": self.book2.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book2.refresh_from_db()
        self.assertEqual(1000, self.book2.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_detail(self):
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        data = {
            'id': 1,
            'name': 'test_book1',
            'price': '25.00',
            'author_name': 'Author 1',
            'owner': 1
        }

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data, response.data)


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book1 = Book.objects.create(name='test_book1', price=25, author_name='Author 1', owner=self.user)
        self.book2 = Book.objects.create(name='test_book2', price=45, author_name='Author 5')
        self.book3 = Book.objects.create(name='test_book Author 1', price=65, author_name='Author 2')


    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            "like": True,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()

        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.like)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            "rate": 1,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()

        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertEqual(1, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            "rate": 6,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
