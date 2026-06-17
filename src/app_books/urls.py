from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, GenreViewSet

router = DefaultRouter()
router.register("authors", AuthorViewSet, basename="author")
router.register("genres", GenreViewSet, basename="genre")
router.register("books", BookViewSet, basename="book")

urlpatterns = router.urls