from django.urls import path
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, auth, UserBookRelationView

router = SimpleRouter()

router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)

urlpatterns = [
    path('auth', auth)
]

urlpatterns += router.urls