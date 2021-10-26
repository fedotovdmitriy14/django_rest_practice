from unittest import TestCase

from django.db.models import Count, Case, When, Avg
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='us1')
        self.user2 = User.objects.create(username='us2')
        self.user3 = User.objects.create(username='us3')

        self.book1 = Book.objects.create(name='test_book1', price=25, author_name='Author 1')
        self.book2 = Book.objects.create(name='test_book2', price=45, author_name='Author 2')



    def test_ok(self):
        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by('id')
        data = BookSerializer(books, many=True).data

        # data = BookSerializer([self.book1, self.book2], many=True).data



        expected_data = [
            {
                'id': self.book1.id,
                'name': 'test_book1',
                'price': '25.00',
                'author_name': 'Author 1',
                'likes_count': 3,
                'annotated_likes': 3,
            },
            {
                'id': self.book2.id,
                'name': 'test_book2',
                'price': '45.00',
                'author_name': 'Author 2',
                'likes_count': 0,
                'annotated_likes': 0,
            },
        ]

        self.assertEqual(expected_data, data)




