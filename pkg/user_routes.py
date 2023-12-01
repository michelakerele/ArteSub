from flask import render_template,request,abort,redirect,flash,make_response,session,url_for,send_file
from werkzeug.security import generate_password_hash,check_password_hash
import os
from sqlalchemy import func
#local Imports
from functools import wraps
from pkg.models import User,db,Genre,Tracks,Albums,Playlist

from pkg import app,csrf
from pkg.forms import RegForm,LogForm,DpForm




@app.after_request
def after_request(response):
    response.headers["Cache-Control"]="no-cache, no-store, must-revalidate"
    return response

def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get("user") !=None: 
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect('/login')
    return login_check

@app.route('/user')
def homepage():
    if request.method=="GET":
            username = session.get("user")
            userdeets = db.session.query(User).filter(User.username == username).first()
            genre=db.session.query(Genre).all()
            tracks=db.session.query(Tracks).all()
            config_items=app.config
            return render_template('user/artist-dash.html',config_items=config_items,genre=genre,tracks=tracks,userdeets=userdeets)
    else:
        pass


        
    
@app.route('/login',methods=['POST','GET'])
def login():
    reg=LogForm()
    if request.method=="GET":
        return render_template('user/login.html',reg=reg)
    else:
        username = request.form.get("Username")
        pwd = request.form.get('Password')
        deets = db.session.query(User).filter(User.username==username).first()
        if deets != None:
            hashed_pwd = deets.password
            if check_password_hash(hashed_pwd,pwd) == True:
                session['user'] = deets.username
                return redirect("/")
            else:
                if username and pwd != deets:
                   flash("Username or password incorrect, Please try again")
                   return redirect("/login")
                else:
                    flash("Username or password incorrect, Please try again")
                    return redirect("/login")
                
@app.route('/logout')
def logout():
    if session.get('user')!=None:
        session.pop('user',None)
        flash('You have been logged out!' )
        return redirect('/login')
        

@app.route("/register", methods=["GET","POST"])
def register():
    regform=RegForm()
    if request.method =="GET":
        return render_template("user/register.html",regform=regform)
    else:
        if regform.validate_on_submit():
            fullName=regform.FirstName.data
            Username=regform.Username.data
            Email=regform.Email.data
            Password=regform.Password.data
            hashed_pwd=generate_password_hash(Password)
            user = User(fullname=fullName,username=Username,email=Email,password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            flash("An account has been created for you. Please login")
            return redirect("/login")
        else:
            return render_template("user/register.html",regform=regform)
        
@app.route("/playlist")
@login_required
def playlist():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    playlist = db.session.query(Playlist).all()
    
    return render_template("user/playlist.html",userdeets=userdeets,playlist=playlist)

@app.route("/topsongs")
@login_required
def topsongs():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    user = db.session.query(User).all()
    songs = db.session.query(Tracks).all()
    return render_template("user/topsongs.html", songs=songs,user=user,userdeets=userdeets)

@app.route("/topalbums")
@login_required
def topalbums():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    user = db.session.query(User).all()
    album = db.session.query(Albums).all()
    return render_template("user/topalbums.html",userdeets=userdeets,user=user,album=album,)

@app.route("/")
@login_required
def home():
    if request.method=="GET":
            username = session.get("user")
            userdeets = db.session.query(User).filter(User.username == username).first()
            genre=db.session.query(Genre).all()
            tracks=db.session.query(Tracks).all()
            config_items=app.config
            return render_template('user/artist-dash.html',config_items=config_items,genre=genre,tracks=tracks,userdeets=userdeets)
    else:
      return render_template("user/artist-dash.html")

@app.route("/about/")
@login_required
def about():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    return render_template("user/about.html",userdeets=userdeets)

@app.route("/profile")
@login_required
def profile():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    return render_template("user/profile.html",userdeets=userdeets)

@app.route("/user")
@login_required
def user():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    return render_template("user/artist-dash.html",userdeets=userdeets)

@app.route("/changeprofile", methods=["POST", "GET"])
@login_required
def change_profile():
    username = session.get("user")
    print("Username:", username)  # Debugging statement
    try:
        userdeets = db.session.query(User).filter(User.username == username).first()
    except Exception as e:
        print("Error during database query:", str(e))  # Debugging statement
        flash("An error occurred while fetching user data", category='error')
        return redirect(url_for('login'))
    if userdeets is None:
        flash("User not found", category='error')
        return redirect(url_for('login'))
    dpform = DpForm()
    if request.method == "GET":
        return render_template("user/changedp.html", dpform=dpform, userdeets=userdeets)
    else:
        if dpform.validate_on_submit():
            pix = request.files.get('dp')
            if pix:
                filename = pix.filename
                pix.save(os.path.join(app.config['USER_PROFILE'], filename))
                userdeets.profilepicture = filename
                db.session.commit()
                flash("Profile picture updated")
            else:
                flash("No file selected for upload", category='error')
            return redirect(url_for('change_profile'))
        else:
            return render_template("user/changedp.html", dpform=dpform, userdeets=userdeets)
        


@app.route("/play/<int:id>")
@login_required
def play_song(id):
    track = db.session.query(Tracks).get(id)
    username = session.get("user")
    user = db.session.query(User).filter(User.username == username).first()
    userdeet = db.session.query(Tracks).filter(Tracks.track_artistid == user.userid).first()
    userdeets = db.session.query(User).filter(User.username == username).first()
    users = db.session.query(User).all()
    songs=db.session.query(Tracks.fileLocation).filter(Tracks.trackid == id).first()
    return render_template("user/listennow.html", userdeet=userdeet,users=users,userdeets=userdeets,user=user,songs=songs,track=track)

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    search_term = request.form.get("search_term")
    if request.method == "POST":
        search_term = request.form.get("search_term")
        username = session.get("user")
        userdeets = db.session.query(User).filter(User.username == username).first()
        # Perform a case-insensitive search for tracks and artists
        songs = db.session.query(Tracks).filter(func.lower(Tracks.title).ilike(f"%{search_term.lower()}%")).all()
        artists = db.session.query(User).filter(func.lower(User.username).ilike(f"%{search_term.lower()}%")).all()
        return render_template("user/search_results.html", songs=songs, artists=artists,userdeets=userdeets,search_term=search_term)

    return render_template("user/search_results.html",userdeets=userdeets,search_term=search_term)

@app.route('/play/album/<int:album_id>')
@login_required
def play_album(album_id):
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    # Retrieve the album from the database
    album = Albums.query.get(album_id)

    # Retrieve the tracks associated with the album
    album_tracks = album.tracks
    songs = db.session.query(Albums).filter(Albums.albumid == album_id).all()
    return render_template('user/play_album.html', album=album, tracks=album_tracks,songs=songs,userdeets=userdeets)


@app.route('/play/playlist/<int:playlist_id>')
@login_required
def play_playlist(playlist_id):
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    # Retrieve the album from the database
    playlist = Playlist.query.get(playlist_id)

    # Retrieve the tracks associated with the album
    playlist_tracks = playlist.playlists
    songs = db.session.query(Playlist).filter(Playlist.playlistid == playlist_id).all()
    return render_template('user/play_playlist.html', playlist=playlist, tracks=playlist_tracks,songs=songs,userdeets=userdeets)

@app.route('/select-genre', methods=['GET'])
@login_required
def select_genre():
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    genres = Genre.query.all()  # Fetch all genres from the database
    return render_template('user_admin/select_genre.html', genres=genres,userdeets=userdeets)

@app.route('/songs_by_genre/',methods=['GET'])
@login_required
def songs_by_genre():
    selected_genre_id = request.args.get('genre')
    genre = Genre.query.get_or_404(selected_genre_id)
    songs = Tracks.query.filter_by(track_genreid=selected_genre_id).all()
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    return render_template('user_admin/songs_by_genre.html', genre=genre, songs=songs,userdeets=userdeets)

@app.errorhandler(404)
@login_required
def page_not_found(error):
    username = session.get("user")
    userdeets = db.session.query(User).filter(User.username == username).first()
    return render_template("user/error.html",error=error,userdeets=userdeets)