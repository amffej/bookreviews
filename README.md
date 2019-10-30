# Book Reviews Site

### Project Summary:
The goal for this project was to build a book review website. Requirements were as follow:
Users will be able to register for your website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. You’ll also use the a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users will be able to query for book details and book reviews programmatically via your website’s API. 

Flask framework was used along with Heroku PostgreSQL


### File Structure:
```
bookreviews/
├── templates/      
│   ├── book.html       # Displays individual books and reviews
│   ├── index.html      # Homepage for search bar and results
│   ├── layout.html     # Shared layout file
│   ├── login.html      # Login form
│   └── register.html   # Registration form
├── static/
│   ├── gr-logo.png     # gooreads logo
│   └── style.css       # Custom CSS file
├── application.py      # Main flask application file
├── books.csv           # CSV used for importing book data
├── import.py           # Script used for import CSV to SQL data
├── README.md           # This file!
└── requirements.txt    # List required packages
```

### Database Structure:
For this project we used heroku app services to host a PostgreSQL.

SQL Structure is as follow:

```
-- Adminer 4.6.3-dev PostgreSQL dump

DROP TABLE IF EXISTS "books";
DROP SEQUENCE IF EXISTS books_id_seq;
CREATE SEQUENCE books_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."books" (
    "id" integer DEFAULT nextval('books_id_seq') NOT NULL,
    "isbn" character varying NOT NULL,
    "title" character varying NOT NULL,
    "author" character varying NOT NULL,
    "year" integer NOT NULL,
    CONSTRAINT "books_id" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "reviews";
DROP SEQUENCE IF EXISTS reviews_id_seq;
CREATE SEQUENCE reviews_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."reviews" (
    "id" integer DEFAULT nextval('reviews_id_seq') NOT NULL,
    "book_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "review_text" text NOT NULL,
    CONSTRAINT "reviews_book_id_fkey" FOREIGN KEY (book_id) REFERENCES books(id) NOT DEFERRABLE,
    CONSTRAINT "reviews_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS user_id_seq;
CREATE SEQUENCE user_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('user_id_seq') NOT NULL,
    "firstname" character varying NOT NULL,
    "lastname" character varying NOT NULL,
    "username" character varying NOT NULL,
    "password" character varying NOT NULL,
    "email" character varying NOT NULL,
    CONSTRAINT "user_id" PRIMARY KEY ("id")
) WITH (oids = false);

-- 2019-07-8 06:27:32.899362+00
```

### Other Features:

- Search for capitalized entries in database
- Generate database safe passwords using md5 + salt
- Dynamic menu fields based on user sign in/out status
- Bootstrap cards for desktop and mobile friendly viewing

### Future improvements:

- Search only capitalizes first word in query 
- When search result is 4 or less items, the cards dont align in most optimal manner.
- Add more details on each review item, including time stamp.
- Add a 5 star CSS book review button.



