from flask import Flask, render_template, request, flash, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import or_
from datetime import datetime, date
from sqlalchemy.orm import joinedload
from data_manager import *

app = Flask(__name__)
app.secret_key = 'pass'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from data_models import Author, Book, print_all_data, create_tables


@app.route("/", methods=["GET"])
def home():
    """
    Home Page Route
    This route handles the home page of the application. It allows users to sort and search for books.
    Returns:
        Rendered HTML template: The home.html template with a list of books based on the sorting and search options.
    """
    sort_option = request.args.get("sort")
    search_query = request.args.get("search", "")

    if sort_option:
        books = sort_books(sort_option, Book, Author)
    elif search_query:
        books = search_books(search_query, Book, Author)
    else:
        books = Book.query.options(joinedload(Book.author)).all()

    if search_query and not books:
        flash(f"No books found for search: '{search_query}'", 'warning')

    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Add Author Route
    This route allows users to add a new author to the library.
    Returns:
        Rendered HTML template: The add_author.html template with a form to add a new author.
    """
    if request.method == "POST":
        name = request.form['name']
        birth_date_str = request.form['birthdate']
        death_date_str = request.form['date_of_death']
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
        death_date = datetime.strptime(death_date_str, '%Y-%m-%d').date() if death_date_str else None
        author = Author(name=name, birth_date=birth_date, death_date=death_date)
        db.session.add(author)
        db.session.commit()
        message = "Author added successfully!"
        flash(message, 'success')
        return redirect(url_for('home', message=message)), 201
    return render_template('add_author.html')


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Add Book Route
    This route allows users to add a new book to the library.
    Returns:
        Rendered HTML template: The add_book.html template with a form to add a new book.
    """
    if request.method == "POST":
        title = request.form['title']
        publication_year = get_book_year_by_title(title)
        author_id = int(request.form['author'])
        author = Author.query.get(author_id)
        db.session.expunge_all()
        isbn = get_isbn(title)
        cover = get_book_cover_url(isbn)
        book = Book(title=title, publication_year=publication_year, isbn=isbn, author=author)
        db.session.merge(book)
        db.session.commit()
        message = "Book added successfully!"
        flash(message, 'success')
        return redirect(url_for('home', message=message)), 201
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Delete Book Route
    This route allows users to delete a book from the library.
    Args:
        book_id (int): The ID of the book to be deleted.
    Returns:
        Redirect: Redirects to the home page after successful deletion.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author
    book = db.session.merge(book)
    db.session.delete(book)
    db.session.commit()
    other_books = Book.query.filter_by(author_id=author.id).count()
    if other_books == 0:
        author = db.session.merge(author)
        db.session.delete(author)
        db.session.commit()

    flash("Book deleted successfully!", "success")
    return redirect(url_for("home"))


@app.route("/description_book", methods=["GET"])
def description_book():
    """
    Book Description Route
    This route displays detailed information about a specific book.
    Returns:
        Rendered HTML template: The description_book.html template with detailed book information.
    """
    book_title = request.args.get("book_title")
    if book_title:
        description = get_book_description(book_title)
        book_year = get_book_year_by_title(book_title)
        if description == "Book not found.":
            flash(description, 'warning')
            return redirect(url_for("home"))
        book_info = {
            "cover_url": get_book_cover_url(get_isbn(book_title)),
            "title": book_title,
            "description": description,
            "publication_year": book_year
        }
        return render_template("description_book.html", book_info=book_info)
    else:
        flash("Book title not provided.", "danger")
        return redirect(url_for("home"))


@app.route("/description_author", methods=["GET"])
def description_author():
    """
    Author Description Route
    This route displays detailed information about a specific author.
    Returns:
        Rendered HTML template: The description_author.html template with detailed author information.
    """
    author_name = request.args.get("author_name")
    if author_name:
        author_info = get_author_info_by_name(author_name)
        author = Author.query.filter_by(name=author_name).first()
        if author_info:
            if author:
                return render_template("description_author.html", author_info=author_info, author=author)
        else:
            flash(f"Author '{author_name}' not found.", 'warning')
            return redirect(url_for("home"))
    else:
        flash("Author name not provided.", "danger")
        return redirect(url_for("home"))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    """
    Delete Author Route
    This route allows users to delete an author and all their associated books from the library.
    Args:
        author_id (int): The ID of the author to be deleted.
    Returns:
        Redirect: Redirects to the home page after successful deletion.
    """
    author = Author.query.get_or_404(author_id)
    books = Book.query.filter_by(author_id=author_id).all()
    for book in books:
        book = db.session.merge(book)
        db.session.delete(book)
    author = db.session.merge(author)
    db.session.delete(author)
    db.session.commit()
    flash("Author deleted successfully!", "success")
    return redirect(url_for("home"))


@app.route("/update_rating/<int:book_id>", methods=["POST"])
def update_book_rating(book_id):
    """
    Update Book Rating Route
    This route allows users to update the rating of a book.
    Args:
        book_id (int): The ID of the book whose rating is to be updated.
    Returns:
        Redirect: Redirects to the home page after successful update.
    """
    with app.app_context():
        book = Book.query.get_or_404(book_id)
        new_rating = float(request.form.get("rating"))
        book.rating = new_rating
        db.session.merge(book)  # Add the book to the session to track changes
        db.session.commit()

        updated_book = Book.query.get(book_id)
        if updated_book:
            books = Book.query.all()
            flash("Book rating updated successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Book not found.", "warning")
            return redirect(url_for("home"))


if __name__ == '__main__':
    # create_tables(app)
    with app.app_context():
        print_all_data()
    app.run(host="0.0.0.0", port=5002, debug=True)