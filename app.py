#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Show, Venue, Artist
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
    results = db.session.query(Venue.id, Venue.name).filter(
        Venue.name.ilike('%'+term+'%'))
    print(results.all())
    search_data = {}
    data = []
    for vid, vname in results:
        temp = {}
        temp['id'] = vid
        temp['name'] = vname
        temp['num_upcoming_shows'] = 0
        data.append(temp)
    search_data['count'] = len(results.all())
    search_data['data'] = data
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
        temp['artist_id'] = show.artist_id
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
        temp['artist_id'] = show.artist_id
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
    print('Received venue', request.form)
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
    results = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.ilike('%'+term+'%'))
    print(results.all())
    search_data = {}
    data = []
    for aid, aname in results:
        temp = {}
        temp['id'] = aid
        temp['name'] = aname
        temp['num_upcoming_shows'] = 0
        data.append(temp)
    search_data['count'] = len(results.all())
    search_data['data'] = data
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
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
        temp['venue_id'] = show.venue_id
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
        temp['venue_id'] = show.venue_id
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
            seeking_venue = request.form['seeking_venue'] == 'y'

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
    print('Received artist', request.form)
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
    print('Received show entry', request.form)
    try:
        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'],
                    start_time=request.form['start_time']
                    )
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
