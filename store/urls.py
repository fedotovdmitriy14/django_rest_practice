from django.urls import path
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, auth

router = SimpleRouter()

router.register(r'book', BookViewSet)

urlpatterns = [
    path('auth', auth)
]

urlpatterns += router.urls