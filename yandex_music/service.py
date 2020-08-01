from datetime import datetime

from .network import Connection
from .queries import Query


class Service:
    """A user's data proccessing.

    Args:
        login: the user's login
    """

    def __init__(self, login: str):
        self._login = login
        self._query = Query(login)

    def download(self):
        """Add new user and its playlists."""
        common = self._common_info()

        self._add_user(common)

        self._add_playlists(common, common["playlistIds"])

        self._update_user_data(common)

    def update(self):
        """Update user's data and playlists."""
        common = self._common_info()
        local_ids = Query.get_playlists_ids()
        remote_ids = common["playlistIds"]
        diff = Service._get_differences(local_ids, remote_ids)

        if diff:
            if diff["add"]:
                self._add_playlists(common, diff["add"])
            if diff["delete"]:
                self._query.delete_playlists(diff["delete"])

            self._query.update_playlists_count(len(remote_ids))

        existed_ids = set(local_ids) - (diff["delete"] if diff else set())
        self._update_existed(
            [i for i in common["playlists"] if i["kind"] in existed_ids]
        )

        Query.delete_unused()

        self._update_user_data(common)

    def _add_playlist_tracks(self, playlist):
        playlist_info = self._get_playlist_info(playlist.id)

        Service._add_tracks_with_artists(
            playlist,
            playlist_info["tracks"],
            set(
                [int(str(i).split(":")[0]) for i in playlist_info["trackIds"]]
            )
        )

    def _add_playlists(self, common, ids):
        playlists = self._insert_playlists(common, ids)

        for playlist in playlists:
            self._add_playlist_tracks(playlist)
            Query.update_playlist_duration(
                playlist,
                Service._format_playlist_ms(playlist.duration_ms)
            )

    @staticmethod
    def _add_tracks_with_artists(playlist, tracks, ids_to_add):
        for track in tracks:
            track_id = int(track["id"])

            if track_id in ids_to_add:
                artists = [
                    {
                        "id": int(artist["id"]),
                        "name": artist["name"]
                    }
                    for artist in track["artists"]
                ]
                Query.insert_track_with_artists(
                    playlist,
                    artists,
                    id=track_id,
                    title=track["title"],
                    year=track["albums"][0].get("year"),
                    genre=track["albums"][0].get("genre"),
                    duration=Service._format_track_ms(track["durationMs"]),
                    duration_ms=track["durationMs"]
                )

                ids_to_add.remove(track_id)

            if not ids_to_add:
                break

    def _add_user(self, common):
        self._query.insert_user(
            id=common["owner"]["uid"],
            login=self._login,
            name=common["owner"]["name"],
            playlists_count=len(common["playlistIds"])
        )

    def _common_info(self):
        return Connection().get_json("playlists", self._login)

    @staticmethod
    def _format_date(date):
        if not date:
            return date
        return datetime.fromisoformat(date).strftime("%d %B %Y %H:%M:%S")

    @staticmethod
    def _format_playlist_ms(total_ms: int) -> str:
        """Format milliseconds to the string.

        :param total_ms: a number of milliseconds
        :return: "%H h. %M min. %S sec." format string
        """
        seconds = total_ms // 1000
        minutes = seconds // 60
        hours = minutes // 60

        return f"{hours} h. {minutes % 60} min. {seconds % 60} sec."

    @staticmethod
    def _format_track_ms(total_ms: int) -> str:
        """Format milliseconds to the string.

        :param total_ms: a number of milliseconds
        :return: "%M min. %S sec." format string
        """
        seconds = total_ms // 1000
        minutes = seconds // 60

        return f"{minutes:02} min. {seconds % 60:02} sec."

    @staticmethod
    def _get_differences(local_ids, remote_ids):
        local_set = set(local_ids)
        remote_set = set(remote_ids)
        diff = {
            "add": remote_set - local_set,
            "delete": local_set - remote_set
        }

        return diff if diff["add"] or diff["delete"] else None

    def _get_playlist_info(self, _id):
        return Connection().get_json(
            "playlist", self._login, _id
        )["playlist"]

    def _insert_playlists(self, common, ids_to_add):
        return [
            self._query.insert_playlist(
                id=playlist["kind"],
                title=playlist["title"],
                created=Service._format_date(playlist.get("created")),
                modified=Service._format_date(playlist.get("modified"))
            )
            for playlist in common["playlists"]
            if playlist["kind"] in ids_to_add
        ]

    def _update_existed(self, existed):
        for playlist in existed:
            _id = playlist["kind"]
            new_title = playlist["title"]
            new_modified = Service._format_date(playlist.get("modified"))

            if self._query.get_playlist_title(_id) != new_title:
                Query.update_playlist_title(_id, new_title)

            if not new_modified:
                self._update_playlist(_id)
            elif self._query.get_modified(_id) != new_modified:
                self._update_playlist(_id)
                Query.update_modified(_id, new_modified)

    def _update_playlist(self, _id):
        playlist_js = self._get_playlist_info(_id)
        local_ids = self._query.get_playlist_tracks_ids(_id)
        remote_ids = [
            int(str(i).split(":")[0])
            for i in playlist_js["trackIds"]
        ]

        diff = Service._get_differences(local_ids, remote_ids)

        if diff:
            playlist = self._query.get_playlist(_id)
            if diff["add"]:
                Service._add_tracks_with_artists(
                    playlist,
                    playlist_js["tracks"],
                    diff["add"]
                )
            if diff["delete"]:
                Query.delete_tracks(playlist, diff["delete"])

            Query.update_playlist_duration(
                playlist,
                Service._format_playlist_ms(playlist.duration_ms)
            )

    def _update_user_data(self, common):
        name = common["owner"]["name"]
        sex = None
        playlists = common["playlists"]

        if len(playlists) > 1:
            sex = playlists[1]["owner"].get("sex")

        self._query.update_user_data(name, sex)
