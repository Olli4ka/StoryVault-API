from datetime import date

from rest_framework import serializers

from .models import Author, Book, Genre


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["name", "birth_date"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    reserved_by = serializers.StringRelatedField(read_only=True)

    book_age = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "description",
            "author",
            "genres",
            "pages",
            "language",
            "publication_date",
            "isbn",
            "is_reserved",
            "reserved_by",
            "owner",
            "book_age",
        ]
        read_only_fields = ["id"]

    def get_book_age(self, obj):
        return date.today().year - obj.publication_date.year


class BookCreateSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=Author.objects.all(), slug_field="name"
    )

    genres = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field="name"
    )

    class Meta:
        model = Book
        fields = [
            "title",
            "description",
            "author",
            "genres",
            "pages",
            "language",
            "publication_date",
            "isbn",
        ]

    def validate_isbn(self, value):
        """Custom isbn field validation"""
        if not value.isdigit():
            raise serializers.ValidationError("ISBN must contain only numbers!")
        if len(value) != 13:
            raise serializers.ValidationError(
                "ISBN must be exactly 13 characters long!"
            )
        return value

    def validate(self, attrs):
        if attrs["pages"] < 10:
            raise serializers.ValidationError("Book must contain at least 10 pages!")
        return attrs
