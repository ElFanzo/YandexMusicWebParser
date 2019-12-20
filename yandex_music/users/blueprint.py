from flask import Blueprint, redirect, render_template, request, url_for

from ..forms import UserForm
from ..queries import Query
from ..service import Service

users = Blueprint("users", __name__, template_folder="templates")


@users.route("/", methods=["GET", "POST"])
def index():
    """Represent all users."""
    form = UserForm(request.form)

    if form.validate_on_submit():
        Service(form.login.data).download()

        form = UserForm()

    return render_template(
        "users/index.html",
        users=Query.get_users(),
        form=form
    )


@users.route("/<int:user_id>")
def user_page(user_id: int):
    """Represent a user."""
    user = Query.get_user(user_id)

    return render_template(
        "users/user_page.html",
        user=user,
        user_id=user_id,
        login=user.login
    )


@users.route("/<int:user_id>/update")
def user_update(user_id):
    """Update user and its data."""
    Service(Query.get_user_login(user_id)).update()

    return redirect(url_for("users.user_page", user_id=user_id))


@users.route("/<int:user_id>/delete")
def user_delete(user_id):
    """Delete user and its data."""
    Query.delete_user(user_id)

    return redirect(url_for("users.index"))


@users.route(
    "/<int:user_id>/playlists/<int:playlist_id>",
    methods=["GET", "POST"]
)
def playlist_page(user_id, playlist_id):
    """Represent a playlist."""
    if not playlist_id:
        return redirect(url_for("users.user_page", user_id=user_id))

    playlist = Query.get_user_playlist(user_id, playlist_id)

    return render_template(
        "users/playlist_page.html",
        playlist=playlist,
        user_id=user_id,
        login=playlist.user.login
    )


@users.route("/<int:user_id>/playlists/<int:playlist_id>/artists")
def playlist_artists(user_id, playlist_id):
    """Represent all artists in a playlist."""
    return render_template(
        "users/playlist_artists.html",
        counter=Query.get_playlist_artists_counter(user_id, playlist_id),
        playlist_id=playlist_id,
        playlist_title=Query.get_user_playlist_title(user_id, playlist_id),
        user_id=user_id,
        login=Query.get_user_login(user_id)
    )


@users.route("/<int:user_id>/playlists/<int:playlist_id>/genres")
def playlist_genres(user_id, playlist_id):
    """Represent all genres in a playlist."""
    return render_template(
        "users/playlist_genres.html",
        counter=Query.get_playlist_genres_counter(user_id, playlist_id),
        playlist_id=playlist_id,
        playlist_title=Query.get_user_playlist_title(user_id, playlist_id),
        user_id=user_id,
        login=Query.get_user_login(user_id)
    )


@users.route("/<int:user_id>/playlists/<int:playlist_id>/years")
def playlist_years(user_id, playlist_id):
    """Represent all release years in a playlist."""
    return render_template(
        "users/playlist_years.html",
        counter=Query.get_playlist_years_counter(user_id, playlist_id),
        playlist_id=playlist_id,
        playlist_title=Query.get_user_playlist_title(user_id, playlist_id),
        user_id=user_id,
        login=Query.get_user_login(user_id)
    )


@users.route("/<int:user_id>/artists/<int:artist_id>")
def artist_page(user_id, artist_id):
    """Represent an artist."""
    artist = Query.get_artist(artist_id)

    return render_template(
        "users/artist_page.html",
        artist=artist,
        genres=Query.get_artist_genres(user_id, artist),
        tracks=Query.get_user_artist_tracks(user_id, artist),
        user_id=user_id,
        login=Query.get_user_login(user_id)
    )


@users.route("/<int:user_id>/playlists/<int:playlist_id>/years/<int:year>")
def year_tracks(user_id, playlist_id, year):
    """Represent tracks released during a year in a playlist."""
    return render_template(
        "users/year_tracks.html",
        year=year,
        playlist_title=Query.get_user_playlist_title(user_id, playlist_id),
        playlist_id=playlist_id,
        tracks=Query.get_playlist_year_tracks(user_id, playlist_id, year),
        user_id=user_id,
        login=Query.get_user_login(user_id)
    )


@users.route(
    "/<int:user_id>/playlists/<int:playlist_id>/genres/<string:genre>"
)
def genre_tracks(user_id, playlist_id, genre):
    """Represent a genre tracks in a playlist."""
    return render_template(
        "users/genre_tracks.html",
        genre=genre,
        playlist_title=Query.get_user_playlist_title(user_id, playlist_id),
        playlist_id=playlist_id,
        tracks=Query.get_playlist_genre_tracks(user_id, playlist_id, genre),
        user_id=user_id,
        login=Query.get_user_login(user_id)
    )
