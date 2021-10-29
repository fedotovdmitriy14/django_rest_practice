from django.db.models import Count, Case, When
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', first_name='Ivan', last_name='Petrov')
        self.user2 = User.objects.create(username='user2', first_name='Dmitriy', last_name='Fedotov')
        self.user3 = User.objects.create(username='user3', first_name='Svetlana', last_name='Fedotova')

        self.book1 = Book.objects.create(name='test_book1', price=25, author_name='Author 1')
        self.book2 = Book.objects.create(name='test_book2', price=45, author_name='Author 2')



    def test_ok(self):
        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True)

        UserBookRelation.objects.create(user=self.user1, book=self.book2, like=False)

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
                # 'likes_count': 3,
                'annotated_likes': 3,
                'owner_name': '',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Dmitriy',
                        'last_name': 'Fedotov'
                    },
                    {
                        'first_name': 'Svetlana',
                        'last_name': 'Fedotova'
                    },
                ]
            },

            {
                'id': self.book2.id,
                'name': 'test_book2',
                'price': '45.00',
                'author_name': 'Author 2',
                # 'likes_count': 0,
                'annotated_likes': 0,
                'owner_name': '',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    }
                ]
            },
        ]

        self.assertEqual(expected_data, data)




