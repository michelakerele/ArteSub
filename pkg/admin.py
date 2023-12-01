
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for,send_file
from werkzeug.security import generate_password_hash,check_password_hash
import os
from sqlalchemy import func
#local Imports
from functools import wraps
from pkg.models import User,db,Genre,Tracks,Albums,Playlist,Admin

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
            return redirect('/admin_login')
    return login_check

@app.route('/admin_login', methods=['POST', 'GET'])

def admin_login():
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()
    users = db.session.query(User).all()
    Songs = db.session.query(Tracks).all()
    playlisted = db.session.query(Playlist).all()
    albums = db.session.query(Albums).all()
    if request.method == 'GET':
        return render_template("admin/login.html",Songs=Songs,users=users,albums=albums,playlisted=playlisted)
    else:
        username = request.form.get('username')
        password = request.form.get('pwd')  # Corrected field name from 'pwd' to 'password'
    
        deets = db.session.query(Admin).filter(Admin.username == username).first()
        if deets is not None:
            hashed_pwd = deets.password
            if check_password_hash(hashed_pwd, password):
                return render_template("admin/allusers.html",Songs=Songs,users=users,albums=albums,playlisted=playlisted)
        flash("Invalid credentials, try again")
        return redirect("/admin_login")
    
@app.route("/admin_dashboard")
@login_required
def sup_admin_dashboard():
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()
    users = db.session.query(User).all()
    user = db.session.query(User).all()
    Songs = db.session.query(Tracks).all()
    playlisted = db.session.query(Playlist).all()
    albums = db.session.query(Albums).all()
    return render_template("admin/allusers.html",Songs=Songs,users=users,albums=albums,playlisted=playlisted,user=user,userdeets=userdeets)


@app.route('/viewusersdeets/<int:userid>', methods=['GET'])

def viewusersdeets(userid):
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()
    user = User.query.get_or_404(userid)
    songs = Tracks.query.filter_by(track_artistid=userid)
    return render_template('admin/viewusersdeets.html', user=user,songs=songs,userdeets=userdeets)

@app.route('/delete_user/<int:user_id>', methods=['POST'])

def delete_user(user_id):
    user = session.get('user')
    userdeets = db.session.query(User).filter(User.username == user).first()
    # Check if the request is a POST request
    if request.method == 'POST':
        # Fetch the user from the database based on the provided user_id
        user_to_delete = User.query.get_or_404(user_id)

        # Delete the user from the database
        db.session.delete(user_to_delete)
        db.session.commit()

        # Optionally, you can flash a message indicating successful deletion
        flash('User successfully deleted!', 'success')

        # Redirect to an appropriate page after deletion, for example, the user list page
        return redirect(url_for('sup_admin_dashboard'))

    # Handle other HTTP methods if needed
    # For example, you can return an error message for unsupported methods
    return 'Method Not Allowed', 405



@app.route('/add_genre', methods=['POST',"GET"])

def add_genre():
    genre_name = request.form.get('genre_name')
    if genre_name:
        new_genre = Genre(genre_name=genre_name)
        db.session.add(new_genre)
        db.session.commit()
        flash('Genre added successfully!', 'success')
    else:
        flash('Genre name cannot be empty.', 'error')
    return render_template("admin/add_genre.html")



@app.route('/genres', methods=['GET'])

def display_genres():
    genres = Genre.query.all()
    return render_template('admin/allgenre.html', genres=genres)



@app.route('/delete_genre/<int:genre_id>', methods=['POST'])
@login_required
def delete_genre(genre_id):
    if request.method == 'POST':
        genre = Genre.query.get_or_404(genre_id)
        db.session.delete(genre)
        db.session.commit()
        flash(f'Genre "{genre.genre_name}" deleted successfully!', 'success')
    return redirect(url_for('display_genres'))


@app.route('/logoutadmin', methods=['GET'])

def logoutadmin():
    # Clear the session data or any other user-specific data
    session.clear()
    # Redirect to the home page or login page after logout
    return redirect(url_for('admin_login'))