import requests
from sqlalchemy import or_
from wikipediaapi import Wikipedia
from bs4 import BeautifulSoup
import re


API_KEY = "Put Here Your API Key"


def sort_books(sort_option, Book, Author):
    """
    Sort Books
    Sorts the list of books based on the given sort_option.
    Args:
        sort_option (str): The sorting option in the format "field_order", e.g., "author_ASC".
        Book (SQLAlchemy Model): The Book model class.
        Author (SQLAlchemy Model): The Author model class.
    Returns:
        list: A list of books sorted according to the sort_option.
    """
    if sort_option:
        sort_by, sort_order = sort_option.split("_")
        if sort_by == "author":
            if sort_order == "ASC":
                return Book.query.join(Author).order_by(Author.name, Book.title).all()
            else:
                return Book.query.join(Author).order_by(Author.name.desc(), Book.title.desc()).all()
        elif sort_by == "year":
            if sort_order == "ASC":
                return Book.query.order_by(Book.publication_year, Book.title).all()
            else:
                return Book.query.order_by(Book.publication_year.desc(), Book.title.desc()).all()
        else:
            if sort_order == "ASC":
                return Book.query.order_by(Book.title).all()
            else:
                return Book.query.order_by(Book.title.desc()).all()
    else:
        return Book.query.all()


def search_books(search_query, Book, Author):
    """
    Search Books
    Searches for books or authors that match the given search_query.
    Args:
        search_query (str): The search query entered by the user.
        Book (SQLAlchemy Model): The Book model class.
        Author (SQLAlchemy Model): The Author model class.
    Returns:
        list: A list of books or authors that match the search_query.
    """
    if search_query:
        return Book.query.join(Author).filter(
            or_(Book.title.like(f"%{search_query}%"), Author.name.like(f"%{search_query}%"))
        ).all()
    else:
        return Book.query.all()



def get_isbn(title):
    """
    Get ISBN
    Retrieves the ISBN (International Standard Book Number) for the given book title
    using the Google Books API.
    Args:
        title (str): The title of the book.
    Returns:
        str or None: The ISBN of the book if found, or None if not found.
    """
    google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}"
    response = requests.get(google_books_api_url)
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        book_info = data["items"][0]["volumeInfo"]
        if "industryIdentifiers" in book_info:
            for identifier in book_info["industryIdentifiers"]:
                if identifier["type"] == "ISBN_13":
                    return identifier["identifier"]
    return None


def get_book_cover_url(isbn):
    """
    Get Book Cover URL
    Retrieves the URL for the book cover image based on the given ISBN
    using the Google Books API.
    Args:
        isbn (str): The ISBN of the book.
    Returns:
        str or None: The URL of the book cover image if found, or None if not found.
    """
    google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(google_books_api_url)
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        book_info = data["items"][0]["volumeInfo"]
        if "imageLinks" in book_info and "thumbnail" in book_info["imageLinks"]:
            return book_info["imageLinks"]["thumbnail"]
    return None


def get_book_description(book_title):
    """
    Get Book Description
    Retrieves the description of the book based on the given book title
    using the Google Books API.
    Args:
        book_title (str): The title of the book.
    Returns:
        str: The description of the book if found, or a default message if not found.
    """
    url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}&key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            book_info = data['items'][0]['volumeInfo']
            description = book_info.get('description', 'Description not available.')
            return description
        else:
            return 'Book not found.'
    else:
        return 'Error: Unable to fetch book details.'


def extract_year_from_date(date_string):
    """
    Extract Year from Date
    Extracts the year from a given date string using regular expressions.
    Args:
        date_string (str): The date string in various formats.
    Returns:
        int or None: The extracted year as an integer if found, or None if not found.
    """
    formats_to_try = ["%Y-%m-%d", "%Y-%m", "%Y"]
    for date_format in formats_to_try:
        match = re.match(r"\d{4}", date_string)
        if match:
            return int(match.group())
    return None

def get_book_year_by_title(book_title):
    """
    Get Book Year by Title
    Retrieves the publication year of the book based on the given book title
    using the Google Books API.
    Args:
        book_title (str): The title of the book.
    Returns:
        int or str: The publication year of the book if found, or a default message if not found.
    """
    google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}&key={API_KEY}"
    response = requests.get(google_books_api_url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            book_info = data['items'][0]['volumeInfo']
            published_date = book_info.get('publishedDate', 'Year not available')
            year = extract_year_from_date(published_date)
            return year if year else 'Year not available'
        else:
            return 'Book not found.'
    else:
        return 'Error: Unable to fetch book details.'


def get_author_info_by_name(author_name):
    """
    Get Author Info by Name
    Retrieves information about an author based on their name from Wikipedia.
    Args:
        author_name (str): The name of the author.
    Returns:
        dict or None: A dictionary containing information about the author
                      (name, description, and image URL) if found, or None if not found.
    """
    wiki_wiki = Wikipedia(user_agent='lybrary (put here your email user)')
    page = wiki_wiki.page(author_name)

    if page.exists():
        description = page.summary
        image_url = None
        url = page.fullurl
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            image_tag = soup.select_one('.infobox img[srcset]')
            if image_tag:
                image_url = image_tag['src']
        return {
            "name": author_name,
            "description": description,
            "image_url": image_url
        }
    else:
        return None
