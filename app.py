#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from logging import Formatter, FileHandler
import dateutil.parser
from flask_wtf.csrf import CSRFProtect
import babel
from flask import (
  Flask,
  render_template, 
  request,
   Response, 
   flash,
   redirect, 
   url_for ,
   abort)
from flask.globals import session
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
import sys
from sqlalchemy.orm import backref, query
from flask_wtf import Form
from forms import *
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import func
from models import db, Venue, Artist, Show 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
db.init_app(app)


migrate = Migrate(app ,db)

with app.app_context():
    db.create_all()
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




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
 locals = []
 venues = Venue.query.all()

 places = Venue.query.distinct(Venue.city, Venue.state).all()

 for place in places:
    locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })
 return render_template('pages/venues.html', areas=locals)

   
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data =[]
  error =False
  search_term=request.form.get('search_term', '')
  
  results = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  
  for result in results:
       data.append(results)

  if results in data:
        response={
    "count": len(results),
    "data": [{
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(result.shows),
       }]
     }
  else:
       response=flash('not found')
  
   
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  
  venue = Venue.query.get_or_404(venue_id)
  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
       temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.Artist.name,
        'artist_image_link': show.Artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
       if show.start_time <= datetime.now():
        past_shows.append(temp_show)
       else:
        upcoming_shows.append(temp_show)


  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)


  
   
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)



@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error =False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
     venue = Venue ()
     form.populate_obj(venue)
  
     db.session.add(venue)
     db.session.commit()
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
    finally:
     db.session.close()
 
  # on successful db insert, flash success
     # TODO: on unsuccessful db insert, flash an error instead.
  else:
     msg = []
     for field , err in form.errors.items():
       msg.append(field + ' ' + '|'.join(err))
       flash('Errors ' + str(msg))
  
     


  return render_template('pages/home.html')






@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(Venue.id == venue_id).delete()
    db.session.commit()
    flash('successfully deleted')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  except:
     db.session.rollback()
     
  finally:
   db.session.close()
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('pages/home.html'))
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 
  data=Artist.query.all()
 
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data=[]
  search_term=request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  
  for result in results:
       data.append(results)

  if results in data:
     response={
    "count": len(results),
    "data": [{
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(result.shows),
       }]
     }
     
  else:
     response=flash('not found')
      
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.get_or_404(artist_id)
  
  past_shows = []
  upcoming_shows = []
  
  for show in artist.shows:
       temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.Artist.name,
        'artist_image_link': show.Artist.image_link,
        'venue_image_link':show.Venue.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
       if show.start_time <= datetime.now():
        past_shows.append(temp_show)
       else:
        upcoming_shows.append(temp_show)
  data = vars(artist)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)
 
  # TODO: populate form with fields from artist with ID <artist_id>
  
  
 #  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
      form = ArtistForm()
      artist = Artist.query.get(artist_id)
  
  
  
  
  
      return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error =False

  lok = True if 'seeking_talent' \
    in request.form else False
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  genres = request.form.getlist('genres')
  address = request.form.get('address')
  phone = request.form.get('phone')  
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website')
  Looking_Venues = lok 
  seeking_description = request.form.get('seeking_description')
  image_link = request.form.get('image_link')
  try:
    artist = Artist.query.get(artist_id)
    artist.name = name
    artist.city = city
    artist.state = state
    artist.address = address
    artist.phone = phone
    artist.genres = genres
    artist.image_link = image_link
    artist.facebook_link = facebook_link
    artist.website = website
    artist.Looking_Venues = Looking_Venues
    artist.seeking_description = seeking_description
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
     db.session.close()
  if error :
     flash('An error occurred. Venue could not be updated.')
     abort(400)
  if not error:
      flash('Venue  was successfully updated')  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    
    
  
    
  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  #form =VenueForm()
  
  error =False 
  lok = True if 'seeking_talent' \
    in request.form else False
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  genres = request.form.getlist('genres')
  address = request.form.get('address')
  phone = request.form.get('phone')
  
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website')
  Looking_Venues = lok 
  seeking_description = request.form.get('seeking_description')
  image_link = request.form.get('image_link')
  try:
        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.city = city
        venue.state = state
        venue.address = address
        venue.phone = phone
        venue.genres = genres
        venue.image_link = image_link
        venue.facebook_link = facebook_link
        venue.website = website
        venue.Looking_Venues = Looking_Venues
        venue.seeking_description = seeking_description
   
  # Venue.query.filter(Venue.id == venue_id).first()
        db.session.commit()
   
  except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
  finally:
     db.session.close()
 
  # on successful db insert, flash success
     # TODO: on unsuccessful db insert, flash an error instead.
  if error :
     flash('An error occurred. Venue could not be updated.')
     abort(400)
  if not error:
      flash('Venue  was successfully updated')


  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))





#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  error=False
  if form.validate():
    try:
     artist = Artist ()
     form.populate_obj(artist)
  
     db.session.add(artist)
     db.session.commit()
     flash('artist ' + request.form['name'] + ' was successfully listed!')
    except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
    finally:
     db.session.close()
 
  # on successful db insert, flash success
     # TODO: on unsuccessful db insert, flash an error instead.
  else:
     msg = []
     for field , err in form.errors.items():
       msg.append(field + ' ' + '|'.join(err))
       flash('Errors ' + str(msg))
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows =Show.query.all()
  data=[]
  #shows =db.session.query(artist  ,venue , show).filter(Venue.id ==Show.venue_id , Artist.id ==Show.artist_id)
  
  for show in shows:
           data.append( {
      'venue_id': show.venue_id,
      'venue_name': show.Venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.Artist.name,
      'artist_image_link': show.Artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
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
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form )
  
  try:
    show = Show()
    form.populate_obj(show)

    db.session.add(show)
    db.session.commit()
  except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
  
  finally:
     db.session.close()
  if error :
     flash('An error occurred. Show could not be listed.')
     abort(400)
  if not error:
      flash('Show was successfully listed!')

  
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
