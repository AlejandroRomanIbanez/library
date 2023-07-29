from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, CheckConstraint
from data_manager import get_book_cover_url


db = SQLAlchemy()

class Author(db.Model):
  """
  Author Model
  Represents an author in the database.
  Attributes:
  id (int): Primary key for the author.
  name (str): The name of the author.
  birth_date (Date): The birth date of the author.
  death_date (Date): The death date of the author.
  book_id (Relationship): One-to-many relationship with Book model, representing the books written by the author.
  Methods:
  __repr__(): Returns a string representation of the Author object.
  __str__(): Returns a human-readable string representation of the Author object.
    """
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  birth_date = db.Column(db.Date, nullable=True)
  death_date = db.Column(db.Date, nullable=True)
  book_id = db.relationship('Book', backref='author')

  def __repr__(self):
      return f"<Author id={self.id}, name='{self.name}', " \
               f"birth_date={self.birth_date}, death_date={self.death_date}>"

  def __str__(self):
      return f"Author: {self.name}"


class Book(db.Model):
  """
  Book Model
  Represents a book in the database.
  Attributes:
  id (int): Primary key for the book.
  isbn (int): The ISBN (International Standard Book Number) of the book.
  title (str): The title of the book.
  rating (float): The rating of the book (0.0 to 10.0).
  publication_year (int): The publication year of the book.
  author_id (int): Foreign key referencing the Author model, representing the author of the book.
  Properties:
  cover_url (str): Property that returns the cover URL of the book.
  Methods:
  __repr__(): Returns a string representation of the Book object.
  __str__(): Returns a human-readable string representation of the Book object.
  """
  id = db.Column(db.Integer, primary_key=True)
  isbn = db.Column(db.Integer)
  title = db.Column(db.String, nullable=False)
  rating = db.Column(db.Float(precision=1), CheckConstraint('rating >= 0 AND rating <= 10'), nullable=True)
  publication_year = db.Column(db.Integer)
  author_id = db.Column(db.Integer, db.ForeignKey('author.id'))


  
  @property
  def cover_url(self):
      """
      Cover URL Property
      Retrieves the cover URL of the book using the get_book_cover_url function.
      Returns:
          str: The URL of the book cover image.
      """
      return get_book_cover_url(self.isbn)

  def __repr__(self):
    return f"<Author id={self.id}, isbn='{self.isbn}', " \
           f"title={self.title}, publication_year={self.publication_year}>"

  def __str__(self):
    return f"title={self.title}, publication_year={self.publication_year}"

def create_tables(app):
    """
    Create Tables
    Creates the database tables based on the defined models.
    Args:
        app (Flask): The Flask application instance.
    """
    with app.app_context():
        db.create_all()


def print_all_data():
    """
    Print All Data
    Retrieves all authors and books from the database and prints their information.
    """
    all_authors = Author.query.all()
    all_books = Book.query.all()

    print("All Authors:")
    for author in all_authors:
        print(f"{author.id} --> {author.name} --> {author.birth_date} --> {author.death_date}")

    print("\nAll Books:")
    for book in all_books:
        print(f" {book.id} --> {book.title} --> {book.publication_year} --> {book.isbn} --> {book.author_id} --> {book.rating}")
