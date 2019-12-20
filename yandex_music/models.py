from sqlalchemy.schema import ForeignKeyConstraint, PrimaryKeyConstraint

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    sex = db.Column(db.String, default=None)
    playlists_count = db.Column(db.Integer)
    all_tracks_count = db.Column(db.Integer, default=0)
    fav_tracks_count = db.Column(db.Integer, default=0)
    playlists = db.relationship(
        "Playlist",
        backref="user",
        cascade="save-update, merge, delete, delete-orphan",
    )

    def __repr__(self):
        return (
            f"User {self.login}({self.name}, "
            f"{self.playlists_count} playlist(s))"
        )


playlist_track = db.Table(
    "playlist_track",
    db.Column("user_id", db.Integer),
    db.Column("playlist_id", db.Integer),
    db.Column(
        "track_id",
        db.Integer,
        db.ForeignKey("track.id", ondelete="CASCADE")
    ),
    PrimaryKeyConstraint("user_id", "playlist_id", "track_id"),
    ForeignKeyConstraint(
        ("user_id", "playlist_id"),
        ("playlist.user_id", "playlist.id"),
        ondelete="CASCADE"
    )
)


class Playlist(db.Model):
    user_id = db.Column(db.Integer)
    id = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    tracks_count = db.Column(db.Integer, default=0)
    duration = db.Column(db.String, default=None)
    duration_ms = db.Column(db.Integer, default=0)
    created = db.Column(db.String, default=None)
    modified = db.Column(db.String, default=None)
    tracks = db.relationship(
        "Track",
        secondary=playlist_track,
        backref=db.backref("playlists", lazy="dynamic"),
    )

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "id"),
        ForeignKeyConstraint(("user_id",), ("user.id",), ondelete="CASCADE")
    )

    def __repr__(self):
        return f"Playlist ({self.title}, {self.tracks_count} track(s))"


artist_track = db.Table(
    "artist_track",
    db.Column(
        "artist_id",
        db.Integer,
        db.ForeignKey("artist.id", ondelete="CASCADE")
    ),
    db.Column(
        "track_id",
        db.Integer,
        db.ForeignKey("track.id", ondelete="CASCADE")
    ),
    PrimaryKeyConstraint("artist_id", "track_id")
)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.String)
    duration = db.Column(db.String)
    duration_ms = db.Column(db.Integer)
    artists = db.relationship(
        "Artist",
        secondary=artist_track,
        backref=db.backref("tracks", lazy="dynamic"),
    )

    def __repr__(self):
        return f"Track ({self.title}, {self.year} year)"


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Artist {self.name}"
