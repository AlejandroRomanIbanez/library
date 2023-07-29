# library
My Library is a web application that allows users to manage their personal library, including books and authors. The application is built using the Flask framework and SQLAlchemy for database management. Users can add, view, search, and rate books in their library. The application also fetches book information from external APIs like Google Books API and Wikipedia API.

Note: To use the application, users need to obtain their own API key for the Google Books API and a user agent for the Wikipedia API. The API key is used to fetch book information and cover images, while the user agent is required for making requests to Wikipedia.
Features

    View a list of all books in the library.
    Sort books by title, author, or publication year.
    Search books by title or author name.
    Add new books to the library, including book details like title, author, and publication year.
    Rate books with a rating between 0.0 and 10.0.
    View book details, including the cover image and description fetched from external APIs.
    Add new authors to the library, including birth and death dates (if available).
    Delete books and authors from the library.
    Use of external APIs (Google Books API and Wikipedia API) to fetch additional book and author information.

API Key and User Agent

Note: To use the application, you need to obtain your own API key for the Google Books API and a user agent for the Wikipedia API.

    Google Books API Key: Obtain your API key by visiting the Google Cloud Console and 
    enabling the Google Books API for your project. Copy the API key and replace the API_KEY 
    variable in the data_manager.py file with your key.

    Wikipedia API User Agent: Wikipedia requires a user agent to be included
    in requests to its API.
    You can set your user agent in the get_author_info_by_name function
    in the data_manager.py file.
