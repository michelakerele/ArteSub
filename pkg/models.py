from datetime import datetime,date
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    userid = db.Column(db.Integer(),primary_key=True,nullable=False,autoincrement=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120),nullable=True)
    profilepicture=db.Column(db.String(255))

    user_track = db.relationship('Tracks', backref='trackrel')
            

class Tracks(db.Model):
    trackid = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    track_artistid = db.Column(db.Integer(), db.ForeignKey('user.userid'), nullable=False)
    track_release_date = db.Column(db.DateTime, default=datetime.utcnow)  # Use the function itself as the default
    track_genreid = db.Column(db.Integer(), db.ForeignKey('genre.genreid'), nullable=False)
    
    track_cover = db.Column(db.String(100))
    fileLocation = db.Column(db.String(100))

    
    

    genre = db.relationship('Genre', backref='tracks')

    # Add backref for album tracks
    albums = db.relationship('Albums', secondary='album_track_association', backref='tracks')
    playlists = db.relationship('Playlist', secondary='playlist_track_association', backref='playlists')
    

    # Add a constructor to create a new track with the artist's ID
    def __init__(self, title, track_artistid, track_genreid, track_cover, fileLocation):
        self.title = title
        self.track_artistid = track_artistid  # Make sure this is a valid user ID
        self.track_genreid = track_genreid
        self.track_cover = track_cover
        self.fileLocation = fileLocation



class Genre(db.Model):
    genreid = db.Column(db.Integer(),primary_key=True,nullable=False,autoincrement=True)
    genre_name = db.Column(db.String(50),nullable = False)
    
    
    

class Playlist(db.Model):
    playlistid = db.Column(db.Integer(),primary_key=True,nullable=False,autoincrement=True)
    playlist_name = db.Column(db.String(50),nullable = False)
    playlist_desc = db.Column(db.Text())
    creator_userid = db.Column(db.Integer(),db.ForeignKey('user.userid'), nullable = False)

    user = db.relationship('User', backref='user')

class PlaylistTrackAssociation(db.Model):
    __tablename__ = 'playlist_track_association'

    association_id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlistid'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.trackid'), nullable=False)

    def __init__(self, playlist_id, track_id):
        self.playlist_id = playlist_id
        self.track_id = track_id

    def __repr__(self):
        return f'PlaylistTrackAssociation(association_id={self.association_id}, playlist_id={self.playlist_id}, track_id={self.track_id})'
    

class Albums(db.Model):
    albumid = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    albumtitle = db.Column(db.String(100), nullable=False)
    album_userid = db.Column(db.Integer(), db.ForeignKey('user.userid'), nullable=False)
    coverArtlocation = db.Column(db.String(100))

    # Add backref for album user
    user = db.relationship('User', backref='albums')




class AlbumTrackAssociation(db.Model):
    __tablename__ = 'album_track_association'
    album_id = db.Column(db.Integer(), db.ForeignKey('albums.albumid'), primary_key=True)
    track_id = db.Column(db.Integer(), db.ForeignKey('tracks.trackid'), primary_key=True)

    # Add backref for album tracks
    album = db.relationship('Albums', backref='album_songs')
    track = db.relationship('Tracks', backref='album_tracks')

class Comments(db.Model):
    commentid = db.Column(db.Integer(),primary_key=True,nullable=False,autoincrement=True)
    comment_userid = db.Column(db.Integer(),db.ForeignKey('user.userid'), nullable = False)
    comment_text = db.Column(db.Text())

    usercoment = db.relationship('User', backref='usercomment')


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class ListeningHistory(db.Model):
    __tablename__ = 'listening_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.trackid'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='listening_history')
    track = db.relationship('Tracks', backref='listening_history_track')


