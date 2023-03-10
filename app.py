#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import collections
collections.Callable = collections.abc.Callable
import sys
from models import *



# class Venue(db.Model):
#     __tablename__ = 'Venue'

#     id = db.Column(db.Integer, primary_key=True,autoincrement=True)
#     name = db.Column(db.String)
#     genres = db.Column(db.String(120))
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website = db.Column(db.String(120))
#     seeking_talent = db.Column(db.Boolean, default = False)
#     seeking_description = db.Column(db.String(120))
#     shows = db.relationship("Show", backref="venues", lazy=False)
 
# class Artist(db.Model):
#     __tablename__ = 'Artist'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String)
#     genres = db.Column(db.String(120))
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website = db.Column(db.String(120))
#     seeking_venue = db.Column(db.Boolean, default = False)
#     seeking_description = db.Column(db.String(120))
#     shows = db.relationship("Show", backref="artists", lazy=False)

# class Show(db.Model):
#   __tablename__ = 'Show'

#   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
#   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)
#   start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data = []
  venue_list = []
  state_city = db.session.query(Venue.state, Venue.city).distinct(Venue.state, Venue.city).all()

  for state, city in state_city:
    venue_list = []
    venues = Venue.query.filter_by(state=state, city=city).all()
    for venue in venues:
      num_upcoming_shows = len([show for show in venue.shows if show.start_time > datetime.utcnow()])
      venue_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })

    data.append({
      "city": city,
      "state": state,
      "venues": venue_list
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  num_upcoming_shows = 0
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()

  for item in results:
    venues = Show.query.filter_by(venue_id = item.id).all()
    num_upcoming_shows = len([show for show in venues if show.start_time > datetime.utcnow()])

    data.append({
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response={
    "count": len(results),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  currentTime = datetime.now()
  for item in venue.shows:
    if(item.start_time < currentTime):
      past_shows_count +=1
      past_shows.append({
        "artist_id": item.artist_id,
        "artist_name": db.session.query(Artist.name).filter(Artist.id == item.artist_id).scalar(),
        "artist_image_link": db.session.query(Artist.image_link).filter(Artist.id == item.artist_id).scalar(),
        "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    else:
      upcoming_shows_count +=1
      upcoming_shows.append({
        "artist_id": item.artist_id,
        "artist_name": db.session.query(Artist.name).filter(Artist.id == item.artist_id).scalar(),
        "artist_image_link": db.session.query(Artist.image_link).filter(Artist.id == item.artist_id).scalar(),
        "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  genres = venue.genres.replace('{','').replace('}','').split(',')
  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "image_link": venue.image_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue(
        name = request.form.get('name', ''),
        genres = request.form.getlist("genres"),
        address = request.form.get('address', ''),
        city = request.form.get('city', ''),
        state = request.form.get('state', ''),
        phone = request.form.get('phone', ''),
        website = request.form.get('website', ''),
        image_link = request.form.get('image_link', ''),
        facebook_link = request.form.get('facebook_link', ''),
        seeking_talent = True if(request.form.get('seeking_talent') == 'on') else False,
        seeking_description = request.form.get('seeking_description', ''),
      )
      db.session.add(venue)
      db.session.commit()
    except Exception as e:
      error = True
      flash('Invalid value in request form data: ' + str(e))
      db.session.rollback()
    finally:
      db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      return render_template('errors/500.html'), 500
  else:
    flash('Please enter the correct format!')
    form = VenueForm()
    return render_template('forms/new_venue.html', form = form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash(f'Venue ' + Venue.name + ' was successfully deleted!')
    return redirect(url_for(venues))
  else:
    flash(f'An error occurred. Venue ' + Venue.name + ' could not be deleted.')
    return redirect(url_for(venues/venue_id))
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artistList = Artist.query.order_by(Artist.name).all()
  for item in artistList:
    data.append({
      "id": item.id,
      "name": item.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  num_upcoming_shows = 0
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()

  for item in results:
    artists = Show.query.filter_by(artist_id = item.id).all()
    num_upcoming_shows = len([show for show in artists if show.start_time > datetime.utcnow()])

    data.append({
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  if not artist:
    flash('Artist not found!')
    return render_template('errors/404.html'), 404
  else:
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    currentTime = datetime.now()
    for item in artist.shows:
        if item.start_time < currentTime:
            past_shows_count += 1
            past_shows.append({
                "venue_id": item.venue_id,
                "venue_name": db.session.query(Venue.name).filter(Venue.id == item.venue_id).scalar(),
                "venue_image_link": db.session.query(Venue.image_link).filter(Venue.id == item.venue_id).scalar(),
                "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            upcoming_shows_count += 1
            upcoming_shows.append({
                "venue_id": item.venue_id,
                "venue_name": db.session.query(Venue.name).filter(Venue.id == item.venue_id).scalar(),
                "venue_image_link": db.session.query(Venue.image_link).filter(Venue.id == item.venue_id).scalar(),
                "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

    # Build artist data
    genres = artist.genres.replace('{', '').replace('}', '').split(',')
    data = {
        "id": artist_id,
        "name": artist.name,
        "genres": genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
    }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).get(artist_id)
  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  artist = db.session.query(Artist).get(artist_id)
  if artist:
    artist.name = request.form["name"]
    artist.genres = request.form.getlist("genres")
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    artist.phone = request.form["phone"]
    artist.image_link = request.form["image_link"]
    artist.facebook_link = request.form["facebook_link"]
    artist.website = request.form["website_link"]
    artist.seeking_venue = True if request.form.get["seeking_venue"] else False
    artist.seeking_description = request.form["seeking_description"]

    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    return render_template('errors/object_not_found.html', object_name = "Artist")

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).get(venue_id)
  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  venue = db.session.query(Venue).get(venue_id)
  if venue:
    venue.name = request.form["name"]
    venue.genres = request.form.getlist("genres")
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.address = request.form["address"]
    venue.phone = request.form["phone"]
    venue.image_link = request.form["image_link"]
    venue.facebook_link = request.form["facebook_link"]
    venue.website = request.form["website_link"]
    venue.seeking_talent = True if request.form.get["seeking_talent"] else False
    venue.seeking_description = request.form["seeking_description"]

    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    return render_template('errors/object_not_found.html', object_name = "Venue")

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist(
        name = request.form["name"],
        city = request.form["city"],
        state = request.form["state"],
        phone = request.form["phone"],
        genres = request.form.getlist("genres"),
        facebook_link = request.form["facebook_link"],
        image_link = request.form["image_link"],
        website = request.form["website_link"],
        seeking_venue = True if "seeking_venue" in request.form else False,
        seeking_description = request.form["seeking_description"],
      )
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
      else:
        flash('An error occurred. Artist ' + (request.form['name']) + ' could not be listed.')
        return render_template('errors/500.html'), 500
  else:
    flash('Please enter the correct format!')
    form = ArtistForm()
    return render_template('forms/new_artist.html', form = form)
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  showList = Show.query.all()

  for item in showList:
    data.append({
      "id": item.id,
      "venue_id": item.venue_id,
      "venue_name": db.session.query(Venue.name).filter(Venue.id == item.venue_id).scalar(),
      "artist_id": item.artist_id,
      "artist_name": db.session.query(Artist.name).filter(Artist.id == item.artist_id).scalar(),
      "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      "artist_image_link": db.session.query(Artist.image_link).filter(Artist.id == item.artist_id).scalar()
  })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  form = ShowForm(request.form)
  if form.validate():
    try:
      show = Show(
        artist_id = request.form['artist_id'],
        venue_id = request.form['venue_id'],
        start_time = request.form['start_time']
      )
      print(f"name: {show.artist_id}, email: {show.venue_id}, message: {show.start_time}")
      db.session.add(show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      exc_type, exc_value, exc_traceback = sys.exc_info()
      print(f"Exception type: {exc_type}")
      print(f"Exception message: {exc_value}")
      print(f"Exception traceback: {exc_traceback}")
    finally:
      db.session.close()
    # on successful db insert, flash success
    if not error:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
    else:
      flash('An error occurred. Show could not be listed.')
      return render_template('errors/500.html'), 500
  else:
    flash('An error occurred.')
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
