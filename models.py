import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String())
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venues', lazy='dynamic')

    def get_json(self):
        return{
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }

    def __repr__(self):
        return f'<Venue {self.id},{self.name}>'

    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String())
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artists', lazy='dynamic')

    def __init__(self, name, genres, city, state, phone, image_link, website, facebook_link,
                 seeking_venue=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_description = seeking_description
        self.image_link = image_link

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def info(self):
        return{
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }

    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String, nullable=False)
# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
