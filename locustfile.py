
import random

from locust import HttpUser, task, between


class BookSearchUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def search_common_title(self):
        self.client.get(
            "/books/search/",
            params={"q": "Book"},
            name="Search: common title",
        )

    @task(2)
    def search_author(self):
        author_number = random.randint(1, 500)

        self.client.get(
            "/books/search/",
            params={"q": f"Author {author_number:03d}"},
            name="Search: author",
        )

    @task(2)
    def search_specific_book(self):
        book_number = random.randint(1, 10000)

        self.client.get(
            "/books/search/",
            params={"q": f"Book {book_number:05d}"},
            name="Search: specific title",
        )

    @task(1)
    def search_no_results(self):
        self.client.get(
            "/books/search/",
            params={"q": "NoSuchBookXYZ999"},
            name="Search: no results",
        )
