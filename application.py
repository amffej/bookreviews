import os
import json
import hashlib
import requests
import pprint as pp
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# goodreads api key
KEY = "xU4eCPbV2hTYGBIO0qhnQ"  

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

# Home page, process search results
@app.route("/", methods=["GET"])
def index():
    # Check is user is logged in
    if 'username' in session:
        firstname = session['firstname']
        firstname = firstname.capitalize()
        search_data = request.args.get("search")
        search_results = []
        # Process search queries
        if search_data is not None:
            search_data_formated = '%{0}%'.format(search_data)
            search_data_capitalized = search_data.capitalize()
            search_data_capitalized_formated = '%{0}%'.format(
                search_data_capitalized)
            pp.pprint(f"Searching for: {search_data_capitalized_formated}")
            search_results = db.execute("select * from books where title LIKE :search or title LIKE :search_cap or isbn LIKE :search or author LIKE :search or author LIKE :search_cap", {
                                        "search": search_data_formated, "search_cap": search_data_capitalized_formated}).fetchall()
            for book in search_results:
                pp.pprint(book.title)
        return render_template("index.html", signed_in=True, firstname=firstname, results=search_results, search_data = search_data)
    return redirect(url_for('login'))

# Book Page, Process all book details, Goodread API, Determine user reviewd book
@app.route("/book/", methods=["GET"])
def book():
    # Check if user is logged in
    if 'username' in session:
        firstname = session['firstname']
        firstname = firstname.capitalize()
        user = session['user_id']
        search_data = request.args.get("id")
        # Pull book information from database
        if search_data is not None:
            book_details = db.execute("select * from books where id = :id", {"id": search_data}).fetchall()
            # Pull goodreads data for current book
            for book in book_details:
                goodread_raw = requests.get(
                    "https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn})
                goodreads_json = goodread_raw.json()
                for data in goodreads_json['books']:
                    goodreads_rating = data['average_rating']
                    goodreads_count = data['ratings_count']
            # Get all reviews for current book
            reviews = db.execute("select review_text, username FROM reviews LEFT JOIN users ON reviews.user_id=users.id WHERE book_id = :book_id ", {
                                 "book_id": search_data}).fetchall()
            # Find out if user already reviewd this book
            if db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id", {"book_id": search_data, "user_id": user}).rowcount > 0:
                user_reviewed = True
            else:
                user_reviewed = False
        return render_template("book.html", signed_in=True, firstname=firstname, results=book_details, goodreads_rating=goodreads_rating, goodreads_count=goodreads_count, reviews=reviews, user_reviewed=user_reviewed)
    return redirect(url_for('login'))

# Inputs user review into database and returns user to page
@app.route("/review", methods=["POST"])
def review():
    if request.method == "POST":
        review = request.form.get("review_txt")
        book = request.form.get("book_id")
        user = session['user_id']
        db.execute("INSERT INTO reviews (book_id, user_id, review_text) VALUES (:book, :user, :review)",
                   {"book": book, "user": user, "review": review})
        db.commit()
        prev_url = url_for('book') + "?id=" + book
    return redirect(prev_url)

# Allows user to register to the site
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # Get form information.
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        uname = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        # Make password database safe
        salt = "4xO9"
        db_password = password+salt
        password_hash = hashlib.md5(db_password.encode())
        print(password_hash.hexdigest())

        # Check that Username is not taken
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": uname}).rowcount > 0:
            return render_template("register.html", alert=True)
        db.execute("INSERT INTO users (firstname, lastname, username, password, email) VALUES (:fname, :lname, :uname, :password, :email )",
                   {"fname": fname, "lname": lname, "uname": uname, "password": password_hash.hexdigest(), "email": email})
        db.commit()
        return render_template("register.html", success_message=True)
    return render_template("register.html")

# Allows user to login to the site
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Get form information.
        uname = request.form.get("username")
        password = request.form.get("password")

        # Check if user is in database
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": uname}).rowcount == 0:
            return render_template("login.html", alert=True)

        # Get user information from database
        db_userinfo = db.execute(
            "SELECT * FROM users where username = :username", {"username": uname}).fetchone()

        # Compare input password vs stored password
        salt = "4xO9"
        db_password = password+salt
        password_hash = hashlib.md5(db_password.encode())
        password_check = (db_userinfo.password == password_hash.hexdigest())

        # If password matches start the sessiond
        if password_check:
            session['username'] = db_userinfo.username
            session['firstname'] = db_userinfo.firstname
            session['lastname'] = db_userinfo.lastname
            session['user_id'] = db_userinfo.id
            return redirect(url_for('index'))
        return render_template("login.html", alert=True)
    return render_template("login.html")

# Logs user out of site
@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))

# External API for site information
@app.route("/api/<string:isbn>")
def api(isbn):

    # Checking if book is in database
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        return json.dumps({'error': 'Not found'}), 404

    # Get book info from database (books)
    book_data = db.execute(
        "SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

    # Get number of reviews from database (reviews) and setting json output
    for book in book_data:
        total_Reviews = db.execute("SELECT COUNT(id) FROM reviews where book_id = :id", {
                                   "id": book.id}).fetchone()
        json_output = json.dumps({'title': book.title, 'author': book.author,
                                  'year': book.year, 'isbn': book.isbn, 'review_count': total_Reviews.count})

    db.commit()
    return json_output
