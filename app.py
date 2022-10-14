# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app. config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many = True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many = True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id is not None and genre_id is not None:
            movies = Movie.query.filter(Movie.director_id == director_id, Movie.genre_id == genre_id).all()
        elif director_id is not None:
            movies = Movie.query.filter(Movie.director_id == director_id).all()
        elif genre_id is not None:
            movies = Movie.query.filter(Movie.genre_id == genre_id).all()
        else:
            movies = Movie.query.all()
        return movies_schema.dump(movies)


@movie_ns.route('/<mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        return movie_schema.dump(movie)


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors)

    def post(self):
        get_director = request.json
        director_db = Director.query.order_by(desc(Director.id)).first()
        get_director['id'] = director_db.id + 1
        new_director = Director(**get_director)
        db.session.add(new_director)
        db.session.commit()
        db.session.close()
        return 'Ok', 201

@director_ns.route('/<did>')
class DirectorView(Resource):
    def put(self, did):
        get_director_put = request.json
        director_update = Director.query.get(did)
        director_update.name = get_director_put.get('name')
        db.session.add(director_update)
        db.session.commit()
        db.session.close()
        return 'Ok', 201

    def delete(self, did):
        director_delete = Director.query.get(did)
        db.session.delete(director_delete)
        db.session.commit()
        db.session.close()
        return 'Ok', 204


if __name__ == '__main__':
    app.run(port = 8082, debug=True)
