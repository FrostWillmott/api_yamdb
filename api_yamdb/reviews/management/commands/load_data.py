import csv

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = "Загрузка данных из CSV файлов в базу данных"

    def handle(self, *args, **kwargs):
        self.load_users()
        self.load_genres()
        self.load_categories()
        self.load_titles()
        self.load_reviews()
        self.load_comments()

    def load_users(self):
        with open("path/to/users.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.create(**row)

    def load_genres(self):
        with open("path/to/genres.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.create(**row)

    def load_categories(self):
        with open("path/to/categories.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.create(**row)

    def load_titles(self):
        with open("path/to/titles.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category.objects.get(pk=row["category_id"])
                title = Title.objects.create(
                    name=row["name"],
                    year=row["year"],
                    description=row["description"],
                    category=category,
                )
                genres = row["genre_ids"].split(",")
                for genre_id in genres:
                    genre = Genre.objects.get(pk=genre_id)
                    title.genre.add(genre)

    def load_reviews(self):
        with open("path/to/reviews.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(pk=row["title_id"])
                author = User.objects.get(pk=row["author_id"])
                Review.objects.create(
                    title=title,
                    text=row["text"],
                    author=author,
                    score=row["score"],
                    pub_date=row["pub_date"],
                )

    def load_comments(self):
        with open("path/to/comments.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                review = Review.objects.get(pk=row["review_id"])
                author = User.objects.get(pk=row["author_id"])
                Comment.objects.create(
                    review=review,
                    text=row["text"],
                    author=author,
                    pub_date=row["pub_date"],
                )
