from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")
 
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)