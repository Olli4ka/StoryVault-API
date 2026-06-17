import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Author, Book, Genre
from .pagination import BookPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AuthorSerializer,
    BookCreateSerializer,
    BookSerializer,
    GenreSerializer,
)


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookViewSet(ModelViewSet):
    pagination_class = BookPagination
    filter_backends = [DjangoFilterBackend]
    queryset = Book.objects.select_related(
        "author", "owner", "reserved_by"
    ).prefetch_related("genres")

    filterset_fields = {
        "title": ["icontains"],
        "author__name": ["icontains"],
        "language": ["exact"],
        "is_reserved": ["exact"],
    }

    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BookCreateSerializer

        return BookSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    def recent_books(self, request):
        """
        Returns books published in the last 100 years.
        """
        one_hundred_years_ago = datetime.date.today() - datetime.timedelta(days=100 * 365)
        recent_books = self.get_queryset().filter(publication_date__gte=one_hundred_years_ago)
        serializer = self.get_serializer(recent_books, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reserve(self, request, pk=None):
        book = self.get_object()

        if book.owner == request.user:
            return Response(
                {"error": "You cannot reserve your own book."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if book.is_reserved:
            return Response(
                {"error": "The book is already reserved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book.is_reserved = True
        book.reserved_by = request.user
        book.save()

        return Response(
            {"status": "Book successfully reserved."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unreserve(self, request, pk=None):
        book = self.get_object()

        if not book.is_reserved:
            return Response(
                {"error": "The book is not reserved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if book.reserved_by != request.user:
            return Response(
                {"error": "You can only cancel your own reservation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        book.is_reserved = False
        book.reserved_by = None
        book.save()

        return Response(
            {"status": "Book reservation cancelled."}, status=status.HTTP_200_OK
        )
