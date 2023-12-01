import random,string
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from functools import wraps
from flask_wtf.csrf import generate_csrf
from pkg.user_routes import login_required
import os
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
#local Imports
from pkg import app,csrf
from pkg.models import db,User,Tracks,Genre,Albums,AlbumTrackAssociation,PlaylistTrackAssociation,Playlist
from pkg.forms import LogForm,RegForm,AlbumForm,PlaylistForm

@app.after_request
def after_request(response):
    response.headers["Cache-Control"]="no-cache, no-store, must-revalidate"
    return response



@app.route('/upload/tracks/dashboard')
@login_required
def dashboard():
        user = session.get('user')
        userdeets = db.session.query(User).filter(User.username == user).first()

        return render_template("user_admin/dashboard.html",userdeets=userdeets)
    
@app.route("/admin/addsongs", methods=["GET", "POST"])
@login_required
def addsongs():
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()
    if request.method == "GET":
        genre = db.session.query(Genre).all()
        tracks = db.session.query(Tracks).all()
        return render_template("user_admin/addsongs.html", genre=genre,tracks=tracks,userdeets=userdeets)
    else:
        # Retrieve the username from the session
        username = session.get("user")
        
        # Query the database to fetch the user object based on the username
        user = db.session.query(User).filter(User.username == username).first()

        if user is None:
            flash("User not found", category='error')
            return redirect(url_for('login'))

        allowed = ['jpg', 'png', 'jpeg','webp']
        songext = ['mp3', 'wav', 'm4a']
        fileobj = request.files['cover']
        song = request.files['song']
        filename = fileobj.filename
        songname = song.filename
        newname = "default.png"  # default cover

        if filename != '':
            pieces = filename.split('.')
            ext = pieces[-1].lower()
            if ext in allowed:
                newname = str(int(random.random()) * 10000000000) + filename
                fileobj.save('pkg/static/songcover/' + newname)
            else:
                flash("File extension not allowed", category='error')

        if songname != '':
            scatter = songname.split('.')
            exten = scatter[-1].lower()
            if exten in songext:
                sname = str(int(random.random() * 10000000000)) + songname
                song.save('pkg/static/uploaded_songs/' + sname)
            else:
                flash("File extension not allowed", category='error')

        ttitle = request.form.get('title')
        genre = request.form.get('genre')
        songcover = newname
        file = sname

        # Use 'user.userid' to create a new track with the correct artist ID
        track = Tracks(
            title=ttitle,
            track_artistid=user.userid,
            track_genreid=genre,
            track_cover=songcover,
            fileLocation=file
        )
        db.session.add(track)
        db.session.commit()

        if track.trackid:
            flash("Song has been added", category='success')
        else:
            flash("Please try again", category='error')

        return redirect(url_for('allsongs'))
    

@app.route('/alluploads')
def allsongs():
        
        user = session.get('user')
        userdeets = db.session.query(User).filter(User.username == user).first()
        songs = Tracks.query.filter_by(track_artistid=userdeets.userid).all()
        albums = Albums.query.filter_by(albumid=userdeets.userid).all()
        playlisted = Playlist.query.filter_by(playlistid=userdeets.userid).all()
        return render_template("user_admin/allsongs.html", songs=songs,userdeets=userdeets,albums=albums,playlisted=playlisted)




ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

@app.route("/edit/song/<int:id>/", methods=["POST", "GET"])
def edit_song(id):
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()

    if request.method == "GET":
        songs = db.session.query(Tracks).filter(Tracks.trackid == id).first_or_404()
        genre = db.session.query(Genre).all()
        return render_template("user_admin/editsongs.html", songs=songs, genre=genre, userdeets=userdeets)
    else:
        song2update = Tracks.query.get(id)
        song2update.title = request.form.get('title')
        song2update.track_genreid = request.form.get('genre')

        song = request.files.get('song')
        if song:
            if allowed_file(song.filename):
                filename = secure_filename(song.filename)
                song.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                song2update.song_path = filename
            else:
                flash("Invalid file format. Allowed formats: jpg, jpeg, png")
                return redirect("/alluploads")
        
        try:
            db.session.commit()
            flash("Song details were updated")
        except Exception as e:
            db.session.rollback()
            flash(f"Error occurred: {str(e)}", "error")
        
        return redirect("/alluploads")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/delete/<id>/",methods=['DELETE'])
def delete_store(id):
   
   return redirect()


@app.route('/create/album', methods=['GET', 'POST'])
def create_album():
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()
    # Retrieve the username from the session
    username = session.get('user')

    # Assuming you have the user object and associated tracks
    user = User.query.filter_by(username=username).first()

    
    user_tracks = Tracks.query.filter_by(track_artistid=user.userid).all()

    form = AlbumForm()

    form.album_tracks.choices = [(track.trackid, track.title) for track in user_tracks]
    if form.validate_on_submit():
        # Handle form submission here, including creating the album and associating selected tracks
        album_title = form.album_title.data

        # Secure the filename of the uploaded cover art file
        cover_art = secure_filename(form.cover_art.data.filename)

        album = Albums(albumtitle=album_title, album_userid=user.userid, coverArtlocation=cover_art)
        db.session.add(album)
        db.session.commit()

        selected_track_ids = form.album_tracks.data
        for track_id in selected_track_ids:
            album_track_association = AlbumTrackAssociation(album_id=album.albumid, track_id=int(track_id))
            db.session.add(album_track_association)
            db.session.commit()

        # Save the uploaded cover art file
        form.cover_art.data.save(f'pkg/static/upload_albums/{cover_art}')

        flash('Album created successfully!')
        return redirect(url_for('create_album'))
    return render_template('user_admin/addalbums.html', user=user, user_tracks=user_tracks, form=form,userdeets=userdeets)








@app.route('/create/playlist', methods=['GET', 'POST'])
def create_playlist():
    # Retrieve the user ID from the session
    user_id = session.get('user')
    loggedinuserid = db.session.query(User).filter(User.username == user_id).first()
    userdeets = db.session.query(User).filter(User.username == user_id).first()
    print(loggedinuserid.userid)

    # Retrieve user details based on the user ID stored in the session
    userdeetss = User.query.filter_by(userid=user_id).first()

    # Query user's tracks from the database
    user_tracks = Tracks.query.filter_by(track_artistid=loggedinuserid.userid).all()

    if request.method == 'POST':
        # Handle form submission here, including creating the playlist and associating selected tracks
        playlist_title = request.form.get('playlist_title')
        selected_track_ids = request.form.getlist('selected_tracks')

        playlist = Playlist(playlist_name=playlist_title, creator_userid=user_id)
        db.session.add(playlist)
        db.session.commit()

        for track_id in selected_track_ids:
            playlist_track_association = PlaylistTrackAssociation(playlist_id=playlist.playlistid, track_id=int(track_id))
            db.session.add(playlist_track_association)
            db.session.commit()

        flash('Playlist created successfully!')
        return redirect(url_for('create_playlist'))

    return render_template('user_admin/addplaylist.html',userdeets=userdeets, userdeetss=userdeetss, user_tracks=user_tracks)


@app.route('/search_tracks', methods=['POST'])
def search_tracks():
    query = request.form.get('query')  # Get the search query from the request

    # Perform the search in your database and filter tracks based on the query
    matching_tracks = Tracks.query.filter(Tracks.title.ilike(f'%{query}%')).all()

    # Prepare the response data as a list of dictionaries
    results = []
    for track in matching_tracks:
        results.append({
            'track_id': track.id,
            'title': track.title
        })

    # Return the matching tracks as JSON
    return jsonify(results)




@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    try:
        data = request.get_json()
        playlist_name = data.get('playlistName')
        selected_songs = data.get('selectedSongs', [])

        # Ensure playlist_name is not None or empty
        if not playlist_name:
            return jsonify({'error': 'Invalid playlist name'}), 400

        # Ensure selected_songs is a non-empty list of dictionaries
        if not isinstance(selected_songs, list) or not selected_songs:
            return jsonify({'error': 'Invalid selected songs data'}), 400

        # Retrieve the username from the session
        username = session.get('user')

        # Ensure user is logged in
        if username is None:
            return jsonify({'error': 'User not authenticated'}), 401

        # Retrieve the corresponding user record from the database based on the username
        user = db.session.query(User).filter(User.username == username).first()

        # Check if the user exists
        if user is None:
            return jsonify({'error': 'User not found'}), 404

        # Get the user ID from the retrieved user record
        user_id = user.userid

        # Create a new playlist with the specified name for the user
        playlist = Playlist(playlist_name=playlist_name, creator_userid=user_id)
        db.session.add(playlist)
        db.session.commit()

        # Extract track_ids from selected songs data
        track_ids = [song['id'] for song in selected_songs if 'id' in song]

        # Insert track_ids into the playlist_track_association table
        for track_id in track_ids:
            # Ensure track_id is not None or empty before creating association
            if track_id:
                playlist_track_association = PlaylistTrackAssociation(playlist_id=playlist.playlistid, track_id=track_id)
                db.session.add(playlist_track_association)

        db.session.commit()

        return jsonify({'message': 'Selected songs added to the playlist successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/get_data', methods=['GET'])
def get_data():
    search_query = request.args.get('query')

    # Fetch songs from the Tracks table in the database based on the search query
    songs = Tracks.query.filter(Tracks.title.ilike(f'%{search_query}%')).all()
    song_list = [{'id': song.trackid, 'title': song.title, 'artist': song.trackrel.username, 'type': 'song'} for song in songs]

    # Fetch albums from the Albums table in the database based on the search query
    albums = Albums.query.filter(Albums.albumtitle.ilike(f'%{search_query}%')).all()
    album_list = [{'id': album.albumid, 'title': album.albumtitle, 'artist': album.user.username, 'type': 'album'} for album in albums]

    # Combine songs and albums into a single list and put matching items at the top
    data_list = song_list + album_list
    matching_items = [item for item in data_list if search_query.lower() in item['title'].lower()]
    non_matching_items = [item for item in data_list if item not in matching_items]
    sorted_data = matching_items + non_matching_items

    # Return sorted songs and albums as JSON response
    return jsonify({'data': sorted_data})






def generate_string(howmany):
    x = random.sample(string.ascii_lowercase,howmany)
    return ''.join(x)




@app.route('/delete_song/<int:id>', methods=['POST',"GET"])
def delete_song(id):
    if request.method =='GET':
        song = Tracks.query.filter_by(trackid=id).first()
        db.session.delete(song)
        db.session.commit()
        flash(f'Song "{song.title}" deleted successfully!', 'success')
    return redirect(url_for('allsongs'))  # Assuming 'songs' is the route where songs are displayed


