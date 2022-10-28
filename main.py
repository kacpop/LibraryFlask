from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Lib.db'
db = SQLAlchemy(app)
app.secret_key = os.urandom(12)


class Books(db.Model):
  id = db.Column("id", db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  author = db.Column(db.String(100), nullable=False)
  year = db.Column(db.Integer, nullable=False)

  def __init__(self, title, author, year):
    self.title = title
    self.author = author
    self.year = year


class Borrowed_books(db.Model):
  id = db.Column("id", db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  author = db.Column(db.String(100), nullable=False)
  year = db.Column(db.Integer, nullable=False)
  surname = db.Column(db.String(100), nullable=False)

  def __init__(self, title, author, year, surname):
    self.title = title
    self.author = author
    self.year = year
    self.surname = surname


@app.route('/')
def home():
  return render_template("index.html")


@app.route('/add', methods=["POST", "GET"])
def add():
  if request.method == "POST":
    title = request.form["Title"]
    author = request.form["Author"]
    year = request.form["PublicationYear"]

    if title == '' or author == '' or year == '':
      flash(
        "Not enough data to add the book. Please fill the information about the book",
        "info")
      return render_template("add.html")
    else:
      book = Books(title, author, year)
      db.session.add(book)
      db.session.commit()
      flash(f"{title} added to the library!", "info")
      return render_template("add.html")
  else:
    return render_template("add.html")


@app.route('/borrow', methods=["POST", "GET"])
def borrow():
  if request.method == "POST":
    title = request.form["Title"]
    surname = request.form["Surname"]

    found_book = Books.query.filter_by(title=title).first()
    found_books = Borrowed_books.query.filter_by(surname=surname).all()
    book_counter = 0

    for book in found_books:
      book_counter += 1

    if book_counter > 2:
      flash("Person has 3 books. Can't borrow more. Action terminated", "info")
      return render_template("borrow.html")
    elif found_book == None:
      flash(f"Title {title} not found in our database. Action Terminanted",
            "info")
      return render_template("borrow.html")
    elif surname == "":
      flash("Please fill all the information. Action terminated", "info")
      return render_template("borrow.html")
    else:
      book = Borrowed_books(found_book.title, found_book.author,
                            found_book.year, surname)
      db.session.add(book)
      db.session.commit()
      Books.query.filter_by(id=found_book.id).delete()
      db.session.commit()
      flash(f"{title} borrowed to {surname}", "info")
      return render_template("borrow.html")
  else:
    return render_template("borrow.html")


@app.route('/return', methods=["POST", "GET"])
def Return():
  if request.method == "POST":
    title = request.form["Title"]
    surname = request.form["Surname"]

    found_book = Borrowed_books.query.filter_by(title=title,
                                                surname=surname).first()
    if found_book == None:
      flash("Borrower does not have this book. Action terminated", "info")
      return render_template("return.html")
    book = Books(found_book.title, found_book.author, found_book.year)
    db.session.add(book)
    db.session.commit()
    Borrowed_books.query.filter_by(id=found_book.id).delete()
    db.session.commit()
    flash(f"{title} returned", "info")
    return render_template("return.html")
  else:
    return render_template("return.html")


@app.route('/av')
def available():
  return render_template("available.html", values=Books.query.all())


@app.route('/bo')
def borrowed():
  return render_template("borrowed.html", values=Borrowed_books.query.all())


if __name__ == "__main__":
  with app.app_context():
    db.create_all()
  app.run(host='0.0.0.0', port=8080, debug=True)
