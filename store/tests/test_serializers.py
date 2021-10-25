from unittest import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book1 = Book.objects.create(name='test_book1', price=25, author_name='Author 1')
        book2 = Book.objects.create(name='test_book2', price=45, author_name='Author 2')
        data = BookSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'name': 'test_book1',
                'price': '25.00',
                'author_name': 'Author 1'
            },
            {
                'id': book2.id,
                'name': 'test_book2',
                'price': '45.00',
                'author_name': 'Author 2'
            },
        ]

        self.assertEqual(expected_data, data)




