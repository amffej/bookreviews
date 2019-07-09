import os, json, hashlib
import pprint as pp
from flask import Flask, session, render_template, request, redirect, url_for
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


@app.route("/", methods=["GET"])
def index():
    if 'username' in session:
        firstname= session['firstname']
        firstname = firstname.capitalize()
        search_data = request.args.get("search")
        search_data_formated = '%{0}%'.format(search_data)
        search_data_capitalized = search_data.capitalize()
        search_data_capitalized_formated = '%{0}%'.format(search_data_capitalized)
        #search_data = search_data.strip('\'')
        pp.pprint(f"Searching for: {search_data_capitalized_formated}")
        search_results = db.execute("select * from books where title LIKE :search or title LIKE :search_cap or isbn LIKE :search or author LIKE :search or author LIKE :search_cap", {"search" : search_data_formated, "search_cap" : search_data_capitalized_formated}).fetchall()
        #search_results = db.execute("select title from books where title LIKE :search or isbn LIKE :search or author LIKE :search", {"search" : search_data_formated})
        #pp.pprint(search_results)
        for book in search_results:
            pp.pprint(book.title)
        return render_template("index.html", signed_in=True, firstname=firstname, results = search_results)
    return redirect(url_for('login'))
    

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
                {"fname": fname, "lname": lname, "uname" : uname, "password" : password_hash.hexdigest(), "email" : email})
        db.commit()
        return render_template("register.html", success_message=True)
    return render_template("register.html")

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
        db_userinfo = db.execute("SELECT * FROM users where username = :username", {"username": uname}).fetchone()
        
        # Compare input password vs stored password
        salt = "4xO9"
        db_password = password+salt
        password_hash = hashlib.md5(db_password.encode())
        password_check = (db_userinfo.password == password_hash.hexdigest())

        if password_check:
            session['username'] = db_userinfo.username
            session['firstname'] = db_userinfo.firstname
            session['lastname'] = db_userinfo.lastname
            return redirect(url_for('index'))
        return render_template("login.html", alert=True) 
    return render_template("login.html")

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))

@app.route("/book")
def book():
    #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": "0380795272"})
    #pp.pprint(res.json())
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

