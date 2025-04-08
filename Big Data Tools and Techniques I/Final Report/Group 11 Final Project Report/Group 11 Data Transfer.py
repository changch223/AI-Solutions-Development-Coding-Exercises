from datetime import datetime
import itertools
import math
from typing import Iterable, Optional, Tuple
import pyodbc
from pymongo import MongoClient


db_connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=MovieRating;Trusted_Connection=yes;"
mongo_connection_string = "mongodb+srv://Sean:Test123@cluster0.eisxg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def parse_movie(movie) -> Optional[Tuple[int, str, datetime]]:
  if movie["Release_Date"]:
    try:
      release_date = datetime.strptime(movie["Release_Date"], "%d-%b-%Y")
      return (movie["Movie_Id"], movie["Movie_Title"], release_date)
    except TypeError:
      print("Movie Data Error:", movie)
      return None
  else:
    return None


def parse_genre(movie) -> Iterable[Tuple[int, str]]:
  all_genre = ["Action", "Adventure", "Animation", "Children", "Comedy",
               "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
               "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
               "Thriller", "War", "Western"]
  movieId = movie["Movie_Id"]
  yield from ((movieId, g) for g in all_genre if movie[g])


def parse_user(user) -> Tuple[int, int, str, str, str]:
  return (user["UserID"], user["Age"], user["Gender"],
          user["Occupation"], user["Zip_Code"])


def parse_rating(rating) -> Tuple[int, int, float]:
  return (rating["ItemID"], rating["UserID"], rating["Rating"])


def get_movies(movies_source) -> Iterable[Tuple[int, str, datetime]]:
  yield from (m for m in map(parse_movie, movies_source) if m)


def get_genre(movies_source) -> Iterable[Tuple[int, str]]:
  yield from itertools.chain.from_iterable(map(parse_genre, movies_source))


def get_users(users_source) -> Iterable[Tuple[int, int, str, str, str]]:
  yield from map(parse_user, users_source)


def get_ratings(rating_source) -> Iterable[Tuple[int, int, float]]:
  yield from map(parse_rating, rating_source)


def write_sql_db(sql, source):
  conn = pyodbc.connect(db_connection_string)
  cursor = conn.cursor()
  cursor.fast_executemany = True
  cursor.executemany(sql, source)
  conn.commit()


def write_movies(source: Iterable[Tuple[int, str, datetime]]):
  sql = "INSERT INTO Movie (MovieId, Title, ReleaseDate) VALUES (?, ?, ?)"
  write_sql_db(sql, source)


def write_genre(source: Iterable[Tuple[int, str]]):
  sql = "INSERT INTO MovieGenre (MovieId, GenreName) VALUES (?, ?)"
  write_sql_db(sql, source)


def write_users(source: Iterable[Tuple[int, int, str, str, str]]):
  sql = "INSERT INTO MovieUser (UserId, Age, Gender, Occupation, ZipCode) VALUES (?, ?, ?, ?, ?)"
  write_sql_db(sql, source)


def write_ratings(source: Iterable[Tuple[int, int, float]]):
  sql = "INSERT INTO MovieRating (MovieId, UserId, Rating) VALUES (?, ?, ?)"
  write_sql_db(sql, source)


client = MongoClient(mongo_connection_string)
db = client["movielens100k"]

missing_release_dates = db["movies"].find({"Release_Date": float('nan')})
print("Release dates missing for", [m["Release_Date"] for m in missing_release_dates])

movies_source = list(db["movies"].find({"_id": {"$nin": [m["_id"] for m in missing_release_dates]}}))
movies = list(get_movies(movies_source))
write_movies(movies)

movie_ids = set(m[0] for m in movies)

write_genre(get_genre(m for m in movies_source if m["Movie_Id"] in movie_ids))

users = db["users"].find()
write_users(get_users(users))

ratings = db["ratings"].find()

write_ratings(get_ratings(r for r in ratings if r["ItemID"] in movie_ids))
