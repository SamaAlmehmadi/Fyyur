#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser

import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for ,abort
from flask.globals import session
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
import sys
from sqlalchemy.orm import backref, query
#from flask_wtf import Form
from forms import *
from datetime import date
from wtforms import Form, StringField, SelectField
from flask_migrate import Migrate
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app ,db)

db.create_all()
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# note for me : 
   # Artist can choose many Genres , and every Artist may has many Genreas
   #rule in many to  many  => one to many  
   #Artist and V .. one to many -(for show) .. o

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    address = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(300))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(130))
    Looking_Venues = db.Column(db.Boolean , default =False)
    seeking_description = db.Column(db.String(320))
    
    #genre = db.relationship('A_Gernes' ,  secondary =A_Gernes ,backref=db.backref('Artist'), lazy=True )
    #page Show 
   
    showTable = db.relationship('Show' , backref='Artist' , lazy=True)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.






class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    genres = db.Column(db.String(300))
    website = db.Column(db.String(130))
    Looking_Venues = db.Column(db.Boolean , default =False)
    seeking_description = db.Column(db.String(320))
    
   
    showTable = db.relationship('Show' , backref= 'Venue' , lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    db.session.commit()


#many - to many  
class Show(db.Model):
   __tablename__ = "Show"
   show_id=db.Column(db.Integer, primary_key=True)

  

   Start_Time = db.Column(db.DateTime, nullable=False , default=datetime.utcnow)
   artist_id = db.Column( 'Artist_ID ',db.Integer , db.ForeignKey('Artist.id')) 
   venue_id= db.Column( 'Venue_ID', db.Integer , db.ForeignKey ('Venue.id'))

   def __repr__(self):
     return f'<show id:{self.show_id} , Artist id: {self.Artist_ID} , Venue id : {self.Venue_ID} '

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
  # TODO: replace with real venues data.
 # venues = Venue.query.all()
  area =[]
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  try:
    city= Venue.city
    state=   Venue.state
    cityData = db.session.query(city ,state ).distinct(city ,state )
    
    for city in cityData:
      id = Venue.id 
      name = Venue.name
      infoData =({
      'city' : city[0],
      'state' : city[1],
      'venues'  : db.session.query(id , name).filter(Venue.city ==city[0] ) .filter(Venue.state ==city[1])
    })
      area.append ( infoData)
  except:
     db.session.rollback()
     print(sys.exc_info())



  '''data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]'''
  return render_template('pages/venues.html', areas=area)

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
      "num_upcoming_shows": len(result.showTable),
       }]
     }
  else:
       response=flash('not found')
  
   
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data=[]
  genr=[]
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #gen_reqs = func.concat('(^|,)', Venue.id, '(,$)')
  data1 =Venue.query.filter(Venue.id == venue_id ).first()
  #data1= Venue.genres.filter(Venue.genres.like('%{0}%').format(Venue.genres))
  g =Venue.query.get(venue_id)
  genres=[]
  #request.form.getlist('genres')
  #if len (data1.genres)>0:
     # for list in data1.genres:
      #   genres.append( list.genres)
  #for genre in Venue.genres:
      #genres.append(genre)
         
  data ={
  "id":data1.id,
    "name": data1.name,
    "genres":  data1.genres,
    "address":data1.address ,
    "city": data1.city,
    "state": data1.state,
    "phone": data1.phone,
    "website": data1.website,
    "facebook_link": data1.facebook_link,
    "seeking_talent": data1.Looking_Venues,
    "seeking_description": data1.seeking_description,
    "image_link": data1.image_link,
    #"past_shows": [{
     # "artist_id": 4,
     # "artist_name": "Guns N Petals",
     # "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
     # "start_time": "2019-05-21T21:30:00.000Z"
  }
  
   
   

  data5={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
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
  
  
  try:
   
   data1 = Venue()
   data1.name =request.form.get('name')
   data1.city = request.form.get('city')
   data1.genres =VenueForm().genres.data
   data1.state =request.form.get('state')
   data1.address=request.form.get('address')
   data1.phone =request.form.get('phone')
   data1.facebook_link=request.form.get('facebook_link')
   data1.image_link=request.form.get('image_link')
   data1.website=request.form.get('website_link')
   data1.Looking_Venues=request.form.get('seeking_talent')=='True' 
   data1.seeking_description=request.form.get('seeking_description')
   
   db.session.add(data1)
   db.session.commit()
    
        #if not VenueForm().validate():
       #flash('you Must Complete')
      # return redirect(url_for('create_venue_form'))
  except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
  finally:
     db.session.close()
 
  # on successful db insert, flash success
     # TODO: on unsuccessful db insert, flash an error instead.
  if error :
     flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
     abort(400)
  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
 
  #data=[{
   # "id": 4,
    #"name": "Guns N Petals",
  #}, {
   # "id": 5,
    #"name": "Matt Quevedo",
  #}, {
    #"id": 6,
  #  "name": "The Wild Sax Band",
  #}]
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
      "num_upcoming_shows": len(result.showTable),
       }]
     }
     
  else:
     response=flash('not found')
      
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist1 = Artist.query.filter(Artist.id == artist_id).first()
  
  data={
    "id":artist1.id,
    "name": artist1.name,
    "genres":  artist1.genres,
    "address":artist1.address ,
    "city": artist1.city,
    "state": artist1.state,
    "phone": artist1.phone,
    "website": artist1.website,
    "facebook_link": artist1.facebook_link,
    "seeking_talent": artist1.Looking_Venues,
    "seeking_description": artist1.seeking_description,
    "image_link": artist1.image_link
    #"past_shows": [{
     # "artist_id": 4,
     # "artist_name": "Guns N Petals",
     # "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
     # "st
  }

  data1={
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  '''artist={
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
  }'''
  # TODO: populate form with fields from artist with ID <artist_id>
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
    form = VenueForm()
  #venue_query = Venue.query.get(venue_id)

    venue = Venue.query.get(venue_id)
    
  
    #'venue={
   # "id": 1,
   # "name": "The Musical Hop",
   # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #"address": "1015 Folsom Street",
    #"city": "San Francisco",
    #"state": "CA",
    #"phone": "123-123-1234",
    #"website": "https://www.themusicalhop.com",
    #"facebook_link": "https://www.facebook.com/TheMusicalHop",
    #"seeking_talent": True,
    #"seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
   # "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
 # }
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
  error=False
  t=""
  genr =request.form.getlist('genres')
  t = ','.join(map(str , genr))
  '''for list in  genr:
     t +=list 
     t.join(list)  ''' 

  try:
   data1 = Artist()
   data1.name =request.form.get('name')
   data1.city = request.form.get('city')
   data1.genres =t #request.form.getlist('genres')#VenueForm().genres.data,
   data1.state =request.form.get('state')
   data1.address=request.form.get('address')
   data1.phone =request.form.get('phone')
   data1.facebook_link=request.form.get('facebook_link')
   data1.image_link=request.form.get('image_link')
   data1.website=request.form.get('website_link')
   data1.Looking_Venues=request.form.get('seeking_talent')=='True' 
   data1.seeking_description=request.form.get('seeking_description')
   
   db.session.add(data1)
   db.session.commit()
  except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
  
  finally:
     db.session.close()
  if error :
     flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
     abort(400)
  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
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
  
  for sh in shows:
           data.append( {
      'venue_id': sh.venue_id,
      'venue_name': sh.Venue.name,
      'artist_id': sh.artist_id,
      'artist_name': sh.Artist.name,
      'artist_image_link': sh.Artist.image_link,
      'start_time': str(sh.Start_Time)
    })
  
  
  '''data=[{
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
  }]'''
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
  try:
    data1 = Show()
    data1.artist_id = request.form.get('artist_id')
    data1.venue_id = request.form.get('venue_id')
    data1.Start_Time=request.form.get('start_time')

    db.session.add(data1)
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

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
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