import csv, os
import pprint as pp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Import CSV File
with open("books.csv", encoding= 'ISO-8859-1') as csvfile:
    rows = csv.DictReader(csvfile)
    data = [row for row in rows]
    data = data[0:5001] # Limit number for testing
    #pp.pprint(data) # Test import data
    for row in data:
        db.execute(''' INSERT INTO books (isbn, title, author, year)
                    VALUES (:isbn, :title, :author, :year)''', row)
        print(f"Added {row['title']} ({row['year']}).")
    db.commit()

