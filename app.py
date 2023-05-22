#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.


  places  = Venue.query.distinct('city','state').order_by('state').all()
  av_ob_list = [] # areas-venues object list
 
  # loop over all of the places
  for place in places:
  # categorize the venues of each place and place in a list
    vens = Venue.query.filter_by(city=place.city, state=place.state)
  # append to list
    av_ob_list.append({
      'area': {
        'city':place.city,
        'state':place.state
      },
      'venues': vens
  })
  print("here",av_ob_list)
  # show the error page STATUS 505
  
  return render_template('pages/venues.html', areas=av_ob_list)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  to_search = request.form['search_term']
  data=[]
  # seach for Hop should return "The Musical Hop".
  try:
    # query the venues for the name filter by lowercase name == lowercase search name
    found_vens= Venue.query.filter(Venue.name.ilike('%' + to_search + '%')).all()
    results['error'] = error
    for ven in found_vens:
      data.append({
        'id':ven.id,
        'name':ven.name,
        'upcomming_shows': Show.query.filter(Show.venue_id == ven.id, Show.startTime>datetime.utcnow()).count()
      })
    
  except:
    error = True 
  
  finally:
    # return the data with match
    result={
     'count': len(found_vens),
     'data':data
   }
    #return render_template('pages/search_venues.html', results=data, search_term=request.form['search_term'])
    return render_template('pages/search_venues.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  ven = Venue.query.filter_by(id = venue_id).all()[0]
  venue_data = None
  error = False
  try:
    # get the related show, and artist details
    shows = Show.query.filter_by(venue_id=venue_id).join(Artist, Show.artist_id == Artist.id).all()
    # Categorize the upcomming shows and the prev shows
    upcommingShows = []
    prevShows = []
    for show in shows:
      sh = {
          'artist_id': show.artist_id,
          'start_time': str(show.startTime),
          'artistName': show.artist.name,
          'artistImageLink': show.artist.image_link,
          'genre': show.venue.genres
      }
      if show.startTime > datetime.utcnow():
        upcommingShows.append(sh)
      else:
        prevShows.append(sh)
      # build response
    venue_data = {'id': ven.id, 'name': ven.name, 'city': ven.city, 'adress': ven.address, "state": ven.state, 'genres': ven.genres, "phone": ven.phone, "image_link": ven.image_link, "facebook_link": ven.facebook_link, "seeking_talent": ven.seeking_talent, "seeking_description": ven.seeking_desc, "past_shows": prevShows,
          "upcoming_shows": upcommingShows}
  except :
   
    error = True
  # return template response
  if not error:
    return render_template('pages/show_venue.html', venue=venue_data)
  else:
    return render_template('errors/404.html')

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
  error = False
  try:
    form = VenueForm(request.form)
    if form.validate_on_submit():
      ven = Venue(
        name=form.name.data, city=form.city.data,
        state=form.state.data, address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data
      )
    db.session.add(ven)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
  if  error or (not form.validate_on_submit()):
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed. Please enter valid inputs')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
 # return redirect('/')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  res = []
  error = False
  try:
    _artists = Artist.query.all()
    for artist in _artists:
      res.append({'id':artist.id,'name':artist.name})
  except:
    error = True 
  finally:
    if not error:
      return render_template('pages/artists.html', artists=res)
    else:
      render_template('errors/500.html')
 

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  to_search = request.form['search_term']
  ar_res = Artist.query.filter(Artist.name.ilike('%' + to_search + '%')).all()
  to_show_as_results = []
  for res in ar_res:
    to_show_as_results.append({
      'id':res.id,
      'name':res.name,
      'num_upcoming_shows': Show.query.filter(Show.artist_id == res.id, Show.start_time > datetime.now()).count()
    })
  result = {
    'count': len(ar_res),
    'data':to_show_as_results
  }
  return render_template('pages/search_artists.html', results=result, search_term=request.form.get('search_term', ''))
 

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist_found = Artist.query.filter_by(id = artist_id).all()[0]
  shows = Show.query.filter_by(artist_id = artist_found.id).join(Venue,Show.venue_id==Venue.id).all()
  error =  False
  try:
    upcomming = []
    prevs = []
    for show in shows:
      # artist show object
      a_s = {
        'venue_id':show.venue_id,
        'venue_image_link': show.venue.image_link,
        'start_time': str(show.startTime),
        'venue_name':show.venue.name
      }
      if show.startTime>datetime.utcnow():
        upcomming.append(a_s)
      else:
        prevs.append(a_s)
    
    to_return = {
      "id": artist_found.id,
      "genres": artist_found.genres,
      "name": artist_found.name,
      "city": artist_found.city,
      "phone": artist_found.phone,
      "state": artist_found.state,
      "facebook_link": artist_found.facebook_link,
      "seeking_venue": artist_found.seeking_venue,
      "image_link": artist_found.image_link,
      "seeking_description": artist_found.seeking_description,
      "past_shows":prevs,
      "upcoming_shows": upcomming,
    }
  except:
    error = True
    
  finally:
    if not error:
      return render_template('pages/show_artist.html', artist=to_return)
    else:
      return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  f_artist = Artist.query.filter_by(id = artist_id).all()[0]
  artist = {
      "id": f_artist.id,
      "name": f_artist.name,
      "city": f_artist.city,
      "genres": f_artist.genres,
      "phone": f_artist.phone,
      "state": f_artist.state,
      "seeking_venue": f_artist.seeking_venue,
      "facebook_link": f_artist.facebook_link,
      "image_link": f_artist.image_link,
      "seeking_description": f_artist.seeking_description
  }
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    form = VenueForm(request.form)
    ven = Venue(
        name=form.name.data, 
        city=form.city.data,
        state=form.state.data, 
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data
    )
    db.session.add(ven)
    db.session.commit()
  except:
   
    db.session.rollback()
   
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  ven = Venue.query.filter_by(id=venue_id).all()[0]
  venue={
    "id": ven.id,
    "name": ven.name,
    "genres": ven.genres,
    "address": ven.address,
    "city": ven.city,
    "state": ven.state,
    "phone": ven.phone,
    "facebook_link": ven.facebook_link,
    "seeking_talent": ven.seeking_talent,
    "seeking_description": ven.seeking_desc,
    "image_link": ven.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  error = False
  try:
    form = VenueForm(request.form)
    ven = Venue(
        name=form.name.data, city=form.city.data,
        state=form.state.data, address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data
    )
    db.session.add(ven)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form=ArtistForm()
  error = False
  # TODO: modify data to be the data object returned from db insertion
  try:
    form=ArtistForm()
    if form.validate_on_submit():
      artist = Artist(
      name = form.name.data, city = form.city.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      state = form.state.data, phone = form.phone.data
      )
    db.session.add(artist)
    db.session.commit()
   
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
    if not error and  form.validate_on_submit():
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
      db.session.rollback()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
    error = False
    places = Show.query.join(Venue,Show.venue_id == Venue.id).join(Artist,Show.artist_id == Artist.id).all()
    res = list()
    for place in places:
  # num_shows should be aggregated based on number of upcoming shows per venue.
     res.append({
      'venue_name':show.venue.name,
      'venue_id': show.venue_id,
      'artist_name':show.artist.name,
      'artist_id': show.artist_id,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.startTime)
    })
    size = len(res)
    return render_template('pages/shows.html', places=res,size = size)
 

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
    form = ShowForm(request.form)
    if form.validate_on_submit():
      to_add = Show(
      start_time = form.start_time.data,
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data
    )
    db.session.add(to_add)
    db.session.commit()
  except:
    error =True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
