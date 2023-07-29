import requests
from sqlalchemy import or_
from wikipediaapi import Wikipedia
from bs4 import BeautifulSoup
import re


API_KEY = "Put Here Your API Key"


def sort_books(sort_option, Book, Author):
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
    if search_query:
        return Book.query.join(Author).filter(
            or_(Book.title.like(f"%{search_query}%"), Author.name.like(f"%{search_query}%"))
        ).all()
    else:
        return Book.query.all()



def get_isbn(title):
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
    google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(google_books_api_url)
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        book_info = data["items"][0]["volumeInfo"]
        if "imageLinks" in book_info and "thumbnail" in book_info["imageLinks"]:
            return book_info["imageLinks"]["thumbnail"]
    return None


def get_book_description(book_title):
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
    formats_to_try = ["%Y-%m-%d", "%Y-%m", "%Y"]
    for date_format in formats_to_try:
        match = re.match(r"\d{4}", date_string)
        if match:
            return int(match.group())
    return None

def get_book_year_by_title(book_title):
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
