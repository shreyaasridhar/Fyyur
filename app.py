#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # start_time = request.form['start_time']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venue_data = []
    venues = Venue.query.group_by(
        Venue.id, Venue.city, Venue.state).all()  # (Venue.id, Venue.city, Venue.state)
    # add a call to join the show database and retrive the show count and the data
    listed = []
    for venue in venues:
        print(venue.id, venue.city, venue.state)
        if venue.city in listed:
            continue
        listed.append(venue.city)
        venues_dict = {}
        venues_dict["city"] = venue.city
        venues_dict["state"] = venue.state
        ven = db.session.query(Venue.id, Venue.name).filter_by(city=venue.city)
        ven_list = []
        for vid, vname in ven:
            upcoming_shows = Show.query.filter(
                Show.venue_id == vid).filter(Show.start_time > now).all()
            print(upcoming_shows)
            temp = {}
            temp["id"] = vid
            temp["name"] = vname
            temp["num_upcoming_shows"] = len(
                upcoming_shows)  # update the value here
            ven_list.append(temp)
        venues_dict["venues"] = ven_list
        print(venues_dict)
        venue_data.append(venues_dict)
    print(venue_data)
    return render_template('pages/venues.html', areas=venue_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    term = request.form.get('search_term', '')
    print('%'+term+'%')
    results = db.session.query(Venue.id, Venue.name, Venue.upcoming_shows_count).filter(
        Venue.name.ilike('%'+term+'%'))
    print(results.all())
    search_data = {}
    data = []
    for vid, vname, vshowcount in results:
        temp = {}
        temp['id'] = vid
        temp['name'] = vname
        temp['num_upcoming_shows'] = vshowcount
        data.append(temp)
    search_data['count'] = len(results.all())
    search_data['data'] = data
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }

    return render_template('pages/search_venues.html', results=search_data, search_term=term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    v_query = Venue.query.get(venue_id)
    venue_details = v_query.get_json()
    upcoming_shows = Show.query.filter(
        Show.venue_id == venue_id).filter(Show.start_time > now).all()
    past_shows = Show.query.filter(
        Show.venue_id == venue_id).filter(Show.start_time <= now).all()
    upcoming = []
    for show in upcoming_shows:
        print(show.id, show.artist_id)
        temp = {}
        a_info = Artist.query.filter(
            Artist.id == show.artist_id).first()
        temp['artist_id'] = show.id
        temp['artist_name'] = a_info.name
        temp['artist_image_link'] = a_info.image_link
        temp['start_time'] = show.start_time
        upcoming.append(temp)

    past = []
    for show in past_shows:
        print(show.id, show.artist_id)
        temp = {}
        a_info = Artist.query.filter(
            Artist.id == show.artist_id).first()
        temp['artist_id'] = show.id
        temp['artist_name'] = a_info.name
        temp['artist_image_link'] = a_info.image_link
        temp['start_time'] = show.start_time
        past.append(temp)

    venue_details['upcoming_shows'] = upcoming
    venue_details['past_shows'] = past
    venue_details["past_shows_count"] = len(past_shows)
    venue_details["upcoming_shows_count"] = len(upcoming_shows)

    print(venue_details)
    return render_template('pages/show_venue.html', venue=venue_details)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    print('Recieved venue', request.form)
    seeking_talent = False
    seeking_description = ""
    try:
        if 'seeking_talent' in request.form:
            print("Seeking_talent", request.form['seeking_talent'])
            seeking_talent = request.form['seeking_talent'] == 'on'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        venue = Venue(name=request.form['name'],
                      city=request.form['city'],
                      state=request.form['state'],
                      phone=request.form['phone'],
                      address=request.form['address'],
                      genres=request.form.getlist('genres'),
                      image_link=request.form['image_link'],
                      website=request.form['website'],
                      facebook_link=request.form['facebook_link'],
                      seeking_talent=seeking_talent,
                      seeking_description=seeking_description
                      )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully listed!')
    except SQLAlchemyError as e:
        flash('Venue could not be listed!')
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.filter(id == venue_id)
        venue.delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    term = request.form.get('search_term', '')
    print('%'+term+'%')
    results = db.session.query(Artist.id, Artist.name, Artist.upcoming_shows_count).filter(
        Artist.name.ilike('%'+term+'%'))
    print(results.all())
    search_data = {}
    data = []
    for aid, aname, ashowcount in results:
        temp = {}
        temp['id'] = aid
        temp['name'] = aname
        temp['num_upcoming_shows'] = ashowcount
        data.append(temp)
    search_data['count'] = len(results.all())
    search_data['data'] = data
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=search_data, search_term=term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    a_query = Artist.query.get(artist_id)
    artist_details = a_query.info()
    upcoming_shows = Show.query.filter(
        Show.artist_id == artist_id).filter(Show.start_time > now).all()
    past_shows = Show.query.filter(
        Show.artist_id == artist_id).filter(Show.start_time <= now).all()
    upcoming = []
    for show in upcoming_shows:
        print(show.id, show.venue_id)
        temp = {}
        v_info = Venue.query.filter(
            Venue.id == show.venue_id).first()
        temp['venue_id'] = show.id
        temp['venue_name'] = v_info.name
        temp['venue_image_link'] = v_info.image_link
        temp['start_time'] = show.start_time
        upcoming.append(temp)

    past = []
    for show in past_shows:
        print(show.id, show.venue_id)
        temp = {}
        v_info = Venue.query.filter(
            Venue.id == show.venue_id).first()
        temp['venue_id'] = show.id
        temp['venue_name'] = v_info.name
        temp['venue_image_link'] = v_info.image_link
        temp['start_time'] = show.start_time
        past.append(temp)

    artist_details['upcoming_shows'] = upcoming
    artist_details['past_shows'] = past
    artist_details["past_shows_count"] = len(past_shows)
    artist_details["upcoming_shows_count"] = len(upcoming_shows)

    print(artist_details)
    return render_template('pages/show_artist.html', artist=artist_details)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    artist_data = Artist.query.get(artist_id)
    if artist_data:
        artist_details = Artist.info(artist_data)
        form.name.data = artist_details["name"]
        form.genres.data = artist_details["genres"]
        form.city.data = artist_details["city"]
        form.state.data = artist_details["state"]
        form.phone.data = artist_details["phone"]
        form.website.data = artist_details["website"]
        form.facebook_link.data = artist_details["facebook_link"]
        form.seeking_venue.data = artist_details["seeking_venue"]
        form.seeking_description.data = artist_details["seeking_description"]
        form.image_link.data = artist_details["image_link"]
        return render_template('forms/edit_artist.html', form=form, artist=artist_details)
    return render_template('errors/404.html')
    # DONE: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist_data = Artist.query.get(artist_id)
    print(request.form)
    seeking_venue = False
    if artist_data:
        if 'seeking_venue' in request.form:
            print("Seeking_venue", request.form['seeking_venue'])
            seeking_venue = request.form['seeking_venue'] == 'on'

        setattr(artist_data, 'name', request.form['name'])
        setattr(artist_data, 'genres', request.form.getlist('genres'))
        setattr(artist_data, 'city', request.form['city'])
        setattr(artist_data, 'state', request.form['state'])
        setattr(artist_data, 'phone', request.form['phone'])
        setattr(artist_data, 'website', request.form['website'])
        setattr(artist_data, 'facebook_link',
                request.form['facebook_link'])
        setattr(artist_data, 'image_link', request.form['image_link'])
        setattr(artist_data, 'seeking_description',
                request.form['seeking_description'])
        setattr(artist_data, 'seeking_venue', seeking_venue)
        db.session.commit()
        return redirect(url_for('show_artist', artist_id=artist_id))
    return render_template('errors/404.html'), 404

    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_data = Venue.query.get(venue_id)
    if venue_data:
        venue_details = Venue.get_json(venue_data)
        form.name.data = venue_details["name"]
        form.genres.data = venue_details["genres"]
        form.city.data = venue_details["city"]
        form.state.data = venue_details["state"]
        form.phone.data = venue_details["phone"]
        form.website.data = venue_details["website"]
        form.address.data = venue_details["address"]
        form.facebook_link.data = venue_details["facebook_link"]
        form.seeking_talent.data = venue_details["seeking_talent"]
        form.seeking_description.data = venue_details["seeking_description"]
        form.image_link.data = venue_details["image_link"]
        return render_template('forms/edit_venue.html', form=form, venue=venue_details)
    return render_template('errors/404.html')
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # DONE: populate form with values from venue with ID <venue_id>


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_data = Venue.query.get(venue_id)
    seeking_talent = False
    if venue_data:
        if 'seeking_talent' in request.form:
            print("Seeking_talent", request.form['seeking_talent'])
            seeking_talent = request.form['seeking_talent'] == 'y'

        setattr(venue_data, 'name', request.form['name'])
        setattr(venue_data, 'genres', request.form.getlist('genres'))
        setattr(venue_data, 'city', request.form['city'])
        setattr(venue_data, 'state', request.form['state'])
        setattr(venue_data, 'phone', request.form['phone'])
        setattr(venue_data, 'address', request.form['address'])
        setattr(venue_data, 'website', request.form['website'])
        setattr(venue_data, 'facebook_link',
                request.form['facebook_link'])
        setattr(venue_data, 'image_link', request.form['image_link'])
        setattr(venue_data, 'seeking_description',
                request.form['seeking_description'])
        setattr(venue_data, 'seeking_talent', seeking_talent)
        db.session.commit()
        return redirect(url_for('show_venue', venue_id=venue_id))
    return render_template('errors/404.html'), 404
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    print('Recieved artist', request.form)
    seeking_venue = False
    if 'seeking_venue' in request.form:
        print("Seeking_venue", request.form['seeking_venue'])
        seeking_venue = request.form['seeking_venue'] == 'y'
    try:
        artist = Artist(name=request.form['name'],
                        city=request.form['city'],
                        state=request.form['state'],
                        phone=request.form['phone'],
                        genres=request.form.getlist('genres'),
                        image_link=request.form['image_link'],
                        website=request.form['website'],
                        facebook_link=request.form['facebook_link'],
                        seeking_venue=seeking_venue,
                        seeking_description=request.form['seeking_description']
                        )
        Artist.insert(artist)
        flash('Artist ' + artist.name + ' was successfully listed!')
    except SQLAlchemyError as e:
        flash('Artist could not be listed!')

    # DONE: insert form data as a new Artist record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    shows_data = []
    venue_artist = db.session.query(
        Show.venue_id, Show.artist_id, Show.start_time)
    print(venue_artist)
    for venue, artist, start in venue_artist:
        temp = {}
        print(venue, artist)
        venue_details = db.session.query(Venue.name).filter_by(id=venue).all()
        artist_details = db.session.query(
            Artist.name, Artist.image_link).filter_by(id=artist).all()
        (name, image) = artist_details[0]
        (venue_name,) = venue_details[0]
        print(venue_name, name, image)
        temp['venue_id'] = venue
        temp['venue_name'] = venue_name
        temp['artist_id'] = artist
        temp['artist_name'] = name
        temp['artist_image_link'] = image
        temp['start_time'] = start
        shows_data.append(temp)

    return render_template('pages/shows.html', shows=shows_data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    print('Recieved show entry', request.form)
    try:
        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'],
                    start_time=request.form['start_time']
                    )
        # modify the show count of artists and venues based on the start time
        start_time = request.form['start_time']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(request.form['start_time'], now,
              request.form['artist_id'], request.form['venue_id'])
        # artist =  db.session.query(Artist.upcoming_shows_count,Artist.past_shows_count).filter_by(id=request.form['artist_id']).first()
        # venue =  db.session.query(Venue.upcoming_shows_count,Venue.past_shows_count).filter_by(id=request.form['venue_id']).first()
        # print(artist,venue)
        # if start_time > now:
        #     # if artist.upcoming_shows_count == None:
        #     #     artist.upcoming_shows_count = 1
        #     # else:
        #     artist.upcoming_shows_count +=  1
        #     # if venue.upcoming_shows_count == None:
        #     #     venue.upcoming_shows_count = 1
        #     # else:
        #     venue.upcoming_shows_count += 1
        # else:
        #     artist.past_shows_count += 1
        #     venue.past_shows_count += 1
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except SQLAlchemyError as e:
        flash('An error occurred. Show could not be listed!')
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
