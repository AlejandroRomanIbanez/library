from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, CheckConstraint
from data_manager import get_book_cover_url


db = SQLAlchemy()

class Author(db.Model):
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
  id = db.Column(db.Integer, primary_key=True)
  isbn = db.Column(db.Integer)
  title = db.Column(db.String, nullable=False)
  rating = db.Column(db.Float(precision=1), CheckConstraint('rating >= 0 AND rating <= 10'), nullable=True)
  publication_year = db.Column(db.Integer)
  author_id = db.Column(db.Integer, db.ForeignKey('author.id'))


  
  @property
  def cover_url(self):
      return get_book_cover_url(self.isbn)

  def __repr__(self):
    return f"<Author id={self.id}, isbn='{self.isbn}', " \
           f"title={self.title}, publication_year={self.publication_year}>"

  def __str__(self):
    return f"title={self.title}, publication_year={self.publication_year}"

def create_tables(app):
    with app.app_context():
        db.create_all()


def print_all_data():
    all_authors = Author.query.all()
    all_books = Book.query.all()

    print("All Authors:")
    for author in all_authors:
        print(f"{author.id} --> {author.name} --> {author.birth_date} --> {author.death_date}")

    print("\nAll Books:")
    for book in all_books:
        print(f" {book.id} --> {book.title} --> {book.publication_year} --> {book.isbn} --> {book.author_id} --> {book.rating}")
