from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import dateutil.parser
db = SQLAlchemy()



# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_desc = db.Column(db.String,)
    venues = db.relationship("Show",backref ='venue',lazy = True,cascade = 'all, delete')
    genres = db.Column(db.ARRAY(db.String))
    def __repr__(self):
      return f"< {self.id} {self.name}>"
    #Relationship between Venues, Artists, and Shows is Many to Many relationship with Shows as a associate table

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))  
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    artists = db.relationship("Show", backref='artist', lazy=True,cascade = 'all, delete')
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    def __repr__(self):
      return f"< {self.id} {self.name}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
      return f'< {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
