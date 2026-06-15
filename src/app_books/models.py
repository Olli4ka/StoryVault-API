from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)
    birth_date = models.DateField()

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    genres = models.ManyToManyField(Genre, related_name="books")
    pages = models.PositiveIntegerField()
    language = models.CharField(
        max_length=2, choices=[("EN", "English"), ("FR", "French"), ("ES", "Espanol")]
    )
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    is_reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reserved_books",
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")

    def __str__(self):
        return self.title
