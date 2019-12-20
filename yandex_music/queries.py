from . import db
from .models import Artist, Playlist, Track, User


class Query:
    """Queries executing class."""

    def __init__(self, login: str):
        self.__uid = self.__get_user_id(login)

    @staticmethod
    def commit(obj):
        db.session.add(obj)
        db.session.commit()

    def delete_playlists(self, ids: set):
        playlists = (
            Playlist.query
            .filter_by(user_id=self.__uid)
            .filter(Playlist.id.in_(ids))
            .all()
        )

        for playlist in playlists:
            db.session.delete(playlist)

        db.session.commit()

    @staticmethod
    def delete_tracks(playlist, ids: set):
        for track in playlist.tracks:
            if track.id in ids:
                playlist.tracks.remove(track)
                playlist.duration_ms -= track.duration_ms
                playlist.tracks_count -= 1

        db.session.commit()

    @staticmethod
    def delete_unused():
        Query.__delete_unused_tracks()
        Query.__delete_unused_artists()

    @staticmethod
    def delete_user(id_):
        db.session.delete(User.query.get(id_))
        Query.delete_unused()

    @staticmethod
    def get_artist(uid: int):
        return Artist.query.get(uid)

    @staticmethod
    def get_artist_genres(uid: int, artist: Artist):
        return [
            i[0]
            for i in artist.tracks
            .join(Track.playlists)
            .filter(Playlist.user_id == uid)
            .distinct()
            .values(Track.genre)
        ]

    def get_modified(self, _id: int):
        return self.get_playlist(_id).modified

    def get_playlist(self, id_: int):
        return self.get_user_playlist(self.__uid, id_)

    @staticmethod
    def get_playlist_artists(uid: int, _id: int):
        return (
            Artist.query
            .join(Artist.tracks)
            .join(Track.playlists)
            .filter(Playlist.user_id == uid, Playlist.id == _id)
            .all()
        )

    @staticmethod
    def get_playlist_artists_counter(uid: int, _id: int):
        playlist = Query.get_user_playlist(uid, _id)
        return [
            (
                sum(
                    [
                        1 for track in artist.tracks
                        if playlist in track.playlists
                    ]
                ),
                artist
            )
            for artist in Query.get_playlist_artists(uid, _id)
        ]

    @staticmethod
    def get_playlist_genre_tracks(uid: int, id_: int, genre: str):
        return (
            Track.query
            .filter_by(genre=genre)
            .join(Track.playlists)
            .filter(Playlist.user_id == uid, Playlist.id == id_)
            .all()
        )

    @staticmethod
    def get_playlist_genres(uid: int, id_: int):
        return set(
            i[0]
            for i in Track.query
            .join(Track.playlists)
            .filter(Playlist.user_id == uid, Playlist.id == id_)
            .values("genre")
        )

    @staticmethod
    def get_playlist_genres_counter(uid: int, id_: int):
        return [
            (len(Query.get_playlist_genre_tracks(uid, id_, genre)), genre)
            for genre in Query.get_playlist_genres(uid, id_)
            if genre
        ]

    def get_playlist_title(self, id_: int):
        return self.get_user_playlist_title(self.__uid, id_)

    def get_playlist_tracks_ids(self, _id: int):
        return [
            i[0]
            for i in Playlist.query
            .filter_by(user_id=self.__uid, id=_id)
            .join(Playlist.tracks)
            .values(Track.id)
        ]

    @staticmethod
    def get_playlist_year_tracks(uid: int, id_: int, year: int):
        return (
            Track.query
            .filter_by(year=year)
            .join(Track.playlists)
            .filter(Playlist.user_id == uid, Playlist.id == id_)
            .all()
        )

    @staticmethod
    def get_playlist_years(uid: int, id_: int):
        return set(
            i[0]
            for i in Track.query
            .join(Track.playlists)
            .filter(Playlist.user_id == uid, Playlist.id == id_)
            .values("year")
        )

    @staticmethod
    def get_playlist_years_counter(uid: int, id_: int):
        return [
            (len(Query.get_playlist_year_tracks(uid, id_, year)), year)
            for year in Query.get_playlist_years(uid, id_)
            if year
        ]

    @staticmethod
    def get_playlists_ids():
        return [i[0] for i in Playlist.query.values(Playlist.id)]

    @staticmethod
    def get_user(uid: int):
        return User.query.get(uid)

    @staticmethod
    def get_user_artist_tracks(uid: int, artist: Artist):
        return (
            artist.tracks
            .join(Track.playlists)
            .filter(Playlist.user_id == uid)
            .all()
        )

    @staticmethod
    def get_user_login(uid: int):
        return User.query.filter_by(id=uid).value("login")

    @staticmethod
    def get_user_playlist(uid: int, id_: int):
        return Playlist.query.get((uid, id_))

    @staticmethod
    def get_user_playlist_title(uid: int, id_: int):
        return Playlist.query.filter_by(user_id=uid, id=id_).value("title")

    def get_user_tracks_count(self, ids):
        return (
            Track.query
            .join(Track.playlists)
            .filter(Playlist.user_id == self.__uid, Playlist.id.in_(ids))
            .distinct()
            .count()
        )

    @staticmethod
    def get_users():
        return User.query.all()

    def insert_playlist(self, **params):
        playlist = Playlist(user_id=self.__uid, **params)

        Query.commit(playlist)

        return playlist

    @staticmethod
    def insert_track_with_artists(playlist, artists: list, **params):
        track = Track.query.get(params["id"])

        if not track:
            track = Track(**params)

            for artist in artists:
                artist_ = Artist.query.get(artist["id"])
                track.artists.append(artist_ if artist_ else Artist(**artist))

        playlist.tracks.append(track)
        playlist.duration_ms += track.duration_ms
        playlist.tracks_count += 1

    def insert_user(self, **params):
        user = User(**params)
        Query.commit(user)

        self.__uid = user.id

    @staticmethod
    def update_modified(_id: int, modified: str):
        Playlist.query.filter_by(id=_id).update({"modified": modified})
        db.session.commit()

    @staticmethod
    def update_playlist_duration(playlist, duration: str):
        playlist.duration = duration
        Query.commit(playlist)

    @staticmethod
    def update_playlist_title(_id: int, title: str):
        Playlist.query.filter_by(id=_id).update({"title": title})
        db.session.commit()

    def update_playlists_count(self, count: int):
        User.query.filter_by(id=self.__uid).update({"playlists_count": count})
        db.session.commit()

    def update_user_data(self, name, sex):
        user = User.query.get(self.__uid)
        user.name = name
        user.sex = sex
        user.fav_tracks_count = self.get_user_tracks_count([3])
        user.all_tracks_count = self.get_user_tracks_count(
            [i.id for i in user.playlists]
        )
        Query.commit(user)

    @staticmethod
    def __get_user_id(login: str):
        return User.query.filter_by(login=login).value("id")

    @staticmethod
    def __delete_unused_artists():
        for artist in Artist.query.filter_by(tracks=None).all():
            db.session.delete(artist)
        db.session.commit()

    @staticmethod
    def __delete_unused_tracks():
        for track in Track.query.filter_by(playlists=None).all():
            db.session.delete(track)
        db.session.commit()
