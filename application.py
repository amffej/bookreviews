import os, requests
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
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": "9781632168146"})
    pp.pprint(res.json())
    return "Project 1: TODO"

@app.route("/test/")
def test():
    #flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("login.html")

@app.route("/book/")
def book():
    #flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("book.html")