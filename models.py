from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()




class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    address = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(130))
    Looking_Venues = db.Column(db.Boolean , default =False)
    seeking_description = db.Column(db.String(320))
   
    shows = db.relationship('Show', backref=db.backref('Artist'), lazy="joined")
    
    






class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(130))
    Looking_Venues = db.Column(db.Boolean , default =False)
    seeking_description = db.Column(db.String(320))
    
   
    shows = db.relationship('Show', backref=db.backref('Venue'), lazy="joined")
    
    
  

class Show(db.Model):
   __tablename__ = 'show'
   show_id=db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime, nullable=False , default=datetime.utcnow)
   artist_id = db.Column( 'artist_id ',db.Integer , db.ForeignKey('artist.id')) 
   venue_id= db.Column( 'venue_id', db.Integer , db.ForeignKey ('venue.id'))
   
   def __repr__(self):
     return f'<show id:{self.show_id} , Artist id: {self.Artist_ID} , Venue id : {self.Venue_ID} '
