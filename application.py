import os, requests, json
import pprint as pp
from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
KEY = "xU4eCPbV2hTYGBIO0qhnQ" #goodreads api key

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": "0380795272"})
    pp.pprint(res.json())
    return "Project 1: TODO"

@app.route("/login/")
def login():
    #flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("login.html")

@app.route("/register/")
def register():
    #flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("register.html")

@app.route("/book/")
def book():
    #flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("book.html")

@app.route("/api/<string:isbn>")
def api(isbn):
   
    # Checking if book is in database
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
       return json.dumps({'error': 'Not found'}), 404

    # Get book info from database (books)
    book_data = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    
    # Get number of reviews from database (reviews) and setting json output
    for book in book_data:
        total_Reviews = db.execute("SELECT COUNT(id) FROM reviews where book_id = :id", {"id": book.id}).fetchone()
        json_output = json.dumps({'title': book.title, 'author': book.author, 'year' : book.year, 'isbn': book.isbn, 'review_count': total_Reviews.count })
    
    db.commit()
    return json_output

